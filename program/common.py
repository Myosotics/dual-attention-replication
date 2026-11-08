"""Shared data and estimation code. Reads only the 15 active observed/proxy inputs."""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats, linalg
import statsmodels.api as sm
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = Path(__file__).resolve().parent
START, END = '2010-02-01', '2019-10-04'
SEED, REPS = 20261108, 500
CONTROL = ['BW','TMS','DFY','dADS','dEPU'] + [f'{x}_L{i}' for x in ['VIX','AbnTurn','MktRet'] for i in range(5)]
LABELS = {'ARA':'ARA','AIA':'AIA option proxy','BW':'BW (lagged monthly proxy)', 'TMS':'TMS (previous month)', 'DFY':'DFY (previous month)', 'dADS':'ΔADS', 'dEPU':'ΔEPU MA7 proxy','const':'Intercept'}
for x in ['VIX','AbnTurn','MktRet']:
    for i in range(5): LABELS[f'{x}_L{i}'] = f'{x} t' + (f'−{i}' if i else '')

class Source:
    def __init__(self, location):
        self.path = Path(location)
        self.z = zipfile.ZipFile(self.path) if self.path.is_file() else None
        self.audit=[]
    def read(self, name):
        if name.startswith(('未采用模拟','附录','模拟')): raise ValueError('Inactive input forbidden')
        b=self.z.read(name) if self.z else (self.path/name).read_bytes()
        self.audit.append({'file':name,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
        return pd.read_csv(io.BytesIO(b))
    def dated(self,name,datefmt=None):
        f=self.read(name);f['date']=pd.to_datetime(f.date,format=datefmt)
        if f.date.duplicated().any():raise ValueError('Duplicate dates: '+name)
        return f.set_index('date').sort_index()

def cli():
    p=argparse.ArgumentParser()
    p.add_argument('--data',type=Path,default=ROOT.parent/'group3_collected_data_v14.zip',help='data ZIP or extracted root directory')
    p.add_argument('--bootstrap-reps',type=int,default=REPS)
    args=p.parse_args()
    if args.bootstrap_reps not in (0,) and args.bootstrap_reps<2:p.error("bootstrap-reps must be 0 or at least 2")
    return args

def panel(location):
    src=Source(location)
    a=src.dated('ARA.csv','%d%b%Y').rename(columns={'ara':'ARA'})
    f=pd.DataFrame(index=a.index)
    f['ARA']=a.ARA
    f['AIA']=src.dated('AIA_option_proxy_替代/AIA_option_proxy.csv','%d%b%Y').aia_option_proxy
    f['MktRet']=src.dated('vwret_标普500替代/vwret.csv','%d%b%Y').vwret
    f['VIX']=src.dated('VIX_Cboe/VIX.csv').VIX
    f['AbnTurn']=src.dated('AbnTurn_volume_proxy/AbnTurn_volume_proxy.csv').AbnTurn_volume_proxy
    f['dADS']=src.dated('dADS_费城联储/dADS.csv').dADS
    f['dEPU']=src.dated('dEPU_proxy/dEPU_proxy.csv').dEPU_proxy
    # Previous-month values: TMS/DFY are shifted once. BW file is already lagged.
    for file,col,new,lag in [('TMS_月度/TMS_monthly.csv','tms','TMS',1),('DFY_月度/DFY_monthly.csv','dfy','DFY',1),('lBWx_一月滞后近似/lBWx_monthly_proxy.csv','lBWx_monthly_proxy','BW',0)]:
        m=src.dated(file)
        m.index=m.index+pd.offsets.MonthBegin(lag) if lag else m.index
        # As-of carry monthly observations, with a 40-calendar-day expiry.
        ix=m.index.get_indexer(f.index,method='pad')
        values=m[col].to_numpy()[np.maximum(ix,0)].astype(float)
        age=(f.index-m.index[np.maximum(ix,0)]).days
        values[(ix<0)|(age>40)]=np.nan
        f[new]=values
        f[new+'_effective_month']=m.index[np.maximum(ix,0)].strftime('%Y-%m')
        reference=m.index[np.maximum(ix,0)]-pd.offsets.MonthBegin(1)
        f[new+'_reference_month']=reference.strftime('%Y-%m')
    f['mnews26']=src.dated('mnews26/mnews26.csv').mnews26
    ted=src.dated('funding_stress_state/funding_stress_state.csv')
    for c in ['funding_stress_state','funding_stress_state_no_fill','TEDRATE_raw','TEDRATE_used','is_filled']:f[c]=ted[c]
    for x in ['VIX','AbnTurn','MktRet']:
        for i in range(5):f[f'{x}_L{i}']=f[x].shift(i)
    for i in range(1,7): f[f'F{i}']=f.MktRet.shift(-i)
    f['F2_6']=100*((1+f[[f'F{i}' for i in range(2,7)]]/100).prod(axis=1,min_count=5)-1)
    saved=src.dated('fvwret5/fvwret5.csv').fvwret5
    if not np.allclose(f.loc[saved.index,'F2_6'],saved,atol=1e-10,rtol=0):raise ValueError('Future-return mismatch')
    # State cutoffs follow attention-available original calendar, before regression complete cases.
    med_ara=float(f.loc[f.ARA.notna(),'VIX'].median())
    med_aia=float(f.loc[f.AIA.notna(),'VIX'].median())
    out=f.loc[START:END].copy()
    meta={'source':str(src.path.name),'window':[START,END],'target_rows':len(out),'vix_cutoff_ARA':med_ara,'vix_cutoff_AIA':med_aia,
          'ted_cutoff':0.32,'monthly_rule':'TMS/DFY previous calendar month; BW existing one-month lag; asof max40 calendar days. Publication vintages unverified.',
          'return_unit':'percent; no second x100','controls':CONTROL,'omitted':['AbnNews','Effective Spread','Short Sale Fee','All News','Appendix 3/4'],
          'actual_environment':{'python':__import__('sys').version.split()[0], 'numpy':np.__version__, 'pandas':pd.__version__, 'statsmodels':__import__('statsmodels').__version__, 'scipy':__import__('scipy').__version__},
          'bootstrap':'IID pairs bootstrap; fixed state labels and thresholds; seed20261108; SE is coefficient SD; no parameter tuning',
          'hodrick':'Not estimated. Original R hardcodes 23 regressors and uses an ambiguous 4-lag sum for H=6; do not relabel HAC as Hodrick.',
          'inputs':src.audit}
    return f,out,meta

def design(d,variables):
    return sm.add_constant(d[variables].astype(float),has_constant='add')

def fit(d,variables,y='F2_6',reps=0,seed=SEED):
    d=d.dropna(subset=[y]+variables).copy();X=design(d,variables); x=X.to_numpy();v=d[y].to_numpy();n,k=x.shape
    if n<=k or np.linalg.matrix_rank(x)!=k:raise ValueError('Insufficient sample or rank-deficient model')
    mod=sm.OLS(v,X).fit();b=mod.params.to_numpy();res=v-x@b
    inv=np.asarray(mod.normalized_cov_params)
    hc=inv@((x*res[:,None]).T@(x*res[:,None]))@inv*n/(n-k)
    # Calendar-preserving Newey-West: gaps receive zero scores, never compress omitted trading dates.
    pos=d['calendar_position'].astype(int).to_numpy();scores=np.zeros((pos.max()-pos.min()+1,k));scores[pos-pos.min()]=x*res[:,None]
    meat=scores.T@scores
    for lag in range(1,31):
        if lag>=len(scores):break
        cross=scores[lag:].T@scores[:-lag];meat+=(1-lag/31)*(cross+cross.T)
    hac=inv@meat@inv*n/(n-k)
    boot=None
    if reps:
        rng=np.random.default_rng(seed);draws=[]
        for _ in range(reps):
            idx=rng.integers(0,n,n);bb,_,rank,_=linalg.lstsq(x[idx],v[idx],lapack_driver='gelsy')
            if rank==k:draws.append(bb)
        if len(draws)<.95*reps:raise ValueError('Too many singular bootstrap samples')
        boot=np.cov(np.asarray(draws),rowvar=False,ddof=1)
    else:draws=[]
    return {'model':mod,'data':d,'names':X.columns.tolist(),'b':b,'hc':hc,'hac':hac,'boot':boot,'n':n,'k':k,'df':n-k,'r2adj':mod.rsquared_adj,'boot_valid':len(draws)}

def stat(m,c,method):
    w=np.zeros(m['k']);w[m['names'].index(c)]=1
    return contrast(m,w,method)

def contrast(m,w,method):
    coef=float(w@m['b']);cov=m[method]
    if cov is None:return coef,np.nan,np.nan,np.nan
    se=float(np.sqrt(max(0,w@cov@w)));t=coef/se if se>0 else np.nan
    return coef,se,t,float(2*stats.t.sf(abs(t),m['df']))

def star(p):return '***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
def cell(b,p):return f'{b:.3f}{star(p)}'
def tcell(t,p):return f'[{t:.2f}]{star(p)}'
def raw_rows(m,panel,model_id):
    rows=[]
    for name in m['names']:
        b,se,t,p=stat(m,name,'hac');_,sw,tw,pw=stat(m,name,'hc');_,sb,tb,pb=stat(m,name,'boot')
        rows.append({'panel':panel,'model':model_id,'variable':name,'coefficient':b,'se_HC1':sw,'t_HC1':tw,'p_HC1':pw,
                     'se_NW30':se,'t_NW30':t,'p_NW30':p,'ci95_NW30_low':b-stats.t.ppf(.975,m['df'])*se,'ci95_NW30_high':b+stats.t.ppf(.975,m['df'])*se,
                     'se_boot':sb,'t_boot':tb,'p_boot':pb,'bootstrap_valid':m['boot_valid'],'N':m['n'],'adj_R2':m['r2adj'],
                     'start':str(m['data'].index.min().date()),'end':str(m['data'].index.max().date()),'rank':m['k'],
                     'condition_number':float(m['model'].condition_number)})
    return rows

def markdown(df):
    return '| '+' | '.join(['指标']+list(map(str,df.columns)))+' |\n|'+ '|'.join(['---']*(len(df.columns)+1))+'|\n'+''.join('| '+' | '.join([str(i)]+[str(x) for x in row])+' |\n' for i,row in df.iterrows())

def export(here,title,panels,raw,meta,notes,extra=None,samples=None):
    here=Path(here);full=pd.DataFrame(raw)
    full.to_csv(here/'coefficients_long.csv',index=False,float_format='%.12g',encoding='utf-8-sig')
    (here/'run_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    note_lines=['注意：代理数据与缩减控制模型，不是原论文原始数据复现；结果未按原文方向调整。']+notes
    md=f'# {title}\n\n'+'\n\n'.join(note_lines)+'\n\n'
    for label,d in panels.items():
        md+=f'## {label}\n\n'+markdown(d)+'\n';d.to_csv(here/(label.split(':')[0].replace(' ','_')+'.csv'),encoding='utf-8-sig')
    (here/'results.md').write_text(md)
    html='<html lang="zh"><meta charset="utf-8"><style>body{font:16px Georgia,serif;margin:32px;color:#18212b}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{padding:6px 9px;text-align:right;border-bottom:1px solid #ddd}th{border-top:2px solid #111}th:first-child,td:first-child{text-align:left}h1{font-size:25px}p{line-height:1.6}caption{font-weight:bold;text-align:left;padding:12px}</style>'
    from html import escape
    html+=f'<h1>{escape(title)}</h1>'+''.join(f'<p>{escape(x)}</p>' for x in note_lines)
    for label,d in panels.items():html+=f'<h2>{escape(label)}</h2>'+d.to_html(border=0,escape=True)
    (here/'results.html').write_text(html+'</html>')
    with pd.ExcelWriter(here/'results.xlsx',engine='openpyxl') as w:
        for label,d in panels.items():d.to_excel(w,sheet_name=label.split(':')[0][:31])
        full.to_excel(w,sheet_name='coefficients',index=False)
        pd.DataFrame({'说明':note_lines}).to_excel(w,sheet_name='notes',index=False)
        if extra is not None:extra.to_excel(w,sheet_name='comparisons',index=False)
        if samples is not None:samples.to_excel(w,sheet_name='sample_audit',index=False)
        for ws in w.book.worksheets:
            ws.freeze_panes='B2';ws.auto_filter.ref=ws.dimensions
            for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='243B53')
            for column in ws.columns:
                letter=column[0].column_letter
                ws.column_dimensions[letter].width=min(75,max(16,max(len(str(c.value or '')) for c in column)+2))
            for row in ws.iter_rows():
                for c in row:c.alignment=Alignment(vertical='top',wrap_text=True)
    return full

def prepare(args):
    allf,d,meta=panel(args.data)
    d['calendar_position']=np.arange(len(d))
    return allf,d,meta

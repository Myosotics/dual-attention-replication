#!/usr/bin/env python3
"""独立运行：读取现有数据、生成回归变量并输出本表CSV。详见同目录README。"""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats, linalg
import statsmodels.api as sm

TABLE = 4
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
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
    if TABLE == 4:
        f['mnews26']=src.dated('mnews26/mnews26.csv').mnews26
    if TABLE == 3:
        ted=src.dated('funding_stress_state/funding_stress_state.csv')
        for c in ['funding_stress_state','funding_stress_state_no_fill','TEDRATE_raw','TEDRATE_used','is_filled']:
            f[c]=ted[c]
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

def prepare(args):
    _, d, meta = panel(args.data)
    d['calendar_position'] = np.arange(len(d))
    return d, meta


def save_panels(tables):
    out = HERE / 'result'
    out.mkdir(exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(out / name, encoding='utf-8-sig', index_label='指标 / statistic')
        print('已输出', out / name)

def group_table(d,attention,control,state,reps,cutoff=None):
    v=[attention]+control
    good=d.dropna(subset=['F2_6']+v+[state]).copy()
    if not set(good[state].unique()).issubset({0,1}):raise ValueError('Expected 0/1 state')
    high=fit(good.loc[good[state]==1],v,reps=reps)
    low=fit(good.loc[good[state]==0],v,reps=reps)
    good['G']=good[state]
    interactions=[]
    for x in v:
        name='Gx_'+x;good[name]=good.G*good[x];interactions.append(name)
    pooled=fit(good,v+['G']+interactions,reps=reps)
    b1=high['b'][high['names'].index(attention)];b0=low['b'][low['names'].index(attention)]
    diff=pooled['b'][pooled['names'].index('Gx_'+attention)]
    if not np.isclose(diff,b1-b0,atol=1e-8):raise ValueError('Interaction coefficient does not match subgroup difference')
    rows=['Coefficient','White HC1 t-stat','Boot t-stat','Hodrick t-stat (not estimated)','NW30 t-stat (supplement)','1 std. mag. (bps)','N','adj. R²']
    vals={}
    key=[]
    for label,m,var in [('High / Yes',high,attention),('Low / No',low,attention),('Difference',pooled,'Gx_'+attention)]:
        b,sw,tw,pw=stat(m,var,'hc');_,sb,tb,pb=stat(m,var,'boot');_,sn,tn,pn=stat(m,var,'hac')
        effect=b*m['data'][attention].std(ddof=1)*100 if label!='Difference' else np.nan
        vals[label]=[f'{b:.3f}',tcell(tw,pw),tcell(tb,pb) if reps else 'not run','—',tcell(tn,pn),f'{effect:.2f}' if np.isfinite(effect) else '',str(m['n']) if label!='Difference' else '',f"{m['r2adj']:.3f}" if label!='Difference' else '']
        key.append({'attention':attention,'state':state,'group':label,'coefficient':b,'se_HC1':sw,'t_HC1':tw,'p_HC1':pw,'se_boot':sb,'t_boot':tb,'p_boot':pb,
                    't_NW30':tn,'p_NW30':pn,'one_sd_effect_bps':effect,'N':m['n'],'start':str(m['data'].index.min().date()),'end':str(m['data'].index.max().date()),'cutoff':cutoff})
    return pd.DataFrame(vals,index=rows),key

def main():
    args = cli()
    d, meta = prepare(args)
    tables = {}
    # 沿用论文Panel顺序，先AIA，再ARA；不生成已取消的All News分支。
    for attention, filename in [('AIA', 'Panel_A_AIA_proxy.csv'), ('ARA', 'Panel_B_ARA.csv')]:
        table, key = group_table(d, attention, CONTROL, 'mnews26', args.bootstrap_reps)
        table.columns = ['Macro News | Yes (1)', 'Macro News | No (2)', 'Macro News | (1) − (2)']
        tables[filename] = table
        print(attention, 'Yes减No：', key[-1]['coefficient'], 'NW30 p=', key[-1]['p_NW30'])
    save_panels(tables)


if __name__ == '__main__':
    main()

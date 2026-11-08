"""State and event regressions; full interaction test for coefficient differences."""
from common import *

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
    raw=[]
    for name,m in [('high',high),('low',low),('difference_full_interaction',pooled)]:raw+=raw_rows(m,attention,state+':'+name)
    return pd.DataFrame(vals,index=rows),key,raw

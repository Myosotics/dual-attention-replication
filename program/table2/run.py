#!/usr/bin/env python3
"""Table 2: 8 ARA columns and 9 AIA-proxy columns, NW(30)."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *

def main():
    args=cli();_,d,meta=prepare(args);panels={};raw=[];samples=[];comparison=[]
    order=['ARA','AIA']+CONTROL+['const']
    for attention,pname in [('ARA','Panel A: Retail attention'),('AIA','Panel B: Institutional attention proxy')]:
        order=[attention]+(['ARA'] if attention=='AIA' else [])+CONTROL+['const']
        specs=[(f'F{i}',[attention]+CONTROL,f'({i}) t+{i}') for i in range(1,7)]
        specs += [('F2_6',[attention],'(7) t+2:t+6 no controls'),('F2_6',[attention]+CONTROL,'(8) t+2:t+6 controls')]
        if attention=='AIA':specs += [('F2_6',['AIA','ARA']+CONTROL,'(9) t+2:t+6 + ARA')]
        models=[]
        for y,variables,label in specs:
            m=fit(d,variables,y=y);models.append(m);raw.extend(raw_rows(m,attention,label))
            samples.append({'panel':attention,'model':label,'N':m['n'],'start':str(m['data'].index.min().date()),'end':str(m['data'].index.max().date()),'omitted_news':True})
        rowkeys=[x for x in order if any(x in m['names'] for m in models)]
        display={}
        for (y,v,label),m in zip(specs,models):
            vals=[]
            for name in rowkeys:
                if name in m['names']:
                    b,s,t,p=stat(m,name,'hac');vals += [cell(b,p),f'[{t:.2f}]']
                else:vals+=['','']
            vals += [str(m['n']),f"{m['r2adj']:.3f}"]
            display[label]=vals
        index=[]
        for name in rowkeys:index += [LABELS.get(name,name),'t-stat: '+LABELS.get(name,name)]
        index+=['N','adj. R²'];panels[pname]=pd.DataFrame(display,index=index)
        selected=models[7];b,se,t,p=stat(selected,attention,'hac')
        comparison.append({'panel':attention,'model':'column8 reduced available controls','coef':b,'t_NW30':t,'p_NW30':p,'one_sd_effect_bps':b*selected['data'][attention].std(ddof=1)*100,'N':selected['n'], 'paper_col8_coef':-4.137 if attention=='ARA' else .927})
    meta['bootstrap_reps']=0
    export(Path(__file__).parent,'Table 2 — 当前可得数据回归',panels,raw,meta,[
        '结构沿用原表：Panel A共8列，Panel B共9列；括号为Newey–West(30) t值，星号按该t值；OLS含截距。',
        '第1—6列为未来单日收益，第7列为未来第2—6日复合收益无控制，第8列加入可得控制，Panel B第9列再加入ARA。',
        'AbnNews已省略；AIA、AbnTurn、ΔEPU及市场收益采用代理。BW/TMS/DFY映射规则、当前历史版本及较短样本造成与原表差异。'
    ],extra=pd.DataFrame(comparison),samples=pd.DataFrame(samples))
    pd.DataFrame(comparison).to_csv(Path(__file__).parent/'key_results.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(samples).to_csv(Path(__file__).parent/'sample_audit.csv',index=False,encoding='utf-8-sig')
    d.to_csv(Path(__file__).parents[1]/'analysis_panel.csv',index_label='date',float_format='%.12g')
    pd.DataFrame(meta['inputs']).to_csv(Path(__file__).parents[1]/'input_sources_sha256.csv',index=False)
    print('Table2 done',[(x['panel'],x['N'],round(x['coef'],4)) for x in comparison])

if __name__=='__main__':main()

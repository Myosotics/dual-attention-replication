#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from grouped import group_table

def main():
    args=cli();_,d,meta=prepare(args);panels={};key=[];raw=[]
    for attention in ['ARA','AIA']:
        state='VIX_high_'+attention;cut=meta['vix_cutoff_'+attention]
        d[state]=(d.VIX>cut).astype(int)
        tables=[]
        for name,control,s,cutoff in [('VIX',[x for x in CONTROL if x!='VIX_L0'],state,cut),('TED funding stress (extension)',CONTROL,'funding_stress_state',.32)]:
            t,k,rr=group_table(d,attention,control,s,args.bootstrap_reps,cutoff);t.columns=[name+' | '+c for c in t.columns];tables.append(t);key+=k;raw+=rr
        panels[('Panel A' if attention=='ARA' else 'Panel B')+': '+attention]=pd.concat(tables,axis=1)
        t,k,rr=group_table(d,attention,CONTROL,'funding_stress_state_no_fill',args.bootstrap_reps,.32)
        panels['Sensitivity '+attention+': TED no fill']=t;key+=k;raw+=rr
    meta['bootstrap_reps']=args.bootstrap_reps
    export(Path(__file__).parent,'Table 3 — 市场状态：VIX与TED融资压力扩展',panels,raw,meta,[
        '原有效价差与股票借贷费用分支不估计；TED另列为融资压力扩展，不是原−75.70bp的复现。',
        'VIX阈值按各注意力可得日期的中位数，回归完整案例筛选前固定；VIX分组遵循原Stata规格，省略当期VIX但保留1—4阶滞后。TED模型包含当期VIX。',
        '差异列是全交互回归中高组减低组的系数，允许截距和全部控制系数不同，不以两组显著性不同代替差异检验。',
        'White为HC1；Boot为500次IID成对重抽样的系数标准差（若命令修改次数则以metadata为准），固定分组。NW30为保留交易日间隔的补充，不能称作Hodrick。',
        'Hodrick行保留原表位置但标为未估计：原提供R代码硬编码变量数及窗口，当前未对其方法作无歧义移植；不填造该t值。',
        'TED同时展示默认短缺口沿用与不填补版本；1标准差效应采用各组实际回归样本的注意力标准差，单位基点。'
    ],extra=pd.DataFrame(key))
    pd.DataFrame(key).to_csv(Path(__file__).parent/'key_results.csv',index=False,encoding='utf-8-sig')
    print('Table3 done')

if __name__=='__main__':main()

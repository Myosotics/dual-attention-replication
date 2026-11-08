#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from grouped import group_table

def main():
    args=cli();_,d,meta=prepare(args);panels={};key=[];raw=[]
    for attention,label in [('AIA','Panel A: AIA option proxy'),('ARA','Panel B: ARA')]:
        t,k,rr=group_table(d,attention,CONTROL,'mnews26',args.bootstrap_reps)
        t.columns=['Macro News | Yes (1)','Macro News | No (2)','Macro News | (1) − (2)'];panels[label]=t;key+=k;raw+=rr
    meta['bootstrap_reps']=args.bootstrap_reps
    export(Path(__file__).parent,'Table 4 — Macro News：公告窗口与非公告窗口',panels,raw,meta,[
        '保留原Panel顺序：A为AIA代理，B为ARA；只输出Macro News有／无公告及差异三列，取消All News。',
        'mnews26使用官方FOMC、非农、PPI公告日期重建未来第2—6个交易日窗口；不为匹配原N调整事件。',
        '使用可得控制，省略AbnNews。White为HC1；Boot为500次IID成对重抽样（实际次数见metadata）；差异使用全交互模型。',
        'Hodrick行未估计，保留位置；NW30为另行标注的交易日间隔HAC补充，绝不当作Hodrick。星号按所在行t检验。',
        'AIA是期权成交量代理，不能将其结果解读为直接验证机构阅读行为。原文+20.82bp仅供对比。'
    ],extra=pd.DataFrame(key))
    pd.DataFrame(key).to_csv(Path(__file__).parent/'key_results.csv',index=False,encoding='utf-8-sig')
    print('Table4 done')

if __name__=='__main__':main()

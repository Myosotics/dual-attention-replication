#!/usr/bin/env python3
"""对日度7日移动平均计算连续自然日一阶差分，无须联网或第三方库。"""
import csv
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal
HERE = Path(__file__).resolve().parent

def main():
    with (HERE/'EPU_Daily_7day_MA.csv').open(encoding='utf-8-sig',newline='') as f:
        records=[(date(int(r['year']),int(r['month']),int(r['day'])),Decimal(r['daily_policy_moving_average'])) for r in csv.DictReader(f)]
    records.sort()
    if len(records)!=len({d for d,v in records}):
        raise ValueError('源文件存在重复日期')
    for (previous,_),(current,_) in zip(records,records[1:]):
        if current-previous!=timedelta(days=1):
            raise ValueError(f'自然日不连续：{previous} 到 {current}；不能跨缺口计算日差分')
    with (HERE/'dEPU_proxy.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['date','dEPU_proxy'])
        for i,(day,value) in enumerate(records):
            w.writerow([day.isoformat(),'' if i==0 else format(value-records[i-1][1],'f')])
    print(f'生成 dEPU_proxy.csv：{len(records)} 个自然日，首日差分为空，其余 {len(records)-1} 个有效值')

if __name__=='__main__':
    main()

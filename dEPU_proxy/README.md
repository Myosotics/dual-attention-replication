# dEPU_proxy：日度 EPU 七日移动平均的一阶差分

本指标使用已收集的真实公开数据构造，作为论文 ΔEPU 的替代控制变量。它不是原始日度 EPU 的差分，也不是随机模拟值。

## 文件与来源

- `EPU_Daily_7day_MA.csv`：日度七日移动平均，正式计算输入。来源：https://www.policyuncertainty.com/media/Daily_Policy_Moving_Average.csv
- `EPU_US_Monthly.csv`：月度新闻政策不确定性指数，仅作参考保留，不参与计算。来源：https://www.policyuncertainty.com/media/US_Policy_Uncertainty_Data.csv
- `build.py`：Python 3 标准库脚本，无须联网。
- `dEPU_proxy.csv`：已生成的单指标结果，列为 `date,dEPU_proxy`。

## 定义与运行

令 M(t) 表示源文件中的 EPU 七日移动平均，计算：

`dEPU_proxy(t) = M(t) - M(t-1)`

这里 t-1 指前一个自然日。先在源文件完整自然日序列中计算，再按日期合并交易日数据；周一使用周一减周日，不是周一减周五。脚本不填补缺失、不插值；重复或不连续日期会报错。首日没有前一日输入，输出为空。使用 Decimal 保留源 CSV 的十进制差分精度，不做标准化或百分比变化。

在此文件夹运行：

```bash
python3 build.py
```

月度 EPU 不用于填充或约束日差分。正式回归将控制项映射至 `dEPU_proxy`，结果须标注采用平滑指数差分代理。原论文 dEPU 的精确口径仍需原始日度序列及作者定义。现有包不运行回归；共享生成器中保留的模拟 EPU 仅是重建其他历史模拟列的内部中间量，不是当前提供的 EPU 控制指标。

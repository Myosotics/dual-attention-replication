# Table 3

运行 `python program/table3/run.py`。

`results.xlsx`保留ARA/AIA两个Panel的VIX高、低、差异，并将TED融资压力另列为扩展；另有TED不填补敏感性页。有效价差与原股票借贷费用不估计。

表中有White HC1、500次IID bootstrap和补充NW30推断。原Hodrick行明确未估计，不能将NW值当成Hodrick。`key_results.csv`记录分组样本和系数，`coefficients_long.csv`含全交互模型完整系数。

详细定义和限制见上级README及结果文件说明。

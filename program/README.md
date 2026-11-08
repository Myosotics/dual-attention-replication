# Table 2、3、4：程序与实际估计结果

本目录使用根目录 `group3_collected_data_v14.zip` 的已取得数据运行回归，不读取任何模拟列或附录交易变量。数据ZIP保持原样；本目录是在其基础上新增的程序和结果。

## 从哪里看结果

| 目录 | 结构 | 主要结果文件 |
|---|---|---|
| [table2](table2/) | Panel A：ARA 8列；Panel B：AIA代理9列；控制变量逐行列出 | [Excel](table2/results.xlsx)、[Markdown](table2/results.md)、本地打开results.html |
| [table3](table3/) | ARA/AIA代理分别列VIX高、低、差异；TED另列为扩展，另附不填补敏感性 | [Excel](table3/results.xlsx)、[Markdown](table3/results.md)、本地打开results.html |
| [table4](table4/) | 按原顺序Panel A AIA、Panel B ARA；Macro News Yes、No、差异三列 | [Excel](table4/results.xlsx)、[Markdown](table4/results.md)、本地打开results.html |

每个目录还有 `run.py`、便于计算的 `key_results.csv`、未四舍五入至展示精度的 `coefficients_long.csv` 和记录输入哈希、软件版本、分组阈值的 `run_metadata.json`。Excel含可对比面板、完整系数、样本或分组记录、说明页。

共同代码位于 `common.py` 和 `grouped.py`；`analysis_panel.csv` 为实际合并并生成滞后／未来收益的日度面板（15个指标中备查项不重复纳入模型），`input_sources_sha256.csv` 记录读取的源文件。`validation_report.json` 为数据和估计核验结果。

## 一键运行

需要Python 3.10及以上，推荐3.12。在仓库根目录：

```bash
python -m pip install -r program/requirements.txt
python program/run_all.py
```

单独重建某张表：

```bash
python program/table2/run.py
python program/table3/run.py
python program/table4/run.py
```

默认读取仓库根目录的数据ZIP，无需先解压。也可指定同版ZIP或其解压根目录：

```bash
python program/run_all.py --data /path/to/group3_collected_data_v14.zip
python program/run_all.py --data /path/to/extracted_data
python program/validate.py
```

Table 3、4默认500次bootstrap，固定种子20261108。可用 `--bootstrap-reps 1000` 改次数；这将重写结果，metadata记录实际次数，不是为了挑显著结果。关闭bootstrap用0，表中明确显示未运行。若本地BLAS多线程导致运行缓慢，可以限制 `OPENBLAS_NUM_THREADS=1`、`OMP_NUM_THREADS=1`。

## 数据对齐及模型口径

1. **共同日期**：现有已生成的收益和AIA代理覆盖2010-02-01—2019-10-04，共2,437个交易日。ARA虽然更长，本程序不擅自扩展已确认的收益样本。Table 2各模型目前均为2,437日；TED不填补敏感性为2,376日。
2. **先生成后筛选**：按ARA完整股票交易日历合并日收益，先生成当期、1—4阶滞后和未来第1—6日收益，再筛选分析窗口。未来第2—6日回报用复合方式计算，与已保存fvwret5逐日核对；不在删除缺失后的序列上跨日移位。
3. **收益单位**：现有vwret已是百分数，读取后不再乘100。其源为sp500d.csv中的vwretx，即标普500范围、不含现金分红的市值加权收益；不是作者全市场CRSP口径。1标准差效应（基点）= 系数 × 对应实际估计样本注意力标准差 × 100。
4. **月度控制**：TMS、DFY使用前一日历月值，最多沿用40个自然日；BW输入文件已经滞后一个月，不再重复滞后。面板保留各月度项的reference_month、effective_month。此为明确的可执行近似，未证明每项月度数据在月初均已实际发布，也未复原当时版本；不能称严格实时交易策略。
5. **其他控制**：包含BW、TMS、DFY、ΔADS、ΔEPU代理，以及VIX、AbnTurn代理、MktRet的当期与1—4阶滞后。AbnNews完全省略，绝不填入历史模拟值。Table 2第7列按原表不加控制，Panel B第9列额外加ARA。
6. **Table 3阈值**：VIX在各注意力可得日期上先计算中位数，再筛选回归完整样本。ARA阈值15.57，AIA代理阈值15.53；这不是强行沿用原AIA阈值15.29。原Stata的VIX分组模型不加当期VIX，保留1—4阶滞后，本程序照此执行。TED模型加当期VIX；TED阈值沿用既定ARA全样本的0.32个百分点。均为描述性全样本阈值，不是实时预测阈值。
7. **TED缺失**：读取此前确认的默认填补及严格不填补两列，不重新推断／填造利差。主窗口内61日为原缺失；剔除后为2,376日，与完整ARA期原缺100日不矛盾。
8. **Table 4事件**：读取真实官方日期重建的mnews26，不调整事件去匹配论文N。当前Yes=1,324日，No=1,113日。All News取消。

## 估计与原表结构

- **Table 2**：OLS点估计；Newey–West(30)、Bartlett权重，有限样本因子N/(N−K)，t分布自由度N−K；报告调整R²。星号使用对应NW p值。
- **Table 3、4**：按原表保留Coefficient、White、Boot、Hodrick、1 std. mag.、N等行。White是HC1。Boot是500次IID成对重抽样后系数的标准差，报告原点估计除以该标准差的t比率；不是block bootstrap或bootstrap-t。分组标签与阈值固定，不重新选事件或中位数。
- **差异检验**：合并样本回归中加入组别、注意力与组别交互，以及所有控制与组别交互；允许截距和全部斜率随组变化。差异系数等于两组分别OLS的“高减低”或“Yes减No”，运行时逐项核验。差异列N在展示表中留空，原始长表记录实际合并样本N。
- **Hodrick限制**：原提供 `Hodrick1992.R` 固定23个变量；H=6时用2至5的4项和，且未提供当前各分组的无歧义实现。本程序不把有歧义的移植填成Hodrick结果。该行保留位置，数值显示“—”，明确未估计。
- **重叠收益的补充**：另列NW30 t-stat。组内样本若日期不连续，HAC用原股票交易日位置插入零score，保留实际交易日间隔，不把两段分隔很久的日期当相邻日。不能把这个NW行叫Hodrick。White和IID bootstrap未充分解决收益重叠，解释结论时同时看NW行。
- **星号**：10%、5%、1%分别为*、**、***，每种t值使用自身p值，不混用标准误。

## 当前实际结果：没有强行贴近原论文

| 对照重点 | 本组实际估计 | 怎样解释 |
|---|---|---|
| Table 2 ARA第8列 | 系数−1.3635，NW30 t=−1.10，p=0.273；1标准差效应−7.28bp | 方向为负，统计证据不足；未复现原全控制−22.34bp及其显著性。 |
| Table 3 ARA VIX高减低 | 差异−1.5004，NW30 p=0.670 | 高VIX组系数更负，但组间差异不显著。 |
| Table 4 AIA代理 Macro Yes减No | 差异0.0707，NW30 p=0.826 | 未找到显著的宏观窗口预测增强；不能声称复现原+20.82bp机制。 |

注意力、收益范围、控制项、样本期和事件重建均有变化，不能据这些结果否定原论文，也不能反过来调整样本／参数直到显著。TED仅为融资压力扩展；价差、借贷费用、All News及附录交易机制均不在当前复现范围。

原表列结构与模型参考：用户提供论文Table 2—4及作者 `DHHP_main_results.do`。上述限制也写入每张结果表，方便截图或单独转发时保留口径。

# Table 3 — 市场状态：VIX与TED融资压力扩展

注意：代理数据与缩减控制模型，不是原论文原始数据复现；结果未按原文方向调整。

原有效价差与股票借贷费用分支不估计；TED另列为融资压力扩展，不是原−75.70bp的复现。

VIX阈值按各注意力可得日期的中位数，回归完整案例筛选前固定；VIX分组遵循原Stata规格，省略当期VIX但保留1—4阶滞后。TED模型包含当期VIX。

差异列是全交互回归中高组减低组的系数，允许截距和全部控制系数不同，不以两组显著性不同代替差异检验。

White为HC1；Boot为500次IID成对重抽样的系数标准差（若命令修改次数则以metadata为准），固定分组。NW30为保留交易日间隔的补充，不能称作Hodrick。

Hodrick行保留原表位置但标为未估计：原提供R代码硬编码变量数及窗口，当前未对其方法作无歧义移植；不填造该t值。

TED同时展示默认短缺口沿用与不填补版本；1标准差效应采用各组实际回归样本的注意力标准差，单位基点。

## Panel A: ARA

| 指标 | VIX | High / Yes | VIX | Low / No | VIX | Difference | TED funding stress (extension) | High / Yes | TED funding stress (extension) | Low / No | TED funding stress (extension) | Difference |
|---|---|---|---|---|---|---|
| Coefficient | -2.192 | -0.692 | -1.500 | -0.436 | -1.303 | 0.866 |
| White HC1 t-stat | [-1.44] | [-0.54] | [-0.76] | [-0.26] | [-1.20] | [0.43] |
| Boot t-stat | [-1.44] | [-0.59] | [-0.76] | [-0.28] | [-1.23] | [0.42] |
| Hodrick t-stat (not estimated) | — | — | — | — | — | — |
| NW30 t-stat (supplement) | [-1.11] | [-0.29] | [-0.43] | [-0.17] | [-0.85] | [0.26] |
| 1 std. mag. (bps) | -11.85 | -3.56 |  | -2.58 | -6.52 |  |
| N | 1208 | 1229 |  | 796 | 1641 |  |
| adj. R² | 0.022 | 0.033 |  | 0.032 | 0.023 |  |

## Sensitivity ARA: TED no fill

| 指标 | High / Yes | Low / No | Difference |
|---|---|---|---|
| Coefficient | -0.370 | -1.317 | 0.947 |
| White HC1 t-stat | [-0.22] | [-1.22] | [0.47] |
| Boot t-stat | [-0.22] | [-1.22] | [0.47] |
| Hodrick t-stat (not estimated) | — | — | — |
| NW30 t-stat (supplement) | [-0.14] | [-0.88] | [0.28] |
| 1 std. mag. (bps) | -2.19 | -6.54 |  |
| N | 776 | 1600 |  |
| adj. R² | 0.036 | 0.027 |  |

## Panel B: AIA

| 指标 | VIX | High / Yes | VIX | Low / No | VIX | Difference | TED funding stress (extension) | High / Yes | TED funding stress (extension) | Low / No | TED funding stress (extension) | Difference |
|---|---|---|---|---|---|---|
| Coefficient | 0.326 | -0.166 | 0.491 | 0.267 | 0.109 | 0.159 |
| White HC1 t-stat | [1.49] | [-1.03] | [1.81]* | [1.00] | [0.67] | [0.51] |
| Boot t-stat | [1.61] | [-1.01] | [1.88]* | [1.01] | [0.67] | [0.51] |
| Hodrick t-stat (not estimated) | — | — | — | — | — | — |
| NW30 t-stat (supplement) | [1.20] | [-0.79] | [1.43] | [0.68] | [0.52] | [0.36] |
| 1 std. mag. (bps) | 12.92 | -4.78 |  | 8.16 | 3.99 |  |
| N | 1218 | 1219 |  | 796 | 1641 |  |
| adj. R² | 0.022 | 0.034 |  | 0.033 | 0.022 |  |

## Sensitivity AIA: TED no fill

| 指标 | High / Yes | Low / No | Difference |
|---|---|---|---|
| Coefficient | 0.250 | 0.116 | 0.134 |
| White HC1 t-stat | [0.93] | [0.71] | [0.43] |
| Boot t-stat | [0.93] | [0.70] | [0.43] |
| Hodrick t-stat (not estimated) | — | — | — |
| NW30 t-stat (supplement) | [0.65] | [0.56] | [0.30] |
| 1 std. mag. (bps) | 7.60 | 4.25 |  |
| N | 776 | 1600 |  |
| adj. R² | 0.037 | 0.026 |  |


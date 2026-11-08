# Table 4 — Macro News：公告窗口与非公告窗口

注意：代理数据与缩减控制模型，不是原论文原始数据复现；结果未按原文方向调整。

保留原Panel顺序：A为AIA代理，B为ARA；只输出Macro News有／无公告及差异三列，取消All News。

mnews26使用官方FOMC、非农、PPI公告日期重建未来第2—6个交易日窗口；不为匹配原N调整事件。

使用可得控制，省略AbnNews。White为HC1；Boot为500次IID成对重抽样（实际次数见metadata）；差异使用全交互模型。

Hodrick行未估计，保留位置；NW30为另行标注的交易日间隔HAC补充，绝不当作Hodrick。星号按所在行t检验。

AIA是期权成交量代理，不能将其结果解读为直接验证机构阅读行为。原文+20.82bp仅供对比。

## Panel A: AIA option proxy

| 指标 | Macro News | Yes (1) | Macro News | No (2) | Macro News | (1) − (2) |
|---|---|---|---|
| Coefficient | 0.280 | 0.209 | 0.071 |
| White HC1 t-stat | [1.35] | [1.08] | [0.25] |
| Boot t-stat | [1.36] | [1.06] | [0.25] |
| Hodrick t-stat (not estimated) | — | — | — |
| NW30 t-stat (supplement) | [1.21] | [0.82] | [0.22] |
| 1 std. mag. (bps) | 9.20 | 7.72 |  |
| N | 1324 | 1113 |  |
| adj. R² | 0.022 | 0.045 |  |

## Panel B: ARA

| 指标 | Macro News | Yes (1) | Macro News | No (2) | Macro News | (1) − (2) |
|---|---|---|---|
| Coefficient | -2.333 | 0.322 | -2.655 |
| White HC1 t-stat | [-1.75]* | [0.25] | [-1.43] |
| Boot t-stat | [-1.80]* | [0.24] | [-1.43] |
| Hodrick t-stat (not estimated) | — | — | — |
| NW30 t-stat (supplement) | [-1.34] | [0.20] | [-1.17] |
| 1 std. mag. (bps) | -12.66 | 1.69 |  |
| N | 1324 | 1113 |  |
| adj. R² | 0.024 | 0.044 |  |


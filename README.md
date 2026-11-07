# Market Returns 课程复现数据整理

最新版：[`group3_collected_data_v3.zip`](group3_collected_data_v3.zip)。旧版 ZIP 已移除。

共 **22 个指标**，其中 **11 个为明确标注的模拟占位指标**。AIA 期权代理、标普500范围的 vwret 替代收益率和本次新增的 dEPU_proxy 均作为已取得的替代数据保留。

本次将原有两个 EPU 数据文件夹与独立模拟 dEPU 文件夹合并为 [`dEPU_proxy/`](dEPU_proxy/)。其中保存日度七日移动平均和月度 EPU 两个源文件、运行脚本、说明，以及结果 [`dEPU_proxy.csv`](dEPU_proxy/dEPU_proxy.csv)。

计算式：`dEPU_proxy(t) = EPU_MA7(t) - EPU_MA7(t-1)`。t-1 是前一个自然日，月度文件仅作参考，不参与计算。首日差分为空，其余 15,284 个差分值已逐行核验。该代理是平滑指数的日差分，不能视作原始日度 EPU 的变化。

压缩包已更新指标清单、说明和文件校验表。共享生成器内部的模拟变量只用于重建其他历史模拟列；包内未运行或更新论文回归。

- 大小：4351458 字节
- SHA-256：`1cbdcfd29e80f562047ec2ee8add028745814c5edef398876f70b2485b662f9e`

解压后先读 README.md、指标清单.csv 和尚未取得的数据.md。

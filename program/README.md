# 主文复现程序：先选表，再看说明

每张表一个独立代码文件，结果只保留CSV。无需阅读其他程序文件。

```text
program/
├── README.md
├── table2/
│   ├── run.py
│   ├── README.md
│   └── result/                 # ARA、AIA两个Panel
├── table3/
│   ├── run.py
│   ├── README.md
│   └── result/                 # 两个Panel、两个TED不填补对照
└── table4/
    ├── run.py
    ├── README.md
    └── result/                 # AIA、ARA两个Panel
```

## 阅读顺序

| 表格 | 先读说明 | 再看结果 |
|---|---|---|
| Table 2：基本预测关系 | [数据、操作、结果与原文对比](table2/README.md) | [result](table2/result/) |
| Table 3：市场状态 | [数据、操作、结果与原文对比](table3/README.md) | [result](table3/result/) |
| Table 4：宏观新闻窗口 | [数据、操作、结果与原文对比](table4/README.md) | [result](table4/result/) |

各说明先解释用了什么数据、为什么替换或省略，再解释结果和论文对比，末尾给运行命令。默认读取根目录 `group3_collected_data_v14.zip`，不必解压。数据ZIP不改动，附录和未采用模拟材料仍完整保留在其中。

安装依赖：`python -m pip install numpy pandas scipy statsmodels`。在仓库根目录分别运行 `python program/table2/run.py`、`python program/table3/run.py`、`python program/table4/run.py`。只想看结果无需运行代码。

样本为2010-02-01—2019-10-04，共2,437日。当前缩减规格与代理没有稳健复现论文主要显著性；按实际结果汇报，不把原文数字当成本组结果。原Hodrick行明确未估计，另有NW30补充。所有模拟值退出主回归。

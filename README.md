# s2s-fdd

Signals-to-Semantics Fault Detection and Diagnosis (S2S-FDD) scaffold for
time-series semantic parsing and explainable industrial fault diagnosis.

## 说明

### 项目定位

本项目用于复现“从信号到语义”的工业故障检测与诊断框架。当前仓库已经搭好可运行的轻量工程骨架，用于把原始工业时序信号转换为结构化语义证据，并为后续接入大语言模型、知识库检索和多轮诊断推理预留接口。

当前版本不是完整论文复现结果，而是面向复现工作的基础框架：先保证数据流、模块边界和最小闭环可运行，再逐步替换为真实 LLM、embedding、reranker 和特定工业对象知识。

### 项目结构

```text
s2s_fdd/
  data.py               # CSV/.mat 数据读取与过程上下文
  reconstruction.py     # 正常样本状态矩阵与样本重构
  variable_selection.py # 残差评分与关键变量筛选
  semantics.py          # 时序语义库、目标变量表格与 Prompt
  knowledge.py          # 知识案例、文本分块、查询改写与检索
  reasoning.py          # 诊断 Prompt、标签解析与工具调用接口
  report.py             # 结构化诊断报告生成
  evaluation.py         # 投票与准确率评估工具
  deepseek_client.py    # DeepSeek Chat Completions 调用封装
  cvacase.py            # CVACaseStudy .mat 数据运行入口
  demo.py               # 可运行的端到端示例
examples/
  normal.csv
  fault.csv
CVACaseStudy/
  license.txt
  CVACaseStudy/         # benchmark .mat 文件与原始 MATLAB 示例
```

### 框架流程

本项目按论文思路拆成两个主要阶段。

1. 信号到语义转换
   - 使用正常样本构建正常状态矩阵
   - 将观测样本重构为正常状态组合
   - 计算重构残差和变量级异常评分
   - 结合异常评分、异常发生时间和方差变化筛选关键变量
   - 为关键变量生成数据表格和时序语义描述

2. 对齐专家逻辑的诊断推理
   - 将时序描述改写为适合知识库检索的查询
   - 从故障案例或专家文档中召回相关知识
   - 组合流程信息、测点信息、语义证据和故障知识构建诊断 Prompt
   - 解析 `<answer>`、`<tool>`、`<uncertain>` 等模型输出
   - 生成可追溯的结构化诊断报告

### 数据集

仓库已加入 `CVACaseStudy` 数据集作为参考，包括正常训练数据、六个故障案例、MATLAB CVA benchmark 脚本、HTML 文档和原始 license。

默认 demo 使用 `examples/` 下的小型 CSV 文件，只依赖 numpy。读取 `CVACaseStudy` 中的 `.mat` 文件需要 scipy：

```bash
python -m pip install scipy
```

### 快速运行

安装最小依赖：

```bash
python -m pip install -r requirements.txt
```

运行默认 demo：

```bash
python -m s2s_fdd.demo
```

默认输出：

```text
outputs/demo_result.json
```

指定参数运行：

```bash
python -m s2s_fdd.demo \
  --normal examples/normal.csv \
  --fault examples/fault.csv \
  --alpha 3.0 \
  --window 3 \
  --top-k 3
```

使用本地知识文件或目录：

```bash
python -m s2s_fdd.demo --knowledge CVACaseStudy/CVACaseStudy/html/CUBenchmark.html
```

运行 CVACaseStudy Fault Case 1 / Set1_1 本地语义描述：

```bash
python -m s2s_fdd.cvacase --fault-case 1 --set Set1_1
```

运行 DeepSeek 时序描述版本：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API key"
python -m s2s_fdd.cvacase --fault-case 1 --set Set1_1 --llm-semantics
```

输出目录：

```text
outputs/cvacase/fault1/set1_1/
  report_local.json
  semantic_descriptions_local.json
  semantic_descriptions_deepseek.json
```

### Fault Case 1 当前结果

当前已运行 `FaultyCase1 / Set1_1`，正常样本使用 `T2+T3` 的前 23 个变量，参数为 `n_states=10`、`alpha=3.0`、`window=10`。

关键变量筛选结果为：

```text
x1, x8, x23, x19, x15, x12, x5, x3, x4, x10, x6, x7
```

最强变量为 `x1`，score 为 `4037.07`。其中与 Fault Case 1 空气管线堵塞直接相关的早期强异常包括：

| 变量 | 含义 | 首次连续异常时间 | 异常比例 | 最大残差 | 主要方向 |
| --- | --- | ---: | ---: | ---: | --- |
| x1 | PT312 air delivery pressure | 962 | 52% | 0.587 | 高于理想值 |
| x8 | FT305 air input flow rate | 899 | 17% | 0.070 | 低于理想值 |

DeepSeek 时序描述显示，`x1` 从 962 附近开始持续高于理想正常值，后期偏差最强，最大偏差出现在 5075；`x8` 从 899 附近开始主要低于理想值，后期出现明显下降和较强波动，最大偏差出现在 4894。这与 Fault Case 1 的“空气输入通道受阻，压力和空气流量首先异常”的方向是一致的。

需要注意：当前 `report_local.json` 中的 fallback 诊断结果为 `04_fault_case_3_top_separator_input_blockage`，这是轻量词法 RAG 和规则诊断器的误召回结果，不应作为最终诊断结论。当前可信的部分是“信号到语义”的变量选择和时序描述；后续需要用 embedding 检索和诊断 LLM 替换 fallback reasoner。

### 当前已实现

- 基于 numpy 的正常状态重构
- 基于残差的关键变量筛选
- 时序语义表格与 Prompt 生成
- DeepSeek 时序描述调用
- CVACaseStudy Fault Case 运行入口
- 轻量级词法 RAG 骨架
- 诊断 Prompt 构建与输出标签解析
- 确定性 fallback reasoner
- 结构化 JSON 报告输出

### 后续工作

- 将词法检索替换为 embedding 粗召回和 cross-encoder 精排
- 将诊断阶段替换为 LLM 多轮假设验证和工具调用
- 批量运行 CVACaseStudy 六类故障与多组 set
- 实现多次独立诊断与投票机制
- 增加重构、变量筛选和标签解析的自动化测试

## Documentation

### Purpose

This project scaffolds a Signals-to-Semantics Fault Detection and Diagnosis
(S2S-FDD) framework for industrial time-series fault diagnosis. It converts raw
process signals into structured semantic evidence and prepares extension points
for large language models, retrieval-augmented generation, and multi-step
diagnostic reasoning.

The current version is not a complete reproduction of the paper results. It is a
runnable foundation that preserves the target data flow and module boundaries,
so model-specific components can be plugged in incrementally.

### Repository Layout

```text
s2s_fdd/
  data.py               # CSV/.mat loading helpers and process context
  reconstruction.py     # normal-state matrix and sample reconstruction
  variable_selection.py # residual scoring and key-variable filtering
  semantics.py          # temporal semantic bank, tables, and prompts
  knowledge.py          # knowledge cases, chunking, query rewrite, retrieval
  reasoning.py          # diagnosis prompt, tag parsing, tool-call interface
  report.py             # structured report assembly
  evaluation.py         # voting and accuracy helpers
  deepseek_client.py    # DeepSeek Chat Completions wrapper
  cvacase.py            # CVACaseStudy .mat runner
  demo.py               # runnable end-to-end demo
examples/
  normal.csv
  fault.csv
CVACaseStudy/
  license.txt
  CVACaseStudy/         # benchmark .mat files and original MATLAB examples
```

### Pipeline

The framework follows two major stages.

1. Signal-to-semantics conversion
   - build a normal state matrix from normal samples
   - reconstruct observed samples as normal-state combinations
   - compute residuals and variable-level abnormal scores
   - select key variables using score, anomaly onset, and variance change
   - generate target tables and temporal descriptions for key variables

2. Expert-aligned diagnostic reasoning
   - rewrite temporal descriptions into retrieval-oriented queries
   - retrieve relevant knowledge from fault cases or expert documents
   - build diagnosis prompts with process context, sensors, evidence, and knowledge
   - parse `<answer>`, `<tool>`, and `<uncertain>` model outputs
   - assemble a traceable structured diagnosis report

### Dataset

The `CVACaseStudy` benchmark is included for reference. It contains normal
training data, six faulty cases, MATLAB CVA benchmark scripts, generated HTML
documentation, and the original license.

The default demo uses the small CSV files under `examples/` and only requires
numpy. Reading `.mat` files from `CVACaseStudy` requires scipy:

```bash
python -m pip install scipy
```

### Quick Start

Install the minimal dependency set:

```bash
python -m pip install -r requirements.txt
```

Run the default demo:

```bash
python -m s2s_fdd.demo
```

Default output:

```text
outputs/demo_result.json
```

Run with custom parameters:

```bash
python -m s2s_fdd.demo \
  --normal examples/normal.csv \
  --fault examples/fault.csv \
  --alpha 3.0 \
  --window 3 \
  --top-k 3
```

Use a local knowledge file or directory:

```bash
python -m s2s_fdd.demo --knowledge CVACaseStudy/CVACaseStudy/html/CUBenchmark.html
```

Run CVACaseStudy Fault Case 1 / Set1_1 with local semantic descriptions:

```bash
python -m s2s_fdd.cvacase --fault-case 1 --set Set1_1
```

Run the DeepSeek semantic-description version:

```powershell
$env:DEEPSEEK_API_KEY="your DeepSeek API key"
python -m s2s_fdd.cvacase --fault-case 1 --set Set1_1 --llm-semantics
```

Output directory:

```text
outputs/cvacase/fault1/set1_1/
  report_local.json
  semantic_descriptions_local.json
  semantic_descriptions_deepseek.json
```

### Fault Case 1 Current Result

`FaultyCase1 / Set1_1` has been run with `T2+T3` as the normal reference over the first 23 variables, using `n_states=10`, `alpha=3.0`, and `window=10`.

Selected key variables:

```text
x1, x8, x23, x19, x15, x12, x5, x3, x4, x10, x6, x7
```

The strongest variable is `x1`, with score `4037.07`. The most relevant early variables for Fault Case 1 air-line blockage are:

| Variable | Meaning | First continuous anomaly | Anomaly ratio | Max residual | Main direction |
| --- | --- | ---: | ---: | ---: | --- |
| x1 | PT312 air delivery pressure | 962 | 52% | 0.587 | above ideal |
| x8 | FT305 air input flow rate | 899 | 17% | 0.070 | below ideal |

The DeepSeek temporal descriptions state that `x1` becomes persistently above the ideal normal value near timestamp 962, with the strongest late-stage deviation and a peak at 5075. `x8` becomes mainly lower than the ideal value near timestamp 899, with a pronounced late-stage drop and stronger volatility, peaking at 4894. This is consistent with the expected air-line blockage direction, where air delivery pressure and air input flow become early abnormal signals.

Note: the fallback diagnosis in `report_local.json` is `04_fault_case_3_top_separator_input_blockage`. This is a misretrieval from the current lightweight lexical RAG plus deterministic fallback reasoner, not the final diagnosis. The reliable part at this stage is the signal-to-semantics output; the diagnostic stage still needs embedding retrieval and an LLM-based multi-round verifier.

### Implemented

- numpy-only normal-state reconstruction
- residual-based key-variable selection
- temporal semantic table and prompt generation
- DeepSeek semantic-description calls
- CVACaseStudy Fault Case runner
- lightweight lexical RAG scaffold
- diagnosis prompt construction and output tag parsing
- deterministic fallback reasoner
- structured JSON report output

### Next Steps

- replace lexical retrieval with embedding recall and cross-encoder reranking
- replace the diagnosis fallback with LLM-based multi-round hypothesis verification
- batch-run all CVACaseStudy fault cases and data sets
- run repeated diagnosis sessions and majority voting for paper-style metrics
- add tests around reconstruction, variable selection, and output parsing

## Version History / 版本记录

### v0.1.2 - CVACase Fault Case 1 result

- Added CVACaseStudy runner and DeepSeek semantic-description usage notes.
- Documented the current `FaultyCase1 / Set1_1` result, selected variables, and output files.
- Marked the current fallback diagnosis as a known retrieval/reasoning limitation.

### v0.1.1 - README bilingual update

- Rewrote the README in Chinese and English.
- Added version history to make future changes traceable.
- No code, dataset, or pipeline behavior changes.

### v0.1.0 - Initial S2S-FDD scaffold

- Added the modular S2S-FDD project structure.
- Added CSV demo data and the CVACaseStudy reference dataset.
- Implemented a runnable local pipeline for reconstruction, key-variable
  selection, semantic evidence generation, retrieval scaffold, reasoning
  scaffold, and JSON report output.

# s2s-fdd

Signals-to-Semantics Fault Detection and Diagnosis (S2S-FDD) scaffold for
time-series semantic parsing and explainable industrial fault diagnosis.

中文说明见下方；English documentation follows after the Chinese section.

## 中文说明

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

### 当前已实现

- 基于 numpy 的正常状态重构
- 基于残差的关键变量筛选
- 时序语义表格与 Prompt 生成
- 轻量级词法 RAG 骨架
- 诊断 Prompt 构建与输出标签解析
- 确定性 fallback reasoner
- 结构化 JSON 报告输出

### 后续工作

- 将本地语义摘要替换为 LLM 调用
- 将词法检索替换为 embedding 粗召回和 cross-encoder 精排
- 补充 CVACaseStudy 的测点名称、流程说明和故障知识
- 实现多次独立诊断与投票机制
- 增加重构、变量筛选和标签解析的自动化测试

## English Documentation

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

### Implemented

- numpy-only normal-state reconstruction
- residual-based key-variable selection
- temporal semantic table and prompt generation
- lightweight lexical RAG scaffold
- diagnosis prompt construction and output tag parsing
- deterministic fallback reasoner
- structured JSON report output

### Next Steps

- replace local semantic summaries with an LLM call
- replace lexical retrieval with embedding recall and cross-encoder reranking
- add CVACaseStudy-specific sensor names, process text, and fault knowledge
- run repeated diagnosis sessions and majority voting for paper-style metrics
- add tests around reconstruction, variable selection, and output parsing

## Version History / 版本记录

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

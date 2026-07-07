# RTL Static Connectivity Framework

## 项目简介

通过本项目可以将RTL中memory的clock时钟路径以drawio格式展示出来。

解决的问题是：在MBIST的时候，将相同的时钟所驱动memory找出来。

## 核心特点

- Harness Engineering
- Graph First
- AI Friendly
- Extensible Analysis

## 架构概览

```tcl
RTL
↓
Lexer
↓
Parser(AST)
↓
Graph
↓
Pass
↓
Analysis
↓
Exporter
```

## 快速开始

- 环境

- 运行
  - 以drawio格式输出
  
    - JSON to Draw.io:
  
    ```bash
    python scripts/json_clock_paths_to_drawio.py --input harness/case_001_four_memory_clock_paths/expected/expected_clock_paths.json --output harness/case_001_four_memory_clock_paths/expected/four_memory_clock_paths.drawio
    ```
  
- Regression
  - Sample RTL: `harness/case_001_four_memory_clock_paths/rtl/four_memory_clock_paths.sv`
  - Golden: `harness/case_001_four_memory_clock_paths/expected/expected_clock_paths.json`
  - Draw.io: `harness/case_001_four_memory_clock_paths/expected/four_memory_clock_paths.drawio`

## 项目目录

```bash
├───docs
├───harness
│   └───case_001_four_memory_clock_paths
├───rtl
├───scripts
└───temp
```

## 文档导航

```bash
AGENTS.md
docs/ARCHITECTURE.md
docs/DESIGN_DECISIONS.md
docs/CONTRIBUTING.md
docs/README.md
```

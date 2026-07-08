# AI Development Guide

## 开发原则：

- Harness First

- Golden First

- Regression First

- Documentation First
- 任何影响系统结构、开发流程或协作方式的变更，都应同步更新相应文档。
- 任何不确定的内容，与用户确认，不可随意推断
- 每一次代码修改后，都要对harness下的case做测试

---
## 必读文档 

- ./docs/ARCHITECTURE.md
- ./docs/DESIGN_DECISIONS.md
- ./docs/CONTRIBUTING.md
- ./docs/README.md

---
# 目录结构

```
project/
├── harness/
├── rtl/
├── lexer/
├── parser/
├── graph/
├── passes/
├── analysis/
├── exporter/
├── docs/
└── scripts/
```

---

## Agent职责

### Lexer

负责：

- Tokenize
- 去除 Comment
- 保留 Line Number
- 输出 Token

禁止：

- Graph
- Clock Analysis
- Drawio

###  Parser(AST)

负责：

识别 RTL 语法：

- module
- port
- parameter
- wire
- logic
- assign
- always
- instance
- generate
- interface（未来）
- package（未来）

输出：

- AST

禁止：

- Graph

- Clock Search

- Exporter

### Graph Builder

输入：

- AST

输出：

- Connectivity Graph

Graph Builder 负责：

- 建立下面内容之间的连接关系

  - Signal

  - Port

  - Instance

  - Memory

  - Constant

  - Parameter


禁止：

- Clock Search

- Exporter

### Graph Pass

负责：

- Graph Normalization。

- 例如：

  - Resolve Parameter

  - Resolve Generate

  - Constant Folding

  - Hierarchy Expansion

  - Alias Merge


Graph Pass 可以修改 Graph。

除此之外：

- 禁止任何模块修改 Graph。

### Analysis

输入：

- Graph

输出：

- 分析结果。

目前支持：

- Clock Path

未来支持：

- Reset Path
- Scan Path
- OCC
- MBIST
- Fanin
- Fanout
- CDC

允许：

- DFS
- BFS
- Backtrace

禁止：

- 重新解析 RTL。

### Exporter

负责：

- Graph

输出：

- Draw.io
- JSON
- DOT
- SVG（未来）
- HTML（未来）

禁止：

- 解析 RTL

### Harness

- 生命周期

  ```bash
  发现 RTL
  ↓
  建立Harness
  ↓
  人工确认Golden
  ↓
  Review Harness
  ↓
  Parser开发
  ↓
  Regression
  ↓
  长期维护
  ↓
  Deprecated（可选）
  ```

- 建立Harness

  ```bash
  harness/
      case001_assign/
          README.md
          rtl/
          expected/
          config.yaml
  
      case002_generate_if/
          README.md
          rtl/
          expected/
          config.yaml
  ```

- 已有的harness

  - 不修改RTL
  - 不修改Golden
  - 不修改测试目的

- 允许修改

  - README.md
  - draw.io文件

- 新增RTL特性

  - 应新增harness case

---



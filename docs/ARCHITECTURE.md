# 系统目标

- 不是：RTL Parser

- 而是：RTL Static Connectivity Framework

---

# 技术栈

本项目可以使用的语言有：

- tcl为主
- phython为辅

---

# 总体架构

```bash
RTL
↓
Lexer
↓
AST
↓
Graph Builder
↓
Graph Pass
↓
Analysis
↓
Exporter
```

---

# Graph

- Graph 是唯一 IR
- Node
- Edge

---

# Design Principles

- Single Responsibility

- Graph First

- Loose Coupling

- High Cohesion

- Harness First
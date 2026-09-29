---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-007
order: 7
title: 模型驱动开发：模型层次
source:
  date: "2026-06-14"
  file: "2026年06月/2026-06-14.md"
  prompt_sha256: 28b1f8615e28cf52ead2f5df07771db09961ada9b818d70b3cabdc07244e81fe
mapping:
  status: exact
  confidence: high
  topic_ids:
    - SOFTWARE.MODELING.FORMAL_MODELING
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 模型驱动开发：模型层次

## 今天学会什么

- 识别原始提纲列出的模型驱动开发主题和三个模型层级名称。
- 说明当前来源能支持哪些内容、哪些定义仍不能可靠补齐。
- 区分“有模型层级标题”与“已有完整转换规则或优势说明”。

## 先建立直觉

模型驱动开发把模型作为主题中心，但要准确解释模型之间的边界，仍需要明确的定义和转换关系。当前打卡 Prompt 只列出计算无关模型（CIM）、平台独立模型（PIM）、平台特定模型（PSM）三个标题，并预留了“优点”标题，没有给出解释正文。

## 核心知识

### 来源明确列出的结构

```text
模型驱动开发方法
├─ 多级模型分层
│  ├─ 计算无关模型（CIM）
│  ├─ 平台独立模型（PIM）
│  └─ 平台特定模型（PSM）
└─ 模型驱动开发方法的优点（仅有标题）
```

原始提示词没有说明每类模型的边界、模型之间如何转换、由谁执行转换、转换是否自动化，也没有列出方法的具体优点。仓库现有 mapping 说明该项与模型驱动建模主题边界相符，但不是上述定义的知识来源。

**SOURCE_GAP：CIM/PIM/PSM 的正式含义、层级关系、转换过程及方法优势均需补充仓库可追踪的教材或大纲证据。本单元不以常见定义填空。**

## 一张脑图式结构

见“来源明确列出的结构”。除三个模型名称外，不扩展关系箭头，以免把未经支持的转换规则写成事实。

## 易混点 / 对比

- 现有资料只支持确认三个层级名称；不支持进一步比较它们依赖的需求信息、技术细节或转换方向。
- 本项未把 MDA 工具、代码生成或平台迁移等背景知识写成结论，因为本次可追踪来源没有提供这些说明。

## 架构师视角

模型层次通常需要连接业务需求与具体技术选择，但当前证据不足以解释各层如何分工。架构决策不应只凭缩写推导自动转换能力或实现收益；补充来源后再讨论工具链、可移植性和维护成本。

## 软考关注

- **大纲明确覆盖：**仓库未提供本单元对应的具体大纲段落。
- **教材明确覆盖：**未找到可引用到具体教材章节的模型层级定义。
- **已索引样题：**Golden Set 有形式化建模相关的题目标注，但没有证据表明其考查本项的 CIM/PIM/PSM 内容。
- **普通知识补充：**无。

不作频次结论。

## 记忆锚点

- 当前来源明确列出 CIM、PIM、PSM 三个名称。
- “模型驱动开发方法的优点”在原 Prompt 中只有标题。
- 不把来源缺失的定义、转换规则或效果当作已验证知识。

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-007` 的来源身份、outline 与 EXACT mapping。
- 用户提供的打卡归档：`2026年06月/2026-06-14.md`；Prompt 区块 SHA-256 见 frontmatter。未复制原文。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：该项与模型驱动建模 Topic 的映射理由。
- `data/golden-set/comprehensive.sample.json`：仅有其他形式化建模边界的样题索引，不作为 CIM/PIM/PSM 的支持证据。

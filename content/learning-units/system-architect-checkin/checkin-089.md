---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-089
order: 89
title: "软件测试方法、类型与缺陷管理"
source:
  date: "2026-09-11"
  file: "2026年09月/2026-09-11 软件测试概述.md"
  prompt_sha256: db21dd6cd5620cabdcef9dbc54b64cde74129d4aeceb9c39f24dac52c70e9b34
mapping:
  status: merge
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.TESTING
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 软件测试方法、类型与缺陷管理

## 今天学会什么
- 按可见性与执行方式整理测试方法分类
- 区分测试对象、阶段和软件形态三类测试分类
- 识别严重程度、优先级和缺陷状态管理主题

## 先建立直觉

测试可以按测试者能看到什么、是否执行程序、测什么对象及处于什么阶段来分类。缺陷严重程度描述影响，处理优先级描述何时解决，两者不是同一尺度。

## 核心知识

### 方法和测试类型

来源列黑盒、白盒、灰盒；静态/动态；自动化。测试对象包括功能、性能、安全、兼容、界面、易用和稳定；阶段包括单元、集成、系统、验收（α/β）；还列 App、Web、IoT、车联网、大数据、AI、小程序以及回归、冒烟测试。

### 缺陷管理

严重程度分严重、一般、次要、建议；优先级分立即解决、高优先级、正常排序、低优先级。管理过程强调结合影响范围和严重级别确定优先级，并同步缺陷状态。

**SOURCE_GAP：软件测试定义、各分类边界及缺陷生命周期仅有目录/标题，需补充来源。**

## 一张脑图式结构

```text
测试分类
├─ 可见性：黑盒 / 白盒 / 灰盒
├─ 执行：静态 / 动态 / 自动化
├─ 对象与阶段：功能/性能…；单元→集成→系统→验收
└─ 缺陷：严重程度 × 优先级 → 状态跟踪
```

## 架构师视角

架构师需要将质量要求转成可验证的测试对象，并确保缺陷信息能被团队同步。严重程度与处理优先级应分别记录，不用一个字段代替另一个。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 黑盒/白盒/灰盒按程序可见性分类
- 静态/动态按是否执行程序分类
- 测试对象、阶段、软件形态是不同分类轴
- 严重程度不等于修复优先级

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-089` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-11 软件测试概述.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。

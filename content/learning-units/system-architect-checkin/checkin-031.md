---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-031
order: 31
title: "软件可靠性：指标与容错战术"
source:
  date: "2026-07-08"
  file: "2026年07月/2026-07-08 可靠性设计.md"
  prompt_sha256: 285199d3d03254948b933316e6777b24998e5f713bbf8ed4d19adb60bd68ffed
mapping:
  status: split
  confidence: high
  topic_ids:
    - RELIABILITY.SOFTWARE.METRICS
    - RELIABILITY.SOFTWARE.FAULT_TOLERANCE
    - QUALITY.ATTRIBUTES.AVAILABILITY
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 软件可靠性：指标与容错战术

## 今天学会什么
- 解释 MTTF、MTTR、MTBF 的关注点和关系
- 区分避错、检错、容错
- 识别集群、N 版本、恢复块及服务容错措施的机制

## 先建立直觉

可靠性不仅是避免故障，也包括尽早发现和在局部故障发生后维持可接受服务。指标帮助描述故障和修复时间，战术则分别作用在故障预防、发现和恢复阶段。

## 核心知识

### 指标

MTTR 是平均修复恢复时间；MTTF 是故障前平均正常运行时间；MTBF 是连续故障之间的平均间隔，来源给出 MTBF = MTTF + MTTR。计算前要按来源所述口径统计运行或修复时间与故障次数。

### 三类战术

避错通过规范和实践预防缺陷；防卫式程序设计预先处理异常。检错通过探针、监控和数据收集发现运行问题，可观测性用指标、日志、追踪观察系统。容错通过冗余、补偿和自动恢复降低局部故障影响。

### 容错实例

集群提供冗余节点，负载均衡分发请求并把流量转向健康节点；N 版本让不同实现并行并由表决器比较结果，代价是高开发成本和复杂性；恢复块以主版本、备选版本和接受测试逐个验证，失败时回到恢复点重试。服务层还列重试、资源隔离、熔断、限流、降级、自愈。

## 一张脑图式结构

```text
可靠性
├─ 避错：降低故障发生可能（MTTF）
├─ 检错：缩短发现时间（指标/日志/追踪）
└─ 容错：故障后保持/恢复服务
   ├─ 冗余：集群、N 版本
   ├─ 回退：恢复块、重试
   └─ 保护：隔离、熔断、限流、降级、自愈
```

## 易混点 / 对比

MTTF 关注故障前运行时长，MTTR 关注修复时长；避错减少错误进入系统，检错缩短发现时间，容错处理故障影响。三者不能互换。

## 架构师视角

容错需要把目标落到故障边界：集群处理节点故障，隔离限制资源耗尽的传播，熔断对失效依赖快速失败，降级把资源留给核心路径。每种措施也会引入资源、复杂性或功能取舍，需匹配故障模型。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h2-q24`, `gs-comp-2025-h1-q08`, `gs-comp-2025-h1-q52`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- MTBF = MTTF + MTTR（按来源定义）
- 避错、检错、容错分别作用于发生、发现、影响
- 可观测性：指标、日志、追踪
- N 版本靠多样性与表决，成本高
- 服务容错不只有重试，还包括隔离/熔断/限流/降级/自愈

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-031` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-08 可靠性设计.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h2-q24`, `gs-comp-2025-h1-q08`, `gs-comp-2025-h1-q52`；不含题干、答案或解析。

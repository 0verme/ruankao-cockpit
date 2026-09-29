---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-029
order: 29
title: "零信任：持续验证与最小权限"
source:
  date: "2026-07-06"
  file: "2026年07月/2026-07-06 安全性设计-05.md"
  prompt_sha256: 7cdb1117d1dab1a845bfd1a8916b56a3fd69a71f837d32b98f5b607082f287c6
mapping:
  status: split
  confidence: medium
  topic_ids:
    - SEC.INFORMATION.ACCESS_CONTROL
    - SEC.ARCHITECTURE.WPDRRC
    - SEC.ARCHITECTURE.NETWORK_SECURITY
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 零信任：持续验证与最小权限

## 今天学会什么
- 用“从不信任，始终验证”概括零信任
- 列出来源支持的身份、网络和数据实践
- 说明零信任如何回应静态信任边界的风险

## 先建立直觉

零信任把信任判断从一次性的网络边界准入改为持续评估：每次访问都要结合身份与上下文验证，权限按任务需要收敛，异常时能够撤销访问。

## 核心知识

### 传统假设的问题

来源指出“内网即安全”在边界被突破后可能允许横向移动；一次认证后长期信任会造成权限累积；一次性判断不能感知访问过程中的风险变化。

### 实践要点

最小权限并即时授予、用毕回收；MFA 组合不同类别因素；持续监控行为和上下文风险，异常时撤销访问；网络微分段将隔离细化到工作负载并默认拒绝跨段流量；安全日志关联分析以便追溯；服务间双向 TLS 校验双方证书；按场景和权限对敏感数据脱敏。

## 一张脑图式结构

```text
从不信任，始终验证
├─ 身份：最小权限 / MFA / 持续验证
├─ 网络：微分段 / 双向 TLS
└─ 数据与证据：脱敏 / 日志审计
```

## 易混点 / 对比

边界信任依赖网络位置；零信任强调逐次且持续验证。MFA 强化身份证据，微分段约束网络访问，二者不是同一个控制面。

## 架构师视角

零信任不是单一产品，而是将身份、访问策略、网络隔离、日志和数据保护组合到访问路径中。设计时要确认权限是否可按任务收回、异常是否能被持续感知，并避免把“内网”当作充分授权条件。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2026-h1-5-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 从不信任，始终验证
- 最小权限要即时授予、用毕回收
- 持续验证要能感知上下文变化
- 微分段限制横向移动
- 日志、双向 TLS、脱敏覆盖审计与数据面

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-029` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-06 安全性设计-05.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2026-h1-5-q1`；不含题干、答案或解析。

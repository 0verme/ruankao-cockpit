---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-028
order: 28
title: "OAuth 2.0 与 JWT：授权和令牌"
source:
  date: "2026-07-05"
  file: "2026年07月/2026-07-05 安全性设计-04.md"
  prompt_sha256: dec14359675e661229b0dffb9cd7a4ea12e9b73c75a16cb028b0cee4d6dc4cc9
mapping:
  status: partial
  confidence: medium
  topic_ids:
    - SEC.INFORMATION.ACCESS_CONTROL
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# OAuth 2.0 与 JWT：授权和令牌

## 今天学会什么
- 说出 OAuth 2.0 四类角色
- 区分来源描述的授权码、客户端、密码和简化流程
- 说明 JWT 的头部、载荷和签名及其限制

## 先建立直觉

OAuth 2.0 重点是让客户端获得访问受保护资源的授权；JWT 是承载声明并可校验完整性的令牌格式。授权流程决定令牌如何签发，令牌格式决定接收方如何读取和验证，两者不是同一概念。

## 核心知识

### OAuth 2.0 角色

资源所有者拥有资源；客户端请求访问；授权服务器负责用户认证与签发访问令牌；资源服务器保存受保护资源并按令牌放行。来源描述授权码流程为浏览器取得一次性授权码，再由客户端后端交换访问令牌/刷新令牌；简化流程则将令牌经 URL 片段返回浏览器。

### 其他流程与版本边界

来源还列密码模式（用户凭证交给客户端申请令牌）和客户端模式（客户端以自身身份申请，不代表用户）。这些模式的安全适用条件没有在仓库中独立核验；该内容仅忠实索引原始提示，不作为当前协议选型建议。

### JWT

JWT 由 Header、Payload、Signature 三部分组成，各部分 Base64 编码并以点号连接。Header 描述类型/算法，Payload 放 claims，Signature 用于验证完整性与真实性。Payload 默认只是编码而非加密；来源指出敏感内容可能暴露。无状态令牌签发后难以立即撤销，需考虑短有效期或额外撤销机制。

**SOURCE_GAP：OAuth 模式的当前安全适用性和 JWT 的实现要求未由仓库规格来源核验；不将该提示视作最新协议建议。**

## 一张脑图式结构

```text
OAuth 授权：资源所有者 → 客户端 → 授权服务器 → 资源服务器
令牌表示：Header . Payload . Signature
授权流程 != 令牌格式
```

## 易混点 / 对比

OAuth 2.0 解决客户端授权访问资源的流程问题；JWT 描述令牌结构。Base64 编码不等于加密。来源列出的模式不自动意味着当前场景适用。

## 架构师视角

架构选型要分别评估授权流程、客户端类型、令牌存放与生命周期。尤其不能把“自包含”理解成载荷保密，也不能把来源列出的密码/简化模式当成默认推荐；实际实现需以可追踪的现行标准和安全审查为准。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2026-h1-5-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- OAuth 角色：资源所有者、客户端、授权服务器、资源服务器
- 授权码：先拿 code，再由后端换令牌
- JWT：Header / Payload / Signature
- Payload 编码不代表加密
- 协议模式适用性需另行核对

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-028` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-05 安全性设计-04.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2026-h1-5-q1`；不含题干、答案或解析。

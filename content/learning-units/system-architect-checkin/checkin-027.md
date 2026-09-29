---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-027
order: 27
title: "身份鉴别、单点登录与 MFA"
source:
  date: "2026-07-04"
  file: "2026年07月/2026-07-04 安全性设计-03.md"
  prompt_sha256: c9afde11245233470023bcb1647bfc03173b0aa10242bb16651da2f368a7847a
mapping:
  status: exact
  confidence: high
  topic_ids:
    - SEC.INFORMATION.ACCESS_CONTROL
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 身份鉴别、单点登录与 MFA

## 今天学会什么
- 按因素类别识别身份鉴别方式
- 复述来源列出的 SSO 重定向与票据流程
- 说明 MFA 要求组合不同类别验证因素

## 先建立直觉

认证系统要建立“当前访问者是谁”的可信依据。密码、持有设备、生物特征和环境信息提供不同证据；单点登录则把身份建立交由共同信任的认证中心，减少每个应用重复登录。

## 核心知识

### 身份鉴别因素

来源按已知秘密（密码、PIN、安全问题）、持有物（令牌、智能卡、手机）、不可改变的生理/行为特征（指纹、人脸、虹膜）、可靠第三方及环境上下文分类。环境可包括位置、网络、时间、设备和行为模式。

### SSO 流程

应用 A 发现未登录后转到认证中心；用户完成凭证验证，认证中心建立全局会话并签发一次性 Ticket；A 将 Ticket 交给认证中心后台核验，取得身份信息后建立本地会话。访问 B 时同样去认证中心；已有全局会话时可为 B 签发新 Ticket。

### 多因素认证

MFA 要求两种或更多不同类别因素共同证明身份。来源给出的目的，是让单独泄露密码不足以完成认证。原提纲的“跨域问题”只有标题，没有解释。

**SOURCE_GAP：跨域 SSO 问题及其解决方式在来源中仅有标题。**

## 一张脑图式结构

```text
用户访问应用
├─ 鉴别证据：知道 / 拥有 / 生物特征 / 第三方 / 环境
├─ SSO：应用 → 认证中心 → Ticket → 应用本地会话
└─ MFA：组合至少两类不同因素
```

## 易混点 / 对比

身份鉴别方式按证据来源分类；MFA 是多个不同类别的组合，不等于同类密码输入两次。SSO 是跨应用会话流程，不是某一种鉴别因素。

## 架构师视角

把凭证验证集中到信任的认证中心可以减少重复登录，但应用仍需验证票据并建立自己的会话。身份验证、跨域传递和授权策略需要分开建模；跨域细节因来源缺失而留空。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2026-h1-5-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 已知、拥有、生物特征、第三方、环境
- SSO 的 Ticket 需回到认证中心核验
- MFA 组合不同类别因素
- 跨域 SSO 为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-027` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-04 安全性设计-03.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2026-h1-5-q1`；不含题干、答案或解析。

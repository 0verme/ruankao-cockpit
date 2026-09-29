---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-024
order: 24
title: "安全属性、加密、摘要与 PKI"
source:
  date: "2026-07-01"
  file: "2026年07月/2026-07-01 安全性设计-01.md"
  prompt_sha256: 858d20887c140feb5d4c6335c668251c6fbdbe9cb28a7079018683b261c4d71a
mapping:
  status: split
  confidence: high
  topic_ids:
    - QUALITY.ATTRIBUTES.SECURITY
    - SEC.INFORMATION.CRYPTOGRAPHY
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 安全属性、加密、摘要与 PKI

## 今天学会什么
- 区分安全性的基本属性
- 比较对称与非对称加密在速度和密钥管理上的取舍
- 描述数字签名校验与 PKI 角色

## 先建立直觉

安全设计不是单一的“加密”：要分别考虑谁能读取、谁能修改、授权用户能否访问，以及出现问题能否追查。密码技术也各有用途，签名、摘要与加密不能互换。

## 核心知识

### 安全属性

来源列出机密性（防止未授权读取）、完整性（授权修改并可发现篡改）、可用性（授权者需要时可访问）、可控性（控制授权范围内的信息流与行为）和可审查性（提供调查依据）。

### 加密与摘要

对称加密速度快、适合大量数据，但密钥安全分发与管理是难点；来源列出 AES、DES、3DES、IDEA。非对称加密可处理密钥分发问题，但计算复杂、速度较慢；列举 RSA、ECC。摘要输出固定长度、不可逆并强调抗碰撞，来源列举 MD5、SHA。

### 签名与 PKI

发送方根据内容生成摘要并用私钥生成签名；接收方验证签名得到摘要，再对内容计算摘要并比较。来源将签名用途列为完整性与不可否认性。PKI 中 CA 签发数字证书，RA 接收并审核申请；证书将实体信息与公钥绑定，并由 CA 私钥签名。

## 一张脑图式结构

```text
安全目标
├─ 保密/完整/可用/可控/可审查
├─ 加密：对称（效率） / 非对称（密钥分发）
├─ 摘要：固定长度、不可逆、抗碰撞
└─ 签名与 PKI：私钥签名 → 证书/身份信任 → 验证内容完整性
```

## 易混点 / 对比

加密关注内容访问保护；摘要是内容的定长表示；数字签名把签名者身份与摘要验证联系起来。对称/非对称加密的主要取舍按来源分别是速度效率与密钥分发。

## 架构师视角

先明确保护目标，再组合机制：大量数据加密要考虑密钥管理；对外身份与公钥信任涉及证书链角色；签名校验需比较签名所代表的摘要与接收内容摘要。来源没有展开协议细节，实施时应另查对应标准。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2023-h2-q18`, `gs-comp-2023-h2-q58`, `gs-case-2025-h1-1-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 机密、完整、可用、可控、可审查
- 对称加密快，密钥管理是难点；非对称较慢
- 摘要不可逆且固定长度；签名承担完整性/不可否认性
- CA 签证书，RA 审申请

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-024` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-01 安全性设计-01.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2023-h2-q18`, `gs-comp-2023-h2-q58`, `gs-case-2025-h1-1-q1`；不含题干、答案或解析。

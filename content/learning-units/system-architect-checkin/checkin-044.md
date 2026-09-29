---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-044
order: 44
title: "物联网分层与 MQTT 主题索引"
source:
  date: "2026-07-21"
  file: "2026年07月/2026-07-21 物联网.md"
  prompt_sha256: 15d94a0ba77303b158a04a46aaea6ec0286f7801473d6079cb660bd6e0d625db
mapping:
  status: split
  confidence: high
  topic_ids:
    - ARCH.LAYERED.IOT
    - ARCH.COMMUNICATION.NETWORK_ARCHITECTURE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 物联网分层与 MQTT 主题索引

## 今天学会什么
- 识别物联网定义中的设备、连接、数据和操作要素
- 按感知、网络、平台、应用列出系统层次
- 明确 MQTT 的 QoS 与持久化细节当前未有来源解释

## 先建立直觉

物联网把物理设备接入网络，让它们能够感知、通信、收集数据或执行操作。层次结构从设备感知向网络传输、平台处理再到应用服务展开。

## 核心知识

### 物联网与分层

来源将 IoT 描述为连接设备、车辆、家电、传感器和执行器的网络，使其能够收集数据、相互通信并接受操作；系统层次列为感知层、网络层、平台层、应用层。

### MQTT

Prompt 列出 MQTT 概念、优点、QoS 级别及非持久性、队列型持久性、确认型持久性等主题，但没有给出协议行为、级别语义或持久化保证。

**SOURCE_GAP：MQTT 的概念、QoS 级别与持久化类型只有标题/名称，具体语义未提供。**

## 一张脑图式结构

```text
物理对象 → 感知层 → 网络层 → 平台层 → 应用层
MQTT：概念 / 优点 / QoS / 持久化（细节待补证）
```

## 架构师视角

物联网架构要贯通设备感知、通信和上层应用。MQTT 的 QoS/持久化会影响消息交付语义，但当前材料没有定义；在设备通信决策前应补齐协议来源。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2024-h1-4-q2`, `gs-case-2024-h1-4-q3`, `gs-case-2024-h2-4-q2`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- IoT 连接物理设备并采集/传递数据
- 四层：感知、网络、平台、应用
- MQTT QoS 与持久化主题待补细节
- 不从层名推导协议保证

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-044` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-21 物联网.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2024-h1-4-q2`, `gs-case-2024-h1-4-q3`, `gs-case-2024-h2-4-q2`；不含题干、答案或解析。

---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-013
order: 13
title: 调用返回、面向对象与分层风格
source:
  date: "2026-06-20"
  file: "2026年06月/2026-06-20.md"
  prompt_sha256: 2938ab364a7b6d856cbfbd2db9fef5c24e8d7a5f32b8255a1b547b78e0e2dd5d
mapping:
  status: split
  confidence: high
  topic_ids:
    - ARCH.FOUNDATION.STYLES
    - ARCH.LAYERED.LAYERS
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 调用返回、面向对象与分层风格

## 今天学会什么
- 说明主程序/子程序风格中的控制关系。
- 用对象交互和封装、继承、多态概括面向对象风格。
- 说明分层风格的服务方向及越层调用限制。

## 先建立直觉

架构风格可以从“谁控制谁、通过什么交互、依赖朝哪个方向”来观察。本单元从显式调用扩展到对象消息，再到有层次约束的服务依赖；分层部分映射到独立的层次式 Topic。

## 核心知识

- **主程序/子程序：**系统以主程序为入口和总控，子程序封装特定功能；调用关系可由主程序发起，也可嵌套形成调用栈，连接机制是显式函数调用。
- **面向对象：**系统由相互作用的对象组成，对象通过消息（通常表现为方法调用）请求其他对象执行操作。来源列出的特性为封装、继承、多态，目标是改善模块化、复用和可维护性。
- **分层：**每层为上层提供服务，同时作为下层客户端。来源描述严格单向调用：通常上层调用下层，下层不能调用上层；同层组件可协作，但不越层调用。

## 一张脑图式结构
```text
交互与依赖
├─ 主程序/子程序：入口总控 → 显式调用 → 子程序
├─ 面向对象：对象 ↔ 消息/方法调用
└─ 分层：上层调用下层服务；约束越层与反向调用
```

## 易混点 / 对比
- 子程序调用围绕控制流程和过程组织；对象风格围绕对象及其交互。
- 分层的依赖方向是该来源的重点；“分成几层”本身不足以证明遵守了分层约束。
- 该 Learning Path Item 是一个 SPLIT mapping，内容仍作为同一单元，不拆成多个 Topic 文件。

## 架构师视角
控制关系会影响模块边界和变更传播。显式调用、对象消息及层间服务代表不同的组织方式；采用分层时要检查依赖是否越层或反向，否则层次边界只剩名称。

## 软考关注
仓库未将本单元具体风格与大纲条目或直接样题关联；不作频率判断。

## 记忆锚点
- 主程序/子程序：总控与显式调用。
- 对象风格：对象交互，消息通常体现为方法调用。
- 分层：上层用下层服务，注意单向及不越层。

## 来源与证据
- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-013` 的来源 outline 与两个 Topic 的 SPLIT mapping。
- 用户提供的打卡归档：`2026年06月/2026-06-20.md`；Prompt 区块 SHA-256 见 frontmatter。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：风格与层次架构边界说明。

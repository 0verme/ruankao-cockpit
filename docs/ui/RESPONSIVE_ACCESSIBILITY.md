# Responsive & Accessibility Contract v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.7）
> **边界**：本文件冻结断点行为、移动端降级策略与无障碍要求；**不实现任何 CSS、媒体查询或 token package**。

---

## 1. 断点定义（冻结）

```text
Desktop   >= 1280px
Tablet    768px – 1279px
Mobile    < 768px
```

策略：

```text
Desktop First + Mobile usable
```

**明确拒绝**：`Mobile First` 不是本项目的目标（桌面高信息密度是核心价值），但也**明确拒绝**「桌面卡片在移动端无限纵向堆叠」。

---

## 2. 断点布局（冻结）

| 断点 | 列数 | 布局 | 重点 |
|---|---|---|---|
| Desktop（≥1280px） | 3 列 | 左：整体状态 / 中：Today / 右：运营统计 + 时间约束 | 高信息密度；六张卡片全部可见 |
| Tablet（768–1279px） | 2 列 | `TodayFocusCard` + `OverallProgressCard` 优先占首屏 | `OperationalStatsGrid` 折叠或降级 |
| Mobile（<768px） | 1 列 | **Today-first** | 只保证：今天做什么 / 到期复习 / 开始学习 / 完成记录 |

### 2.1 三栏职责的降级顺序

```text
左栏  OverallProgressCard   → 优先级高（保留）
中栏  TodayFocusCard        → 优先级最高（永远第一）
右栏  OperationalStatsGrid  → Tablet 折叠；Mobile 折叠为摘要
右栏  ExamCountdown         → 保留（紧凑形态）
右栏  StudyCalendar         → Mobile 默认折叠
右栏  SubjectStatusGrid     → Mobile 默认折叠
```

**冻结规则**：

```text
1. TodayFocusCard 在任何断点都不得被折叠到首屏之外
2. 移动端的默认展开项不得超过 3 个区块
3. 折叠 ≠ 删除：被折叠的内容必须可通过显式交互展开
```

---

## 3. 移动端降级策略（冻结）

移动端**不得**把桌面所有卡片纵向堆叠成几十屏。

### 3.1 默认折叠 / 降级的区块

| 区块 | Mobile 默认 | 说明 |
|---|---|---|
| `ExplainPanel` | **折叠** | Progressive Disclosure；Explain 是二级信息 |
| `StudyCalendar` | **折叠** | 月份视图在窄屏价值低；保留摘要入口 |
| `SubjectStatusGrid` | **折叠** | 三科详情的价值在桌面更高；折叠为一行摘要 |
| `DailyNoteCard` | **折叠**（且当前属于 Future） | Note 不参与事实指标 |
| `OperationalStatsGrid` | 降级为摘要 | 只保留 ≤4 个 tile；其余需展开 |
| `ProgressSummary` 明细列表 | 折叠 | `TopicAccuracyList` / `CoverageBreakdown` / `ErrorCauseBreakdown` 默认折叠 |
| `PlanModeSwitcher` | 不渲染（未冻结前） | Planner 冻结后进入设置或溢出菜单 |

### 3.2 移动端必须保留

```text
TodayFocusCard（今天做什么）
Review 到期入口摘要（哪些要复习）—— Gate B PASS，domain source 为 P4.5 replay 且 Available；UI Read Model / 前端尚未实现
开始学习 CTA
完成记录入口（写事实事件）
ExamCountdown（紧凑形态）
```

### 3.3 移动端允许的简化（不改变语义）

| 简化 | 允许 | 不允许 |
|---|---|---|
| 隐藏分类明细列表 | ✅ 折叠 | ❌ 隐藏后把聚合值伪装成明细 |
| 把三科合并成一行摘要 | ✅ | ❌ 合并成一个「mastery %」 |
| 缩小非交互说明文字 | ✅（仍须满足可读性） | ❌ 缩小到低于无障碍可读阈值 |
| 用横向滚动展示表格 | ✅（必须有键盘/触控等价） | ❌ 隐藏关键列而不提供替代 |
| 减少同时可见的 tile 数 | ✅ | ❌ 用假数据补齐网格 |

---

## 4. 组件 × 断点行为矩阵

| 组件 | Desktop（≥1280） | Tablet（768–1279） | Mobile（<768） |
|---|---|---|---|
| `AppShell` | 3 列 + 顶部 header + ContextStrip + PrimaryNav | 2 列 + 顶部导航（可横向滚动） | 单列 + 顶栏 + 底部/抽屉导航 |
| `TopHeader` | 全宽，含 `PlanModeSwitcher` / `ReplayControl` | 全宽，次要控件进溢出菜单 | 紧凑，只保留标题 + 设置 / 重放入口 |
| `ContextStrip` | 全宽（白名单字段，最多 5 项） | 精简为 3 项 | 折叠（点击展开） |
| `PrimaryNav` | 横向 7 项 | 横向可滚动 | 抽屉 / 底部导航 |
| `OverallProgressCard` | 左栏 | 首屏（与 Today 并列） | 首屏（Today 之后） |
| `TodayFocusCard` | 中栏，首屏 | 首屏（优先） | **首屏第一位** |
| `OperationalStatsGrid` | 右栏完整网格 | 折叠 / 降级 | 摘要（≤4 tile）+ 展开 |
| `ExamCountdown` | 右栏 | 首屏可见（紧凑） | 紧凑条（Today 之后） |
| `StudyCalendar` | 右栏 | 降级为紧凑摘要 | **默认折叠** |
| `SubjectStatusGrid` | 右栏三卡 | 折叠为一行摘要 | **默认折叠** |
| `ReviewQueue` | 单列列表 + 内联 Explain | 单列列表 | 单列列表（Explain 默认折叠） |
| `ProgressSummary` | 多区块并排 | 单列 | 单列（明细默认折叠） |
| `ExplainPanel` | 内联展开 | 内联展开 | 折叠 + 全屏抽屉（避免挤压） |
| `PolicyVersionFooter` | 页脚常驻 | 页脚常驻 | 折叠进「关于本视图」 |
| `DailyNoteCard` | Future | Future | Future（默认折叠） |

---

## 5. 触控与交互

| 规则 | 要求 |
|---|---|
| 触控目标 | ≥ 44 × 44 px（含 padding） |
| hover-only 交互 | **禁止**；所有 hover 揭示的信息必须有触控 / 键盘等价 |
| 手势 | 不得使用无替代的手势（如仅靠滑动删除） |
| 滚动 | 不阻断浏览器默认滚动；不劫持滚轮 |
| 点击热区 | 卡片可点击区域必须明确，不与内部按钮冲突 |
| 拖动 | 不做拖拽排序（排序来自 engine） |

---

## 6. 无障碍（WCAG 2.1 AA）

### 6.1 对比度

| 要求 | 内容 |
|---|---|
| 正文文字 | ≥ 4.5:1 |
| 大号文字（≥18.66px bold / ≥24px） | ≥ 3:1 |
| 非文本 UI 边界 / 图标 | ≥ 3:1 |
| **橙色在白色背景上的文字** | 必须使用足够深的色阶以满足 AA；**浅橙色只用于填充 / 描边** |
| 图表元素（圆环 / 进度条） | 与背景 ≥ 3:1，且提供文本等价 |

**验证要求**：token 冻结前必须做对比度校验；未校验的组合不得上线。

### 6.2 颜色不是唯一状态信号

以下状态必须同时有**文字或图标**：

```text
mastery status
due / overdue
insufficient_evidence
estimation / unavailable
错误归因类别
coverage 等级
```

禁止：

```text
只用一个红点表示「逾期 N 天」
只用绿/红区分「达到当前策略阈值 / 学习中」
只用颜色深浅表示覆盖程度
```

### 6.3 键盘可达性

| 要求 | 内容 |
|---|---|
| 全部交互元素可键盘到达 | Tab 顺序符合视觉顺序 |
| 可见 focus 状态 | focus ring 不得被 `outline: none` 静默移除 |
| 折叠控件 | 必须可通过键盘展开 / 收起（`button` + `aria-expanded`） |
| 跳过导航 | 提供 skip-to-content |
| 无键盘陷阱 | 抽屉 / 对话框必须可 Esc 关闭并返回焦点 |
| 焦点管理 | 展开 Explain / 抽屉后焦点进入内容区，关闭后回到触发元素 |

### 6.4 语义结构

```text
1. 使用语义化标题层级（h1 → h6，不跳级）
2. 使用 landmark：header / nav / main / aside / footer
3. 每张卡片是一个带标题的 section
4. 列表使用 list 语义（Review Queue、Topic 列表）
5. 表格使用 table 语义（如使用表格布局展示明细）
6. 数据表格与图表必须有 caption / 文本等价
```

### 6.5 `aria-live`

| 场景 | 用法 |
|---|---|
| 重放完成 / 视图更新 | 使用 `aria-live="polite"` |
| 高频变化（如实时计数） | **不使用** `aria-live`，避免刷屏 |
| 错误提交 | 使用 `role="alert"`（谨慎） |

要求：

```text
1. `aria-live` 区域只播报「用户可理解的结论」，不播报每个字段
2. 避免在滚动或过滤时触发连续播报
3. 播报文案必须包含语义（「已逾期 3 天」而不是「badge」）
```

### 6.6 动效

| 要求 | 内容 |
|---|---|
| `prefers-reduced-motion` | 必须尊重；禁用非必要动画与过渡 |
| 自动播放 | 禁止自动播放动画 / 轮播 |
| 闪烁 | 避免 >3 Hz 闪烁 |
| 进度动画 | 允许，但必须有静态最终值 |

### 6.7 图表与可视化

| 要求 | 内容 |
|---|---|
| 提供文本等价 | 圆环 / 进度条必须提供文本描述（例如「综合正确率：尚未评估」） |
| 提供数值 | 图表旁必须有可读数值或说明 |
| 不做唯一表达 | 不得只用颜色 + 面积表达状态 |
| 空态 | 无数据时显示空态文案，而不是 0 长度的圆环 |

### 6.8 Badge 的 screen-reader 文案

| Badge | 可见内容 | screen-reader 文案要求 |
|---|---|---|
| `MasteryBadge` | 图标 + 文字 | 必须读出状态与含义（如「证据不足，尚无足够作答记录」） |
| `DueBadge` | 图标 + 文字 | 必须读出具体信息（如「已逾期 3 天」），不得只有「badge」 |
| `UnavailableBadge` | 文字 | 必须读出依赖（如「依赖 Mastery / Review v0.1」） |
| `EmptyState` | 文字 | 必须读出「为什么没有数据」 |

### 6.9 语言与文本

| 要求 | 内容 |
|---|---|
| 页面 `lang` | 必须声明（`zh-CN`） |
| 语言切换 | 若未来存在，切换处必须标注 `lang` |
| 缩写 | 首次出现给出全称 |
| 数字格式 | 必须固定 locale，避免千分位 / 小数点歧义 |
| 比例表达 | 必须说明分母（避免只显示百分比造成误读） |

---

## 7. 响应式下的语义不变量

以下语义在任何断点都不得改变：

```text
1. null / insufficient_evidence / unavailable 不得在移动端被简化为 0
2. Topic 与 Capability 不得在移动端合并成一个百分比
3. 折叠不得把「有学习记录」升级为「已完成」
4. 折叠不得隐藏 `as_of` 与版本信息的可追溯入口
5. 排序不得因断点改变（Review Queue 顺序在所有断点一致）
```

---

## 8. 已知未决

| # | 未决问题 | 影响 | 阻塞 |
|---|---|---|---|
| 1 | 移动端导航形态（底部导航 vs 抽屉） | 一级导航可达性 | 无（可先实现最小可用形态） |
| 2 | 「折叠摘要」的具体 tile 数量与字段 | 移动端首屏密度 | Gate B / C 冻结后 |
| 3 | 表格在小屏的替代形态 | 明细可读性 | 无 |
| 4 | 深色模式 | 是否支持 | **本轮不承诺**；`light theme first` |
| 5 | 具体色值 | 对比度校验 | 见 [`DESIGN_DIRECTION.md`](DESIGN_DIRECTION.md) §5 |
| 6 | 移动端 Calendar 的替代展示 | 复习债务可视化 | Gate B |

---

## 9. 与其余 UI 文档的关系

| 关注点 | 文档 |
|---|---|
| 卡片组成与断点优先级 | [`COCKPIT_UI_BLUEPRINT.md`](COCKPIT_UI_BLUEPRINT.md) |
| 语义色与 token 方向 | [`DESIGN_DIRECTION.md`](DESIGN_DIRECTION.md) |
| 组件边界（含无障碍职责归属） | [`COMPONENT_MAP.md`](COMPONENT_MAP.md) |
| 路由 | [`PAGE_MAP.md`](PAGE_MAP.md) |
| 值状态与不可用语义 | [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md) §3 / §4 |

# Design Direction v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.8 · token 方向部分）
> **边界**：本文件冻结**视觉方向、语义色和 token 语义**。
> **明确不做**：不创建完整 token package，不创建 CSS framework，不创建主题引擎，不冻结具体色值。

---

## 1. 视觉关键词（冻结）

```text
light
clean
dense
study cockpit
warm accent
card based
progress oriented
action oriented
```

定位一句话：

> 一个**明亮、克制、信息密度高**的备考控制台，让人一眼看到「现在该做什么」。

---

## 2. 采用的方向（冻结）

| 元素 | 方向 | 说明 |
|---|---|---|
| 页面背景 | off-white | 非纯白，降低长时间阅读疲劳 |
| 卡片 | white | 卡片与背景形成轻微层次，不依赖重阴影 |
| 主强调色 | warm orange | 用于主 CTA、当前焦点、需要行动 |
| 正文 / 次要文字 | neutral slate | 冷静的中性色阶，不用纯黑 |
| 边框 | subtle border | 细边框承担主要层次，而不是阴影 |
| 阴影 | soft shadow | 轻、低对比、仅用于浮层与卡片分组 |
| 圆角 | 10–16px | 卡片级圆角；内部小组件使用更小圆角 |
| 间距 | compact dashboard spacing | 高信息密度；区块间距小于营销型布局 |
| 布局 | card based + dashboard | 卡片网格，不做通栏长段落 |
| 语气 | progress oriented + action oriented | 每个区块都要能回答「所以我现在做什么」 |

---

## 3. 明确拒绝的方向（冻结）

```text
❌ 深色科技大屏
❌ 赛博朋克
❌ 玻璃拟态（glassmorphism）
❌ 重渐变
❌ 巨大 Hero Banner
❌ 营销官网式 Landing Page
❌ 每张卡都五颜六色
❌ 巨型 KPI 数字占据首屏
❌ 过量 Emoji
```

理由：

| 拒绝项 | 原因 |
|---|---|
| 深色科技大屏 / 赛博朋克 | 与「长时间学习使用」冲突；高对比霓虹会干扰文字阅读 |
| 玻璃拟态 / 重渐变 | 降低文字对比度，易违反 WCAG AA |
| 巨大 Hero / 营销 Landing | 首屏空间必须留给「今天做什么」，不是品牌宣传 |
| 五颜六色卡片 | 颜色必须承载语义；装饰性配色会让风险色失效 |
| 巨型 KPI 数字 | 单一数字无法解释；本项目要求 Explainability |
| 过量 Emoji | 语义不稳定、无障碍不可靠；状态必须用文字 / 图标表达 |

---

## 4. 语义色（冻结语义，不冻结色值）

| Token 语义 | 颜色方向 | 允许用途 | 禁止用途 |
|---|---|---|---|
| `primary` / `attention` | 暖橙 | 主 CTA、当前焦点、今天到期、需要行动 | 不得同时承担「警告 / 风险」含义 |
| `healthy` / `completed` | 绿 | 已完成、状态良好、sufficient evidence | 不得用于「正在学习中」 |
| `risk` / `overdue` / `weak` | 红 | 已逾期、明确弱项、风险 | 不得用于「证据不足 / 未评估」 |
| `neutral` / `unavailable` | 灰 | 未评估、证据不足、Future、禁用、空态 | 不得用于真实失败 |

### 4.1 语义色硬约束

```text
1. 同一颜色不得同时承担互相冲突的含义（例如橙色既是 primary 又是 warning）
2. insufficient_evidence = neutral（灰），不是 red
3. 颜色不是唯一状态信号：所有状态必须同时有文字或图标
4. 橙色文字在白色背景上必须使用足够深的色阶以满足 WCAG AA；
   浅橙色只用于填充 / 描边
5. 不使用颜色作为唯一区分手段
```

### 4.2 「证据不足」为什么是灰色

```text
insufficient_evidence = 尚未评估
≠ 失败
≠ 0 分
≠ 需要立即行动
```

用红色会把「尚未评估」误报为负面结论，违反 `Honest null` 原则，并制造虚假的紧迫感。

---

## 5. Token 语义草案（方向级，非 package）

以下只定义**语义层 token 名称与用途**。

```text
具体色值、色阶数量、命名规范、暗色模式、生成方式
→ 不在本轮冻结范围
→ 实现前必须完成对比度校验（WCAG 2.1 AA）
```

### 5.1 颜色 token（语义层）

| 语义 token | 用途 |
|---|---|
| `surface.page` | 页面背景（off-white） |
| `surface.card` | 卡片背景（white） |
| `surface.muted` | 次级区块 / 空态背景 |
| `border.subtle` | 卡片与分隔线 |
| `border.strong` | 需要强调的边界 / focus 相关边界 |
| `text.primary` | 主文本（neutral slate 深色阶） |
| `text.secondary` | 次要说明文字 |
| `text.muted` | 元数据 / 版本信息 |
| `accent.primary` | 主强调（暖橙，填充） |
| `accent.primary.text` | 暖橙文字（足够深的色阶，满足 AA） |
| `status.healthy` | 已完成 / 状态良好 |
| `status.risk` | 逾期 / 弱项 / 风险 |
| `status.neutral` | 未评估 / 证据不足 / Future |

### 5.2 间距 token（语义层）

| 语义 token | 用途 |
|---|---|
| `space.card.inner` | 卡片内边距（compact） |
| `space.card.gap` | 卡片之间间距 |
| `space.section.gap` | 区块之间间距 |
| `space.inline` | 行内元素间距 |

**方向**：compact dashboard spacing —— 区块间距必须小于典型营销型页面，但不得压缩到影响可读性或触控目标（≥44px）。

### 5.3 圆角 token（语义层）

| 语义 token | 用途 |
|---|---|
| `radius.card` | 卡片（10–16px 区间） |
| `radius.control` | 按钮 / 输入（小于卡片圆角） |
| `radius.badge` | 徽标 |

### 5.4 阴影 token（语义层）

| 语义 token | 用途 |
|---|---|
| `elevation.card` | 卡片极轻阴影（层次主要由边框承担） |
| `elevation.overlay` | 抽屉 / 浮层 |

### 5.5 排版方向（语义层）

| 方向 | 说明 |
|---|---|
| 层级 | 页面标题 → 区块标题 → 卡片标题 → 正文 → 元数据 |
| 密度 | 正文行高适中，元数据可更紧凑但须满足可读性 |
| 数字 | 数值需要与单位一起显示；比例必须说明分母 |
| 禁止 | 巨型 KPI 数字；首屏被单个数字占据 |

> 具体字体族、字号、行高不在本轮冻结范围。

---

## 6. 视觉层级规则（冻结）

| 层级 | 表达方式 | 禁止 |
|---|---|---|
| 页面（AppShell） | 背景色 + 顶栏 + 导航 | 巨型 Hero |
| 区块（卡片） | 白底 + 细边框 + 极轻阴影 + 卡片圆角 | 彩色卡片堆叠 |
| 卡片内标题 | 字号 / 字重区分，不使用背景色块 | 标题背景填充强调色 |
| 数值 | 与单位 / 分母同时出现 | 脱离语义的巨型数字 |
| 状态 | 文字 / 图标 + 语义色 | 只用颜色 |
| 操作 | 单一主 CTA（primary），次级操作用中性样式 | 多个同权重主色按钮 |
| 元数据 / 版本 | `text.muted`，默认折叠 | 首屏展示 policy 版本 |

---

## 7. 卡片与密度约束

```text
1. 卡片是信息容器，不是装饰容器
2. 每个卡片必须有明确标题，且标题能对应一个 user question
3. 卡片内的数值必须能追溯到 domain source（见 DOMAIN_TO_UI_MAPPING.md）
4. 空态 / 不可用态必须在视觉上与「有数据」明确区分（中性灰）
5. 不允许为了视觉对称而补字段
```

---

## 8. 非目标（本轮明确不做）

```text
❌ 完整 token package
❌ CSS framework / utility class 体系
❌ 主题引擎 / 设计系统运行时
❌ 暗色模式
❌ 组件库实现
❌ 品牌视觉资产（logo / 插画 / 图标集完整方案）
❌ 动画规范（仅保留 prefers-reduced-motion 约束）
```

**理由**：`AGENTS.md` 的 Architecture Priority 明确 `domain correctness > data contract > rule correctness > UI`。在 domain / progress model 稳定前不主动初始化大型前端技术栈，也不以 UI 反推尚未确定的数据模型。

---

## 9. 已知未决

| # | 未决问题 | 阻塞 | 影响 |
|---|---|---|---|
| 1 | 具体色值与色阶 | 对比度校验 | 所有颜色 token |
| 2 | 字体族与字号阶 | 无 | 排版密度 |
| 3 | 图标集 | 无 | 状态的非颜色信号 |
| 4 | 暗色模式是否支持 | **本轮不承诺** | 未来可能的重构成本 |
| 5 | token 交付形式（CSS 变量 / JSON / 代码常量） | Gate D | 实现方式 |
| 6 | 图表可视化库 | 前端技术栈决策（本轮不做） | 圆环 / 进度条实现 |

---

## 10. 与其余 UI 文档的关系

| 关注点 | 文档 |
|---|---|
| 语义色在组件中的使用 | [`COMPONENT_MAP.md`](COMPONENT_MAP.md) |
| 对比度 / 非颜色信号 / 动效 | [`RESPONSIVE_ACCESSIBILITY.md`](RESPONSIVE_ACCESSIBILITY.md) |
| 卡片组成 | [`COCKPIT_UI_BLUEPRINT.md`](COCKPIT_UI_BLUEPRINT.md) §4 |
| 不可用态表达 | [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md) §3 / §4 |

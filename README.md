# ruankao-cockpit

> ruankao-cockpit 是个人软考备考工作台（Control Plane），不是课程、题库或学习内容平台。当前长期 Browser Presentation 主路径为 Astro + React + FastAPI；Streamlit 保留为可回退 fallback（仅修 blocker，不新增 Feature），CLI 保留为 Advanced / Debug 入口。

## 当前能做什么

用户可通过 Browser Cockpit（推荐）或 CLI 初始化本地数据、查看 Today Plan，并将真实综合题作答作为 immutable fact 记录下来：

```text
Progress / Review facts
→ replay
→ Today Plan
→ 真实 attempt
→ Progress + Review Context + Review Item
→ replay
→ 后续 Today Plan
```

计划与进度来自仓库现有生产 engine；CLI 不读取 `tests/` 或 synthetic fixture 作为用户数据。

## 产品边界与当前路线

- 工程闭环已具备：`init → today → record → replay → next-day today`（PR #26 merged）。
- 当前产品验证仍未完成：Issue #16 保持 OPEN；Browser Cockpit 提供本地日常入口后，下一步是继续真实 dogfood、记录明确摩擦；工程 PASS 不等于产品验证 PASS。
- 当前 Astro Browser Presentation 覆盖 Today、`ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS` Topic Learning Experience，以及 `/learn` 的 Learning Path 只读目录和 `/learning-units/{path_id}/{item_id}` 单节浏览。目录顺序来自当前版本化 Learning Path manifest；用户可自主选择并连续浏览，不经 Planner 决定。阅读和上一节/下一节导航不写 Progress、Review、Mastery 或 Completion。Streamlit fallback 仍是 Today 入口。
- Rolling 7-Day、完整 Curriculum Backbone、30-Day Plan 与长期阶段规划已由 Issue #27 deferred，不是默认下一阶段。

## Streamlit fallback：运行现有 Browser Cockpit

Astro + React + FastAPI 已通过 Slice 1 部署态 UAT，是当前长期 Browser Presentation 主路径。仓库尚未提交正式生产 reverse-proxy 配置；需要立即启动既有可用入口时，可使用 Streamlit fallback。需要 Python 3.10+，在仓库根目录安装项目运行依赖并启动：

```bash
python3 -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

首次打开浏览器页面后点击「初始化」，再查看 Today；有学习卡时先阅读目标、核心知识和考试关注点，再决定是否记录真实验证题结果。用户事实保存在本机 `.local/`，这是本地单用户 MVP：无登录、无账号、无数据库、无云同步。仓库只附带一条项目整理的短摘要与出处索引，不复制教材或题库正文；未整理的 Topic 明确显示材料缺失，不实时调用 LLM 补写。

## Astro + React Frontend Migration（Slice 1 — 部署态 PASS）

Astro static + React islands → same-origin `/api/*` → FastAPI → 现有 service/domain。Today 与 Topic 页面消费 Planner、Progress、Review read model；`/learn` 与 `/learning-units/{path_id}/{item_id}` 通过只读 Learning Path / Learning Unit loader 浏览版本化 manifest 和静态 Markdown。目录/翻页不读取或写入 Progress / Review，也不实现 Completion。Browser 不复制 Python Domain Truth。FastAPI 在验证拓扑中仅绑定 loopback，事实目录由显式绝对路径 `COCKPIT_LOCAL_DIR` 指定。

UAT 使用临时本地 reverse proxy 将已构建 `dist/` 与 FastAPI 托管在同一 origin；临时代理配置未提交，正式部署仍需提供受控的 static-server / reverse-proxy 配置。Streamlit 不删除，保留为 fallback，停止新增 Feature 投资，只修阻挡现有可用性的 blocker。真实浏览器持久化、刷新/服务重启 replay、API/domain 一致性及测试证据见 [Frontend Migration Slice 1](docs/frontend/FRONTEND_MIGRATION_SLICE_1.md)。

## FastAPI Transport（Frontend API v0.1）

FastAPI 是 Astro Browser Presentation 的 HTTP adapter；Streamlit fallback 与 API 均复用现有 Python service/domain，不在 route 中重算 Planner / Progress / Review。用绝对路径 `COCKPIT_LOCAL_DIR` 固定本地事实目录；未设置时固定使用仓库根目录下 `.local/`，不随启动 cwd 变化。GET 不会执行初始化。

```bash
# requirements.txt 同时安装 Streamlit 与 FastAPI transport 所需依赖
COCKPIT_LOCAL_DIR=/absolute/path/to/.local uvicorn api:app --host 127.0.0.1 --port 8000
```

接口与 request/response、错误类别、timezone 和 Domain Truth 边界见 [`docs/api/FRONTEND_API_V01.md`](docs/api/FRONTEND_API_V01.md)。

## CLI（Advanced / Debug）

CLI 可用于脚本、工程验证和诊断；CLI 本身使用 Python 标准库。先在仓库根目录运行：

```bash
python3 cockpit.py init
python3 cockpit.py today
```

### 初始化

```bash
python3 cockpit.py init
```

会创建 `.local/`。重复运行不会覆盖已有事实或配置。首次默认配置为 `Asia/Shanghai`、每天 60 分钟、周一至周日均可学习；weekday 编码遵循现有 User Configuration contract（ISO：周一=1 至周日=7）。需要调整时可编辑 `.local/config.json`，字段及版本必须符合该 contract。

### 查看今天计划

```bash
python3 cockpit.py today
```

CLI 在边界读取一次当前时间，按配置 timezone 转换后传给 engine；输出会显示实际使用的 `as_of`（UTC instant）和 `timezone`。复现或测试时可显式提供带时区的时间：

```bash
python3 cockpit.py today --as-of 2026-09-27T09:00:00+08:00
```

输出包含任务类型、canonical Topic ID（以及 taxonomy 已提供的名称）、时长、逾期/到期状态和可供记录使用的 `task_id`。无任务时会说明 `Today has no scheduled tasks.`。

### 记录一次真实作答

先从当天输出复制 `task_id`，再准备 `attempt.json`。它必须是实际作答对应的 `progress-event/v0.1`、`comprehensive_attempt`，并至少包含真实的 `event_id`、带时区的 `occurred_at`、`question` 来源引用、与计划目标一致的 `topics` 及客观 `correct` boolean。来源引用中的 source ID、不可变 source commit、仓库相对 source path 和 question ID 必须来自用户实际使用的题目来源；不要填写猜测或虚构的 provenance。不要把题干、选项、答案或解析写进 fact。

```bash
python3 cockpit.py record \
  --task-id <从 Today 复制的 task_id> \
  --attempt attempt.json \
  --review-context-event-id <稳定且唯一的 Review Context ID>
```

例如可由使用者按自己的事实 ID 命名 `context-attempt-20260927-001`；该 ID 必须符合 Review Event ID contract。CLI 不随机生成 identity，也不把任务完成、计划时长或“我学完了”推断成答对。Browser Cockpit 对技术 event ID 使用 attempt 事实内容与 task ID 的确定性 SHA-256 identity，并从该 identity 派生 Review Context ID；相同事实重提会得到相同 ID 并被 duplicate 校验拒绝。已索引的题目来源会按当前 Topic 提供引用选择器（只选择实际使用过的题目）；其他来源仍可手动填写。CLI 原有显式参数行为不变。`record --as-of <ISO8601>` 可用于确定性复现；实际作答时间应不晚于该 instant。

成功后会报告新增的 Progress Event、Review Item 和 Review Context 数量。相同 event ID 再提交会明确报 duplicate，不会静默去重或覆盖。

### 第二天为什么计划会变化

对新学习任务记录一条 topic-matched 真实 attempt 后，现有 execution adapter 会基于这条 attempt 的来源 provenance 注册稳定的 `review/topic/<topic_id>`，并写入 `initial_learning` context。之后由现有 Review replay / Policy 决定首次到期时间；topic 不再作为 new learning，首次到期时会成为 review，planner 再选择下一个无学习证据的 Topic。

可使用两个固定时间验证同一组数据：

```bash
python3 cockpit.py today --as-of 2026-09-27T09:00:00+08:00
# 复制 [NEW] task_id，使用该 topic 准备真实 attempt.json
python3 cockpit.py record --task-id <task_id> --attempt attempt.json \
  --review-context-event-id context-<attempt-event-id> \
  --as-of 2026-09-27T09:00:00+08:00
python3 cockpit.py today --as-of 2026-09-28T09:00:00+08:00
```

同一 topic 应按现有首次复习规则进入 `[REVIEW]`，下一 Topic 成为 `[NEW]`；实际输出取决于用户已有 facts、配置及 attempt 时间。

### 数据保存在哪里

```text
.local/
├── config.json                 # User Configuration v0.1
├── progress-events.jsonl       # append-only Progress facts
├── review-events.jsonl         # append-only Review Context facts
├── review-items.json           # Review Item catalog；整文件 atomic replace
└── pending/record.json         # record 中断时用于恢复的最小 staging journal
```

`.local/` 已加入 `.gitignore`，不会作为默认仓库内容提交。Progress / Review facts 只追加完整 JSON 行；无效输入会在写入前先经过 Progress 与 Review replay 校验。Review Item catalog、初始化 JSON 与 pending journal 通过同目录临时文件和 `os.replace` 原子替换。多文件本地存储不是数据库事务，突然断电时不承诺跨文件 ACID；保留的 pending journal 会在下次 `today` 或 `record` 命令时尝试完成已预验证的 transaction。

## 当前限制

- 当前是本地单用户 Browser Cockpit MVP；没有数据库、登录、账号或云同步。
- `record` 必须由用户提供真实 attempt provenance 和显式 Review Context event ID；没有 AI 自动判题。
- 当前完整日常执行闭环仅覆盖综合题 attempt；case / essay 尚未进入完整日常闭环。
- Planner 目前只实现 Today；Rolling 7-Day 排程已由 Issue #27 deferred，不是当前 MVP blocker。
- `exam_date` 不参与当前排程策略。

## 架构 / Contract / 历史阶段文档

项目不重新发布完整软考教材。优先维护内容元数据、稳定知识索引、来源引用、immutable facts 与确定性规则；对第三方内容遵循仓库版权边界，license 不明确时不复制正文。

- [当前架构方向](docs/architecture/README.md)
- [Taxonomy 边界](taxonomy/README.md)
- [内容源审计](docs/CONTENT_SOURCE_AUDIT.md)
- [30 天课程草案（历史 Draft；Deferred，不是当前 roadmap）](docs/30_DAY_CURRICULUM_DRAFT.md)
- [Golden Set 策略](data/golden-set/README.md)
- [Phase 2 Golden Set 扩量验证报告](docs/GOLDEN_SET_EXPANSION_VALIDATION.md)
- [Progress Model v0.1 / Replay 边界](engine/progress/README.md)
- [Progress Model v0.1 验证报告](docs/PROGRESS_MODEL_V01_VALIDATION.md)
- [Review Model v0.1](docs/review/REVIEW_MODEL_V01.md)
- [Review Evidence v0.1](docs/review/REVIEW_EVIDENCE_V01.md)
- [Mastery / Review Policy 文档索引](docs/review/README.md)
- [Progress / Adaptive Engine 边界](engine/rules/README.md)
- [Planner 输入、用户配置与输出契约](docs/planner/README.md)
- [Today Planner MVP engine](engine/planner/README.md)
- [当前执行 adapter](engine/execution/README.md)
- [Cockpit UI / UX Blueprint（历史设计参考，非 roadmap / 未实现）](docs/ui/README.md)
- [项目开发边界与测试策略](AGENTS.md)

## 项目状态

Taxonomy / Progress / Review replay、Mastery / Review Policy、Today-only Planner、task execution → replay → next-day replan、new learning → initial review registration，以及最小 CLI 工程闭环已实现。最小 Browser Cockpit 提供 #16 暴露出的 CLI friction 修复入口；#16 仍保持 OPEN，继续真实 dogfood，后续 Slice 只由新证据决定。完整 Phase 5 policy、Rolling 计划、Curriculum Backbone、30 天计划实例化均由 Issue #27 deferred。`mastered` 只表示达到当前 Review Policy 阈值，不是对真实掌握程度的绝对断言。

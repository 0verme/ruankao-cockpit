# 系统架构设计师打卡目录映射审计

> Issue #44 / Taxonomy v0.1。结论：`MAPPING_REVIEW_REQUIRED`。本审计验证打卡归档能否成为用户偏好的学习顺序来源；不修改 Planner、Taxonomy、Progress / Review 或 Learning Payload。

## 结论摘要

原始归档具有可复现的日期/文件顺序，共 110 个带知识点的学习项和 2 个显式休息项。基于实际文件名、Prompt 目标与知识点列表，可映射到现有 active L3 的学习项为 98/110；另 12 项没有足够边界证据而保留为 `UNMAPPED`。

归档可作为“用户希望按什么顺序学”的版本化 **Draft 来源**；当前不能直接作为 Planner 的最终运行时输入：40 项为 `SPLIT`，27 项为 `PARTIAL`，12 项为低置信度 `UNMAPPED`；映射只覆盖 60/110 active L3。所有日期仅作 provenance，不构成学习日历。

## ZIP 与实际文件审计

- Source: user-provided archive `系统架构设计师打卡.zip`（不记录或传播原始机器路径）。
- ZIP 大小：175,511 bytes；SHA-256：`d7e8f68374f250dab72f2a08c543cbe9cbd44533fdc8e1e32c1a0d0e67fce17a`；ZIP CRC 检查通过。
- ZIP entries：118（112 个文件 + 6 个显式目录）。
- Files：112；Markdown：112；非 Markdown：0；空文件：0。
- 重复 ZIP member name：0；SHA-256 完全相同的重复文件：0。
- 目录层级：

```text
系统架构设计师打卡/
├── 2026年06月/  (23 Markdown)
├── 2026年07月/  (31 Markdown)
├── 2026年08月/  (24 Markdown)
├── 2026年09月/  (29 Markdown)
└── 2026年10月/  (5 Markdown)
```

- 日期范围：`2026-06-08` – `2026-10-05`。在该范围内没有文件的日期：`2026-08-02`, `2026-08-03`, `2026-08-04`, `2026-08-06`, `2026-08-29`, `2026-08-30`, `2026-08-31`, `2026-09-29`。这些缺日没有休息标记，**不推断为休息日**。
- 显式非学习项：order 20 `2026-06-27 休息.md`、order 26 `2026-07-03 休息.md`。未发现独立总结页或说明页；110 个其余文件均包含学习知识点与 Prompt。
- 110 个学习文件均出现 `wh-plain-explainer`（或其等价调用）Prompt；Prompt 是来源中的离线讲解辅助指令，不是运行时领域事实。
- 异常命名/元数据：27 个 Markdown 文件名只有日期、没有主题后缀；主题需由文件知识点和 Prompt 补足。
- 明确标题不一致：2026-08-07 文件名/知识点为“领域驱动设计-战术设计”，Prompt 标题却写“领域驱动设计-战略设计”；2026-09-14 文件名/知识点为“白盒测试”，Prompt 标题却写“静态测试”；2026-08-26 文件名为“软件工程-需求工程-概述”，Prompt 标题泛化为“软件工程”。Draft 同时保留 filename-derived `source_title`、`original_topic_title` 和逐项说明，不静默改写原值。
- 原始 Markdown 中包含外部链接、卡片图片和刷题入口；这些正文、图片、URL、题目和 Prompt 全文均未复制进仓库。Draft 只保留短标题/知识点标题与映射审计信息。

## 顺序提取与稳定身份

- 排序规则 deterministic：ISO 日期升序；同日以归档内相对 `source_file` 升序作为 tie-break。没有按 Topic ID、文件在 ZIP 中的压缩顺序或数组位置猜测 taxonomy 映射。
- `item_id` 为按该排序分配的 `checkin-001`…`checkin-112`；`order` 是覆盖全部归档文件的一基序号，显式 NON_LEARNING 项保留其原位。过滤 NON_LEARNING 后得到原始学习顺序；不为缺失日期合成节点。
- `source_file` 是归档根目录下的相对路径；`source_date` 是来源日期 provenance。未来学习日期不受其约束。

## Mapping 方法与状态

- 对每项同时检查文件名/日期、一级知识点标题、Prompt 目标以及可辨识的小节；不按项数、文件位置或日期与 110 个 Taxonomy Topic 做 1:1 假设。
- 只映射到记录的 Taxonomy 版本中的 active L3；未修改 Taxonomy，不把 L1/L2 或 Case Capability 冒充 L3。
- 状态：`EXACT` 单一概念边界；`PARTIAL` 与单一 Topic 部分重叠；`SPLIT` 一项明显跨多个 Topic；`MERGE` 多个来源项在 audit group 中共同覆盖一个 Topic；`UNMAPPED` 无合理 L3；`NON_LEARNING` 不进入学习序列。
- 状态优先级：一项本身对应多个 L3 时标 `SPLIT`，即使也属于重复覆盖 group；`mapping_group_id` 仅补充跨项关系，不覆盖该项的 SPLIT/PARTIAL 状态。`MERGE` 项必须属于一个可审计的多项 group。
- `mapping_confidence` 衡量“选中的语义边界是否有证据”，不衡量覆盖完整度。因此 `PARTIAL` 也可以是 high；high 不等于源项覆盖了 Topic 全部内容。LOW 不得作为最终 Planner 输入。
- `UNMAPPED` 保持空 `topic_ids`。候选相邻领域只在 notes 中解释，不为了清零未映射而填入 Topic。`NON_LEARNING` 的 confidence 为 null。

## Mapping 统计

| 指标 | 数量 |
|---|---:|
| Source items | 112 |
| Learning items | 110 |
| Non-learning items | 2 |
| EXACT | 15 |
| PARTIAL | 27 |
| SPLIT | 40 |
| MERGE | 16 |
| UNMAPPED | 12 |
| HIGH / MEDIUM / LOW | 77 / 21 / 12 |
| Source items with multiple Topic IDs | 40 |

### Source Coverage：98/110 学习项（89.1%）至少映射到一个现有 active L3；12 项明确未映射。

### Taxonomy Coverage：60/110 active L3（54.5%）被路径覆盖；完全未覆盖 50；被多个 source item 重复覆盖 31。此路径不是 Taxonomy 全覆盖课程，未覆盖 Topic 不被补映射。

**uncovered_topic_ids**：

- `ARCH.COMMUNICATION.5G_SDN`
- `ARCH.COMMUNICATION.NETWORK_SECURITY`
- `ARCH.EMBEDDED.EMBEDDED_MIDDLEWARE`
- `ARCH.EMBEDDED.EMBEDDED_SOFTWARE`
- `ARCH.EMBEDDED.REAL_TIME`
- `ARCH.EMBEDDED.SAFETY_CRITICAL`
- `ARCH.INFORMATION.ARCHITECTURE_MODELS`
- `ARCH.INFORMATION.ENTERPRISE_ARCHITECTURE`
- `ARCH.LAYERED.DATA_ACCESS`
- `ARCH.LAYERED.PRESENTATION_MIDDLE`
- `ARCH.SYSTEM_PLANNING.EVALUATION`
- `ARCH.SYSTEM_PLANNING.FEASIBILITY`
- `EMERGING.TECHNOLOGY.CPS`
- `EMERGING.TECHNOLOGY.DIGITAL_TWIN`
- `EMERGING.TECHNOLOGY.ROBOTICS`
- `EVOLUTION.ARCHITECTURE.LEGACY`
- `EVOLUTION.ARCHITECTURE.MAINTENANCE`
- `EVOLUTION.ARCHITECTURE.PROCESS`
- `GOVERNANCE.LAW_IP.COPYRIGHT`
- `GOVERNANCE.LAW_IP.PATENT_TRADEMARK`
- `GOVERNANCE.LAW_IP.SOFTWARE_PROTECTION`
- `GOVERNANCE.STANDARD.PROFESSIONAL_REGULATION`
- `GOVERNANCE.STANDARD.STANDARDIZATION`
- `INFO.FOUNDATION.ENTERPRISE`
- `INFO.FOUNDATION.LIFECYCLE`
- `INFO.FOUNDATION.TYPES`
- `LANGUAGE.PROFESSIONAL_ENGLISH.ARCHITECTURE_TERMS`
- `LANGUAGE.PROFESSIONAL_ENGLISH.READING`
- `MATH.APPLICATION.ALGORITHMS`
- `MATH.APPLICATION.OPTIMIZATION`
- `MATH.APPLICATION.PROBABILITY`
- `QUALITY.ATTRIBUTES.INTEROPERABILITY`
- `QUALITY.ATTRIBUTES.TESTABILITY`
- `QUALITY.ATTRIBUTES.USABILITY`
- `QUALITY.EVALUATION.UTILITY_TREE`
- `RELIABILITY.SOFTWARE.MODELING`
- `SEC.ARCHITECTURE.DATABASE_SECURITY`
- `SEC.INFORMATION.ATTACK_DEFENSE`
- `SEC.INFORMATION.GOVERNANCE`
- `SEC.INFORMATION.SECURITY_PROPERTIES`
- `SOFTWARE.ENGINEERING.CONFIGURATION`
- `SOFTWARE.ENGINEERING.PROJECT_MANAGEMENT`
- `SYSTEM.COMPUTER.EMBEDDED`
- `SYSTEM.COMPUTER.HARDWARE`
- `SYSTEM.COMPUTER.LANGUAGES`
- `SYSTEM.COMPUTER.MIDDLEWARE`
- `SYSTEM.COMPUTER.MULTIMEDIA`
- `SYSTEM.COMPUTER.NETWORKING`
- `SYSTEM.COMPUTER.PERFORMANCE`
- `SYSTEM.COMPUTER.SYSTEM_ENGINEERING`

**duplicate_covered_topic_ids**：

- `ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS`
- `ARCH.CLOUD_NATIVE.EVENT_DRIVEN`
- `ARCH.CLOUD_NATIVE.MICROSERVICES`
- `ARCH.FOUNDATION.REUSE`
- `ARCH.FOUNDATION.STYLES`
- `ARCH.LAYERED.LAYERS`
- `ARCH.SOA.SERVICE_BUS`
- `ARCH.SOA.SERVICE_MODEL`
- `DATA.BIGDATA.DATA_PIPELINE`
- `DATA.CACHE.CACHE_FAILURE`
- `DATA.CACHE.CACHE_PERSISTENCE`
- `DATA.DATABASE.NORMALIZATION`
- `DATA.DATABASE.RELATIONAL`
- `DATA.DATABASE.TRANSACTION`
- `DATA.DISTRIBUTED.CONSISTENCY`
- `DATA.DISTRIBUTED.DISTRIBUTED_LOCK`
- `DATA.DISTRIBUTED.REPLICATION_PARTITIONING`
- `EMERGING.TECHNOLOGY.AI`
- `EMERGING.TECHNOLOGY.CLOUD_COMPUTING`
- `EMERGING.TECHNOLOGY.EDGE`
- `QUALITY.ATTRIBUTES.AVAILABILITY`
- `QUALITY.ATTRIBUTES.PERFORMANCE`
- `QUALITY.ATTRIBUTES.SECURITY`
- `QUALITY.EVALUATION.SCENARIOS`
- `RELIABILITY.SOFTWARE.FAULT_TOLERANCE`
- `SEC.INFORMATION.ACCESS_CONTROL`
- `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN`
- `SOFTWARE.ENGINEERING.PROCESS`
- `SOFTWARE.ENGINEERING.REQUIREMENTS`
- `SOFTWARE.ENGINEERING.TESTING`
- `SOFTWARE.MODELING.UML`

## 完整 Source → Taxonomy Mapping Table

该表覆盖全部 112 个归档文件，包括两个显式休息项。所有 `SPLIT`、`PARTIAL`、`MERGE`、`UNMAPPED` 项的理由见 Notes；完整字段和短 outline 同时冻结于 Draft JSON。

| Order | Source file | Source title | Mapping | Topic ID(s) | Confidence | Notes |
|---:|---|---|---|---|---|---|
| 1 | `2026年06月/2026-06-08.md` | 软件工程 | MERGE | `SOFTWARE.ENGINEERING.PROCESS` | HIGH | 与第 2–5 项共同构成连续的软件过程与开发方法学习簇；本项覆盖生命周期和工程三要素。 |
| 2 | `2026年06月/2026-06-09.md` | 软件工程 | MERGE | `SOFTWARE.ENGINEERING.PROCESS` | HIGH | 瀑布、演化、螺旋、RAD 等开发模型是同一过程主题的分日展开。 |
| 3 | `2026年06月/2026-06-10.md` | 软件工程 | MERGE | `SOFTWARE.ENGINEERING.PROCESS` | HIGH | RUP 的阶段与工作流属于软件过程方法；与相邻开发模型日合并覆盖同一 L3。 |
| 4 | `2026年06月/2026-06-11.md` | 软件工程 | MERGE | `SOFTWARE.ENGINEERING.PROCESS` | HIGH | 敏捷宣言与 Scrum、XP 等方法属于软件过程方法；与相邻 check-in 合并覆盖同一 L3。 |
| 5 | `2026年06月/2026-06-12.md` | 软件工程 | SPLIT | `SOFTWARE.ENGINEERING.PROCESS`<br>`SOFTWARE.ENGINEERING.TESTING` | HIGH | V/W 模型属于开发过程与验证关系，测试左移明确跨越软件过程和软件测试两个边界。 |
| 6 | `2026年06月/2026-06-13.md` | 软件工程 | EXACT | `SOFTWARE.ENGINEERING.COMPONENTS` | HIGH | 构件开发、构件特征、适配和组装与构件技术边界一致。 |
| 7 | `2026年06月/2026-06-14.md` | 软件工程 | EXACT | `SOFTWARE.MODELING.FORMAL_MODELING` | HIGH | 计算无关、平台独立和平台特定模型直接对应模型驱动建模。 |
| 8 | `2026年06月/2026-06-15.md` | 软件工程 | EXACT | `ARCH.FOUNDATION.ABSD` | HIGH | 主题及 ABSD 需求、设计、文档化、复审、实现和演化活动与现有 L3 一致。 |
| 9 | `2026年06月/2026-06-16.md` | 架构 | SPLIT | `ARCH.FOUNDATION.CONCEPTS`<br>`ARCH.FOUNDATION.REUSE` | HIGH | 架构概念/描述与可复用资产及架构复用是两个可区分主题。 |
| 10 | `2026年06月/2026-06-17.md` | 架构 | PARTIAL | `ARCH.FOUNDATION.REUSE` | MEDIUM | DSSA 是领域架构和复用的一个具体方法，仅覆盖架构复用主题的一部分。 |
| 11 | `2026年06月/2026-06-18.md` | 架构 | SPLIT | `QUALITY.ATTRIBUTES.MODIFIABILITY`<br>`QUALITY.EVALUATION.SCENARIOS` | HIGH | 质量属性场景覆盖评估场景，后续可修改性部分映射可修改性属性；不是完整质量属性课程。 |
| 12 | `2026年06月/2026-06-19.md` | 架构 | PARTIAL | `ARCH.FOUNDATION.STYLES` | HIGH | 仅覆盖数据流、批处理与管道过滤器等架构风格子集。 |
| 13 | `2026年06月/2026-06-20.md` | 架构 | SPLIT | `ARCH.FOUNDATION.STYLES`<br>`ARCH.LAYERED.LAYERS` | HIGH | 调用返回与面向对象风格属于架构风格；层次风格/层次组成另属层次式架构。 |
| 14 | `2026年06月/2026-06-21.md` | 架构 | PARTIAL | `ARCH.FOUNDATION.STYLES` | HIGH | 仓库和黑板架构只是以数据为中心风格的部分实例。 |
| 15 | `2026年06月/2026-06-22.md` | 架构 | PARTIAL | `ARCH.FOUNDATION.STYLES` | HIGH | 解释器和规则系统是架构风格专题的局部覆盖，不覆盖其他风格。 |
| 16 | `2026年06月/2026-06-23.md` | 架构 | SPLIT | `ARCH.FOUNDATION.STYLES`<br>`ARCH.CLOUD_NATIVE.EVENT_DRIVEN` | HIGH | 独立构件/进程通信属于风格分类，事件驱动部分直接映射事件驱动架构。 |
| 17 | `2026年06月/2026-06-24.md` | 架构 | PARTIAL | `QUALITY.EVALUATION.SCENARIOS` | MEDIUM | 知识点明确包含基于场景的评估，但也概述问卷和度量方法；当前 L3 仅能覆盖场景部分。 |
| 18 | `2026年06月/2026-06-25.md` | 架构 | SPLIT | `QUALITY.EVALUATION.ATAM`<br>`QUALITY.EVALUATION.TRADEOFF` | HIGH | SAAM/ATAM 对应架构评估，CBAM 与效用权衡相关；来源同时覆盖多个评估边界。 |
| 19 | `2026年06月/2026-06-26.md` | 架构 | PARTIAL | `QUALITY.ATTRIBUTES.PERFORMANCE` | HIGH | 性能指标与并发/并行/池化战术属于性能，但只覆盖该 L3 的若干战术。 |
| 20 | `2026年06月/2026-06-27 休息.md` | 休息 | NON_LEARNING | — | — | 文件明确标记为休息日，无知识点或学习 Prompt。 |
| 21 | `2026年06月/2026-06-28.md` | 性能设计 | MERGE | `QUALITY.ATTRIBUTES.PERFORMANCE` | HIGH | 资源隔离、异步、内存计算、预计算和批处理与第 19、22、23 项共同深化性能主题。 |
| 22 | `2026年06月/2026-06-29.md` | 性能设计战术 | SPLIT | `QUALITY.ATTRIBUTES.PERFORMANCE`<br>`QUALITY.ATTRIBUTES.SCALABILITY` | HIGH | 扩缩容直接涉及可伸缩性；动静分离和读写分离属于性能战术，跨两个 L3。 |
| 23 | `2026年06月/2026-06-30.md` | 性能设计战术 | SPLIT | `DATA.DATABASE.NORMALIZATION`<br>`QUALITY.ATTRIBUTES.PERFORMANCE` | HIGH | 反规范化设计与数据库设计相关，降低锁粒度及写热点分散明确以性能优化为目标。 |
| 24 | `2026年07月/2026-07-01 安全性设计-01.md` | 安全性设计-01 | SPLIT | `QUALITY.ATTRIBUTES.SECURITY`<br>`SEC.INFORMATION.CRYPTOGRAPHY` | HIGH | 安全属性、加密、摘要、签名和 PKI 分别涉及质量安全属性与密码技术。 |
| 25 | `2026年07月/2026-07-02 安全性设计-02.md` | 安全性设计-02 | SPLIT | `SEC.INFORMATION.ACCESS_CONTROL`<br>`SEC.ARCHITECTURE.MODELS` | HIGH | 访问控制类型/技术与 BLP、Biba、Chinese Wall 安全模型属于两个明确边界。 |
| 26 | `2026年07月/2026-07-03 休息.md` | 休息 | NON_LEARNING | — | — | 文件明确标记为休息日，无知识点或学习 Prompt。 |
| 27 | `2026年07月/2026-07-04 安全性设计-03.md` | 安全性设计-03 | EXACT | `SEC.INFORMATION.ACCESS_CONTROL` | HIGH | 身份鉴别、SSO 和 MFA 属于身份认证与访问控制；与后续令牌机制存在重复深化。 |
| 28 | `2026年07月/2026-07-05 安全性设计-04.md` | 安全性设计-04 | PARTIAL | `SEC.INFORMATION.ACCESS_CONTROL` | MEDIUM | OAuth2/JWT 主要覆盖身份授权与令牌访问，仅是访问控制主题的协议/机制子集。 |
| 29 | `2026年07月/2026-07-06 安全性设计-05.md` | 安全性设计-05 | SPLIT | `SEC.INFORMATION.ACCESS_CONTROL`<br>`SEC.ARCHITECTURE.WPDRRC`<br>`SEC.ARCHITECTURE.NETWORK_SECURITY` | MEDIUM | 零信任包含最小权限/持续认证、安全体系措施和网络微分段；多边界映射且不等于完整安全架构。 |
| 30 | `2026年07月/2026-07-07 容灾设计.md` | 容灾设计 | SPLIT | `QUALITY.ATTRIBUTES.AVAILABILITY`<br>`RELIABILITY.SOFTWARE.FAULT_TOLERANCE`<br>`DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | HIGH | 容灾指标、备份恢复、复制和多活架构共同涉及可用性、容错恢复与数据复制。 |
| 31 | `2026年07月/2026-07-08 可靠性设计.md` | 可靠性设计 | SPLIT | `RELIABILITY.SOFTWARE.METRICS`<br>`RELIABILITY.SOFTWARE.FAULT_TOLERANCE`<br>`QUALITY.ATTRIBUTES.AVAILABILITY` | HIGH | 可靠性指标、检错容错技术及集群/负载均衡分别覆盖指标、容错和可用性。 |
| 32 | `2026年07月/2026-07-09 可观测性设计.md` | 可观测性设计 | UNMAPPED | — | LOW | 可观测性（指标、日志、链路追踪）没有同边界 active L3；不把可测试性或可用性强行当作可观测性。 |
| 33 | `2026年07月/2026-07-10 人工智能.md` | 人工智能 | EXACT | `EMERGING.TECHNOLOGY.AI` | HIGH | 人工智能概念、分类与关键技术与人工智能 L3 边界一致。 |
| 34 | `2026年07月/2026-07-11 机器学习.md` | 机器学习 | PARTIAL | `EMERGING.TECHNOLOGY.AI` | HIGH | 机器学习和 Transformer 是人工智能主题的子集；Taxonomy 没有机器学习专属 L3。 |
| 35 | `2026年07月/2026-07-12 大模型应用开发.md` | 大模型应用开发 | PARTIAL | `EMERGING.TECHNOLOGY.AI` | MEDIUM | 大模型及其应用属于 AI 子集，但本项混合提示词、训练、智能体、RAG 等多个内容点。 |
| 36 | `2026年07月/2026-07-13 检索增强生成-RAG.md` | 检索增强生成-RAG | PARTIAL | `EMERGING.TECHNOLOGY.AI` | HIGH | RAG 是 AI 应用技术子集；Taxonomy 没有 RAG 专属 Topic。 |
| 37 | `2026年07月/2026-07-14 智能体架构.md` | 智能体架构 | SPLIT | `EMERGING.TECHNOLOGY.AI`<br>`ARCH.SOA.SERVICE_MODEL`<br>`ARCH.CLOUD_NATIVE.EVENT_DRIVEN` | MEDIUM | 智能体本体属于 AI；服务治理和基于事件的 Agent 通信跨入服务模型与事件驱动边界。 |
| 38 | `2026年07月/2026-07-15 知识图谱.md` | 知识图谱 | SPLIT | `DATA.BIGDATA.KNOWLEDGE_GRAPH`<br>`EMERGING.TECHNOLOGY.KNOWLEDGE_REPRESENTATION` | HIGH | 知识图谱构建/存储/查询与实体、本体、谓词等知识表示概念均有明确覆盖。 |
| 39 | `2026年07月/2026-07-16 推荐系统.md` | 推荐系统 | PARTIAL | `EMERGING.TECHNOLOGY.AI` | MEDIUM | 推荐算法及冷启动/同质化治理属于 AI 应用，但不是独立推荐系统 L3。 |
| 40 | `2026年07月/2026-07-17 数据挖掘.md` | 数据挖掘 | UNMAPPED | — | LOW | 数据挖掘与 OLAP/分类聚类没有同边界 active L3；不将其宽泛归入 AI 或数据流水线。 |
| 41 | `2026年07月/2026-07-18 云计算.md` | 云计算 | EXACT | `EMERGING.TECHNOLOGY.CLOUD_COMPUTING` | HIGH | 云计算部署模式与 IaaS/PaaS/SaaS/FaaS 等服务模式直接对应。 |
| 42 | `2026年07月/2026-07-19 边缘计算.md` | 边缘计算 | EXACT | `EMERGING.TECHNOLOGY.EDGE` | HIGH | 边缘计算概念及优缺点与边缘计算 L3 一致。 |
| 43 | `2026年07月/2026-07-20 边云协同.md` | 边云协同 | SPLIT | `EMERGING.TECHNOLOGY.EDGE`<br>`EMERGING.TECHNOLOGY.CLOUD_COMPUTING` | MEDIUM | 边云协同同时涉及边缘计算与云计算；现有 Taxonomy 没有边云协同专属边界。 |
| 44 | `2026年07月/2026-07-21 物联网.md` | 物联网 | SPLIT | `ARCH.LAYERED.IOT`<br>`ARCH.COMMUNICATION.NETWORK_ARCHITECTURE` | HIGH | 物联网系统架构与 MQTT 通信协议分别对应 IoT 层次架构和通信网络架构。 |
| 45 | `2026年07月/2026-07-22 区块链.md` | 区块链 | UNMAPPED | — | LOW | 区块链/智能合约没有同边界 active L3；不以分布式一致性替代区块链专题。 |
| 46 | `2026年07月/2026-07-23 锁.md` | 锁 | SPLIT | `SYSTEM.COMPUTER.OPERATING_SYSTEMS`<br>`DATA.DATABASE.TRANSACTION`<br>`QUALITY.ATTRIBUTES.PERFORMANCE` | MEDIUM | 通用锁、死锁、数据库并发锁及降低锁粒度分别涉及 OS 同步、数据库事务和性能战术。 |
| 47 | `2026年07月/2026-07-24 分布式锁.md` | 分布式锁 | EXACT | `DATA.DISTRIBUTED.DISTRIBUTED_LOCK` | HIGH | 关系库、Redis、ZooKeeper、Etcd 分布式锁机制与分布式锁 L3 一致。 |
| 48 | `2026年07月/2026-07-25 微服务架构.md` | 微服务架构 | EXACT | `ARCH.CLOUD_NATIVE.MICROSERVICES` | HIGH | 微服务架构概念、特征、原则和模式与微服务 L3 边界一致。 |
| 49 | `2026年07月/2026-07-26 服务间的通信.md` | 服务间的通信 | SPLIT | `ARCH.SOA.SERVICE_PROTOCOLS`<br>`ARCH.SOA.SERVICE_BUS` | HIGH | HTTP/REST、gRPC 属于服务协议；同步/异步通信范式还覆盖消息服务总线。 |
| 50 | `2026年07月/2026-07-27 服务治理.md` | 服务治理 | SPLIT | `ARCH.SOA.SERVICE_MODEL`<br>`QUALITY.ATTRIBUTES.AVAILABILITY`<br>`QUALITY.ATTRIBUTES.PERFORMANCE` | MEDIUM | 注册发现、治理属于服务模型；负载均衡/熔断/限流覆盖可用性与性能；没有把治理等同于 Service Mesh。 |
| 51 | `2026年07月/2026-07-28 负载均衡.md` | 负载均衡 | SPLIT | `ARCH.COMMUNICATION.HIGH_AVAILABILITY`<br>`QUALITY.ATTRIBUTES.PERFORMANCE` | MEDIUM | 负载均衡算法和部署层次涉及性能，并与网络高可用有交集，但不能代表该主题全部内容。 |
| 52 | `2026年07月/2026-07-29 限流.md` | 限流 | PARTIAL | `QUALITY.ATTRIBUTES.PERFORMANCE` | HIGH | 限流算法和请求处置是性能/容量控制战术的一部分。 |
| 53 | `2026年07月/2026-07-30 重试策略.md` | 重试策略 | PARTIAL | `RELIABILITY.SOFTWARE.FAULT_TOLERANCE` | HIGH | 重试条件与退避策略属于容错恢复战术，但仅覆盖可靠性 L3 的一部分。 |
| 54 | `2026年07月/2026-07-31 微服务划分.md` | 微服务划分 | PARTIAL | `ARCH.CLOUD_NATIVE.MICROSERVICES` | HIGH | 微服务拆分原则与因素直接关联微服务架构，但没有覆盖其完整边界。 |
| 55 | `2026年08月/2026-08-01 领域驱动设计-核心理念.md` | 领域驱动设计-核心理念 | UNMAPPED | — | LOW | DDD 核心理念没有同边界 active L3；架构复用/建模主题不足以代表领域驱动设计。 |
| 56 | `2026年08月/2026-08-05 领域驱动设计-战略设计.md` | 领域驱动设计-战略设计 | UNMAPPED | — | LOW | DDD 战略设计、限界上下文、上下文映射和事件风暴无专属 L3，不强行归入微服务。 |
| 57 | `2026年08月/2026-08-07 领域驱动设计-战术设计.md` | 领域驱动设计-战术设计 | UNMAPPED | — | LOW | DDD 战术设计的实体/值对象/聚合等没有同边界 active L3，不以架构基础代替；文件名/知识点为“战术设计”，Prompt 标题误写“战略设计”。 |
| 58 | `2026年08月/2026-08-08 领域驱动设计-架构模式.md` | 领域驱动设计-架构模式 | SPLIT | `ARCH.FOUNDATION.STYLES`<br>`ARCH.LAYERED.LAYERS`<br>`ARCH.CLOUD_NATIVE.EVENT_DRIVEN` | MEDIUM | 分层/六边形/洋葱属于架构风格或层次；事件溯源与 CQRS 是事件驱动相关，但 CQRS 未独立建模。 |
| 59 | `2026年08月/2026-08-09 云原生架构概述.md` | 云原生架构概述 | UNMAPPED | — | LOW | 云原生通用原则超出现有四个云原生子主题的明确边界；不映射到父级或任意子 Topic。 |
| 60 | `2026年08月/2026-08-10 云原生架构-容器技术.md` | 云原生架构-容器技术 | PARTIAL | `ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS` | HIGH | 容器、镜像、引擎和编排直接对应容器子主题，但不覆盖 Serverless 部分。 |
| 61 | `2026年08月/2026-08-11 云原生架构-架构模式.md` | 云原生架构-架构模式 | SPLIT | `ARCH.SOA.SERVICE_MODEL`<br>`ARCH.CLOUD_NATIVE.SERVICE_MESH`<br>`ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS`<br>`DATA.DISTRIBUTED.CONSISTENCY` | MEDIUM | 清单跨服务化、服务网格、Serverless、分布式事务；存储计算分离和可观测性没有精确 L3。 |
| 62 | `2026年08月/2026-08-12 Kubernetes 资源类型.md` | Kubernetes 资源类型 | PARTIAL | `ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS` | HIGH | Kubernetes 资源和探针是容器编排实现细节，不等于容器与 Serverless 全部边界。 |
| 63 | `2026年08月/2026-08-13 消息中间件-概述.md` | 消息中间件-概述 | PARTIAL | `ARCH.SOA.SERVICE_BUS` | MEDIUM | 消息中间件作用、通信与消费模式属于消息服务总线的一部分。 |
| 64 | `2026年08月/2026-08-14 消息中间件-kafka.md` | 消息中间件-kafka | PARTIAL | `ARCH.SOA.SERVICE_BUS` | HIGH | Kafka 组件与消费模型属于消息中间件专题；现有 L3 不细分具体产品或分区机制。 |
| 65 | `2026年08月/2026-08-15 消息中间件-常见问题及解决方案.md` | 消息中间件-常见问题及解决方案 | SPLIT | `ARCH.SOA.SERVICE_BUS`<br>`DATA.DISTRIBUTED.CONSISTENCY`<br>`RELIABILITY.SOFTWARE.FAULT_TOLERANCE` | MEDIUM | 消息可靠投递属于服务总线，顺序/重复/事务涉及一致性，丢失与积压治理涉及容错。 |
| 66 | `2026年08月/2026-08-16 Redis-数据类型.md` | Redis-数据类型 | UNMAPPED | — | LOW | Redis 数据结构没有 active L3；不能因为它是缓存产品就映射到缓存读写或失效治理。 |
| 67 | `2026年08月/2026-08-17 Redis-持久化.md` | Redis-持久化 | PARTIAL | `DATA.CACHE.CACHE_PERSISTENCE` | HIGH | RDB/AOF/混合持久化直接覆盖缓存持久化的一部分；未覆盖复制。 |
| 68 | `2026年08月/2026-08-18 Redis-数据过期与内存淘汰机制.md` | Redis-数据过期与内存淘汰机制 | PARTIAL | `DATA.CACHE.CACHE_FAILURE` | MEDIUM | 键过期和淘汰与缓存失效治理相邻，但不等于击穿/穿透/雪崩等完整边界。 |
| 69 | `2026年08月/2026-08-19 Redis-批量操作与事务.md` | Redis-批量操作与事务 | UNMAPPED | — | LOW | Redis Pipeline/Lua/事务语义没有同边界 active L3；不直接套用关系数据库事务。 |
| 70 | `2026年08月/2026-08-20 Redis-集群架构.md` | Redis-集群架构 | SPLIT | `DATA.CACHE.CACHE_PERSISTENCE`<br>`DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | HIGH | Redis 主从/哨兵复制与 Cluster 分片分别涉及缓存复制和通用数据分布。 |
| 71 | `2026年08月/2026-08-21 Redis-缓存更新模式.md` | Redis-缓存更新模式 | PARTIAL | `DATA.CACHE.CACHE_ASIDE` | HIGH | 旁路缓存与 Cache-Aside 对齐；读写穿透、写回及 CDC 异步更新超出该 L3。 |
| 72 | `2026年08月/2026-08-22 Redis-常见问题及解决方案.md` | Redis-常见问题及解决方案 | MERGE | `DATA.CACHE.CACHE_FAILURE` | HIGH | 击穿/穿透/雪崩覆盖缓存失效主题核心，与第 68 项共同覆盖；冷启动和 BigKey 是相邻补充。 |
| 73 | `2026年08月/2026-08-23 大数据架构-概述.md` | 大数据架构-概述 | EXACT | `DATA.BIGDATA.DATA_PIPELINE` | HIGH | 数据采集、清洗、存储、分析及批/流处理架构与数据处理流水线一致。 |
| 74 | `2026年08月/2026-08-24 大数据架构-架构模式.md` | 大数据架构-架构模式 | EXACT | `DATA.BIGDATA.LAMBDA_KAPPA` | HIGH | Lambda 与 Kappa 架构名称及实现原理直接对应现有 L3。 |
| 75 | `2026年08月/2026-08-25 大数据架构-湖仓一体架构.md` | 大数据架构-湖仓一体架构 | UNMAPPED | — | LOW | 数据湖、数据仓库与湖仓一体缺少同边界 active L3；数据流水线不覆盖其存储/计算架构。 |
| 76 | `2026年08月/2026-08-26 软件工程-需求工程-概述.md` | 软件工程-需求工程-概述 | EXACT | `SOFTWARE.ENGINEERING.REQUIREMENTS` | HIGH | 需求工程、基线、需求开发/管理和跟踪与需求工程 L3 一致；文件名指向需求工程，Prompt 标题泛化为“软件工程”。 |
| 77 | `2026年08月/2026-08-27 分布式协调.md` | 分布式协调 | SPLIT | `DATA.DISTRIBUTED.DISTRIBUTED_LOCK`<br>`ARCH.SOA.SERVICE_MODEL` | MEDIUM | ZooKeeper 协调包含分布式锁和服务注册/集群治理；队列/配置等细目没有独立映射。 |
| 78 | `2026年08月/2026-08-28 分布式事务.md` | 分布式事务 | SPLIT | `DATA.DISTRIBUTED.CONSISTENCY`<br>`DATA.DATABASE.TRANSACTION`<br>`ARCH.SOA.SERVICE_BUS` | HIGH | CAP/BASE、2PC/TCC/Saga、最终一致性及消息事务横跨分布式一致性、事务与消息总线。 |
| 79 | `2026年09月/2026-09-01 结构化需求分析.md` | 结构化需求分析 | EXACT | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | HIGH | 结构化分析、DFD 功能模型及分析过程与系统分析 L3 对齐。 |
| 80 | `2026年09月/2026-09-02 结构化需求分析.md` | 结构化需求分析 | PARTIAL | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | HIGH | ER 图和数据字典是结构化分析模型的一部分，仅覆盖系统分析与设计边界的一段。 |
| 81 | `2026年09月/2026-09-03 面向对象分析.md` | 面向对象分析 | PARTIAL | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | HIGH | 面向对象分析概念与模型是系统分析/设计的一种方法，未单独映射为 UML。 |
| 82 | `2026年09月/2026-09-04 面向对象分析.md` | 面向对象分析 | SPLIT | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN`<br>`SOFTWARE.MODELING.UML` | HIGH | 用例模型与分析模型兼具系统分析和 UML 建模内容。 |
| 83 | `2026年09月/2026-09-05 面向对象分析.md` | 面向对象分析 | MERGE | `SOFTWARE.MODELING.UML` | HIGH | UML 静态/动态图分类与第 82、84 项共同覆盖 UML 建模主题。 |
| 84 | `2026年09月/2026-09-06 面向对象分析.md` | 面向对象分析 | SPLIT | `SOFTWARE.MODELING.UML`<br>`ARCH.FOUNDATION.VIEWS` | HIGH | 活动/顺序/通信/状态图属于 UML；4+1 视图属于架构视图，明确跨两个 Topic。 |
| 85 | `2026年09月/2026-09-07 需求验证.md` | 需求验证 | PARTIAL | `SOFTWARE.ENGINEERING.REQUIREMENTS` | HIGH | 需求评审与需求测试直接覆盖需求验证，但只覆盖需求工程的一部分；与 8 月 26 日主题相隔数项。 |
| 86 | `2026年09月/2026-09-08 系统设计.md` | 系统设计 | SPLIT | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN`<br>`SOFTWARE.MODELING.BUSINESS_PROCESS` | HIGH | 系统设计/UI 与业务处理流程、WFMS 是系统设计和业务流程建模两个边界。 |
| 87 | `2026年09月/2026-09-09 结构化设计.md` | 结构化设计 | PARTIAL | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | HIGH | 模块、耦合与内聚属于结构化系统设计的局部内容。 |
| 88 | `2026年09月/2026-09-10 面向对象设计.md` | 面向对象设计 | SPLIT | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN`<br>`ARCH.FOUNDATION.DESIGN_PATTERNS` | HIGH | 面向对象设计原则与设计活动属于系统设计；设计模式是独立架构基础 Topic。 |
| 89 | `2026年09月/2026-09-11 软件测试概述.md` | 软件测试概述 | MERGE | `SOFTWARE.ENGINEERING.TESTING` | HIGH | 测试定义/分类及缺陷管理开启连续测试专题，与后续测试方法和阶段项共同覆盖同一 L3。 |
| 90 | `2026年09月/2026-09-12 黑盒测试.md` | 黑盒测试 | MERGE | `SOFTWARE.ENGINEERING.TESTING` | HIGH | 黑盒测试及等价类、边界值和判定表是软件测试方法的深化。 |
| 91 | `2026年09月/2026-09-13 静态测试.md` | 静态测试 | MERGE | `SOFTWARE.ENGINEERING.TESTING` | HIGH | 静态测试、走查、审查与静态分析属于软件测试专题的一部分。 |
| 92 | `2026年09月/2026-09-14 白盒测试.md` | 白盒测试 | MERGE | `SOFTWARE.ENGINEERING.TESTING` | HIGH | 知识点正文为白盒测试；文件名为“白盒测试”，但 Prompt 标题误写“静态测试”，按正文映射并保留该异常。 |
| 93 | `2026年09月/2026-09-15 单元测试.md` | 单元测试 | MERGE | `SOFTWARE.ENGINEERING.TESTING` | HIGH | 单元测试方法、覆盖、自动化及依赖隔离深化软件测试主题。 |
| 94 | `2026年09月/2026-09-16 集成测试.md` | 集成测试 | MERGE | `SOFTWARE.ENGINEERING.TESTING` | HIGH | 集成测试策略与集成方向属于软件测试主题。 |
| 95 | `2026年09月/2026-09-17 性能测试.md` | 性能测试 | SPLIT | `SOFTWARE.ENGINEERING.TESTING`<br>`QUALITY.ATTRIBUTES.PERFORMANCE` | HIGH | 测试类型/过程属于软件测试；负载、稳定、压力等测试目标直接关联性能属性。 |
| 96 | `2026年09月/2026-09-18 安全性测试.md` | 安全性测试 | SPLIT | `SOFTWARE.ENGINEERING.TESTING`<br>`QUALITY.ATTRIBUTES.SECURITY`<br>`SEC.ARCHITECTURE.VULNERABILITY` | MEDIUM | 安全测试活动跨软件测试、安全属性与脆弱性分析；社会工程等细项并无单独 L3。 |
| 97 | `2026年09月/2026-09-19 可靠性测试.md` | 可靠性测试 | SPLIT | `SOFTWARE.ENGINEERING.TESTING`<br>`RELIABILITY.SOFTWARE.EVALUATION` | HIGH | 可靠性测试既是测试活动，也对应可靠性测试与评价 Topic。 |
| 98 | `2026年09月/2026-09-20 自动化测试.md` | 自动化测试 | MERGE | `SOFTWARE.ENGINEERING.TESTING` | HIGH | 自动化测试、CI 触发和 UI 自动化是连续测试专题的后续深化。 |
| 99 | `2026年09月/2026-09-21 关系模型.md` | 关系模型 | SPLIT | `DATA.DATABASE.RELATIONAL`<br>`DATA.DATABASE.NORMALIZATION` | HIGH | 关系运算属于关系数据库；关系模式分解及无损/依赖保持进入规范化与数据库设计。 |
| 100 | `2026年09月/2026-09-22 规范化设计.md` | 规范化设计 | MERGE | `DATA.DATABASE.NORMALIZATION` | HIGH | 范式和反规范化原则与关系模式/数据库设计日共同覆盖规范化主题。 |
| 101 | `2026年09月/2026-09-23 数据库索引.md` | 数据库索引 | PARTIAL | `DATA.DATABASE.RELATIONAL` | HIGH | 数据库索引属于关系数据库实现，但现有 Taxonomy 没有索引专属 L3。 |
| 102 | `2026年09月/2026-09-24 反规范化设计.md` | 反规范化设计 | SPLIT | `DATA.DATABASE.NORMALIZATION`<br>`QUALITY.ATTRIBUTES.PERFORMANCE` | HIGH | 反规范化与数据库设计相关，来源明确以性能为取舍依据。 |
| 103 | `2026年09月/2026-09-25 视图-触发器-锁-存储过程.md` | 视图-触发器-锁-存储过程 | SPLIT | `DATA.DATABASE.RELATIONAL`<br>`DATA.DATABASE.TRANSACTION` | MEDIUM | 视图/触发器/存储过程属于关系数据库对象，锁属于数据库并发事务机制。 |
| 104 | `2026年09月/2026-09-26 数据库事务.md` | 数据库事务 | MERGE | `DATA.DATABASE.TRANSACTION` | HIGH | 事务 ACID、并发异常和隔离级别与第 103 项的锁共同覆盖数据库事务边界。 |
| 105 | `2026年09月/2026-09-27 数据库设计过程.md` | 数据库设计过程 | PARTIAL | `DATA.DATABASE.NORMALIZATION` | HIGH | 三级模式、独立性和设计过程属于数据库设计，但没有覆盖规范化概念全貌。 |
| 106 | `2026年09月/2026-09-28 MySQL 集群架构.md` | MySQL 集群架构 | SPLIT | `DATA.DATABASE.RELATIONAL`<br>`DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | HIGH | MySQL 关系数据库主从/读写分离同时覆盖关系数据库和分布式复制。 |
| 107 | `2026年09月/2026-09-30 NoSQL数据库.md` | NoSQL数据库 | EXACT | `DATA.DATABASE.NOSQL` | HIGH | NoSQL 概念、分类及与关系数据库比较与 NoSQL L3 一致。 |
| 108 | `2026年10月/2026-10-01.md` | 数据架构设计-数据仓库 | UNMAPPED | — | LOW | OLAP、数据仓库层次和湖仓一体没有同边界 active L3；不将其强塞入数据处理流水线。 |
| 109 | `2026年10月/2026-10-02.md` | 数据架构设计-数据同步 | SPLIT | `DATA.DISTRIBUTED.REPLICATION_PARTITIONING`<br>`DATA.BIGDATA.DATA_PIPELINE`<br>`ARCH.SOA.SERVICE_BUS` | MEDIUM | 全量/增量同步、CDC/消息与零停机迁移跨复制分布、数据处理和消息技术。 |
| 110 | `2026年10月/2026-10-03.md` | 数据架构设计-数据分片技术 | EXACT | `DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | HIGH | 垂直/水平分片、哈希/范围算法与分片实现直接对应复制、分片与数据分布。 |
| 111 | `2026年10月/2026-10-04.md` | 数据架构设计-数据分片技术-分布式 ID | UNMAPPED | — | LOW | 分布式 ID 的生成算法没有同边界 active L3；不以分布式分片主题替代 ID 设计。 |
| 112 | `2026年10月/2026-10-05.md` | 数据架构设计-数据分片技术-常见问题及其解决方案 | SPLIT | `DATA.DISTRIBUTED.REPLICATION_PARTITIONING`<br>`DATA.DISTRIBUTED.CONSISTENCY`<br>`DATA.DATABASE.TRANSACTION` | MEDIUM | 分片问题涉及数据分布、跨分片一致性与事务/查询治理，映射到三个相关 L3。 |

## 顺序合理性审计

**ORDER_REVIEW_NEEDED**（只记录，不重排）。

- 可观察到分阶段结构：6 月软件过程/架构基础与质量评估；7 月安全、可靠性、AI 与云边/微服务；8 月 DDD、云原生、消息/Redis 与大数据；9 月需求/分析设计、测试和关系数据库；10 月数据仓库/同步/分片主题。微服务设计 → 服务通信/治理 → 负载均衡/限流/重试 → 微服务划分，主题内有渐进深化；测试专题 9/11–9/20 连续展开；数据库与数据分布 9/21–10/05 大体由基础走向集群/分片问题。
- 有显式休息项穿插在性能战术与安全系列中；8 月 DDD 文件日期有缺口。休息文件本身保留在序号里；8/2–8/4、8/6、8/29–8/31、9/29 只是缺少文件，不能自动当成休息或非学习日。
- 需求主题从 8/26 概述开始，8/27–8/28 转到分布式协调/事务，9/1–9/7 才继续结构化分析、OO 分析与需求验证；存在主题间断，是否刻意间隔/先修需要用户确认。
- 安全系列以密码/访问控制/认证延伸到零信任，方向基本递进；但 7/4 身份认证主题和 7/5 OAuth/JWT 存在交叠。Redis 项 8/16–8/22 连续深入数据类型、持久化、淘汰、事务、集群、更新与失效；多个项映射同一 L3 不代表同一天自动变成一个 Planner 任务或完成事实。
- 未发现必须判为严重的硬性先修倒置证据；但“从基础直接跳高级”不能仅由文件标题判定。尤其 cloud-native、DDD、数据仓库/湖仓等未被当前 Taxonomy 细分，顺序合理性与映射未决项需一并复核。
- 该目录从软件工程/架构主题开始，未覆盖很多基础、法规、数学、英语、嵌入式等 L3；这是覆盖边界，不凭 coverage 缺口改 Taxonomy 或重新排序。

## Prompt 与内容治理

- `wh-plain-explainer` 是来源中的 offline `Learning Payload authoring / offline content generation aid`，不是 Runtime Domain Truth。浏览器不依赖 Prompt 运行时生成事实；Planner 不读取 Prompt；Progress / Review 不读取 Prompt；Prompt 不自动成为 Learning Payload。
- 任何 AI 输出都需经过人工内容治理、事实核验和来源/provenance 审核后，才可另行版本化为 Learning Payload。本 PR 不生成 payload、不复制正文、不引入 AI runtime。

## 审计决定

原始归档的 110 项学习顺序可以 deterministic 提取，且大多数学习项至少可挂接一个现有 Topic；因此保留 `system-architect-checkin` v1 Draft。当前映射包含 40 个多 Topic split、27 个部分覆盖项、12 个 low-confidence unmapped，且 taxonomy 有 50 个未覆盖 L3。将其提升为正式 Planner 顺序前，需要人工复核映射边界、split/partial 的原子化方式、merge 重复项语义与 ORDER_REVIEW_NEEDED 项。

Planner integration remains DEFERRED. 此审计没有改变 new-learning 选择规则。

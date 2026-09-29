# 系统架构设计师打卡学习单元索引

> 静态 Markdown authoring artifacts；不接入 Planner、Progress、Review 或运行时 AI。
> 每个文件保留原始 `item_id` / `order`。休息记录不生成学习单元。

## 来源与状态

- Learning Path：`system-architect-checkin` v1.0.0（当前仍为 `draft`）。
- 来源归档：`系统架构设计师打卡.zip`；SHA-256：`d7e8f68374f250dab72f2a08c543cbe9cbd44533fdc8e1e32c1a0d0e67fce17a`。原始正文未作为归档副本加入仓库。
- 学习单元：110；休息/非学习项：2（`checkin-020`, `checkin-026`).
- Mapping：EXACT 15, PARTIAL 27, SPLIT 40, MERGE 16, UNMAPPED 12.
- 内容缺证标记：`source_gap` 75；未标记已知缺口：35。所有文件仍为 `generation.status: draft`，生成/校验通过不等于人工内容审核通过。
- `UNMAPPED` 项保持空 `topic_ids`；SPLIT/MERGE 不合并成 Topic 文件，文件仍按 Path Item 身份生成。
- 依 Issue #50 范围，这些 Markdown 是离线 authoring artifacts，不是 runtime Learning Unit、Learning Payload 或 completion facts。
- [Learning Unit v0.1 合同](../../../docs/learning-path/LEARNING_UNIT_V01.md)保持冻结；[#51 Pilot 报告](../../../docs/content/CONTENT_AUTHORING_PILOT_01.md)中的 `CONTENT_MODEL_GAP` 仍未解决。

## 学习单元（按原始 order）

| Order | 来源日期 | Item | 标题 | Mapping | Confidence | Topic IDs | Review marker |
|---:|---|---|---|---|---|---|---|
| 001 | 2026-06-08 | [`checkin-001`](checkin-001.md) | 软件工程：生命周期与基本要素 | MERGE | high | `SOFTWARE.ENGINEERING.PROCESS` | source_gap |
| 002 | 2026-06-09 | [`checkin-002`](checkin-002.md) | 软件开发模型与方法（一） | MERGE | high | `SOFTWARE.ENGINEERING.PROCESS` | unreviewed |
| 003 | 2026-06-10 | [`checkin-003`](checkin-003.md) | RUP：迭代、阶段与工作流 | MERGE | high | `SOFTWARE.ENGINEERING.PROCESS` | unreviewed |
| 004 | 2026-06-11 | [`checkin-004`](checkin-004.md) | 敏捷开发：宣言与常见方法 | MERGE | high | `SOFTWARE.ENGINEERING.PROCESS` | unreviewed |
| 005 | 2026-06-12 | [`checkin-005`](checkin-005.md) | V 模型、W 模型与质量左移 | SPLIT | high | `SOFTWARE.ENGINEERING.PROCESS`, `SOFTWARE.ENGINEERING.TESTING` | unreviewed |
| 006 | 2026-06-13 | [`checkin-006`](checkin-006.md) | 基于构件的软件开发 | EXACT | high | `SOFTWARE.ENGINEERING.COMPONENTS` | unreviewed |
| 007 | 2026-06-14 | [`checkin-007`](checkin-007.md) | 模型驱动开发：模型层次 | EXACT | high | `SOFTWARE.MODELING.FORMAL_MODELING` | source_gap |
| 008 | 2026-06-15 | [`checkin-008`](checkin-008.md) | ABSD：从架构需求到架构演化 | EXACT | high | `ARCH.FOUNDATION.ABSD` | unreviewed |
| 009 | 2026-06-16 | [`checkin-009`](checkin-009.md) | 架构视图与软件复用 | SPLIT | high | `ARCH.FOUNDATION.CONCEPTS`, `ARCH.FOUNDATION.REUSE` | source_gap |
| 010 | 2026-06-17 | [`checkin-010`](checkin-010.md) | DSSA：领域软件架构的形成 | PARTIAL | medium | `ARCH.FOUNDATION.REUSE` | unreviewed |
| 011 | 2026-06-18 | [`checkin-011`](checkin-011.md) | 质量属性、场景与可修改性 | SPLIT | high | `QUALITY.ATTRIBUTES.MODIFIABILITY`, `QUALITY.EVALUATION.SCENARIOS` | source_gap |
| 012 | 2026-06-19 | [`checkin-012`](checkin-012.md) | 数据流风格：批处理与管道过滤器 | PARTIAL | high | `ARCH.FOUNDATION.STYLES` | unreviewed |
| 013 | 2026-06-20 | [`checkin-013`](checkin-013.md) | 调用返回、面向对象与分层风格 | SPLIT | high | `ARCH.FOUNDATION.STYLES`, `ARCH.LAYERED.LAYERS` | unreviewed |
| 014 | 2026-06-21 | [`checkin-014`](checkin-014.md) | 仓库与黑板架构 | PARTIAL | high | `ARCH.FOUNDATION.STYLES` | unreviewed |
| 015 | 2026-06-22 | [`checkin-015`](checkin-015.md) | 解释器与规则系统 | PARTIAL | high | `ARCH.FOUNDATION.STYLES` | source_gap |
| 016 | 2026-06-23 | [`checkin-016`](checkin-016.md) | 进程通信与事件驱动风格 | SPLIT | high | `ARCH.FOUNDATION.STYLES`, `ARCH.CLOUD_NATIVE.EVENT_DRIVEN` | unreviewed |
| 017 | 2026-06-24 | [`checkin-017`](checkin-017.md) | 架构评估：方法与关键概念 | PARTIAL | medium | `QUALITY.EVALUATION.SCENARIOS` | source_gap |
| 018 | 2026-06-25 | [`checkin-018`](checkin-018.md) | SAAM、ATAM 与 CBAM | SPLIT | high | `QUALITY.EVALUATION.ATAM`, `QUALITY.EVALUATION.TRADEOFF` | unreviewed |
| 019 | 2026-06-26 | [`checkin-019`](checkin-019.md) | 性能指标、并发、并行与池化 | PARTIAL | high | `QUALITY.ATTRIBUTES.PERFORMANCE` | source_gap |
| 021 | 2026-06-28 | [`checkin-021`](checkin-021.md) | 性能设计战术：资源、异步与批处理 | MERGE | high | `QUALITY.ATTRIBUTES.PERFORMANCE` | unreviewed |
| 022 | 2026-06-29 | [`checkin-022`](checkin-022.md) | 扩展、动静分离与读写分离 | SPLIT | high | `QUALITY.ATTRIBUTES.PERFORMANCE`, `QUALITY.ATTRIBUTES.SCALABILITY` | source_gap |
| 023 | 2026-06-30 | [`checkin-023`](checkin-023.md) | 反规范化、锁粒度与写热点 | SPLIT | high | `DATA.DATABASE.NORMALIZATION`, `QUALITY.ATTRIBUTES.PERFORMANCE` | unreviewed |
| 024 | 2026-07-01 | [`checkin-024`](checkin-024.md) | 安全属性、加密、摘要与 PKI | SPLIT | high | `QUALITY.ATTRIBUTES.SECURITY`, `SEC.INFORMATION.CRYPTOGRAPHY` | unreviewed |
| 025 | 2026-07-02 | [`checkin-025`](checkin-025.md) | 访问控制模型与实现技术 | SPLIT | high | `SEC.INFORMATION.ACCESS_CONTROL`, `SEC.ARCHITECTURE.MODELS` | source_gap |
| 027 | 2026-07-04 | [`checkin-027`](checkin-027.md) | 身份鉴别、单点登录与 MFA | EXACT | high | `SEC.INFORMATION.ACCESS_CONTROL` | source_gap |
| 028 | 2026-07-05 | [`checkin-028`](checkin-028.md) | OAuth 2.0 与 JWT：授权和令牌 | PARTIAL | medium | `SEC.INFORMATION.ACCESS_CONTROL` | source_gap |
| 029 | 2026-07-06 | [`checkin-029`](checkin-029.md) | 零信任：持续验证与最小权限 | SPLIT | medium | `SEC.INFORMATION.ACCESS_CONTROL`, `SEC.ARCHITECTURE.WPDRRC`, `SEC.ARCHITECTURE.NETWORK_SECURITY` | unreviewed |
| 030 | 2026-07-07 | [`checkin-030`](checkin-030.md) | 容灾设计：RPO、RTO 与恢复路径 | SPLIT | high | `QUALITY.ATTRIBUTES.AVAILABILITY`, `RELIABILITY.SOFTWARE.FAULT_TOLERANCE`, `DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | source_gap |
| 031 | 2026-07-08 | [`checkin-031`](checkin-031.md) | 软件可靠性：指标与容错战术 | SPLIT | high | `RELIABILITY.SOFTWARE.METRICS`, `RELIABILITY.SOFTWARE.FAULT_TOLERANCE`, `QUALITY.ATTRIBUTES.AVAILABILITY` | unreviewed |
| 032 | 2026-07-09 | [`checkin-032`](checkin-032.md) | 可观测性：指标、日志与链路追踪 | UNMAPPED | low | — | source_gap |
| 033 | 2026-07-10 | [`checkin-033`](checkin-033.md) | 人工智能：分类与技术目录 | EXACT | high | `EMERGING.TECHNOLOGY.AI` | source_gap |
| 034 | 2026-07-11 | [`checkin-034`](checkin-034.md) | 机器学习分类与 Transformer 主题索引 | PARTIAL | high | `EMERGING.TECHNOLOGY.AI` | source_gap |
| 035 | 2026-07-12 | [`checkin-035`](checkin-035.md) | 大模型应用开发：概念与选型索引 | PARTIAL | medium | `EMERGING.TECHNOLOGY.AI` | source_gap |
| 036 | 2026-07-13 | [`checkin-036`](checkin-036.md) | 检索增强生成：索引、检索与生成 | PARTIAL | high | `EMERGING.TECHNOLOGY.AI` | unreviewed |
| 037 | 2026-07-14 | [`checkin-037`](checkin-037.md) | 智能体：ReAct 循环与组件边界 | SPLIT | medium | `EMERGING.TECHNOLOGY.AI`, `ARCH.SOA.SERVICE_MODEL`, `ARCH.CLOUD_NATIVE.EVENT_DRIVEN` | source_gap |
| 038 | 2026-07-15 | [`checkin-038`](checkin-038.md) | 知识图谱：构建、查询与存储 | SPLIT | high | `DATA.BIGDATA.KNOWLEDGE_GRAPH`, `EMERGING.TECHNOLOGY.KNOWLEDGE_REPRESENTATION` | source_gap |
| 039 | 2026-07-16 | [`checkin-039`](checkin-039.md) | 推荐系统：算法、流程与多样性 | PARTIAL | medium | `EMERGING.TECHNOLOGY.AI` | unreviewed |
| 040 | 2026-07-17 | [`checkin-040`](checkin-040.md) | 数据挖掘与 OLAP：发现与汇总 | UNMAPPED | low | — | unreviewed |
| 041 | 2026-07-18 | [`checkin-041`](checkin-041.md) | 云计算：部署与服务模式 | EXACT | high | `EMERGING.TECHNOLOGY.CLOUD_COMPUTING` | source_gap |
| 042 | 2026-07-19 | [`checkin-042`](checkin-042.md) | 边缘计算：靠近数据源处理 | EXACT | high | `EMERGING.TECHNOLOGY.EDGE` | unreviewed |
| 043 | 2026-07-20 | [`checkin-043`](checkin-043.md) | 边云协同：资源、数据与服务分工 | SPLIT | medium | `EMERGING.TECHNOLOGY.EDGE`, `EMERGING.TECHNOLOGY.CLOUD_COMPUTING` | unreviewed |
| 044 | 2026-07-21 | [`checkin-044`](checkin-044.md) | 物联网分层与 MQTT 主题索引 | SPLIT | high | `ARCH.LAYERED.IOT`, `ARCH.COMMUNICATION.NETWORK_ARCHITECTURE` | source_gap |
| 045 | 2026-07-22 | [`checkin-045`](checkin-045.md) | 区块链：账本、共识与分层 | UNMAPPED | low | — | source_gap |
| 046 | 2026-07-23 | [`checkin-046`](checkin-046.md) | 锁、死锁与锁优化主题索引 | SPLIT | medium | `SYSTEM.COMPUTER.OPERATING_SYSTEMS`, `DATA.DATABASE.TRANSACTION`, `QUALITY.ATTRIBUTES.PERFORMANCE` | source_gap |
| 047 | 2026-07-24 | [`checkin-047`](checkin-047.md) | 分布式锁：数据库、Redis、ZooKeeper 与 Etcd | EXACT | high | `DATA.DISTRIBUTED.DISTRIBUTED_LOCK` | source_gap |
| 048 | 2026-07-25 | [`checkin-048`](checkin-048.md) | 微服务架构：自治、解耦与演进 | EXACT | high | `ARCH.CLOUD_NATIVE.MICROSERVICES` | source_gap |
| 049 | 2026-07-26 | [`checkin-049`](checkin-049.md) | 服务间通信：同步、异步、REST 与 gRPC | SPLIT | high | `ARCH.SOA.SERVICE_PROTOCOLS`, `ARCH.SOA.SERVICE_BUS` | source_gap |
| 050 | 2026-07-27 | [`checkin-050`](checkin-050.md) | 微服务治理：控制面主题索引 | SPLIT | medium | `ARCH.SOA.SERVICE_MODEL`, `QUALITY.ATTRIBUTES.AVAILABILITY`, `QUALITY.ATTRIBUTES.PERFORMANCE` | source_gap |
| 051 | 2026-07-28 | [`checkin-051`](checkin-051.md) | 负载均衡类型与算法目录 | SPLIT | medium | `ARCH.COMMUNICATION.HIGH_AVAILABILITY`, `QUALITY.ATTRIBUTES.PERFORMANCE` | source_gap |
| 052 | 2026-07-29 | [`checkin-052`](checkin-052.md) | 限流：算法、范围与超限处置 | PARTIAL | high | `QUALITY.ATTRIBUTES.PERFORMANCE` | source_gap |
| 053 | 2026-07-30 | [`checkin-053`](checkin-053.md) | 重试策略：条件、退避与终止 | PARTIAL | high | `RELIABILITY.SOFTWARE.FAULT_TOLERANCE` | unreviewed |
| 054 | 2026-07-31 | [`checkin-054`](checkin-054.md) | 微服务划分：边界与质量需求 | PARTIAL | high | `ARCH.CLOUD_NATIVE.MICROSERVICES` | unreviewed |
| 055 | 2026-08-01 | [`checkin-055`](checkin-055.md) | 领域驱动设计：以业务领域建模 | UNMAPPED | low | — | source_gap |
| 056 | 2026-08-05 | [`checkin-056`](checkin-056.md) | DDD 战略设计：子域与上下文映射 | UNMAPPED | low | — | source_gap |
| 057 | 2026-08-07 | [`checkin-057`](checkin-057.md) | DDD 战术设计：领域模型构件索引 | UNMAPPED | low | — | source_gap |
| 058 | 2026-08-08 | [`checkin-058`](checkin-058.md) | DDD 架构模式：层次、六边形与事件模式 | SPLIT | medium | `ARCH.FOUNDATION.STYLES`, `ARCH.LAYERED.LAYERS`, `ARCH.CLOUD_NATIVE.EVENT_DRIVEN` | source_gap |
| 059 | 2026-08-09 | [`checkin-059`](checkin-059.md) | 云原生架构：特性与原则目录 | UNMAPPED | low | — | source_gap |
| 060 | 2026-08-10 | [`checkin-060`](checkin-060.md) | 容器技术：部署问题与学习范围 | PARTIAL | high | `ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS` | source_gap |
| 061 | 2026-08-11 | [`checkin-061`](checkin-061.md) | 云原生架构模式：服务化到可观测 | SPLIT | medium | `ARCH.SOA.SERVICE_MODEL`, `ARCH.CLOUD_NATIVE.SERVICE_MESH`, `ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS`, `DATA.DISTRIBUTED.CONSISTENCY` | source_gap |
| 062 | 2026-08-12 | [`checkin-062`](checkin-062.md) | Kubernetes 资源类型与探针主题 | PARTIAL | high | `ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS` | source_gap |
| 063 | 2026-08-13 | [`checkin-063`](checkin-063.md) | 消息中间件：通信与消费模式 | PARTIAL | medium | `ARCH.SOA.SERVICE_BUS` | source_gap |
| 064 | 2026-08-14 | [`checkin-064`](checkin-064.md) | Kafka 架构组件索引 | PARTIAL | high | `ARCH.SOA.SERVICE_BUS` | source_gap |
| 065 | 2026-08-15 | [`checkin-065`](checkin-065.md) | 消息系统：丢失、积压、顺序与重复 | SPLIT | medium | `ARCH.SOA.SERVICE_BUS`, `DATA.DISTRIBUTED.CONSISTENCY`, `RELIABILITY.SOFTWARE.FAULT_TOLERANCE` | source_gap |
| 066 | 2026-08-16 | [`checkin-066`](checkin-066.md) | Redis 数据类型主题索引 | UNMAPPED | low | — | source_gap |
| 067 | 2026-08-17 | [`checkin-067`](checkin-067.md) | Redis 持久化：RDB、AOF 与混合模式 | PARTIAL | high | `DATA.CACHE.CACHE_PERSISTENCE` | source_gap |
| 068 | 2026-08-18 | [`checkin-068`](checkin-068.md) | Redis 过期与内存淘汰主题索引 | PARTIAL | medium | `DATA.CACHE.CACHE_FAILURE` | source_gap |
| 069 | 2026-08-19 | [`checkin-069`](checkin-069.md) | Redis 批量操作与事务主题索引 | UNMAPPED | low | — | source_gap |
| 070 | 2026-08-20 | [`checkin-070`](checkin-070.md) | Redis 集群：主从、哨兵与 Cluster | SPLIT | high | `DATA.CACHE.CACHE_PERSISTENCE`, `DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | source_gap |
| 071 | 2026-08-21 | [`checkin-071`](checkin-071.md) | 缓存更新模式：旁路、穿透、写回与 CDC | PARTIAL | high | `DATA.CACHE.CACHE_ASIDE` | source_gap |
| 072 | 2026-08-22 | [`checkin-072`](checkin-072.md) | Redis 缓存故障：击穿、穿透、雪崩与大 Key | MERGE | high | `DATA.CACHE.CACHE_FAILURE` | source_gap |
| 073 | 2026-08-23 | [`checkin-073`](checkin-073.md) | 大数据处理流程与架构类型 | EXACT | high | `DATA.BIGDATA.DATA_PIPELINE` | source_gap |
| 074 | 2026-08-24 | [`checkin-074`](checkin-074.md) | Lambda 与 Kappa 大数据架构 | EXACT | high | `DATA.BIGDATA.LAMBDA_KAPPA` | source_gap |
| 075 | 2026-08-25 | [`checkin-075`](checkin-075.md) | 湖仓一体：存储与计算层主题 | UNMAPPED | low | — | source_gap |
| 076 | 2026-08-26 | [`checkin-076`](checkin-076.md) | 需求工程：开发、基线与管理 | EXACT | high | `SOFTWARE.ENGINEERING.REQUIREMENTS` | source_gap |
| 077 | 2026-08-27 | [`checkin-077`](checkin-077.md) | 分布式协调与 ZooKeeper 主题索引 | SPLIT | medium | `DATA.DISTRIBUTED.DISTRIBUTED_LOCK`, `ARCH.SOA.SERVICE_MODEL` | source_gap |
| 078 | 2026-08-28 | [`checkin-078`](checkin-078.md) | CAP、BASE 与分布式事务方案索引 | SPLIT | high | `DATA.DISTRIBUTED.CONSISTENCY`, `DATA.DATABASE.TRANSACTION`, `ARCH.SOA.SERVICE_BUS` | source_gap |
| 079 | 2026-09-01 | [`checkin-079`](checkin-079.md) | 结构化分析：DFD 模型与平衡规则 | EXACT | high | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | unreviewed |
| 080 | 2026-09-02 | [`checkin-080`](checkin-080.md) | E-R 数据模型与数据字典 | PARTIAL | high | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | unreviewed |
| 081 | 2026-09-03 | [`checkin-081`](checkin-081.md) | 面向对象分析：对象模型与基本概念 | PARTIAL | high | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | unreviewed |
| 082 | 2026-09-04 | [`checkin-082`](checkin-082.md) | 用例模型与分析类关系 | SPLIT | high | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN`, `SOFTWARE.MODELING.UML` | unreviewed |
| 083 | 2026-09-05 | [`checkin-083`](checkin-083.md) | UML 静态图：从结构到部署 | MERGE | high | `SOFTWARE.MODELING.UML` | unreviewed |
| 084 | 2026-09-06 | [`checkin-084`](checkin-084.md) | UML 动态图与 4+1 视图 | SPLIT | high | `SOFTWARE.MODELING.UML`, `ARCH.FOUNDATION.VIEWS` | unreviewed |
| 085 | 2026-09-07 | [`checkin-085`](checkin-085.md) | 需求验证：正确、完整、一致与可行 | PARTIAL | high | `SOFTWARE.ENGINEERING.REQUIREMENTS` | unreviewed |
| 086 | 2026-09-08 | [`checkin-086`](checkin-086.md) | 系统设计、业务流程与工作流管理 | SPLIT | high | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN`, `SOFTWARE.MODELING.BUSINESS_PROCESS` | unreviewed |
| 087 | 2026-09-09 | [`checkin-087`](checkin-087.md) | 结构化设计：耦合与内聚 | PARTIAL | high | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN` | unreviewed |
| 088 | 2026-09-10 | [`checkin-088`](checkin-088.md) | 面向对象设计原则与模式 | SPLIT | high | `SOFTWARE.ENGINEERING.ANALYSIS_DESIGN`, `ARCH.FOUNDATION.DESIGN_PATTERNS` | unreviewed |
| 089 | 2026-09-11 | [`checkin-089`](checkin-089.md) | 软件测试方法、类型与缺陷管理 | MERGE | high | `SOFTWARE.ENGINEERING.TESTING` | source_gap |
| 090 | 2026-09-12 | [`checkin-090`](checkin-090.md) | 黑盒测试：等价类、边界与判定表 | MERGE | high | `SOFTWARE.ENGINEERING.TESTING` | source_gap |
| 091 | 2026-09-13 | [`checkin-091`](checkin-091.md) | 静态测试与质量左移主题索引 | MERGE | high | `SOFTWARE.ENGINEERING.TESTING` | source_gap |
| 092 | 2026-09-14 | [`checkin-092`](checkin-092.md) | 白盒测试：逻辑覆盖主题 | MERGE | high | `SOFTWARE.ENGINEERING.TESTING` | source_gap |
| 093 | 2026-09-15 | [`checkin-093`](checkin-093.md) | 单元测试、覆盖标准与外部依赖 | MERGE | high | `SOFTWARE.ENGINEERING.TESTING` | source_gap |
| 094 | 2026-09-16 | [`checkin-094`](checkin-094.md) | 集成测试：策略与集成方向 | MERGE | high | `SOFTWARE.ENGINEERING.TESTING` | source_gap |
| 095 | 2026-09-17 | [`checkin-095`](checkin-095.md) | 性能测试：负载、稳定、压力与并发 | SPLIT | high | `SOFTWARE.ENGINEERING.TESTING`, `QUALITY.ATTRIBUTES.PERFORMANCE` | source_gap |
| 096 | 2026-09-18 | [`checkin-096`](checkin-096.md) | 安全性测试：从身份到应急响应 | SPLIT | medium | `SOFTWARE.ENGINEERING.TESTING`, `QUALITY.ATTRIBUTES.SECURITY`, `SEC.ARCHITECTURE.VULNERABILITY` | source_gap |
| 097 | 2026-09-19 | [`checkin-097`](checkin-097.md) | 可靠性测试、混沌与故障恢复 | SPLIT | high | `SOFTWARE.ENGINEERING.TESTING`, `RELIABILITY.SOFTWARE.EVALUATION` | source_gap |
| 098 | 2026-09-20 | [`checkin-098`](checkin-098.md) | 自动化测试：触发方式与 UI 测试 | MERGE | high | `SOFTWARE.ENGINEERING.TESTING` | source_gap |
| 099 | 2026-09-21 | [`checkin-099`](checkin-099.md) | 关系运算与关系模式分解 | SPLIT | high | `DATA.DATABASE.RELATIONAL`, `DATA.DATABASE.NORMALIZATION` | source_gap |
| 100 | 2026-09-22 | [`checkin-100`](checkin-100.md) | 数据库规范化与范式目录 | MERGE | high | `DATA.DATABASE.NORMALIZATION` | source_gap |
| 101 | 2026-09-23 | [`checkin-101`](checkin-101.md) | 数据库索引：类型与设计原则 | PARTIAL | high | `DATA.DATABASE.RELATIONAL` | source_gap |
| 102 | 2026-09-24 | [`checkin-102`](checkin-102.md) | 反规范化：冗余与查询性能权衡 | SPLIT | high | `DATA.DATABASE.NORMALIZATION`, `QUALITY.ATTRIBUTES.PERFORMANCE` | source_gap |
| 103 | 2026-09-25 | [`checkin-103`](checkin-103.md) | 数据库视图、触发器、锁与存储过程 | SPLIT | medium | `DATA.DATABASE.RELATIONAL`, `DATA.DATABASE.TRANSACTION` | source_gap |
| 104 | 2026-09-26 | [`checkin-104`](checkin-104.md) | 数据库事务：ACID、并发异常与隔离级别 | MERGE | high | `DATA.DATABASE.TRANSACTION` | source_gap |
| 105 | 2026-09-27 | [`checkin-105`](checkin-105.md) | 数据库三级模式与设计过程 | PARTIAL | high | `DATA.DATABASE.NORMALIZATION` | source_gap |
| 106 | 2026-09-28 | [`checkin-106`](checkin-106.md) | MySQL 主从复制与读写分离 | SPLIT | high | `DATA.DATABASE.RELATIONAL`, `DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | source_gap |
| 107 | 2026-09-30 | [`checkin-107`](checkin-107.md) | NoSQL 数据库：类型与选型目录 | EXACT | high | `DATA.DATABASE.NOSQL` | source_gap |
| 108 | 2026-10-01 | [`checkin-108`](checkin-108.md) | 数据仓库：特征、OLAP 操作与分层 | UNMAPPED | low | — | unreviewed |
| 109 | 2026-10-02 | [`checkin-109`](checkin-109.md) | 数据同步：目标、方式与校验 | SPLIT | medium | `DATA.DISTRIBUTED.REPLICATION_PARTITIONING`, `DATA.BIGDATA.DATA_PIPELINE`, `ARCH.SOA.SERVICE_BUS` | source_gap |
| 110 | 2026-10-03 | [`checkin-110`](checkin-110.md) | 数据分片：方式、算法与实现位置 | EXACT | high | `DATA.DISTRIBUTED.REPLICATION_PARTITIONING` | source_gap |
| 111 | 2026-10-04 | [`checkin-111`](checkin-111.md) | 分布式 ID：要求与生成方式索引 | UNMAPPED | low | — | source_gap |
| 112 | 2026-10-05 | [`checkin-112`](checkin-112.md) | 分片系统常见问题：事务与跨分片查询 | SPLIT | medium | `DATA.DISTRIBUTED.REPLICATION_PARTITIONING`, `DATA.DISTRIBUTED.CONSISTENCY`, `DATA.DATABASE.TRANSACTION` | source_gap |

## 使用边界

- 学习路径日期/order 是来源追踪与排列信息，不是学习完成事实或学习日程。
- `source_gap` 表示来源未支持的知识部分已显式留缺，不表示已完成内容审校。
- `content_version: offline-learning-unit/v0.1` 只标识这些静态 Markdown 文件格式；按 Issue #50，它们不是 runtime Learning Unit、Topic-scoped Learning Payload、Progress/Review evidence 或 completion facts。
- Learning Unit v0.1 语义保持冻结；[#51 Pilot 报告](../../../docs/content/CONTENT_AUTHORING_PILOT_01.md)中的 `CONTENT_MODEL_GAP` 仍未解决。本批仅校准了静态 Markdown 模板，不声称解决 Unit-specific Payload / Topic Experience 选择。
- Golden Set 仅做主题级索引，不推断本学习日细目的考试频率。
- 参见 [`SYSTEM_ARCHITECT_CHECKIN_CONTENT_BUILD_REPORT.md`](../../../docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_CONTENT_BUILD_REPORT.md)、[`SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`](../../../docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md) 与 [`LEARNING_UNIT_V01.md`](../../../docs/learning-path/LEARNING_UNIT_V01.md)。

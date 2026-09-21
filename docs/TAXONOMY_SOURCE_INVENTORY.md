# Taxonomy v0.1 — Source Schema Inventory

> 状态：Phase A inventory，先记录来源自身的分类方式，不把来源改写成统一 taxonomy。
>
> 研究证据只来自本地 Research Evidence Store；正式文件只记录 `source_id`、`source_commit` 和仓库内相对 `source_path`。

## 1. 盘点范围与结论

本轮实际检查了以下 10 个 source，重点覆盖任务要求的六个 source：

- `YoungHong1992/ruankao-senior-architecture-designer`
- `wujiaming88/awesome-ruankao`
- `Zhang-986/ruankao-architect-practice`
- `xiaomabenten/system_architect`
- `Altria1979/System_Architect`
- `Nye-2/archprep`

同时登记并抽查了 `longyi-xw`、`sobermh`、`xxlllq`、`ruankaodaren`，用于识别章节路径、PDF 目录和无授权链接源的边界。

发现的不是一套分类，而是至少 **8 种分类形态**：

1. 官方大纲的知识领域 / 案例专题 / 论文选题范围；
2. 现行教材的 20 章及章节标题；
3. 题库的 `module` + `knowledge` 字段；
4. 按科目 / 年份 / 试卷的文件路径分类；
5. 三色卡、案例模板和论文主题的专题标签；
6. PDF 目录的资料集合 / 年份 / 材料类型；
7. 个人笔记、重点目录和旧版章节分类；
8. 学情 CSV 的模块 `M00–M14` 与课次 `L00–L33`。

最主要的命名冲突是：

- `架构 / 软件架构设计 / 系统架构设计基础知识` 既可能指教材第 7 章，也可能指云原生、SOA、案例专题的总称；
- `安全 / 信息安全 / 安全架构 / 安全性和保密性` 在基础知识、案例安全架构、通信安全和安全关键系统之间发生语义重叠；
- `数据库 / 数据库系统 / 数据与数据架构` 常把关系数据库、NoSQL、缓存、复制和分布式一致性合并；
- `其他 / other / 新技术` 是来源内部的兜底分组，不能直接作为 canonical `OTHER`；
- 旧版章节号（例如 `第9章软件架构设计`）与现行第 2 版 20 章不对应；
- `案例分析解题能力`、`论文写作素材库` 是能力或自产内容入口，不是 Knowledge Topic。

## 2. 官方 / 教材轴

### 2.1 官方大纲

`younghong1992` 的清洗版大纲保留了三科的真实层级：

- 科目一：13 个知识领域；
- 科目二：9 个案例架构实践专题；
- 科目三：5 个论文选题范围。

本轮把 13 个科目一知识领域作为 Canonical Taxonomy 的 13 个 L1 domain 锚点，把案例 9 类作为跨教材章节的 L2/L3 topic 映射；论文 5 类作为 topic 覆盖证据，不把论文写作能力塞入 topic 层。

### 2.2 教材 20 章

现行第 2 版教材目录提供 20 个章节锚点。第 1–11 章主要对应基础知识，第 12–19 章对应架构设计实践，第 20 章是论文写作要点。第 20 章是跨主题表达材料，本轮映射到 `ARCH.FOUNDATION` 的上位 topic，并在 mapping note 中保留这一限制；它不会被当成新的知识域或 Case Capability。

## 3. Source Schema Matrix

| source_id | source_type | classification_field | hierarchy_depth | example_values | coverage | known_quality_issue | recommended_usage |
|---|---|---|---:|---|---|---|---|
| `younghong1992` | 官方大纲 + 教材 + 真题 Markdown / manifest | 大纲章 / 节 / 小节；教材章；`subject`、`source_catalog`、文件路径 | 3（大纲） / 2–3（教材） | `计算机系统基本知识`、`第6章 数据库设计基础知识`、`案例分析` | 现行大纲、20 章教材、36 场试卷 | 非官方题面与答案；清洗版保留来源冲突和低答案可信度 | **Canonical 锚点、题目 source reference、schema 参考**；不复制正文 |
| `wujiaming88` | 真题 Markdown + 案例模板 + 论文方法论 | 文件路径；案例模板专题 / 关键词 / 易错点；三色卡 heading；论文分类 | 3（科目 / 年份 / 试卷）或专题层级 | `缓存`、`架构风格辨析`、`测试、质量与性能` | 系统架构师真题约 2020–2026 上；案例 / 论文模板 | README 与文件数量有不一致；真题版权和 CC-BY-SA 边界不能混同；专题标签跨多个知识域 | **专题与案例能力证据、source mapping 候选**；不把频次当权重 |
| `zhang-986` | 可解析题库 + 进度模型 | `module`、`knowledge`、`sourceType`、`term` | 1–2（module → knowledge） | `architecture`、`database`、`操作系统—进程同步与互斥` | 1822 选择题、78 案例、60 论文的 bank schema | `module` 过粗；`other` 混合；`knowledge` 有空串和 `PDF自动抽取` 占位；上游产物 provenance 未确认 | **题库字段与数据契约参考**；逐题导入时重新标注 |
| `xiaomabenten` | PDF 资料集合 | 目录 / 年份 / 材料类型 / 文件名 | 2–3（集合 → 年份或材料） | `最新教材-新大纲`、`历年真题`、`论文`、`案例分析 新大纲` | 2009–2025 真题 PDF、教材 / 计划 / 论文资料 | 几乎没有机器可读元数据；PDF 版权风险高；文件名有旧版误标 | **索引 / fetch hint / 版权审计证据**；不导入正文 |
| `altria1979` | 个人备考日志、PDF / DOCX 资料档案 | 目录重点标记、旧版章节分类、README 日志标题 | 2–4 | `案例分析 (重点)`、`章节分类真题及解析`、`论文素材` | 2009–2024 多年个人备考资料 | 已归档；旧版教材与机构 / 文库材料混杂；DOCX/PDF 不具稳定 schema | **学习路径和失败模式证据**；旧版分类只作低置信候选 |
| `nye-2` | 学情 CSV、记忆卡片、课次计划 | `模块ID`、`类别`、`课次ID`、学习目标 / 达标标准 | 2（M module → L lesson） | `M03 质量属性与架构评估`、`L10` | M00–M14、L00–L33 | 自定义模块不是官方 taxonomy；无 LICENSE；M11/M12 是能力 / 素材而非 topic | **学习字段和 Topic/Capability 分离的反例证据** |
| `longyi-xw` | 教材笔记 + flashcards | 目录路径的章 / 节；review flashcard 章 | 2–3 | `notes/第二章.../2.2.2...` | 部分教材章节 | 覆盖不完整；无 LICENSE；教材衍生内容不可再分发 | **路径即章节的索引结构参考** |
| `sobermh` | 机构 PDF 学习资料 | 扁平文件名 | 1 | `30天冲刺学习指南`、`学员版` | 2025 上半年资料 | 明确“内部资料，禁止传播”；MIT 声明不能覆盖第三方内容 | **计划结构审计**，不入库、不映射正文 |
| `xxlllq` | 更新日志、图片和外链 | 目录 / 时间线 / 外链 | 1–2 | `UpdateLog`、机考指南 | 时间线至 2026；正文分类弱 | 无 LICENSE；大量外链 / 付费站点，不能当内容源 | **新鲜度与考务时间线** |
| `ruankaodaren` | 官方教材 PDF 汇总 | 科目 / 版本 / PDF 文件名 | 2 | `高级/官方教材/系统架构设计师` | 教材 PDF 线索 | MIT 不能覆盖官方教材 PDF；存在“第4版”旧版误标 | **版本核验与索引线索**，不入库 |

## 4. 设计影响

### 4.1 不直接复制 source taxonomy

Source 的 `module`、目录名和专题标题保留在 `source-mappings.json` 的 `source_value` 中。Canonical Topic 只承担稳定聚合；source 的红黄绿、模块数量和个人重点标记不被转换成伪精确的考试权重。

### 4.2 允许一对多

示例：

- `zhang-986: database` → `DATA.DATABASE`、`DATA.CACHE`、`DATA.DISTRIBUTED`；
- `Nye-2: M07 计算机网络与分布式系统` → 网络、分布式数据、通信架构；
- 教材第 17 章 → 基础网络 + 通信系统架构；
- 案例中的“Redis 锁比较”同时属于数据、分布式和权衡能力。

### 4.3 未决不等于 OTHER

不能从 `other`、`新技术专题` 或旧版目录名推导题目级事实的地方，记录在 `taxonomy/unresolved-mappings.json`，并保留候选 topic、理由和证据。验证样本不使用 canonical `OTHER` 节点。

## 5. Evidence Boundary

本轮只读取 Research Evidence Store 中的第三方仓库快照，没有执行 `pull`、`fetch`、`checkout`、`reset` 或文件修改。正式数据没有写入本地 NAS 绝对路径，也没有复制教材、题库、PDF、OCR 或答案全文。

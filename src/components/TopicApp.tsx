import { useCallback, useEffect, useState } from 'react';
import { CockpitApiError } from '../api/errors';
import { useCockpitApi } from '../api/context';
import type {
  LearningPayload,
  LearningSourceReference,
  TodayResponse,
  TopicResponse,
} from '../api/types';
import { ApiNotice } from './ApiNotice';
import { AppShell } from './AppShell';
import { VerificationForm } from './VerificationForm';

type LoadState =
  | { kind: 'loading' }
  | { kind: 'ready'; topic: TopicResponse }
  | { kind: 'error'; error: unknown };

function errorCode(error: unknown): string {
  return error instanceof CockpitApiError ? error.code : 'api_error';
}

function taskIdFromLocation(): string {
  return typeof window === 'undefined'
    ? ''
    : new URLSearchParams(window.location.search).get('task_id') ?? '';
}

export function TopicApp({ topicId }: { topicId: string }) {
  const api = useCockpitApi();
  const [state, setState] = useState<LoadState>({ kind: 'loading' });
  const [taskId] = useState(taskIdFromLocation);
  const [lastToday, setLastToday] = useState<TodayResponse | null>(null);

  const load = useCallback(async () => {
    setState({ kind: 'loading' });
    try {
      const topic = await api.getTopic(topicId);
      setState({ kind: 'ready', topic });
    } catch (error) {
      setState({ kind: 'error', error });
    }
  }, [api, topicId]);

  useEffect(() => {
    void load();
  }, [load]);

  function refreshed(topic: TopicResponse, today: TodayResponse) {
    setState({ kind: 'ready', topic });
    setLastToday(today);
  }

  return (
    <AppShell activePage="topic">
      {state.kind === 'loading' && (
        <div className="loading-panel" role="status" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          正在读取 Topic API…
        </div>
      )}
      {state.kind === 'error' && (
        <section className="empty-state">
          <a className="back-link" href="/">← 返回 Today</a>
          <h1>{['invalid_source_provenance', 'invalid_learning_payload'].includes(errorCode(state.error)) ? '材料来源校验未通过' : 'Topic 暂时不可用'}</h1>
          <ApiNotice code={errorCode(state.error)} />
          <button className="button button--secondary" type="button" onClick={() => void load()}>重试读取</button>
        </section>
      )}
      {state.kind === 'ready' && (
        <TopicContent topic={state.topic} taskId={taskId} onRefresh={refreshed} />
      )}
      {lastToday && <span className="visually-hidden" aria-live="polite">Today replay 已重新读取：{lastToday.planner.days[0]?.local_date}</span>}
    </AppShell>
  );
}

function TopicContent({
  topic,
  taskId,
  onRefresh,
}: {
  topic: TopicResponse;
  taskId: string;
  onRefresh: (topic: TopicResponse, today: TodayResponse) => void;
}) {
  const payload = topic.learning_payload_status === 'available' ? topic.learning_payload : null;
  return (
    <article className="topic-page">
      <a className="back-link" href="/">← 返回 Today</a>
      <header className="topic-header">
        <nav className="breadcrumbs" aria-label="面包屑">
          <a href="/">Today</a>
          {topic.topic.breadcrumb.map((crumb, index) => (
            <span className="breadcrumb-item" key={crumb.topic_id}>
              <span className="breadcrumb-separator" aria-hidden="true">/</span>
              <span aria-current={index === topic.topic.breadcrumb.length - 1 ? 'page' : undefined}>{crumb.name}</span>
            </span>
          ))}
        </nav>
        <div className="topic-title-row">
          <div>
            <p className="eyebrow">Knowledge Topic</p>
            <h1>{topic.topic.name}</h1>
            <p className="topic-id">{topic.topic.topic_id}</p>
          </div>
          <div className={`payload-badge ${payload ? 'payload-badge--available' : 'payload-badge--unavailable'}`}>
            <span className="payload-badge__dot" aria-hidden="true" />
            {payload ? `Learning Payload · v${topic.learning_payload_version ?? payload.version}` : '材料尚未整理'}
          </div>
        </div>
        <p className="topic-version">Taxonomy v{topic.topic.taxonomy_version}{payload?.taxonomy_version ? ` · Payload schema ${payload.schema_version}` : ''}</p>
      </header>

      <aside className="state-grid" aria-label="Progress 与 Review 状态">
        <div className="state-card">
          <span className="state-label">Progress</span>
          <strong>{topic.progress.attempt_count} 次验证 attempt</strong>
          <span>{topic.progress.accuracy === null ? '准确率：尚无可用数据' : `准确率：${new Intl.NumberFormat('zh-CN', { style: 'percent', maximumFractionDigits: 0 }).format(topic.progress.accuracy)}`}</span>
        </div>
        <div className="state-card">
          <span className="state-label">Review</span>
          <strong>{reviewMasteryLabel(topic.review.mastery_state)}</strong>
          <span>{reviewStatusLabel(topic.review.status)}{topic.review.next_due_local_date ? ` · 下次复习 ${topic.review.next_due_local_date}` : ''}</span>
          {topic.review.policy_version && <small>Policy · {topic.review.policy_version}</small>}
        </div>
      </aside>

      {!payload ? (
        <section className="unavailable-panel" aria-labelledby="payload-unavailable-title">
          <span className="status-mark" aria-hidden="true">i</span>
          <div>
            <h2 id="payload-unavailable-title">材料尚未整理</h2>
            <p>当前没有已校验的 Learning Payload。此页面不会运行时生成或补写学习材料。</p>
          </div>
        </section>
      ) : (
        <LearningSections payload={payload} />
      )}

      <VerificationForm topic={topic} taskId={taskId} onRefresh={onRefresh} />
    </article>
  );
}

function LearningSections({ payload }: { payload: LearningPayload }) {
  const sourceById = new Map(payload.source_references.map((source) => [source.reference_id, source]));
  return (
    <div className="learning-content">
      <section className="content-section" aria-labelledby="objectives-title">
        <p className="eyebrow">学习目标</p>
        <h2 id="objectives-title">学完后，你可以</h2>
        <ul className="objective-list">
          {payload.objectives.map((item, index) => <li key={`${index}-${item.text}`}>{item.text}</li>)}
        </ul>
      </section>

      <section className="content-section" aria-labelledby="core-knowledge-title">
        <p className="eyebrow">Core Knowledge</p>
        <h2 id="core-knowledge-title">核心知识</h2>
        <div className="knowledge-list">
          {payload.core_points.map((point, index) => (
            <article className="knowledge-card" key={`${index}-${point.heading}`}>
              <h3>{point.heading}</h3>
              <p>{point.text}</p>
              <EvidenceReferences ids={point.evidence_refs} sources={sourceById} />
            </article>
          ))}
        </div>
      </section>

      <section className="content-section" aria-labelledby="exam-context-title">
        <p className="eyebrow">Exam Context</p>
        <h2 id="exam-context-title">软考关注点</h2>
        <div className="exam-list">
          {payload.exam_focus.map((item, index) => (
            <article className="exam-item" key={`${index}-${item.text}`}>
              <p>{item.text}</p>
              <EvidenceReferences ids={item.evidence_refs} sources={sourceById} />
            </article>
          ))}
        </div>
      </section>

      <section className="content-section" aria-labelledby="provenance-title">
        <p className="eyebrow">Sources / Provenance</p>
        <h2 id="provenance-title">来源与证据</h2>
        <p className="section-intro">只展示 API 返回的来源引用与版本信息；页面不复制来源正文。</p>
        <div className="source-list">
          {payload.source_references.map((source) => <SourceCard key={source.reference_id} source={source} />)}
        </div>
        <details className="provenance-details">
          <summary>查看技术来源详情</summary>
          <div className="source-list provenance-details__list">
            {payload.source_references.map((source) => <SourceProvenance key={source.reference_id} source={source} />)}
          </div>
        </details>
      </section>
    </div>
  );
}

function EvidenceReferences({
  ids,
  sources,
}: {
  ids: string[];
  sources: Map<string, LearningSourceReference>;
}) {
  if (!ids.length) return null;
  return (
    <p className="evidence-line">
      <span>证据：</span>
      {ids.map((id, index) => <span key={`${id}-${index}`}>{index > 0 ? '；' : ''}{sources.get(id)?.display_title ?? id}</span>)}
    </p>
  );
}

function SourceCard({ source }: { source: LearningSourceReference }) {
  const hasReadableAnchor = source.source_anchor && !source.display_title.includes(source.source_anchor);
  return (
    <article className="source-card">
      <div className="source-card__heading">
        <h3>{source.display_title}</h3>
      </div>
      {hasReadableAnchor && <p className="source-card__anchor">相关章节：{source.source_anchor}</p>}
    </article>
  );
}

function SourceProvenance({ source }: { source: LearningSourceReference }) {
  return (
    <article className="source-card">
      <div className="source-card__heading">
        <h3>{source.display_title}</h3>
      </div>
      <dl className="provenance-list">
        <div><dt>来源类型</dt><dd>{source.kind}</dd></div>
        <div><dt>Source ID</dt><dd>{source.source_id}</dd></div>
        <div><dt>Source commit</dt><dd><code>{source.source_commit}</code></dd></div>
        <div><dt>Source path</dt><dd><code>{source.source_path}</code></dd></div>
        {source.source_value && <div><dt>Source value</dt><dd>{source.source_value}</dd></div>}
        {source.source_anchor && <div><dt>Source anchor</dt><dd>{source.source_anchor}</dd></div>}
        {source.source_question_id && <div><dt>Question ID</dt><dd>{source.source_question_id}</dd></div>}
        {source.golden_set_record_id && <div><dt>Golden Set record</dt><dd>{source.golden_set_record_id}</dd></div>}
        <div><dt>Confidence</dt><dd>{source.confidence}</dd></div>
      </dl>
    </article>
  );
}

function reviewMasteryLabel(value: TopicResponse['review']['mastery_state']): string {
  switch (value) {
    case 'new': return '新建';
    case 'learning': return '学习中';
    case 'mastered': return '达到当前 Review Policy 阈值';
    default: return '尚无 Review 状态';
  }
}

function reviewStatusLabel(value: TopicResponse['review']['status']): string {
  switch (value) {
    case 'not_scheduled': return '尚未排期';
    case 'scheduled': return '已安排';
    case 'due': return '今日到期';
    case 'overdue': return '已逾期';
    default: return 'Review 状态不可用';
  }
}

import { useState, type SubmitEvent } from 'react';
import { CockpitApiError } from '../api/errors';
import { useCockpitApi } from '../api/context';
import type {
  ErrorCause,
  TodayResponse,
  TopicResponse,
  VerificationSource,
} from '../api/types';
import { ApiNotice, messageForApiError } from './ApiNotice';

const ERROR_CAUSES: { value: ErrorCause; label: string }[] = [
  { value: 'knowledge_gap', label: '知识缺口' },
  { value: 'reading_error', label: '阅读错误' },
  { value: 'calculation_error', label: '计算错误' },
  { value: 'scoring_point_expression', label: '得分点表达' },
];
const MANUAL_SOURCE = '__manual_source__';

type SubmitState = 'idle' | 'submitting' | 'success' | 'refresh-error';

function toUtcIso(value: string): string | null {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
}

function errorCode(error: unknown): string {
  return error instanceof CockpitApiError ? error.code : 'api_error';
}

export function VerificationForm({
  topic,
  taskId,
  onRefresh,
}: {
  topic: TopicResponse;
  taskId: string;
  onRefresh: (topic: TopicResponse, today: TodayResponse) => void;
}) {
  const api = useCockpitApi();
  const sources = topic.verification_sources;
  const [sourceChoice, setSourceChoice] = useState(sources.length ? '' : MANUAL_SOURCE);
  const [occurredAt, setOccurredAt] = useState('');
  const [outcome, setOutcome] = useState<'correct' | 'incorrect' | ''>('');
  const [errorCause, setErrorCause] = useState<ErrorCause | ''>('');
  const [manualReference, setManualReference] = useState({
    source_id: '',
    source_commit: '',
    source_path: '',
    source_question_id: '',
  });
  const [submitState, setSubmitState] = useState<SubmitState>('idle');
  const [notice, setNotice] = useState<{ code?: string; message: string } | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  function selectedSource(): VerificationSource | undefined {
    return sources.find((source) => source.record_id === sourceChoice);
  }

  function sourceReference() {
    if (sourceChoice === MANUAL_SOURCE) {
      return {
        source_id: manualReference.source_id.trim(),
        source_commit: manualReference.source_commit.trim(),
        source_path: manualReference.source_path.trim(),
        source_question_id: manualReference.source_question_id.trim(),
      };
    }
    return selectedSource()?.source_reference;
  }

  async function refreshFromServer() {
    try {
      const [latestTopic, latestToday] = await Promise.all([
        api.getTopic(topic.topic.topic_id),
        api.getToday(),
      ]);
      onRefresh(latestTopic, latestToday);
      setSubmitState('success');
      setNotice({
        message: 'API 已接受 attempt；Topic 与 Today 已重新读取。下方 Progress / Review 显示服务端 replay 结果。',
      });
    } catch (error) {
      setSubmitState('refresh-error');
      setNotice({
        code: errorCode(error),
        message: `attempt 已被 API 接受，但刷新 replay 状态失败。${messageForApiError(errorCode(error))} 请先重试刷新，不要重复提交。`,
      });
    }
  }

  async function submit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setNotice(null);
    if (!taskId.trim()) {
      setFormError('缺少 Today task id；请从 Today 任务入口进入后再提交。');
      return;
    }
    if (!outcome) {
      setFormError('请明确选择答对或答错。');
      return;
    }
    const occurredAtIso = toUtcIso(occurredAt);
    if (!occurredAtIso) {
      setFormError('请填写有效的实际作答时间。');
      return;
    }
    const reference = sourceReference();
    if (!reference || Object.values(reference).some((value) => !value.trim())) {
      setFormError('请选择实际使用的已索引来源，或填写完整的来源引用；信息不完整时不会提交。');
      return;
    }

    setSubmitState('submitting');
    try {
      await api.recordAttempt({
        task_id: taskId,
        occurred_at: occurredAtIso,
        question: reference,
        correct: outcome === 'correct',
        ...(outcome === 'incorrect' && errorCause ? { error_cause: errorCause } : {}),
      });
      await refreshFromServer();
    } catch (error) {
      setSubmitState('idle');
      setNotice({ code: errorCode(error), message: messageForApiError(errorCode(error)) });
    }
  }

  const indexedSource = selectedSource();
  const showManual = sourceChoice === MANUAL_SOURCE;
  const submitted = submitState === 'success' || submitState === 'refresh-error';

  return (
    <section className="verification-panel" aria-labelledby="verification-title">
      <div className="section-heading section-heading--compact">
        <div>
          <p className="eyebrow">真实输入 · 可选</p>
          <h2 id="verification-title">Verification</h2>
        </div>
      </div>
      <p className="section-intro">只记录你实际作答的题目、时间和结果。阅读 Topic 本身不会写入 Progress。</p>
      {!taskId ? (
        <ApiNotice variant="info" message="请从 Today 的实际任务进入此 Topic，才能关联服务端 task 并提交验证。" />
      ) : (
        <form className="verification-form" noValidate onSubmit={(event) => void submit(event)}>
          <label className="field">
            <span>验证题来源（只选择实际使用过的题目）</span>
            <select
              value={sourceChoice}
              onChange={(event) => setSourceChoice(event.currentTarget.value)}
              required
              disabled={submitted || submitState === 'submitting'}
            >
              {sources.length > 0 && <option value="">请选择已索引来源</option>}
              {sources.map((source) => <option key={source.record_id} value={source.record_id}>{source.display_title}</option>)}
              <option value={MANUAL_SOURCE}>其他来源（手动填写引用）</option>
            </select>
          </label>

          {indexedSource && (
            <details className="source-details">
              <summary>查看所选题目来源</summary>
              <ProvenanceList values={indexedSource.source_reference} />
            </details>
          )}
          {showManual && (
            <fieldset className="manual-source">
              <legend>备用：填写未索引题目引用</legend>
              <label className="field">
                <span>来源 ID</span>
                <input required value={manualReference.source_id} onChange={(event) => setManualReference({ ...manualReference, source_id: event.currentTarget.value })} />
              </label>
              <label className="field">
                <span>来源不可变版本（commit）</span>
                <input required value={manualReference.source_commit} onChange={(event) => setManualReference({ ...manualReference, source_commit: event.currentTarget.value })} />
              </label>
              <label className="field">
                <span>来源相对路径</span>
                <input required value={manualReference.source_path} onChange={(event) => setManualReference({ ...manualReference, source_path: event.currentTarget.value })} />
              </label>
              <label className="field">
                <span>来源题目 ID</span>
                <input required value={manualReference.source_question_id} onChange={(event) => setManualReference({ ...manualReference, source_question_id: event.currentTarget.value })} />
              </label>
            </fieldset>
          )}

          <label className="field">
            <span>实际作答时间（必填；浏览器本地时间）</span>
            <input type="datetime-local" step="1" required value={occurredAt} onChange={(event) => setOccurredAt(event.currentTarget.value)} disabled={submitted || submitState === 'submitting'} aria-describedby="occurred-at-help" />
          </label>
          <small id="occurred-at-help" className="field-help">请填写真实作答时间；提交时转换为带 UTC 时区的 ISO 8601 时间，不会自动填入当前时间。</small>

          <fieldset className="outcome-fieldset">
            <legend>作答结果（必选）</legend>
            <label className="choice-label"><input type="radio" name="outcome" checked={outcome === 'correct'} onChange={() => setOutcome('correct')} disabled={submitted || submitState === 'submitting'} /> 答对</label>
            <label className="choice-label"><input type="radio" name="outcome" checked={outcome === 'incorrect'} onChange={() => setOutcome('incorrect')} disabled={submitted || submitState === 'submitting'} /> 答错</label>
          </fieldset>

          {outcome === 'incorrect' && (
            <label className="field">
              <span>错误原因（可选）</span>
              <select value={errorCause} onChange={(event) => setErrorCause(event.currentTarget.value as ErrorCause | '')} disabled={submitted || submitState === 'submitting'}>
                <option value="">不填写</option>
                {ERROR_CAUSES.map((cause) => <option key={cause.value} value={cause.value}>{cause.label}</option>)}
              </select>
            </label>
          )}

          <p className="privacy-note">只提交事实和来源引用；请勿粘贴题干、选项、答案或解析。</p>
          {formError && <ApiNotice code="invalid_input" message={formError} />}
          {notice && <ApiNotice code={notice.code} message={notice.message} variant={submitState === 'success' ? 'success' : 'error'} />}
          {submitState === 'refresh-error' && (
            <button className="button button--secondary" type="button" onClick={() => void refreshFromServer()}>
              重试读取 replay 状态
            </button>
          )}
          {!submitted && (
            <button className="button button--primary" type="submit" disabled={submitState === 'submitting'}>
              {submitState === 'submitting' ? '提交并刷新中…' : '提交真实 attempt'}
            </button>
          )}
        </form>
      )}
    </section>
  );
}

function ProvenanceList({ values }: { values: object }) {
  return (
    <dl className="provenance-list">
      {Object.entries(values).map(([key, value]) => (
        <div key={key}><dt>{key}</dt><dd>{String(value)}</dd></div>
      ))}
    </dl>
  );
}

import { useCallback, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { CockpitApiError } from '../api/errors';
import { useCockpitApi } from '../api/context';
import type { LearningUnitResponse } from '../api/types';
import { ApiNotice } from './ApiNotice';
import { AppShell } from './AppShell';

type LoadState =
  | { kind: 'loading' }
  | { kind: 'ready'; unit: LearningUnitResponse }
  | { kind: 'error'; error: unknown };

function errorCode(error: unknown): string {
  return error instanceof CockpitApiError ? error.code : 'api_error';
}

function errorTitle(code: string): string {
  if (code === 'not_a_learning_unit') return '这不是一个学习单元';
  if (code === 'unknown_learning_path' || code === 'unknown_learning_unit') return '学习单元不存在';
  return '学习单元暂不可用';
}

export function LearningUnitApp({ pathId, itemId }: { pathId: string; itemId: string }) {
  const api = useCockpitApi();
  const [state, setState] = useState<LoadState>({ kind: 'loading' });

  const load = useCallback(async () => {
    setState({ kind: 'loading' });
    try {
      const unit = await api.getLearningUnit(pathId, itemId);
      setState({ kind: 'ready', unit });
    } catch (error) {
      setState({ kind: 'error', error });
    }
  }, [api, pathId, itemId]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <AppShell
      activePage="learning-unit"
      footerText="阅读静态 Learning Unit 不会产生 Progress、Review 或 Completion 事实。"
    >
      {state.kind === 'loading' && (
        <div className="loading-panel" role="status" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          正在读取学习单元…
        </div>
      )}
      {state.kind === 'error' && (
        <section className="empty-state">
          <a className="back-link" href="/">← 返回 Cockpit</a>
          <h1>{errorTitle(errorCode(state.error))}</h1>
          <ApiNotice code={errorCode(state.error)} />
          {errorCode(state.error) !== 'not_a_learning_unit'
            && errorCode(state.error) !== 'unknown_learning_path'
            && errorCode(state.error) !== 'unknown_learning_unit' && (
              <button className="button button--secondary" type="button" onClick={() => void load()}>
                重试读取
              </button>
          )}
        </section>
      )}
      {state.kind === 'ready' && <LearningUnitContent unit={state.unit} />}
    </AppShell>
  );
}

function splitMarkdownSources(markdown: string): { content: string; sources: string | null } {
  const heading = /^## 来源与证据\s*$/m;
  const match = heading.exec(markdown);
  if (!match) return { content: markdown, sources: null };
  return {
    content: markdown.slice(0, match.index).trimEnd(),
    sources: markdown.slice(match.index),
  };
}

function MarkdownBody({ markdown, className = 'learning-unit-markdown' }: { markdown: string; className?: string }) {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        components={{
          pre: ({ children, ...props }) => <pre tabIndex={0} {...props}>{children}</pre>,
          table: ({ children, ...props }) => (
            <div className="markdown-table-wrap" role="region" aria-label="可横向滚动的 Markdown 表格" tabIndex={0}>
              <table {...props}>{children}</table>
            </div>
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}

function LearningUnitContent({ unit }: { unit: LearningUnitResponse }) {
  const markdown = splitMarkdownSources(unit.content_markdown);
  return (
    <article className="learning-unit-page">
      <a className="back-link" href="/">← 返回 Cockpit</a>
      <header className="learning-unit-header">
        <p className="eyebrow">{unit.path_title}</p>
        <p className="learning-unit-order">第 {unit.order} 节</p>
        <div className="learning-unit-status" aria-label="内容状态">
          {unit.generation_status === 'draft' && <span className="unit-status-badge">草稿</span>}
          {unit.review_status === 'source_gap' && <span className="unit-status-badge">来源待补充</span>}
          {unit.review_status === 'unreviewed' && <span className="unit-status-badge">内容待复核</span>}
        </div>
      </header>

      <section className="learning-unit-mapping" aria-labelledby="learning-unit-mapping-title">
        <span id="learning-unit-mapping-title" className="eyebrow">关联知识</span>
        {unit.mapping_status === 'unmapped' ? (
          <p className="unmapped-note">尚未映射到现有知识 Topic</p>
        ) : (
          <ul className="topic-label-list">
            {unit.topics.map((topic) => <li key={topic.topic_id}>{topic.name}</li>)}
          </ul>
        )}
      </section>

      <MarkdownBody markdown={markdown.content} />

      <section className="learning-unit-sources" aria-labelledby="learning-unit-sources-title">
        <p className="eyebrow">来源与证据</p>
        <h2 id="learning-unit-sources-title">来源</h2>
        <p>用户提供的系统架构设计师打卡资料 · {unit.source_date}</p>
        <details className="provenance-details">
          <summary>查看来源与技术证据</summary>
          <dl className="provenance-list">
            <div><dt>Learning Path</dt><dd>{unit.path_id} · v{unit.path_version}</dd></div>
            <div><dt>Path status</dt><dd>{unit.path_status}</dd></div>
            <div><dt>Path Item</dt><dd>{unit.item_id} · order {unit.order}</dd></div>
            <div><dt>Mapping</dt><dd>{unit.mapping_status} · {unit.mapping_confidence}</dd></div>
            <div><dt>Topic IDs</dt><dd><code>{unit.topic_ids.length ? unit.topic_ids.join(', ') : '—'}</code></dd></div>
            <div><dt>Generation</dt><dd>{unit.generation_status}</dd></div>
            <div><dt>Review</dt><dd>{unit.review_status}</dd></div>
            <div><dt>Source file</dt><dd><code>{unit.source_file}</code></dd></div>
            <div><dt>Prompt fingerprint</dt><dd><code>{unit.source_prompt_sha256}</code></dd></div>
          </dl>
          {markdown.sources && (
            <MarkdownBody markdown={markdown.sources} className="learning-unit-markdown learning-unit-source-markdown" />
          )}
        </details>
      </section>
    </article>
  );
}

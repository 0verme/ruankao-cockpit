import { useCallback, useEffect, useState } from 'react';
import { CockpitApiError } from '../api/errors';
import { useCockpitApi } from '../api/context';
import type { LearningPathDirectoryResponse } from '../api/types';
import { ApiNotice } from './ApiNotice';
import { AppShell } from './AppShell';

type LoadState =
  | { kind: 'loading' }
  | { kind: 'ready'; directory: LearningPathDirectoryResponse }
  | { kind: 'error'; error: unknown };

function errorCode(error: unknown): string {
  return error instanceof CockpitApiError ? error.code : 'api_error';
}

function errorTitle(code: string): string {
  if (code === 'unknown_learning_path') return '学习目录不存在';
  return '学习目录暂不可用';
}

export function LearningPathDirectoryApp({ pathId }: { pathId: string }) {
  const api = useCockpitApi();
  const [state, setState] = useState<LoadState>({ kind: 'loading' });

  const load = useCallback(async () => {
    setState({ kind: 'loading' });
    try {
      const directory = await api.getLearningPath(pathId);
      setState({ kind: 'ready', directory });
    } catch (error) {
      setState({ kind: 'error', error });
    }
  }, [api, pathId]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <AppShell
      activePage="learn"
      footerText="只读浏览 Learning Path 与 Learning Unit；打开、阅读和导航不会产生 Progress、Review 或 Completion 事实。"
    >
      {state.kind === 'loading' && (
        <div className="loading-panel" role="status" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          正在读取学习目录…
        </div>
      )}
      {state.kind === 'error' && (
        <section className="empty-state">
          <h1>{errorTitle(errorCode(state.error))}</h1>
          <ApiNotice code={errorCode(state.error)} />
          {errorCode(state.error) !== 'unknown_learning_path' && (
            <button className="button button--secondary" type="button" onClick={() => void load()}>
              重试读取
            </button>
          )}
        </section>
      )}
      {state.kind === 'ready' && <DirectoryContent directory={state.directory} />}
    </AppShell>
  );
}

function DirectoryContent({ directory }: { directory: LearningPathDirectoryResponse }) {
  return (
    <section className="learning-path-directory" aria-labelledby="learning-path-title">
      <header className="learning-path-heading">
        <p className="eyebrow">Learn / Learning Path</p>
        <h1 id="learning-path-title">{directory.title}</h1>
        <p className="lede">
          按原始目录顺序自主选择学习单元。休息项保留在原位置；打开、阅读和翻页不会记录完成或进度。
        </p>
        {directory.path_status === 'draft' && (
          <p className="learning-path-draft-note" role="note">
            当前目录顺序仍在复核中；这里仅供自主浏览，不代表 Planner 推荐或排程。
          </p>
        )}
      </header>

      <ol className="learning-path-list" aria-label="Learning Path 目录">
        {directory.items.map((item) => {
          const orderLabel = item.kind === 'learning_unit' ? `第 ${item.order} 节` : `第 ${item.order} 项`;
          const content = (
            <>
              <span className="learning-path-item-order">{orderLabel}</span>
              <span className="learning-path-item-title">{item.title}</span>
              {item.kind === 'non_learning' && (
                <span className="learning-path-item-badge learning-path-item-badge--rest">非学习项</span>
              )}
              {item.kind === 'learning_unit' && item.mapping_status === 'unmapped' && (
                <span className="learning-path-item-badge">尚未映射知识主题</span>
              )}
            </>
          );

          return (
            <li key={item.item_id}>
              {item.kind === 'learning_unit' ? (
                <a
                  className="learning-path-item"
                  href={`/learning-units/${encodeURIComponent(directory.path_id)}/${encodeURIComponent(item.item_id)}`}
                  aria-label={`${orderLabel}：${item.title}${item.mapping_status === 'unmapped' ? '，尚未映射知识主题' : ''}`}
                >
                  {content}
                </a>
              ) : (
                <div className="learning-path-item learning-path-item--disabled" aria-disabled="true">
                  {content}
                </div>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}

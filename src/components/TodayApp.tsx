import { useCallback, useEffect, useState } from 'react';
import { CockpitApiError } from '../api/errors';
import { useCockpitApi } from '../api/context';
import { IMPLEMENTED_TOPIC_ID, type TodayResponse } from '../api/types';
import { ApiNotice, messageForApiError } from './ApiNotice';
import { AppShell } from './AppShell';

type LoadState =
  | { kind: 'loading' }
  | { kind: 'ready'; data: TodayResponse }
  | { kind: 'error'; error: unknown };

function errorCode(error: unknown): string {
  return error instanceof CockpitApiError ? error.code : 'api_error';
}

function topicHref(topicId: string, taskId: string): string {
  const query = new URLSearchParams({ task_id: taskId });
  return `/topics/${encodeURIComponent(topicId)}?${query.toString()}`;
}

export function TodayApp() {
  const api = useCockpitApi();
  const [state, setState] = useState<LoadState>({ kind: 'loading' });
  const [initializing, setInitializing] = useState(false);
  const [initError, setInitError] = useState<unknown>(null);
  const [initializedNotice, setInitializedNotice] = useState(false);

  const load = useCallback(async () => {
    setState({ kind: 'loading' });
    try {
      const data = await api.getToday();
      setState({ kind: 'ready', data });
    } catch (error) {
      setState({ kind: 'error', error });
    }
  }, [api]);

  useEffect(() => {
    void load();
  }, [load]);

  async function initialize() {
    setInitializing(true);
    setInitError(null);
    try {
      await api.initialize();
      setInitializedNotice(true);
      await load();
    } catch (error) {
      setInitError(error);
    } finally {
      setInitializing(false);
    }
  }

  return (
    <AppShell activePage="today">
      <div className="page-heading">
        <div>
          <p className="eyebrow">个人备考工作台</p>
          <h1>Today</h1>
          <p className="lede">从服务端 Today 计划进入当前已整理的 Topic 学习体验。</p>
        </div>
        <button className="button button--secondary" type="button" onClick={() => void load()} disabled={state.kind === 'loading'}>
          刷新
        </button>
      </div>

      {initializedNotice && <ApiNotice variant="success" message="初始化请求已完成；Today 内容已重新读取。" />}
      {state.kind === 'loading' && (
        <div className="loading-panel" role="status" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          正在读取 Today API…
        </div>
      )}
      {state.kind === 'error' && errorCode(state.error) === 'not_initialized' && (
        <section className="empty-state">
          <span className="status-mark" aria-hidden="true">!</span>
          <h2>尚未初始化</h2>
          <p>{messageForApiError('not_initialized')}</p>
          <button className="button button--primary" type="button" onClick={() => void initialize()} disabled={initializing}>
            {initializing ? '正在初始化…' : '初始化 Cockpit'}
          </button>
          {initError !== null && <ApiNotice code={errorCode(initError)} message={messageForApiError(errorCode(initError))} />}
        </section>
      )}
      {state.kind === 'error' && errorCode(state.error) !== 'not_initialized' && (
        <section className="empty-state">
          <h2>Today 暂时不可用</h2>
          <ApiNotice code={errorCode(state.error)} />
          <button className="button button--secondary" type="button" onClick={() => void load()}>重试读取</button>
        </section>
      )}
      {state.kind === 'ready' && (
        <TodayContent data={state.data} />
      )}
    </AppShell>
  );
}

function TodayContent({ data }: { data: TodayResponse }) {
  const planner = data.planner;
  const day = planner.days[0];
  const tasks = day.tasks;
  return (
    <>
      <section className="today-overview" aria-labelledby="today-overview-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">{planner.timezone}</p>
            <h2 id="today-overview-title">今天 · {day.local_date}</h2>
          </div>
          <p className="source-caption">服务端计划 · as_of {planner.as_of}</p>
        </div>
        <div className="metric-grid" aria-label="Today 计划容量">
          <Metric label="今日可用" value={`${day.capacity_minutes} min`} />
          <Metric label="已安排" value={`${day.planned_minutes} min`} />
          <Metric label="剩余容量" value={`${day.remaining_minutes} min`} />
        </div>
      </section>

      <section aria-labelledby="tasks-title" className="task-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">服务端 Planner 输出</p>
            <h2 id="tasks-title">今日任务</h2>
          </div>
        </div>
        {tasks.length === 0 ? (
          <div className="notice notice--info" role="status">Today Planner 当前没有安排任务。</div>
        ) : (
          <div className="task-list">
            {tasks.map((task) => {
              const topic = data.task_topics[task.task_id];
              const supported = topic?.topic_id === IMPLEMENTED_TOPIC_ID;
              const taskLabel = task.task_type === 'review'
                ? 'REVIEW'
                : task.task_type === 'new_learning'
                  ? 'NEW LEARNING'
                  : task.task_type;
              return (
                <article className="task-card" key={task.task_id}>
                  <div className="task-card__topline">
                    <span className="task-kind">{taskLabel}</span>
                    <span className="task-duration">{task.planned_minutes} 分钟</span>
                  </div>
                  <h3>{topic?.topic_name ?? '当前任务没有 Knowledge Topic 映射'}</h3>
                  {supported ? (
                    <a className="button button--primary" href={topicHref(topic.topic_id, task.task_id)}>
                      打开 Topic 学习体验 <span aria-hidden="true">→</span>
                    </a>
                  ) : (
                    <p className="scope-note">此 Slice 仅开放容器与 Serverless Topic 页面。</p>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>
    </>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

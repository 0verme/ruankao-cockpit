import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiProvider } from '../api/context';
import { createFixtureApiClient } from '../api/fixtureClient';
import type { CockpitApiClient } from '../api/contracts';
import { TodayApp } from './TodayApp';
import { TopicApp } from './TopicApp';

const topicId = 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS';

function renderWithApi(element: React.ReactElement, api = createFixtureApiClient()) {
  return render(<ApiProvider client={api}>{element}</ApiProvider>);
}

function enterFromToday() {
  window.history.replaceState({}, '', `/topics/${topicId}?task_id=contract-fixture-task-001`);
}

function chooseIndexedSourceAndCorrectAnswer() {
  fireEvent.change(screen.getByLabelText('验证题来源（只选择实际使用过的题目）'), {
    target: { value: 'gs-comp-2024-h1-q65' },
  });
  fireEvent.change(screen.getByLabelText('实际作答时间（必填；浏览器本地时间）'), {
    target: { value: '2026-09-27T18:00:00' },
  });
  fireEvent.click(screen.getByRole('radio', { name: /答对/ }));
}

afterEach(() => {
  window.history.replaceState({}, '', '/');
});

describe('Today island', () => {
  it('loads the server-provided Today task and marks fixture truth explicitly', async () => {
    renderWithApi(<TodayApp />);
    expect(await screen.findByRole('heading', { name: '容器与 Serverless' })).toBeInTheDocument();
    expect(screen.getByText(/DEV FIXTURE \/ CONTRACT FIXTURE/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /打开 Topic 学习体验/ })).toHaveAttribute(
      'href',
      `/topics/${topicId}?task_id=contract-fixture-task-001`,
    );
  });

  it('shows not-initialized separately and requires an explicit initialization action', async () => {
    const api = createFixtureApiClient('not-initialized');
    renderWithApi(<TodayApp />, api);
    expect(await screen.findByRole('heading', { name: '尚未初始化' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '初始化 Cockpit' }));
    expect(await screen.findByRole('heading', { name: '今日任务' })).toBeInTheDocument();
  });

  it('renders API failure with a specific message and retry action', async () => {
    renderWithApi(<TodayApp />, createFixtureApiClient('api-error'));
    expect(await screen.findByRole('heading', { name: 'Today 暂时不可用' })).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent('Cockpit API 返回错误');
    expect(screen.getByRole('button', { name: '重试读取' })).toBeInTheDocument();
  });
});

describe('Topic island and Verification', () => {
  it('renders unavailable material honestly without generating content', async () => {
    renderWithApi(<TopicApp topicId={topicId} />, createFixtureApiClient('payload-unavailable'));
    expect(await screen.findByRole('heading', { name: '材料尚未整理' })).toBeInTheDocument();
    expect(screen.getByText(/不会运行时生成或补写学习材料/)).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: '核心知识' })).not.toBeInTheDocument();
  });

  it('shows invalid provenance as a separate fail-closed state', async () => {
    renderWithApi(<TopicApp topicId={topicId} />, createFixtureApiClient('invalid-provenance'));
    expect(await screen.findByRole('heading', { name: '材料来源校验未通过' })).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent('材料已隐藏');
  });

  it('keeps readable source titles and sections visible while technical provenance starts collapsed', async () => {
    renderWithApi(<TopicApp topicId={topicId} />);
    expect(await screen.findByRole('heading', { name: '来源与证据' })).toBeVisible();
    const readableSources = document.querySelector<HTMLElement>('.source-list:not(.provenance-details__list)');
    expect(readableSources).toBeInTheDocument();
    expect(within(readableSources!).getByRole('heading', { name: /第 14 章 14\.3\.1 容器技术/ })).toBeVisible();
    expect(within(readableSources!).getByText('相关章节：第 4 类：云原生架构设计理论与实践')).toBeVisible();

    const summary = screen.getByText('查看技术来源详情');
    const disclosure = summary.closest('details');
    expect(disclosure).not.toHaveAttribute('open');
    const hiddenCommit = within(disclosure!).getAllByText('Source commit')[0];
    expect(hiddenCommit).not.toBeVisible();

    fireEvent.click(summary);
    expect(disclosure).toHaveAttribute('open');
    for (const field of ['Source ID', 'Source commit', 'Source path', 'Source value', 'Source anchor', 'Confidence']) {
      expect(within(disclosure!).getAllByText(field)[0]).toBeVisible();
    }
    fireEvent.click(summary);
    expect(disclosure).not.toHaveAttribute('open');
  });

  it('posts only user facts and rereads Topic and Today after API success', async () => {
    enterFromToday();
    const api = createFixtureApiClient();
    const recordAttempt = vi.spyOn(api, 'recordAttempt');
    const getToday = vi.spyOn(api, 'getToday');
    const getTopic = vi.spyOn(api, 'getTopic');
    renderWithApi(<TopicApp topicId={topicId} />, api);

    expect(await screen.findByRole('heading', { name: 'Verification' })).toBeInTheDocument();
    chooseIndexedSourceAndCorrectAnswer();
    fireEvent.click(screen.getByRole('button', { name: '提交真实 attempt' }));

    expect(await screen.findByText(/API 已接受 attempt；Topic 与 Today 已重新读取/)).toBeInTheDocument();
    expect(await screen.findByText('1 次验证 attempt')).toBeInTheDocument();
    expect(recordAttempt).toHaveBeenCalledTimes(1);
    expect(getToday).toHaveBeenCalledTimes(1);
    expect(getTopic).toHaveBeenCalledTimes(2);
    const body = recordAttempt.mock.calls[0][0];
    expect(body).toMatchObject({ task_id: 'contract-fixture-task-001', correct: true });
    for (const forbidden of ['event_id', 'review_context_id', 'mastery', 'review_due', 'progress_percent']) {
      expect(body).not.toHaveProperty(forbidden);
    }
  });

  it('requires the user to enter the actual answer time; it never defaults to now', async () => {
    enterFromToday();
    const api = createFixtureApiClient();
    const recordAttempt = vi.spyOn(api, 'recordAttempt');
    renderWithApi(<TopicApp topicId={topicId} />, api);
    expect(await screen.findByRole('heading', { name: 'Verification' })).toBeInTheDocument();
    expect(screen.getByLabelText('实际作答时间（必填；浏览器本地时间）')).toHaveValue('');
    fireEvent.change(screen.getByLabelText('验证题来源（只选择实际使用过的题目）'), {
      target: { value: 'gs-comp-2024-h1-q65' },
    });
    fireEvent.click(screen.getByRole('radio', { name: /答对/ }));
    fireEvent.click(screen.getByRole('button', { name: '提交真实 attempt' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('请填写有效的实际作答时间');
    expect(recordAttempt).not.toHaveBeenCalled();
  });

  it('shows local invalid source input without making an API write', async () => {
    enterFromToday();
    const api = createFixtureApiClient();
    const recordAttempt = vi.spyOn(api, 'recordAttempt');
    renderWithApi(<TopicApp topicId={topicId} />, api);
    expect(await screen.findByRole('heading', { name: 'Verification' })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('实际作答时间（必填；浏览器本地时间）'), {
      target: { value: '2026-09-27T18:00:00' },
    });
    fireEvent.click(screen.getByRole('radio', { name: /答对/ }));
    fireEvent.click(screen.getByRole('button', { name: '提交真实 attempt' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('请选择实际使用的已索引来源');
    expect(recordAttempt).not.toHaveBeenCalled();
  });

  it('shows API input failure without claiming success or refreshing replay', async () => {
    enterFromToday();
    const api: CockpitApiClient = createFixtureApiClient('attempt-invalid-input');
    const getToday = vi.spyOn(api, 'getToday');
    renderWithApi(<TopicApp topicId={topicId} />, api);
    expect(await screen.findByRole('heading', { name: 'Verification' })).toBeInTheDocument();
    chooseIndexedSourceAndCorrectAnswer();
    fireEvent.click(screen.getByRole('button', { name: '提交真实 attempt' }));
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('提交未通过 API 输入或来源校验'));
    expect(screen.queryByText(/API 已接受 attempt/)).not.toBeInTheDocument();
    expect(getToday).not.toHaveBeenCalled();
  });

  it('requires a Today task context before allowing Verification', async () => {
    renderWithApi(<TopicApp topicId={topicId} />);
    expect(await screen.findByText(/请从 Today 的实际任务进入此 Topic/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '提交真实 attempt' })).not.toBeInTheDocument();
  });
});

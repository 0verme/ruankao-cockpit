import { render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ApiProvider } from '../api/context';
import { createFixtureApiClient } from '../api/fixtureClient';
import { CockpitApiError } from '../api/errors';
import type { CockpitApiClient } from '../api/contracts';
import type { LearningUnitResponse } from '../api/types';
import { LearningUnitApp } from './LearningUnitApp';

const unitFixture: LearningUnitResponse = {
  path_id: 'system-architect-checkin',
  path_version: '1.0.0',
  path_title: '系统架构设计师打卡学习路径',
  path_status: 'draft',
  item_id: 'checkin-005',
  order: 5,
  title: 'V 模型、W 模型与质量左移',
  content_markdown: [
    '# V 模型、W 模型与质量左移',
    '',
    '## 核心知识',
    '',
    '| 开发侧 | 对应测试 |',
    '| --- | --- |',
    '| 需求分析 | 验收测试 |',
    '',
    '```text',
    '问题',
    '├─ 验证',
    '```',
    '',
    '<script>window.compromised = true</script>',
    '',
    '## 来源与证据',
    '',
    '- `data/learning-paths/system-architect-checkin-v1.json`',
  ].join('\n'),
  generation_status: 'draft',
  review_status: 'unreviewed',
  mapping_status: 'split',
  mapping_confidence: 'high',
  topic_ids: ['SOFTWARE.ENGINEERING.PROCESS', 'SOFTWARE.ENGINEERING.TESTING'],
  topics: [
    { topic_id: 'SOFTWARE.ENGINEERING.PROCESS', name: '软件过程与开发方法' },
    { topic_id: 'SOFTWARE.ENGINEERING.TESTING', name: '软件测试' },
  ],
  source_date: '2026-06-12',
  source_file: '2026年06月/2026-06-12.md',
  source_prompt_sha256: 'a'.repeat(64),
};

function renderUnit(
  unit: LearningUnitResponse | null = unitFixture,
  error?: Error,
) {
  const fixtureApi = createFixtureApiClient();
  const getLearningUnit = vi.fn(async () => {
    if (error) throw error;
    return unit!;
  });
  const api: CockpitApiClient = {
    ...fixtureApi,
    getLearningUnit,
  };
  return {
    ...render(
      <ApiProvider client={api}>
        <LearningUnitApp pathId="system-architect-checkin" itemId={unit?.item_id ?? unitFixture.item_id} />
      </ApiProvider>,
    ),
    api,
    getLearningUnit,
  };
}

describe('Learning Unit Experience', () => {
  it('renders one SPLIT unit with both Topic labels and safely formatted Markdown', async () => {
    const { container, getLearningUnit } = renderUnit();

    expect(await screen.findByRole('heading', { level: 1, name: unitFixture.title })).toBeVisible();
    expect(screen.getByText('第 5 节')).toBeVisible();
    expect(screen.getByText('草稿')).toBeVisible();
    expect(screen.getByText('内容待复核')).toBeVisible();
    const mapping = screen.getByRole('region', { name: '关联知识' });
    expect(within(mapping).getByText('软件过程与开发方法')).toBeVisible();
    expect(within(mapping).getByText('软件测试')).toBeVisible();
    expect(screen.getByRole('table')).toBeVisible();
    expect(screen.getByRole('region', { name: '可横向滚动的 Markdown 表格' })).toBeInTheDocument();
    expect(screen.getByText(/问题\s*├─ 验证/)).toBeVisible();
    expect(container.querySelector('.learning-unit-markdown script')).toBeNull();
    expect(screen.getByRole('heading', { name: '来源' })).toBeVisible();
    expect(getLearningUnit).toHaveBeenCalledWith(
      'system-architect-checkin', 'checkin-005',
    );
    expect(screen.queryByRole('button', { name: /完成|已学会|打卡/ })).not.toBeInTheDocument();
  });

  it('keeps technical provenance collapsed by default', async () => {
    renderUnit();
    expect(await screen.findByRole('heading', { level: 1, name: unitFixture.title })).toBeVisible();
    const details = screen.getByText('查看来源与技术证据').closest('details');
    expect(details).not.toHaveAttribute('open');
    expect(within(details!).getByText('Source file')).not.toBeVisible();
    expect(within(details!).getByText('checkin-005 · order 5')).not.toBeVisible();
    expect(within(details!).getByText('data/learning-paths/system-architect-checkin-v1.json')).not.toBeVisible();
  });

  it('shows UNMAPPED units without Topic links or fabricated associations', async () => {
    renderUnit({
      ...unitFixture,
      mapping_status: 'unmapped',
      mapping_confidence: 'low',
      topic_ids: [],
      topics: [],
      review_status: 'source_gap',
      item_id: 'checkin-032',
      title: '可观测性：指标、日志与链路追踪',
      content_markdown: '# 可观测性：指标、日志与链路追踪\n\n## SOURCE_GAP\n\n目前没有 Topic 映射。',
    });
    expect(await screen.findByRole('heading', { level: 1, name: '可观测性：指标、日志与链路追踪' })).toBeVisible();
    expect(screen.getByText('来源待补充')).toBeVisible();
    expect(screen.getByText('尚未映射到现有知识 Topic')).toBeVisible();
    expect(screen.queryByRole('link', { name: /软件测试|软件过程/ })).not.toBeInTheDocument();
    expect(screen.getByText('目前没有 Topic 映射。')).toBeVisible();
  });

  it('explains NON_LEARNING and missing-unit responses without rendering content', async () => {
    renderUnit(null, new CockpitApiError('not_a_learning_unit', 'not a unit', 404));
    expect(await screen.findByRole('heading', { name: '这不是一个学习单元' })).toBeVisible();
    expect(screen.getByRole('alert')).toHaveTextContent('不是学习单元');
    expect(screen.getByRole('link', { name: '← 返回 Cockpit' })).toHaveAttribute('href', '/');
    expect(screen.queryByRole('heading', { name: unitFixture.title })).not.toBeInTheDocument();
  });
});

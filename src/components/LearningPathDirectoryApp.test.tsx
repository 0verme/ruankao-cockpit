import { render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ApiProvider } from '../api/context';
import { createFixtureApiClient } from '../api/fixtureClient';
import { CockpitApiError } from '../api/errors';
import type { CockpitApiClient } from '../api/contracts';
import type { LearningPathDirectoryResponse } from '../api/types';
import { LearningPathDirectoryApp } from './LearningPathDirectoryApp';

const directoryFixture: LearningPathDirectoryResponse = {
  path_id: 'system-architect-checkin',
  version: '1.0.0',
  title: '系统架构设计师打卡学习路径',
  path_status: 'draft',
  items: [
    {
      item_id: 'checkin-001',
      order: 1,
      title: '软件工程：生命周期与基本要素',
      kind: 'learning_unit',
      mapping_status: 'merge',
    },
    {
      item_id: 'checkin-020',
      order: 20,
      title: '休息',
      kind: 'non_learning',
      mapping_status: 'non_learning',
    },
    {
      item_id: 'checkin-032',
      order: 32,
      title: '可观测性：指标、日志与链路追踪',
      kind: 'learning_unit',
      mapping_status: 'unmapped',
    },
  ],
};

function renderDirectory(error?: Error) {
  const getLearningPath = vi.fn(async () => {
    if (error) throw error;
    return directoryFixture;
  });
  const api: CockpitApiClient = {
    ...createFixtureApiClient(),
    getLearningPath,
  };
  return {
    ...render(
      <ApiProvider client={api}>
        <LearningPathDirectoryApp pathId="system-architect-checkin" />
      </ApiProvider>,
    ),
    getLearningPath,
  };
}

describe('Learning Path Directory', () => {
  it('renders manifest order, keeps NON_LEARNING disabled, and links UNMAPPED units', async () => {
    const { getLearningPath } = renderDirectory();

    expect(await screen.findByRole('heading', { name: directoryFixture.title })).toBeVisible();
    expect(screen.getByRole('note')).toHaveTextContent('当前目录顺序仍在复核中');
    const list = screen.getByRole('list', { name: 'Learning Path 目录' });
    const items = within(list).getAllByRole('listitem');
    expect(items).toHaveLength(3);
    expect(items[0]).toHaveTextContent('第 1 节');
    expect(items[0]).toHaveTextContent('软件工程：生命周期与基本要素');
    expect(within(items[0]).getByRole('link')).toHaveAttribute(
      'href', '/learning-units/system-architect-checkin/checkin-001',
    );
    expect(items[1]).toHaveTextContent('第 20 项');
    expect(items[1]).toHaveTextContent('非学习项');
    expect(within(items[1]).queryByRole('link')).not.toBeInTheDocument();
    expect(within(items[2]).getByRole('link', { name: /尚未映射知识主题/ })).toHaveAttribute(
      'href', '/learning-units/system-architect-checkin/checkin-032',
    );
    expect(getLearningPath).toHaveBeenCalledWith('system-architect-checkin');
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /完成|打卡|已学会/ })).not.toBeInTheDocument();
  });

  it('fails visibly for an unknown path without inventing an empty directory', async () => {
    renderDirectory(new CockpitApiError('unknown_learning_path', 'missing', 404));
    expect(await screen.findByRole('heading', { name: '学习目录不存在' })).toBeVisible();
    expect(screen.queryByRole('list', { name: 'Learning Path 目录' })).not.toBeInTheDocument();
  });
});

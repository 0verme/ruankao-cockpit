import { describe, expect, it, vi } from 'vitest';
import { CockpitApiError } from './errors';
import { createFixtureApiClient } from './fixtureClient';
import { createHttpApiClient } from './httpClient';
import type { AttemptRequest, AttemptResponse, TodayResponse, TopicResponse } from './types';

const topicId = 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS';
const replay = {
  planner: { schema_version: 'planner-output/v0.1', as_of: '2026-09-28T01:00:00Z', timezone: 'Asia/Shanghai', days: [] },
  progress: {},
  review: { state: {}, items: [] },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function topicResponse(): TopicResponse {
  return {
    topic: {
      topic_id: topicId,
      name: '容器与 Serverless',
      taxonomy_version: '0.1',
      breadcrumb: [{ topic_id: topicId, name: '容器与 Serverless' }],
    },
    learning_payload_status: 'unavailable',
    learning_payload_version: null,
    learning_payload: null,
    progress: { attempt_count: 0, accuracy: null },
    review: { mastery_state: null, status: null, next_due_local_date: null, policy_version: null },
    verification_sources: [],
  };
}

describe('HTTP API client — merged FastAPI v0.1 contract', () => {
  it('uses the frozen endpoints and sends only attempt facts in the server request shape', async () => {
    const today: TodayResponse = {
      ...replay,
      planner: {
        ...replay.planner,
        days: [{ local_date: '2026-09-28', capacity_minutes: 60, planned_minutes: 25, remaining_minutes: 35, tasks: [] }],
      },
      task_topics: {},
    };
    const topic = topicResponse();
    const recorded: AttemptResponse = {
      recorded: { progress_event_count: 1, review_item_count: 1, review_context_count: 1 },
      today: replay,
    };
    const fetcher = vi.fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse({ state: 'created' }))
      .mockResolvedValueOnce(jsonResponse(today))
      .mockResolvedValueOnce(jsonResponse(topic))
      .mockResolvedValueOnce(jsonResponse(recorded));
    const client = createHttpApiClient('', fetcher);
    const request: AttemptRequest = {
      task_id: 'task-from-today',
      occurred_at: '2026-09-28T01:00:00.000Z',
      question: {
        source_id: 'source',
        source_commit: 'a'.repeat(40),
        source_path: 'questions/q1.md',
        source_question_id: 'q1',
      },
      correct: false,
      error_cause: 'knowledge_gap',
    };

    await expect(client.initialize()).resolves.toEqual({ state: 'created' });
    await expect(client.getToday()).resolves.toEqual(today);
    await expect(client.getTopic(topicId)).resolves.toEqual(topic);
    await expect(client.recordAttempt(request)).resolves.toEqual(recorded);

    expect(fetcher.mock.calls.map(([url, init]) => [url, init?.method ?? 'GET'])).toEqual([
      ['/api/init', 'POST'],
      ['/api/today', 'GET'],
      [`/api/topics/${topicId}`, 'GET'],
      ['/api/attempts', 'POST'],
    ]);
    const body = JSON.parse(String(fetcher.mock.calls[3]?.[1]?.body)) as Record<string, unknown>;
    expect(body).toEqual(request);
    for (const forbidden of ['event_id', 'review_context_id', 'mastery', 'review_due', 'topic_progress', 'as_of']) {
      expect(body).not.toHaveProperty(forbidden);
    }
  });

  it('reads error.category and distinguishes an unreachable API', async () => {
    const client = createHttpApiClient('', vi.fn<typeof fetch>().mockResolvedValueOnce(
      jsonResponse({ error: { category: 'not_initialized', message: 'not initialized' } }, 409),
    ));
    await expect(client.getToday()).rejects.toMatchObject({ code: 'not_initialized', status: 409 });

    const offline = createHttpApiClient('', vi.fn<typeof fetch>().mockRejectedValueOnce(new TypeError('offline')));
    await expect(offline.getToday()).rejects.toMatchObject({ code: 'network_error' });
    expect(() => { throw new CockpitApiError('invalid_input', 'bad input'); }).toThrow('bad input');
  });
});

describe('Learning Unit API client', () => {
  it('uses the deterministic path/item endpoint and recognizes explicit NON_LEARNING errors', async () => {
    const unit = {
      path_id: 'system-architect-checkin',
      path_version: '1.0.0',
      path_title: '系统架构设计师打卡学习路径',
      path_status: 'draft',
      item_id: 'checkin-001',
      order: 1,
      title: '软件工程：生命周期与基本要素',
      content_markdown: '# 软件工程',
      generation_status: 'draft',
      review_status: 'source_gap',
      mapping_status: 'merge',
      mapping_confidence: 'high',
      topic_ids: ['SOFTWARE.ENGINEERING.PROCESS'],
      topics: [{ topic_id: 'SOFTWARE.ENGINEERING.PROCESS', name: '软件过程与开发方法' }],
      source_date: '2026-06-08',
      source_file: '2026年06月/2026-06-08.md',
      source_prompt_sha256: 'a'.repeat(64),
      navigation: { previous_item_id: null, next_item_id: 'checkin-002' },
    };
    const fetcher = vi.fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(unit))
      .mockResolvedValueOnce(jsonResponse({ error: { category: 'not_a_learning_unit', message: '休息日' } }, 404));
    const client = createHttpApiClient('', fetcher);

    await expect(client.getLearningUnit('system-architect-checkin', 'checkin-001')).resolves.toEqual(unit);
    await expect(client.getLearningUnit('system-architect-checkin', 'checkin-020')).rejects.toMatchObject({
      code: 'not_a_learning_unit',
      status: 404,
    });
    expect(fetcher.mock.calls.map(([url]) => url)).toEqual([
      '/api/learning-units/system-architect-checkin/checkin-001',
      '/api/learning-units/system-architect-checkin/checkin-020',
    ]);
  });
});

describe('Learning Path Directory API client', () => {
  it('uses the read-only directory endpoint and handles unknown paths', async () => {
    const directory = {
      path_id: 'system-architect-checkin',
      version: '1.0.0',
      title: '系统架构设计师打卡学习路径',
      path_status: 'draft',
      items: [
        { item_id: 'checkin-001', order: 1, title: '软件工程：生命周期与基本要素', kind: 'learning_unit', mapping_status: 'merge' },
        { item_id: 'checkin-020', order: 20, title: '休息', kind: 'non_learning', mapping_status: 'non_learning' },
      ],
    };
    const fetcher = vi.fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(directory))
      .mockResolvedValueOnce(jsonResponse({ error: { category: 'unknown_learning_path', message: 'missing' } }, 404));
    const client = createHttpApiClient('', fetcher);

    await expect(client.getLearningPath('system-architect-checkin')).resolves.toEqual(directory);
    await expect(client.getLearningPath('unknown-path')).rejects.toMatchObject({
      code: 'unknown_learning_path', status: 404,
    });
    expect(fetcher.mock.calls.map(([url, init]) => [url, init?.method ?? 'GET'])).toEqual([
      ['/api/learning-paths/system-architect-checkin', 'GET'],
      ['/api/learning-paths/unknown-path', 'GET'],
    ]);
  });
});

describe('DEV FIXTURE / CONTRACT FIXTURE adapter', () => {
  it('is explicitly labeled and distinguishes unavailable payload from invalid provenance', async () => {
    const unavailable = createFixtureApiClient('payload-unavailable');
    expect(unavailable.kind).toBe('contract-fixture');
    await expect(unavailable.getTopic(topicId)).resolves.toMatchObject({
      learning_payload_status: 'unavailable',
      learning_payload: null,
    });

    const invalid = createFixtureApiClient('invalid-provenance');
    await expect(invalid.getTopic(topicId)).rejects.toMatchObject({ code: 'invalid_source_provenance' });
  });

  it('models initialization as an explicit POST-like action', async () => {
    const client = createFixtureApiClient('not-initialized');
    await expect(client.getToday()).rejects.toMatchObject({ code: 'not_initialized' });
    await expect(client.initialize()).resolves.toEqual({ state: 'created' });
    await expect(client.getToday()).resolves.toHaveProperty('planner.days.0.tasks.length', 1);
  });
});

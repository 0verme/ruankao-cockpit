import { describe, expect, it, vi } from 'vitest';
import { CockpitApiError } from './errors';
import { createFixtureApiClient } from './fixtureClient';
import { createHttpApiClient } from './httpClient';
import type { AttemptRequest, TodayResponse } from './types';

const topicId = 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('HTTP API client contract assumptions', () => {
  it('uses only the frozen API paths and sends attempt facts, not generated IDs or replay fields', async () => {
    const today: TodayResponse = {
      as_of: '2026-09-28T09:00:00+08:00',
      timezone: 'Asia/Shanghai',
      day: { local_date: '2026-09-28', capacity_minutes: 60, planned_minutes: 25, remaining_minutes: 35, tasks: [] },
    };
    const fetcher = vi.fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse({ initialized: true }))
      .mockResolvedValueOnce(jsonResponse(today))
      .mockResolvedValueOnce(jsonResponse({ topic_id: topicId }))
      .mockResolvedValueOnce(jsonResponse({ accepted: true }));
    const client = createHttpApiClient('', fetcher);
    const request: AttemptRequest = {
      task_id: 'task-from-today',
      occurred_at: '2026-09-28T01:00:00.000Z',
      source_reference: {
        source_id: 'source',
        source_commit: 'a'.repeat(40),
        source_path: 'questions/q1.md',
        source_question_id: 'q1',
      },
      correct: false,
      error_cause: 'knowledge_gap',
    };

    await expect(client.initialize()).resolves.toEqual({ initialized: true });
    await expect(client.getToday()).resolves.toEqual(today);
    await expect(client.getTopic(topicId)).resolves.toEqual({ topic_id: topicId });
    await expect(client.recordAttempt(request)).resolves.toEqual({ accepted: true });

    expect(fetcher.mock.calls.map(([url, init]) => [url, init?.method ?? 'GET'])).toEqual([
      ['/api/init', 'POST'],
      ['/api/today', 'GET'],
      [`/api/topics/${topicId}`, 'GET'],
      ['/api/attempts', 'POST'],
    ]);
    const body = JSON.parse(String(fetcher.mock.calls[3]?.[1]?.body)) as Record<string, unknown>;
    expect(body).toEqual(request);
    for (const forbidden of ['event_id', 'review_context_id', 'mastery', 'review_due', 'progress_percent']) {
      expect(body).not.toHaveProperty(forbidden);
    }
  });

  it('preserves typed API errors and distinguishes an unreachable API', async () => {
    const client = createHttpApiClient('', vi.fn<typeof fetch>().mockResolvedValueOnce(
      jsonResponse({ error: { code: 'not_initialized', message: 'not initialized' } }, 409),
    ));
    await expect(client.getToday()).rejects.toMatchObject({ code: 'not_initialized', status: 409 });

    const offline = createHttpApiClient('', vi.fn<typeof fetch>().mockRejectedValueOnce(new TypeError('offline')));
    await expect(offline.getToday()).rejects.toMatchObject({ code: 'network_error' });
    expect(() => { throw new CockpitApiError('invalid_input', 'bad input'); }).toThrow('bad input');
  });
});

describe('DEV FIXTURE / CONTRACT FIXTURE adapter', () => {
  it('is explicitly labeled and distinguishes unavailable payload from invalid provenance', async () => {
    const unavailable = createFixtureApiClient('payload-unavailable');
    expect(unavailable.kind).toBe('contract-fixture');
    await expect(unavailable.getTopic(topicId)).resolves.toMatchObject({ learning_payload: null });

    const invalid = createFixtureApiClient('invalid-provenance');
    await expect(invalid.getTopic(topicId)).rejects.toMatchObject({ code: 'invalid_payload_provenance' });
  });

  it('models initialization as an explicit POST-like action', async () => {
    const client = createFixtureApiClient('not-initialized');
    await expect(client.getToday()).rejects.toMatchObject({ code: 'not_initialized' });
    await expect(client.initialize()).resolves.toEqual({ initialized: true });
    await expect(client.getToday()).resolves.toHaveProperty('day.tasks.length', 1);
  });
});

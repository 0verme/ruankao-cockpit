import { CockpitApiError } from './errors';
import type { CockpitApiClient } from './contracts';
import type {
  ApiErrorCode,
  ApiErrorEnvelope,
  AttemptRequest,
  AttemptResponse,
  InitializeResponse,
  LearningPathDirectoryResponse,
  LearningUnitResponse,
  TodayResponse,
  TopicResponse,
} from './types';

const knownErrorCodes = new Set<ApiErrorCode>([
  'not_initialized', 'incomplete_local_data', 'unknown_topic', 'unknown_task',
  'non_active_topic', 'invalid_request', 'invalid_timestamp', 'invalid_attempt',
  'invalid_source_reference', 'invalid_source_provenance', 'invalid_learning_payload',
  'forbidden_path', 'future_evidence', 'target_mismatch', 'task_not_scheduled',
  'duplicate_event', 'pending_transaction', 'conflicting_transaction', 'storage_error',
  'invalid_local_data', 'invalid_catalog', 'invalid_learning_catalog', 'invalid_topic_experience',
  'invalid_learning_path', 'invalid_learning_unit', 'unknown_learning_path', 'unknown_learning_unit',
  'not_a_learning_unit', 'invalid_planner_output', 'domain_error', 'api_error',
]);

function responseError(body: unknown, status: number): CockpitApiError {
  const maybeEnvelope = body as Partial<ApiErrorEnvelope> | null;
  const error = maybeEnvelope && typeof maybeEnvelope === 'object' ? maybeEnvelope.error : undefined;
  const rawCategory = error && typeof error.category === 'string' ? error.category : undefined;
  const category = rawCategory && knownErrorCodes.has(rawCategory as ApiErrorCode)
    ? (rawCategory as ApiErrorCode)
    : status === 404
      ? 'unknown_topic'
      : status >= 500
        ? 'api_error'
        : 'invalid_request';
  const message = error && typeof error.message === 'string'
    ? error.message
    : `API request failed with HTTP ${status}`;
  return new CockpitApiError(category, message, status);
}

export function createHttpApiClient(
  baseUrl = '',
  fetcher: typeof fetch = fetch,
): CockpitApiClient {
  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    let response: Response;
    try {
      response = await fetcher(`${baseUrl}${path}`, {
        ...init,
        headers: {
          Accept: 'application/json',
          ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
          ...init?.headers,
        },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'The API could not be reached.';
      throw new CockpitApiError('network_error', message);
    }

    let body: unknown;
    try {
      body = await response.json();
    } catch {
      body = undefined;
    }
    if (!response.ok) throw responseError(body, response.status);
    if (body === undefined) {
      throw new CockpitApiError('api_error', 'The API returned an empty or invalid JSON response.', response.status);
    }
    return body as T;
  }

  return {
    kind: 'http',
    getToday: () => request<TodayResponse>('/api/today'),
    initialize: () => request<InitializeResponse>('/api/init', { method: 'POST' }),
    getTopic: (topicId) => request<TopicResponse>(`/api/topics/${encodeURIComponent(topicId)}`),
    getLearningPath: (pathId) => request<LearningPathDirectoryResponse>(
      `/api/learning-paths/${encodeURIComponent(pathId)}`,
    ),
    getLearningUnit: (pathId, itemId) => request<LearningUnitResponse>(
      `/api/learning-units/${encodeURIComponent(pathId)}/${encodeURIComponent(itemId)}`,
    ),
    recordAttempt: (input: AttemptRequest) => request<AttemptResponse>('/api/attempts', {
      method: 'POST',
      body: JSON.stringify(input),
    }),
  };
}

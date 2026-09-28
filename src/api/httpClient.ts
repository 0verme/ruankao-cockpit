import { CockpitApiError } from './errors';
import type { CockpitApiClient } from './contracts';
import type {
  ApiErrorCode,
  ApiErrorEnvelope,
  AttemptRequest,
  AttemptResponse,
  InitializeResponse,
  TodayResponse,
  TopicExperience,
} from './types';

const knownErrorCodes = new Set<ApiErrorCode>([
  'not_initialized',
  'payload_unavailable',
  'unknown_topic',
  'invalid_payload_provenance',
  'invalid_input',
  'task_not_scheduled',
  'duplicate_attempt',
  'network_error',
  'api_error',
]);

function responseError(body: unknown, status: number): CockpitApiError {
  const maybeEnvelope = body as Partial<ApiErrorEnvelope> | null;
  const error = maybeEnvelope && typeof maybeEnvelope === 'object' ? maybeEnvelope.error : undefined;
  const rawCode = error && typeof error.code === 'string' ? error.code : undefined;
  const code = rawCode && knownErrorCodes.has(rawCode as ApiErrorCode)
    ? (rawCode as ApiErrorCode)
    : status === 404
      ? 'unknown_topic'
      : status >= 500
        ? 'api_error'
        : 'invalid_input';
  const message = error && typeof error.message === 'string'
    ? error.message
    : `API request failed with HTTP ${status}`;
  return new CockpitApiError(code, message, status);
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
    getTopic: (topicId) => request<TopicExperience>(`/api/topics/${encodeURIComponent(topicId)}`),
    recordAttempt: (input: AttemptRequest) => request<AttemptResponse>('/api/attempts', {
      method: 'POST',
      body: JSON.stringify(input),
    }),
  };
}

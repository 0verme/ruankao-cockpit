import type { ApiErrorCode } from './types';

export class CockpitApiError extends Error {
  readonly name = 'CockpitApiError';

  constructor(
    readonly code: ApiErrorCode,
    message: string,
    readonly status?: number,
  ) {
    super(message);
  }
}

export function isCockpitApiError(error: unknown): error is CockpitApiError {
  return error instanceof CockpitApiError;
}

import type {
  ApiAdapterKind,
  AttemptRequest,
  AttemptResponse,
  InitializeResponse,
  TodayResponse,
  TopicResponse,
} from './types';

export interface CockpitApiClient {
  readonly kind: ApiAdapterKind;
  getToday(): Promise<TodayResponse>;
  initialize(): Promise<InitializeResponse>;
  getTopic(topicId: string): Promise<TopicResponse>;
  recordAttempt(input: AttemptRequest): Promise<AttemptResponse>;
}

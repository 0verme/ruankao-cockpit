import type {
  ApiAdapterKind,
  AttemptRequest,
  AttemptResponse,
  InitializeResponse,
  TodayResponse,
  TopicExperience,
} from './types';

export interface CockpitApiClient {
  readonly kind: ApiAdapterKind;
  getToday(): Promise<TodayResponse>;
  initialize(): Promise<InitializeResponse>;
  getTopic(topicId: string): Promise<TopicExperience>;
  recordAttempt(input: AttemptRequest): Promise<AttemptResponse>;
}

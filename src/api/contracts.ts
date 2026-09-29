import type {
  ApiAdapterKind,
  AttemptRequest,
  AttemptResponse,
  InitializeResponse,
  LearningUnitResponse,
  TodayResponse,
  TopicResponse,
} from './types';

export interface CockpitApiClient {
  readonly kind: ApiAdapterKind;
  getToday(): Promise<TodayResponse>;
  initialize(): Promise<InitializeResponse>;
  getTopic(topicId: string): Promise<TopicResponse>;
  getLearningUnit(pathId: string, itemId: string): Promise<LearningUnitResponse>;
  recordAttempt(input: AttemptRequest): Promise<AttemptResponse>;
}

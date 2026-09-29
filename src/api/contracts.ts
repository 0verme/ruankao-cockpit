import type {
  ApiAdapterKind,
  AttemptRequest,
  AttemptResponse,
  InitializeResponse,
  LearningPathDirectoryResponse,
  LearningUnitResponse,
  TodayResponse,
  TopicResponse,
} from './types';

export interface CockpitApiClient {
  readonly kind: ApiAdapterKind;
  getToday(): Promise<TodayResponse>;
  initialize(): Promise<InitializeResponse>;
  getTopic(topicId: string): Promise<TopicResponse>;
  getLearningPath(pathId: string): Promise<LearningPathDirectoryResponse>;
  getLearningUnit(pathId: string, itemId: string): Promise<LearningUnitResponse>;
  recordAttempt(input: AttemptRequest): Promise<AttemptResponse>;
}

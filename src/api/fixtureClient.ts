import payloadDocument from '../../data/learning-payloads/ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS.json';
import { CockpitApiError } from './errors';
import { createHttpApiClient } from './httpClient';
import type { CockpitApiClient } from './contracts';
import type {
  AttemptRequest,
  AttemptResponse,
  LearningPayload,
  PlannerOutput,
  TodayResponse,
  TopicResponse,
} from './types';

/**
 * DEV FIXTURE / CONTRACT FIXTURE ONLY.
 * The response shapes mirror the merged FastAPI v0.1 wire contract. They are
 * not a live API, replay result, or production truth. The checked-in payload
 * is shown under an always-visible fixture banner and is not revalidated here.
 */
export type FixtureScenario =
  | 'ready'
  | 'not-initialized'
  | 'payload-unavailable'
  | 'invalid-provenance'
  | 'api-error'
  | 'network-error'
  | 'attempt-failure'
  | 'attempt-invalid-input';

const payload = payloadDocument as LearningPayload;
const taskId = 'contract-fixture-task-001';

const planner: PlannerOutput = {
  schema_version: 'planner-output/v0.1',
  as_of: '2026-09-28T01:00:00Z',
  timezone: 'Asia/Shanghai',
  days: [{
    local_date: '2026-09-28',
    capacity_minutes: 60,
    planned_minutes: 25,
    remaining_minutes: 35,
    tasks: [{
      task_id: taskId,
      task_type: 'new_learning',
      target_kind: 'topic',
      target_ref: 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS',
      planned_minutes: 25,
      explain_trace_id: 'contract-fixture-trace-001',
    }],
  }],
};

const todayFixture: TodayResponse = {
  planner,
  task_topics: {
    [taskId]: {
      topic_id: 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS',
      topic_name: '容器与 Serverless',
      taxonomy_version: '0.1',
      breadcrumb: [
        { topic_id: 'ARCH', name: '系统架构设计基础知识' },
        { topic_id: 'ARCH.CLOUD_NATIVE', name: '云原生架构设计' },
        { topic_id: 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS', name: '容器与 Serverless' },
      ],
      learning_payload_status: 'available',
      learning_payload_version: '1.0.0',
    },
  },
  progress: {},
  review: { state: {}, items: [] },
};

const topicFixture: TopicResponse = {
  topic: {
    topic_id: 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS',
    name: '容器与 Serverless',
    taxonomy_version: '0.1',
    breadcrumb: [
      { topic_id: 'ARCH', name: '系统架构设计基础知识' },
      { topic_id: 'ARCH.CLOUD_NATIVE', name: '云原生架构设计' },
      { topic_id: 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS', name: '容器与 Serverless' },
    ],
  },
  learning_payload_status: 'available',
  learning_payload_version: '1.0.0',
  learning_payload: payload,
  progress: { attempt_count: 0, accuracy: null },
  review: {
    mastery_state: null,
    status: null,
    next_due_local_date: null,
    policy_version: null,
  },
  verification_sources: [{
    record_id: 'gs-comp-2024-h1-q65',
    display_title: '2024年上半年综合知识 · 第 65 题：云计算虚拟化技术识别',
    source_reference: {
      source_id: 'younghong1992',
      source_commit: 'c467a7cbc16970c52cf6d723badbb22938963ae6',
      source_path: '02.历年真题-清洗版/2024年上半年-系统架构设计师-综合知识.md',
      source_question_id: '2024-h1-comprehensive-q65',
      golden_set_record_id: 'gs-comp-2024-h1-q65',
    },
  }],
};

// Pre-recorded API response fixture, not a client-side replay calculation.
const topicAfterAttemptFixture: TopicResponse = {
  ...topicFixture,
  progress: { attempt_count: 1, accuracy: 1 },
  review: {
    mastery_state: 'learning',
    status: 'scheduled',
    next_due_local_date: '2026-09-29',
    policy_version: 'review-policy/simple-ladder/v0.1',
  },
};

const replayFixture: AttemptResponse['today'] = {
  planner,
  progress: {},
  review: { state: {}, items: [] },
};

export function createFixtureApiClient(scenario: FixtureScenario = 'ready'): CockpitApiClient {
  let initialized = scenario !== 'not-initialized';
  // Learning Units are static repository content, not part of the Today fixture.
  const learningUnitApi = createHttpApiClient(import.meta.env.PUBLIC_API_BASE_URL ?? '');
  let hasRecordedAttempt = false;

  return {
    kind: 'contract-fixture',
    async getToday() {
      if (!initialized) {
        throw new CockpitApiError('not_initialized', 'Cockpit 尚未初始化。');
      }
      if (scenario === 'api-error') {
        throw new CockpitApiError('api_error', 'DEV FIXTURE：Today API 返回 HTTP 503。', 503);
      }
      if (scenario === 'network-error') {
        throw new CockpitApiError('network_error', 'DEV FIXTURE：无法连接到 API。');
      }
      return structuredClone(todayFixture);
    },
    async initialize() {
      initialized = true;
      return { state: 'created' };
    },
    getLearningUnit: (pathId, itemId) => learningUnitApi.getLearningUnit(pathId, itemId),
    async getTopic(topicId) {
      if (scenario === 'invalid-provenance') {
        throw new CockpitApiError(
          'invalid_source_provenance',
          'DEV FIXTURE：Learning Payload provenance validation failed.',
          422,
        );
      }
      if (topicId !== topicFixture.topic.topic_id) {
        throw new CockpitApiError('unknown_topic', '此 Topic 不在当前 Slice 的实现范围内。', 404);
      }
      if (scenario === 'payload-unavailable') {
        return {
          ...structuredClone(topicFixture),
          learning_payload_status: 'unavailable',
          learning_payload_version: null,
          learning_payload: null,
        };
      }
      return structuredClone(hasRecordedAttempt ? topicAfterAttemptFixture : topicFixture);
    },
    async recordAttempt(_input: AttemptRequest): Promise<AttemptResponse> {
      if (scenario === 'attempt-failure') {
        throw new CockpitApiError('task_not_scheduled', 'DEV FIXTURE：任务已不在当前 Today 计划中。', 409);
      }
      if (scenario === 'attempt-invalid-input') {
        throw new CockpitApiError('invalid_source_reference', 'DEV FIXTURE：来源引用未通过 API 校验。', 422);
      }
      hasRecordedAttempt = true;
      return {
        recorded: {
          progress_event_count: 1,
          review_item_count: 1,
          review_context_count: 1,
        },
        today: structuredClone(replayFixture),
      };
    },
  };
}

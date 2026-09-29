export const IMPLEMENTED_TOPIC_ID = 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS';

export type TodayTaskType = 'new_learning' | 'review' | string;
export type ErrorCause =
  | 'knowledge_gap'
  | 'reading_error'
  | 'calculation_error'
  | 'scoring_point_expression';

export interface TodayTask {
  task_id: string;
  task_type: TodayTaskType;
  target_kind: string;
  target_ref: string;
  planned_minutes: number;
  explain_trace_id: string;
}

export interface PlannerDay {
  local_date: string;
  capacity_minutes: number;
  planned_minutes: number;
  remaining_minutes: number;
  tasks: TodayTask[];
}

export interface PlannerOutput {
  schema_version: string;
  as_of: string;
  timezone: string;
  days: PlannerDay[];
  explain_traces?: unknown[];
}

export interface TodayTopicMetadata {
  topic_id: string;
  topic_name: string;
  taxonomy_version: string;
  breadcrumb: TopicBreadcrumb[];
  learning_payload_status: 'available' | 'unavailable';
  learning_payload_version: string | null;
}

export interface ReplayReadModel {
  planner: PlannerOutput;
  progress: Record<string, unknown>;
  review: {
    state: Record<string, unknown>;
    items: unknown[];
  };
}

/** Exact wire response from GET /api/today. */
export interface TodayResponse extends ReplayReadModel {
  task_topics: Record<string, TodayTopicMetadata>;
}

export interface LearningEvidenceItem {
  text: string;
  evidence_refs: string[];
}

export interface LearningCorePoint extends LearningEvidenceItem {
  heading: string;
}

export type LearningSourceKind =
  | 'textbook_section'
  | 'exam_outline'
  | 'golden_set_question';

export interface LearningSourceReference {
  reference_id: string;
  kind: LearningSourceKind;
  display_title: string;
  source_id: string;
  source_commit: string;
  source_path: string;
  confidence: 'high' | 'medium' | 'low';
  source_value?: string;
  source_anchor?: string;
  source_question_id?: string;
  golden_set_record_id?: string;
}

export interface LearningPayload {
  schema_version: string;
  version: string;
  topic_id: string;
  taxonomy_version?: string;
  objectives: LearningEvidenceItem[];
  core_points: LearningCorePoint[];
  exam_focus: LearningEvidenceItem[];
  source_references: LearningSourceReference[];
}

export interface TopicBreadcrumb {
  topic_id: string;
  name: string;
}

export interface TopicWireMetadata {
  topic_id: string;
  name: string;
  taxonomy_version: string;
  breadcrumb: TopicBreadcrumb[];
}

export interface AttemptSourceReference {
  source_id: string;
  source_commit: string;
  source_path: string;
  source_question_id: string;
  golden_set_record_id?: string;
}

export interface VerificationSource {
  record_id: string;
  display_title: string;
  source_reference: AttemptSourceReference;
}

/** Exact wire response from GET /api/topics/{topic_id}. */
export interface TopicResponse {
  topic: TopicWireMetadata;
  learning_payload_status: 'available' | 'unavailable';
  learning_payload_version: string | null;
  learning_payload: LearningPayload | null;
  progress: {
    attempt_count: number;
    accuracy: number | null;
  };
  review: {
    mastery_state: 'new' | 'learning' | 'mastered' | null;
    status: 'not_scheduled' | 'scheduled' | 'due' | 'overdue' | null;
    next_due_local_date: string | null;
    policy_version: string | null;
  };
  verification_sources: VerificationSource[];
}

export interface LearningUnitTopic {
  topic_id: string;
  name: string;
}

export type LearningUnitMappingStatus = 'exact' | 'partial' | 'split' | 'merge' | 'unmapped';

/** Exact wire response from GET /api/learning-units/{path_id}/{item_id}. */
export interface LearningUnitResponse {
  path_id: string;
  path_version: string;
  path_title: string;
  path_status: string;
  item_id: string;
  order: number;
  title: string;
  content_markdown: string;
  generation_status: string;
  review_status: 'source_gap' | 'unreviewed';
  mapping_status: LearningUnitMappingStatus;
  mapping_confidence: 'high' | 'medium' | 'low';
  topic_ids: string[];
  topics: LearningUnitTopic[];
  source_date: string;
  source_file: string;
  source_prompt_sha256: string;
}

export interface InitializeResponse {
  state: 'created' | 'already_exists';
}

export interface AttemptRequest {
  task_id: string;
  occurred_at: string;
  question: AttemptSourceReference;
  correct: boolean;
  error_cause?: ErrorCause;
}

/** Exact service-derived response from POST /api/attempts. */
export interface AttemptResponse {
  recorded: {
    progress_event_count: number;
    review_item_count: number;
    review_context_count: number;
  };
  today: ReplayReadModel;
}

export type ApiErrorCode =
  | 'not_initialized'
  | 'incomplete_local_data'
  | 'unknown_topic'
  | 'unknown_task'
  | 'non_active_topic'
  | 'invalid_request'
  | 'invalid_timestamp'
  | 'invalid_attempt'
  | 'invalid_source_reference'
  | 'invalid_source_provenance'
  | 'invalid_learning_payload'
  | 'forbidden_path'
  | 'future_evidence'
  | 'target_mismatch'
  | 'task_not_scheduled'
  | 'duplicate_event'
  | 'pending_transaction'
  | 'conflicting_transaction'
  | 'storage_error'
  | 'invalid_local_data'
  | 'invalid_catalog'
  | 'invalid_learning_catalog'
  | 'invalid_topic_experience'
  | 'invalid_learning_path'
  | 'invalid_learning_unit'
  | 'unknown_learning_path'
  | 'unknown_learning_unit'
  | 'not_a_learning_unit'
  | 'invalid_planner_output'
  | 'domain_error'
  | 'network_error'
  | 'api_error'
  /** UI-only validation state; not a FastAPI error category. */
  | 'invalid_input';

export interface ApiErrorEnvelope {
  error: {
    category: ApiErrorCode | string;
    message: string;
  };
}

export type ApiAdapterKind = 'http' | 'contract-fixture';

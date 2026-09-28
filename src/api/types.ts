export const IMPLEMENTED_TOPIC_ID = 'ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS';

export type TodayTaskType = 'new_learning' | 'review';
export type ErrorCause =
  | 'knowledge_gap'
  | 'reading_error'
  | 'calculation_error'
  | 'scoring_point_expression';

export interface TodayTask {
  task_id: string;
  task_type: TodayTaskType;
  /** Resolved by the API adapter, including for review tasks. */
  topic_id: string;
  topic_name: string;
  planned_minutes: number;
  display_reason: string;
}

export interface TodayResponse {
  as_of: string;
  timezone: string;
  day: {
    local_date: string;
    capacity_minutes: number;
    planned_minutes: number;
    remaining_minutes: number;
    tasks: TodayTask[];
  };
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
  /** Optional link built by the server from its validated source catalog. */
  source_url?: string;
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
  source_reference: AttemptSourceReference & { golden_set_record_id: string };
}

/** Read-only projection from cockpit_service.TopicExperience. */
export interface TopicExperience {
  topic_id: string;
  topic_name: string;
  taxonomy_version: string;
  breadcrumb: TopicBreadcrumb[];
  learning_payload: LearningPayload | null;
  progress_attempt_count: number;
  progress_accuracy: number | null;
  review_mastery_state: 'new' | 'learning' | 'mastered' | null;
  review_status: 'not_scheduled' | 'scheduled' | 'due' | 'overdue' | null;
  review_next_due_local_date: string | null;
  review_policy_version: string | null;
  verification_sources: VerificationSource[];
}

export interface InitializeResponse {
  initialized: boolean;
}

export interface AttemptRequest {
  task_id: string;
  occurred_at: string;
  source_reference: AttemptSourceReference;
  correct: boolean;
  error_cause?: ErrorCause;
}

/** IDs and replay-derived metrics are intentionally server-owned. */
export interface AttemptResponse {
  accepted: true;
}

export type ApiErrorCode =
  | 'not_initialized'
  | 'payload_unavailable'
  | 'unknown_topic'
  | 'invalid_payload_provenance'
  | 'invalid_input'
  | 'task_not_scheduled'
  | 'duplicate_attempt'
  | 'network_error'
  | 'api_error';

export interface ApiErrorEnvelope {
  error: {
    code: ApiErrorCode | string;
    message: string;
  };
}

export type ApiAdapterKind = 'http' | 'contract-fixture';

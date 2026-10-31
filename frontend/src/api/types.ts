export interface HealthResponse {
  status: string;
  version: string;
  app_name: string;
  project: string;
}

export interface DashboardSummary {
  total_repairs: number;
  verified_repairs: number;
  reproduced_count: number;
  tests_passed: number;
  active_repairs: number;
  failed_validations: number;
  configured_provider: string;
  execution_mode: string;
  recent_repairs: RepairTask[];
  recent_reports: Array<{
    filename: string;
    task_id: string;
    size_bytes: number;
    modified: number;
  }>;
}

export interface BugReport {
  title: string;
  description: string;
  expected_behavior: string;
  actual_behavior: string;
  error_message?: string | null;
  stack_trace?: string | null;
  reproduction_command?: string | null;
}

export interface RepoSummary {
  root_path: string;
  total_files: number;
  languages: string[];
  has_git: boolean;
  has_tests: boolean;
  test_framework?: string | null;
  dependency_files: string[];
  source_files?: string[];
}

export interface ReproductionResult {
  status: 'REPRODUCED' | 'NOT_REPRODUCED' | 'BLOCKED';
  command: string;
  exit_code: number;
  stdout: string;
  stderr: string;
  duration_seconds: number;
  evidence_notes: string;
}

export interface RootCauseRecord {
  file_path: string;
  function_name?: string | null;
  line_number?: number | null;
  explanation: string;
  uncertainty_level: 'LOW' | 'MEDIUM' | 'HIGH';
  evidence: string;
}

export interface PatchRecord {
  file_path: string;
  diff: string;
  summary: string;
  is_mock: boolean;
  generation_timestamp?: number;
}

export interface VerificationResult {
  verified: boolean;
  syntax_valid: boolean;
  tests_passed: string[];
  tests_failed: string[];
  command: string;
  exit_code: number;
  stdout: string;
  stderr: string;
  duration_seconds: number;
  status_label: string;
}

export interface StateTransitionRecord {
  from_state: string;
  to_state: string;
  timestamp: number;
  reason?: string | null;
}

export interface RepairTask {
  task_id: string;
  repo_path: string;
  model_name: string;
  is_mock: boolean;
  current_state: string;
  status: 'VERIFIED' | 'RUNNING' | 'VALIDATION_FAILED' | 'NOT_REPRODUCED' | 'EXECUTION_BLOCKED' | 'PATCH_GENERATED_UNVERIFIED';
  start_time: number;
  end_time?: number | null;
  duration_seconds?: number | null;
  bug_report?: BugReport | null;
  repo_summary?: RepoSummary | null;
  reproduction_result?: ReproductionResult | null;
  root_cause_analysis?: RootCauseRecord | null;
  patch?: PatchRecord | null;
  verification_result?: VerificationResult | null;
  state_history: StateTransitionRecord[];
  failure_reason?: string | null;
  human_approved?: boolean | null;
}

export interface RepairCreateRequest {
  repo_path: string;
  title: string;
  description: string;
  expected_behavior: string;
  actual_behavior: string;
  error_message?: string;
  stack_trace?: string;
  test_command?: string;
  provider_type: string;
  isolate_workspace: boolean;
  auto_approve: boolean;
}

export interface LogEntry {
  timestamp: number;
  level: string;
  stage: string;
  message: string;
}

export interface RepairLogsResponse {
  task_id: string;
  logs: LogEntry[];
}

export interface TestResultItem {
  test: string;
  passed: boolean;
  observed: string;
}

export interface EvaluationItem {
  id: string;
  source_type: 'Kaggle Experiment' | 'Local Repair Run';
  project: string;
  experiment: string;
  model: string;
  inference_time_seconds?: number | null;
  bugs_attempted: number;
  bugs_reproduced: number;
  patches_generated: number;
  patches_verified: number;
  baseline_tests_passed: number;
  patched_tests_passed: number;
  total_tests: number;
  repair_status: string;
  baseline_results: TestResultItem[];
  patched_results: TestResultItem[];
  patch?: string | null;
  timestamp?: number | null;
}

export interface RepositoryInspectResponse {
  root_path: string;
  total_files: number;
  languages: string[];
  has_git: boolean;
  has_tests: boolean;
  test_framework?: string | null;
  dependency_files: string[];
  source_files: string[];
}

export interface ModelProviderInfo {
  id: string;
  name: string;
  provider_type: string;
  is_active: boolean;
  is_deterministic: boolean;
  description: string;
  base_url?: string | null;
  model_name: string;
  status: string;
}

export interface SkillInfo {
  name: string;
  description: string;
  valid: boolean;
  skill_file_path: string;
  phases: string[];
  security_rules: string[];
  supporting_resources: string[];
}


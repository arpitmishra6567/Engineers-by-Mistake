import {
  DashboardSummary,
  EvaluationItem,
  HealthResponse,
  ModelProviderInfo,
  RepairCreateRequest,
  RepairLogsResponse,
  RepairTask,
  RepositoryInspectResponse,
  SkillInfo,
} from './types';

// Base URL for API requests. In production (Vercel), VITE_API_URL points to the deployed Railway backend.
// In local development, leaving it empty uses the Vite dev server proxy to localhost:8000.
const rawApiUrl = (import.meta.env.VITE_API_URL || '').trim();
const BASE_URL = rawApiUrl.replace(/\/+$/, '');

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  getHealth: () => fetchJson<HealthResponse>('/api/health'),
  getDashboardSummary: () => fetchJson<DashboardSummary>('/api/dashboard/summary'),
  listRepairs: () => fetchJson<RepairTask[]>('/api/repairs'),
  getRepair: (taskId: string) => fetchJson<RepairTask>(`/api/repairs/${taskId}`),
  getRepairLogs: (taskId: string) => fetchJson<RepairLogsResponse>(`/api/repairs/${taskId}/logs`),
  getRepairReportMarkdown: (taskId: string) => fetchJson<{ task_id: string; content: string }>(`/api/repairs/${taskId}/report`),
  createRepair: (data: RepairCreateRequest) =>
    fetchJson<RepairTask>('/api/repairs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  listEvaluations: () => fetchJson<EvaluationItem[]>('/api/evaluations'),
  getEvaluation: (id: string) => fetchJson<EvaluationItem>(`/api/evaluations/${id}`),
  listKnownRepositories: () => fetchJson<Array<{ name: string; path: string; type: string }>>('/api/repositories/known'),
  inspectRepository: (path: string = '.') =>
    fetchJson<RepositoryInspectResponse>(`/api/repositories/inspect?path=${encodeURIComponent(path)}`),
  listModels: () => fetchJson<ModelProviderInfo[]>('/api/models'),
  getSkillInfo: () => fetchJson<SkillInfo>('/api/skills'),
  validateSkill: () =>
    fetchJson<{ valid: boolean; name?: string; message: string }>('/api/skills/validate', {
      method: 'POST',
    }),
};


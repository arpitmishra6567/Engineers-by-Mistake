import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  PlayCircle,
  GitPullRequest,
  CheckCircle,
  RefreshCw,
} from 'lucide-react';
import { api } from '../api/client';
import { StatusBadge } from '../components/ui/StatusBadge';
import { RepairTimeline } from '../components/ui/RepairTimeline';
import { ExecutionLog } from '../components/ui/ExecutionLog';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const LiveExecutionPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const queryTaskId = searchParams.get('task');

  // Fetch all tasks
  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['repairs-list'],
    queryFn: api.listRepairs,
    refetchInterval: (query) => {
      const activeTask = query.state.data?.find((t) => t.status === 'RUNNING');
      return activeTask ? 1500 : 8000;
    },
  });

  const selectedTaskId = queryTaskId || tasks?.[0]?.task_id;

  // Set default query param if not set
  useEffect(() => {
    if (!queryTaskId && tasks && tasks.length > 0) {
      setSearchParams({ task: tasks[0].task_id }, { replace: true });
    }
  }, [queryTaskId, tasks, setSearchParams]);

  // Fetch specific task details
  const { data: currentTask, refetch: refetchTask } = useQuery({
    queryKey: ['repair-task', selectedTaskId],
    queryFn: () => (selectedTaskId ? api.getRepair(selectedTaskId) : null),
    enabled: !!selectedTaskId,
    refetchInterval: (query) => (query.state.data?.status === 'RUNNING' ? 1500 : false),
  });

  // Fetch task logs
  const { data: logsData } = useQuery({
    queryKey: ['repair-logs', selectedTaskId],
    queryFn: () => (selectedTaskId ? api.getRepairLogs(selectedTaskId) : null),
    enabled: !!selectedTaskId,
    refetchInterval: () => (currentTask?.status === 'RUNNING' ? 1500 : false),
  });

  if (tasksLoading) {
    return <LoadingSkeleton rows={8} />;
  }

  if (!tasks || tasks.length === 0) {
    return (
      <EmptyState
        title="No active or past repair runs"
        description="Start a new repair task or run the demonstration fixture to observe live agent execution."
        actionText="Start Repair"
        onAction={() => navigate('/new')}
      />
    );
  }

  const isRunning = currentTask?.status === 'RUNNING';

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col animate-in fade-in duration-150">
      {/* Top Bar Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-forge bg-forge-surface border border-forge-border shrink-0">
        <div className="flex items-center gap-3">
          <PlayCircle className="w-5 h-5 text-forge-primary" />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-forge-text">Task:</span>
              <select
                value={selectedTaskId || ''}
                onChange={(e) => setSearchParams({ task: e.target.value })}
                className="bg-forge-elevated border border-forge-border rounded px-2.5 py-1 text-xs font-mono text-cyan-400 font-semibold focus:outline-none focus:border-forge-primary"
              >
                {tasks.map((t) => (
                  <option key={t.task_id} value={t.task_id}>
                    {t.task_id} — {t.bug_report?.title?.slice(0, 30) || 'Repair'} ({t.status})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {currentTask && <StatusBadge status={currentTask.status} size="md" />}

          <button
            onClick={() => refetchTask()}
            className="p-1.5 rounded-lg bg-forge-elevated border border-forge-border text-forge-muted hover:text-forge-text transition-colors"
            title="Refresh state"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
          </button>

          {currentTask?.patch && (
            <button
              onClick={() => navigate(`/patch-review?task=${currentTask.task_id}`)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-forge-elevated border border-forge-border hover:bg-forge-border text-xs text-forge-text font-medium transition-colors"
            >
              <GitPullRequest className="w-3.5 h-3.5 text-forge-primary" /> Review Patch
            </button>
          )}

          {currentTask?.verification_result && (
            <button
              onClick={() => navigate(`/verification?task=${currentTask.task_id}`)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-forge-elevated border border-forge-border hover:bg-forge-border text-xs text-forge-text font-medium transition-colors"
            >
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> Verification
            </button>
          )}
        </div>
      </div>

      {/* 3-Column Execution Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* LEFT PANEL: 7-Phase Workflow Timeline */}
        <div className="lg:col-span-3 flex flex-col bg-forge-surface border border-forge-border rounded-forge p-4 overflow-y-auto">
          <h2 className="text-xs font-bold uppercase tracking-wider text-forge-muted mb-3">
            Workflow Checkpoints
          </h2>
          <RepairTimeline
            currentState={currentTask?.current_state || 'INITIALIZED'}
            status={currentTask?.status || 'RUNNING'}
            history={currentTask?.state_history || []}
          />
        </div>

        {/* CENTER PANEL: Live Technical Execution Log */}
        <div className="lg:col-span-6 flex flex-col min-h-[300px]">
          <ExecutionLog
            logs={logsData?.logs || []}
            isLive={isRunning}
            title={`Execution Stream: ${selectedTaskId || ''}`}
          />
        </div>

        {/* RIGHT PANEL: Metadata, Diagnostics & Context */}
        <div className="lg:col-span-3 flex flex-col gap-4 overflow-y-auto">
          {/* Metadata Card */}
          <div className="p-4 rounded-forge bg-forge-surface border border-forge-border text-xs space-y-3">
            <h3 className="font-bold uppercase tracking-wider text-forge-muted text-[10px]">
              Task Context & Config
            </h3>

            <div className="space-y-2 font-mono text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-forge-muted">Target Path</span>
                <span className="text-forge-text truncate max-w-[140px]" title={currentTask?.repo_path}>
                  {currentTask?.repo_path?.split(/[\\/]/).pop()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-forge-muted">Model ID</span>
                <span className="text-cyan-400 font-semibold">{currentTask?.model_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-forge-muted">Is Mock?</span>
                <span className={currentTask?.is_mock ? 'text-amber-400' : 'text-emerald-400'}>
                  {currentTask?.is_mock ? 'Yes (Deterministic)' : 'Live LLM'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-forge-muted">Duration</span>
                <span className="text-forge-text">
                  {currentTask?.duration_seconds ? `${currentTask.duration_seconds}s` : isRunning ? 'Running...' : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Root Cause Summary if diagnosed */}
          {currentTask?.root_cause_analysis && (
            <div className="p-4 rounded-forge bg-forge-surface border border-forge-primary/30 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-forge-primary text-[11px] uppercase tracking-wide">
                  Root Cause Diagnosis
                </h4>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-forge-primary/10 text-forge-primary">
                  Confidence: {currentTask.root_cause_analysis.uncertainty_level}
                </span>
              </div>
              <p className="text-forge-text text-xs leading-relaxed">
                {currentTask.root_cause_analysis.explanation}
              </p>
              <div className="font-mono text-[10px] text-forge-muted pt-1 border-t border-forge-border">
                File: {currentTask.root_cause_analysis.file_path}
              </div>
            </div>
          )}

          {/* Failure reason if any */}
          {currentTask?.failure_reason && (
            <div className="p-4 rounded-forge bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              <h4 className="font-semibold text-rose-400 mb-1">Execution Halted</h4>
              <p className="text-[11px] leading-relaxed">{currentTask.failure_reason}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

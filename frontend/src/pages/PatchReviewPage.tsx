import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  GitPullRequest,
  Check,
  X,
  ArrowRight,
  Info,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';
import { DiffViewer } from '../components/ui/DiffViewer';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const PatchReviewPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [approvalMessage, setApprovalMessage] = useState<string | null>(null);

  const queryTaskId = searchParams.get('task');

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['repairs-list'],
    queryFn: api.listRepairs,
  });

  const selectedTaskId = queryTaskId || tasks?.find((t) => t.patch)?.task_id || tasks?.[0]?.task_id;

  const { data: currentTask, isLoading: taskLoading } = useQuery({
    queryKey: ['repair-task', selectedTaskId],
    queryFn: () => (selectedTaskId ? api.getRepair(selectedTaskId) : null),
    enabled: !!selectedTaskId,
  });

  if (tasksLoading || taskLoading) {
    return <LoadingSkeleton rows={6} />;
  }

  if (!currentTask || !currentTask.patch) {
    return (
      <EmptyState
        title="No patch generated for review"
        description="Select a task that has reached the PATCH_GENERATED checkpoint, or run the demonstration repair."
        actionText="Go to Repairs"
        onAction={() => navigate('/new')}
      />
    );
  }

  const handleApprove = () => {
    setApprovalMessage('Human approval confirmed. (Note: RepairForge retains all changes local; no remote push executed).');
  };

  const handleReject = () => {
    setApprovalMessage('Patch marked as rejected. Requires revised investigation or manual review.');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-150">
      {/* Review Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-forge bg-forge-surface border border-forge-border">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <GitPullRequest className="w-5 h-5 text-forge-primary" />
            <h1 className="text-lg md:text-xl font-bold tracking-tight text-forge-text">
              Review Proposed Repair: <span className="font-mono text-cyan-400">{currentTask.task_id}</span>
            </h1>
            <StatusBadge status={currentTask.status} size="sm" />
          </div>
          <p className="text-xs text-forge-muted font-mono">
            Target: {currentTask.repo_path} • File: {currentTask.patch.file_path}
          </p>
        </div>

        {/* Task Switcher */}
        {tasks && tasks.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-forge-muted">Task:</span>
            <select
              value={selectedTaskId || ''}
              onChange={(e) => {
                setSearchParams({ task: e.target.value });
                setApprovalMessage(null);
              }}
              className="bg-forge-elevated border border-forge-border rounded px-2.5 py-1 text-xs font-mono text-forge-text focus:outline-none"
            >
              {tasks.filter((t) => t.patch).map((t) => (
                <option key={t.task_id} value={t.task_id}>
                  {t.task_id} ({t.status})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {approvalMessage && (
        <div className="p-4 rounded-lg bg-forge-primary/10 border border-forge-primary/30 text-forge-text text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{approvalMessage}</span>
          </div>
          <button onClick={() => setApprovalMessage(null)} className="text-forge-muted hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Root Cause & Defect Diagnosis */}
      {currentTask.root_cause_analysis && (
        <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted flex items-center gap-2">
              <Info className="w-4 h-4 text-cyan-400" />
              Root Cause & Defect Diagnosis
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-forge-elevated text-forge-muted border border-forge-border">
              Confidence: {currentTask.root_cause_analysis.uncertainty_level}
            </span>
          </div>

          <p className="text-xs text-forge-text leading-relaxed">
            {currentTask.root_cause_analysis.explanation}
          </p>

          <div className="p-3 rounded-lg bg-forge-elevated/40 border border-forge-border/40 font-mono text-[11px] text-forge-muted">
            Evidence: {currentTask.root_cause_analysis.evidence}
          </div>
        </div>
      )}

      {/* Code Review Diff Viewer */}
      <DiffViewer
        diffText={currentTask.patch.diff}
        filePath={currentTask.patch.file_path}
        title={currentTask.patch.summary}
      />

      {/* Patch Explanation Card */}
      <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted">
          Patch Scope & Minimalism Guarantee
        </h3>
        <ul className="text-xs text-forge-muted space-y-1.5 list-disc pl-4">
          <li>
            <strong className="text-forge-text">Targeted Modification:</strong> Changes are strictly confined to{' '}
            <code className="text-cyan-400 font-mono">{currentTask.patch.file_path}</code>.
          </li>
          <li>
            <strong className="text-forge-text">No Unrelated Refactoring:</strong> Docstrings, formatting, and public interfaces outside defect scope are preserved.
          </li>
          <li>
            <strong className="text-forge-text">Safety:</strong> Workspace boundaries verified; path traversal prevented.
          </li>
        </ul>
      </div>

      {/* Human Approval Action Bar */}
      <div className="p-5 rounded-forge bg-forge-surface border border-forge-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h4 className="text-xs font-bold text-forge-text uppercase tracking-wider">
            Human Review Gate
          </h4>
          <p className="text-[11px] text-forge-muted mt-0.5">
            RepairForge AI never pushes code automatically. Changes remain local until approved.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleReject}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-rose-500/30 text-rose-300 hover:bg-rose-500/10 text-xs font-medium transition-colors"
          >
            <X className="w-3.5 h-3.5" /> Reject
          </button>

          <button
            onClick={handleApprove}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors shadow-sm"
          >
            <Check className="w-3.5 h-3.5" /> Approve Patch
          </button>

          <button
            onClick={() => navigate(`/verification?task=${currentTask.task_id}`)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-forge-elevated border border-forge-border hover:bg-forge-border text-xs text-forge-text transition-colors"
          >
            View Verification <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
};

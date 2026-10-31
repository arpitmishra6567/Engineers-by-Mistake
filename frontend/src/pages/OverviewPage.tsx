import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Wrench,
  CheckCircle,
  FileSearch,
  Activity,
  Plus,
  ArrowRight,
  ExternalLink,
  Code2,
  FileText,
  AlertTriangle,
} from 'lucide-react';
import { api } from '../api/client';
import { MetricCard } from '../components/ui/MetricCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { RepairTimeline } from '../components/ui/RepairTimeline';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const OverviewPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: summary, isLoading, error } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: api.getDashboardSummary,
  });

  const { data: repoInspect } = useQuery({
    queryKey: ['repo-inspect-root'],
    queryFn: () => api.inspectRepository('.'),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-10 bg-forge-elevated rounded w-1/4 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 bg-forge-elevated rounded-forge animate-pulse" />
          ))}
        </div>
        <LoadingSkeleton rows={5} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-forge border border-rose-500/30 bg-rose-500/10 text-rose-300">
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className="w-5 h-5 text-rose-400" />
          <h2 className="text-base font-semibold">Backend API Offline</h2>
        </div>
        <p className="text-xs text-rose-200">
          Could not connect to the Forge Command API server. Ensure the backend is running with:
        </p>
        <code className="block mt-2 p-2 bg-black/40 rounded text-xs font-mono text-white">
          python -m uvicorn web_api.main:app --reload --host 127.0.0.1 --port 8000
        </code>
      </div>
    );
  }

  const s = summary || {
    total_repairs: 0,
    verified_repairs: 0,
    reproduced_count: 0,
    tests_passed: 0,
    active_repairs: 0,
    failed_validations: 0,
    configured_provider: 'mock',
    execution_mode: 'SAFE_FIXTURE',
    recent_repairs: [],
    recent_reports: [],
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-150">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-forge bg-forge-surface border border-forge-border">
        <div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-forge-text">
            Welcome to RepairForge AI
          </h1>
          <p className="text-xs md:text-sm text-forge-muted mt-1">
            Monitor agent execution, investigate defects, and verify software repairs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="https://github.com/arpitmishra6567/Engineers-by-Mistake#readme"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-forge-elevated border border-forge-border text-xs text-forge-text hover:bg-forge-border transition-colors font-medium"
          >
            <ExternalLink className="w-3.5 h-3.5 text-forge-muted" /> View Docs
          </a>

          <button
            onClick={() => navigate('/new')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-forge-primary hover:bg-forge-primary/90 text-white text-xs font-medium transition-colors shadow-sm shadow-forge-primary/20"
          >
            <Plus className="w-4 h-4" /> Start New Repair
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Repairs"
          value={s.total_repairs}
          subtitle={`${s.active_repairs} currently active`}
          icon={Wrench}
        />
        <MetricCard
          title="Verified Repairs"
          value={s.verified_repairs}
          subtitle={`${s.total_repairs > 0 ? Math.round((s.verified_repairs / s.total_repairs) * 100) : 0}% success rate`}
          icon={CheckCircle}
          trend={s.verified_repairs > 0 ? '+100% target' : undefined}
          trendPositive={true}
          highlight={true}
        />
        <MetricCard
          title="Reproduction Count"
          value={s.reproduced_count}
          subtitle="Confirmed before patching"
          icon={FileSearch}
        />
        <MetricCard
          title="Tests Passed"
          value={s.tests_passed}
          subtitle={`${s.failed_validations} failed validations`}
          icon={Activity}
        />
      </div>

      {/* 2-Column Section: Pipeline & Active Repo Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: 7-Phase Repair Pipeline Card */}
        <div className="p-5 rounded-forge bg-forge-surface border border-forge-border">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-forge-muted">
              7-Phase Repair Lifecycle
            </h2>
            <span className="text-[10px] font-mono text-forge-primary bg-forge-primary/10 px-2 py-0.5 rounded">
              STANDARD HARNESS
            </span>
          </div>

          <RepairTimeline
            currentState={s.recent_repairs[0]?.current_state || 'COMPLETED'}
            status={s.recent_repairs[0]?.status || 'VERIFIED'}
            history={s.recent_repairs[0]?.state_history || []}
          />
        </div>

        {/* Right: Repository Overview & Recent Reports */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Repo Panel */}
          {repoInspect && (
            <div className="p-5 rounded-forge bg-forge-surface border border-forge-border">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Code2 className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-semibold text-forge-text">Active Repository Environment</h3>
                </div>
                <button
                  onClick={() => navigate('/repositories')}
                  className="text-xs text-forge-primary hover:underline flex items-center gap-1 font-medium"
                >
                  Explore <ArrowRight className="w-3 h-3" />
                </button>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-lg bg-forge-elevated/40 border border-forge-border/40 font-mono text-xs">
                <div>
                  <span className="text-[10px] text-forge-muted block uppercase">Files</span>
                  <span className="font-semibold text-forge-text">{repoInspect.total_files}</span>
                </div>
                <div>
                  <span className="text-[10px] text-forge-muted block uppercase">Languages</span>
                  <span className="font-semibold text-forge-text">{repoInspect.languages.join(', ') || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-forge-muted block uppercase">Framework</span>
                  <span className="font-semibold text-forge-text">{repoInspect.test_framework || 'pytest'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-forge-muted block uppercase">Git Status</span>
                  <span className="text-emerald-400 font-semibold">{repoInspect.has_git ? 'Clean Tree' : 'None'}</span>
                </div>
              </div>
            </div>
          )}

          {/* Recent Reports Panel */}
          <div className="p-5 rounded-forge bg-forge-surface border border-forge-border">
            <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted mb-3">
              Generated Evaluation & Verification Reports
            </h3>
            {s.recent_reports.length === 0 ? (
              <p className="text-xs text-forge-muted">No markdown reports generated yet.</p>
            ) : (
              <div className="space-y-2">
                {s.recent_reports.slice(0, 3).map((rep, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-forge-elevated/40 border border-forge-border/40 hover:border-forge-border text-xs"
                  >
                    <div className="flex items-center gap-2.5">
                      <FileText className="w-4 h-4 text-forge-muted" />
                      <div>
                        <span className="font-mono font-medium text-forge-text">{rep.filename}</span>
                        <span className="text-[10px] text-forge-muted block">
                          Task ID: {rep.task_id} • {(rep.size_bytes / 1024).toFixed(1)} KB
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => navigate(`/execution?task=${rep.task_id}`)}
                      className="px-2.5 py-1 rounded bg-forge-elevated hover:bg-forge-border text-forge-text font-mono text-[11px] transition-colors"
                    >
                      View Report
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Repairs Table */}
      <div className="p-5 rounded-forge bg-forge-surface border border-forge-border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-forge-text">Recent Repair Runs</h2>
            <p className="text-xs text-forge-muted">Real execution records captured by RepairForge</p>
          </div>
          <button
            onClick={() => navigate('/new')}
            className="text-xs text-forge-primary hover:underline flex items-center gap-1 font-medium"
          >
            New Investigation <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        {s.recent_repairs.length === 0 ? (
          <EmptyState
            title="No repair tasks yet"
            description="Start your first investigation or run the deterministic demonstration."
            actionText="Start Repair"
            onAction={() => navigate('/new')}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-forge-border text-forge-muted font-mono uppercase text-[10px]">
                  <th className="pb-2.5 font-semibold">Task ID</th>
                  <th className="pb-2.5 font-semibold">Repository</th>
                  <th className="pb-2.5 font-semibold">Defect Title</th>
                  <th className="pb-2.5 font-semibold">Provider</th>
                  <th className="pb-2.5 font-semibold">Status</th>
                  <th className="pb-2.5 font-semibold">Duration</th>
                  <th className="pb-2.5 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-forge-border/40 font-mono">
                {s.recent_repairs.map((task) => (
                  <tr key={task.task_id} className="hover:bg-forge-elevated/40 transition-colors">
                    <td className="py-3 text-cyan-400 font-semibold">{task.task_id}</td>
                    <td className="py-3 text-forge-muted truncate max-w-[140px]">
                      {task.repo_path.split(/[\\/]/).pop()}
                    </td>
                    <td className="py-3 font-sans text-forge-text font-medium truncate max-w-[220px]">
                      {task.bug_report?.title || 'Defect Investigation'}
                    </td>
                    <td className="py-3 text-forge-muted text-[11px]">{task.model_name}</td>
                    <td className="py-3">
                      <StatusBadge status={task.status} size="sm" />
                    </td>
                    <td className="py-3 text-forge-muted text-[11px]">
                      {task.duration_seconds ? `${task.duration_seconds}s` : 'N/A'}
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => navigate(`/execution?task=${task.task_id}`)}
                        className="px-2.5 py-1 rounded bg-forge-elevated hover:bg-forge-border text-forge-text text-[11px] font-sans transition-colors"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};


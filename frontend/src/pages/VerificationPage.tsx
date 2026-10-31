import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  CheckCircle,
  XCircle,
  Terminal,
  Search,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';
import { StatusBadge } from '../components/ui/StatusBadge';
import { MetricCard } from '../components/ui/MetricCard';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const VerificationPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [filter, setFilter] = useState<'all' | 'passed' | 'failed'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const queryTaskId = searchParams.get('task');

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['repairs-list'],
    queryFn: api.listRepairs,
  });

  const selectedTaskId = queryTaskId || tasks?.[0]?.task_id;

  const { data: currentTask, isLoading: taskLoading } = useQuery({
    queryKey: ['repair-task', selectedTaskId],
    queryFn: () => (selectedTaskId ? api.getRepair(selectedTaskId) : null),
    enabled: !!selectedTaskId,
  });

  if (tasksLoading || taskLoading) {
    return <LoadingSkeleton rows={6} />;
  }

  if (!currentTask) {
    return (
      <EmptyState
        title="No verification results available"
        description="Run a repair task to see test execution records, reproduction evidence, and regression suite outcomes."
        actionText="Start Repair"
        onAction={() => navigate('/new')}
      />
    );
  }

  const verif = currentTask.verification_result;
  const repro = currentTask.reproduction_result;

  const passedTests = verif?.tests_passed || [];
  const failedTests = verif?.tests_failed || [];

  const allTests = [
    ...passedTests.map((t) => ({ name: t, status: 'PASSED' as const })),
    ...failedTests.map((t) => ({ name: t, status: 'FAILED' as const })),
  ];

  const filteredTests = allTests.filter((t) => {
    if (filter === 'passed' && t.status !== 'PASSED') return false;
    if (filter === 'failed' && t.status !== 'FAILED') return false;
    if (searchTerm && !t.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-forge bg-forge-surface border border-forge-border">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <h1 className="text-lg md:text-xl font-bold tracking-tight text-forge-text">
              Verification Center: <span className="font-mono text-cyan-400">{currentTask.task_id}</span>
            </h1>
            <StatusBadge status={currentTask.status} size="sm" />
          </div>
          <p className="text-xs text-forge-muted font-mono">
            Automated test verification and reproduction evidence
          </p>
        </div>

        {tasks && tasks.length > 1 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-forge-muted">Task:</span>
            <select
              value={selectedTaskId || ''}
              onChange={(e) => setSearchParams({ task: e.target.value })}
              className="bg-forge-elevated border border-forge-border rounded px-2.5 py-1 text-xs font-mono text-forge-text focus:outline-none"
            >
              {tasks.map((t) => (
                <option key={t.task_id} value={t.task_id}>
                  {t.task_id} ({t.status})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <MetricCard
          title="Verification Status"
          value={verif?.verified ? 'VERIFIED' : 'FAILED'}
          subtitle={verif?.verified ? 'All regression tests passed' : 'Validation not proven'}
          highlight={verif?.verified}
          trendPositive={verif?.verified}
        />
        <MetricCard
          title="Syntax Check"
          value={verif?.syntax_valid ? 'VALID' : 'INVALID'}
          subtitle="Python AST Parse"
        />
        <MetricCard
          title="Tests Passed"
          value={passedTests.length}
          subtitle={`${failedTests.length} failed`}
        />
        <MetricCard
          title="Test Duration"
          value={verif?.duration_seconds ? `${verif.duration_seconds.toFixed(2)}s` : '0.0s'}
          subtitle={`Command Exit: ${verif?.exit_code ?? 'N/A'}`}
        />
      </div>

      {/* Phase 3 Reproduction Proof */}
      {repro && (
        <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-forge-muted flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              Reproduction Evidence (Pre-Patch Phase)
            </h2>
            <StatusBadge status={repro.status} size="sm" />
          </div>

          <div className="p-3 rounded-lg bg-forge-bg border border-forge-border font-mono text-xs space-y-1.5">
            <div className="flex items-center justify-between text-forge-muted text-[11px]">
              <span>Command: <code className="text-forge-text">{repro.command}</code></span>
              <span>Exit Code: <strong className={repro.exit_code !== 0 ? 'text-rose-400' : 'text-emerald-400'}>{repro.exit_code}</strong></span>
            </div>
            <p className="text-forge-text text-[11px] pt-1">{repro.evidence_notes}</p>
          </div>
        </div>
      )}

      {/* Test Results Table */}
      <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-forge-text">Regression Test Executions</h3>
            <p className="text-xs text-forge-muted">Verified against the patched workspace clone</p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            {/* Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2 top-2 text-forge-muted" />
              <input
                type="text"
                placeholder="Search test name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-forge-elevated border border-forge-border rounded px-2 py-1 pl-7 text-xs text-forge-text focus:outline-none"
              />
            </div>

            {/* Filter buttons */}
            <div className="flex items-center bg-forge-elevated border border-forge-border rounded p-0.5">
              {(['all', 'passed', 'failed'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-2.5 py-0.5 rounded text-[11px] capitalize ${
                    filter === f ? 'bg-forge-surface text-forge-text font-semibold' : 'text-forge-muted hover:text-forge-text'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        {filteredTests.length === 0 ? (
          <div className="text-center py-8 text-xs text-forge-muted">
            No test suites match the selected filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-forge-border text-forge-muted uppercase text-[10px]">
                  <th className="pb-2 font-semibold">Status</th>
                  <th className="pb-2 font-semibold">Test Specification</th>
                  <th className="pb-2 font-semibold text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-forge-border/40">
                {filteredTests.map((test, idx) => (
                  <tr key={idx} className="hover:bg-forge-elevated/40">
                    <td className="py-2.5">
                      {test.status === 'PASSED' ? (
                        <span className="flex items-center gap-1.5 text-emerald-400 font-semibold text-xs">
                          <CheckCircle2 className="w-3.5 h-3.5" /> PASSED
                        </span>
                      ) : (
                        <span className="flex items-center gap-1.5 text-rose-400 font-semibold text-xs">
                          <XCircle className="w-3.5 h-3.5" /> FAILED
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 text-forge-text">{test.name}</td>
                    <td className="py-2.5 text-right text-forge-muted text-[11px]">
                      Exit code {verif?.exit_code ?? 0}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Captured Output Panels */}
      {verif && (verif.stdout || verif.stderr) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {verif.stdout && (
            <div className="p-4 rounded-forge bg-forge-bg border border-forge-border font-mono text-[11px] space-y-1.5">
              <span className="text-forge-muted text-[10px] uppercase font-bold block">Test Suite stdout</span>
              <pre className="text-forge-text max-h-48 overflow-y-auto whitespace-pre-wrap">{verif.stdout}</pre>
            </div>
          )}
          {verif.stderr && (
            <div className="p-4 rounded-forge bg-forge-bg border border-forge-border font-mono text-[11px] space-y-1.5">
              <span className="text-rose-400 text-[10px] uppercase font-bold block">Test Suite stderr</span>
              <pre className="text-rose-300 max-h-48 overflow-y-auto whitespace-pre-wrap">{verif.stderr}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

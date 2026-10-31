import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  FolderGit2,
  Bug,
  Cpu,
  Shield,
  Play,
  AlertCircle,
} from 'lucide-react';
import { api } from '../api/client';
import { RepairCreateRequest } from '../api/types';

export const NewRepairPage: React.FC = () => {
  const navigate = useNavigate();

  // Known repositories
  const { data: knownRepos } = useQuery({
    queryKey: ['known-repos'],
    queryFn: api.listKnownRepositories,
  });

  // Form State
  const [repoPath, setRepoPath] = useState('examples/buggy_average');
  const [title, setTitle] = useState('ZeroDivisionError in calculate_average on empty list');
  const [description, setDescription] = useState(
    'Function calculate_average raises ZeroDivisionError when passed an empty list [] instead of ValueError.'
  );
  const [expectedBehavior, setExpectedBehavior] = useState(
    'Raise explicit ValueError("Cannot calculate average of an empty list") when list is empty.'
  );
  const [actualBehavior, setActualBehavior] = useState(
    'Raises unhandled ZeroDivisionError: division by zero.'
  );
  const [errorMessage, setErrorMessage] = useState('ZeroDivisionError: division by zero');
  const [stackTrace, setStackTrace] = useState(
    'ZeroDivisionError: division by zero\n  File "average.py", line 11, in calculate_average\n    return sum(numbers) / len(numbers)'
  );
  const [testCommand, setTestCommand] = useState('python -m pytest test_average.py');
  const [providerType, setProviderType] = useState('mock');
  const [isolateWorkspace, setIsolateWorkspace] = useState(true);
  const [autoApprove, setAutoApprove] = useState(true);

  // Mutation
  const createMutation = useMutation({
    mutationFn: (data: RepairCreateRequest) => api.createRepair(data),
    onSuccess: (task) => {
      navigate(`/execution?task=${task.task_id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      repo_path: repoPath,
      title,
      description,
      expected_behavior: expectedBehavior,
      actual_behavior: actualBehavior,
      error_message: errorMessage || undefined,
      stack_trace: stackTrace || undefined,
      test_command: testCommand || undefined,
      provider_type: providerType,
      isolate_workspace: isolateWorkspace,
      auto_approve: autoApprove,
    });
  };

  const handleSelectTemplate = (type: 'average' | 'custom') => {
    if (type === 'average') {
      setRepoPath('examples/buggy_average');
      setTitle('ZeroDivisionError in calculate_average on empty list');
      setDescription('Function calculate_average raises ZeroDivisionError on empty list instead of ValueError.');
      setExpectedBehavior('Raise explicit ValueError("Cannot calculate average of an empty list")');
      setActualBehavior('Raises unhandled ZeroDivisionError: division by zero');
      setErrorMessage('ZeroDivisionError: division by zero');
      setStackTrace('ZeroDivisionError: division by zero\n  File "average.py", line 11, in calculate_average');
      setTestCommand('python -m pytest test_average.py');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-150">
      {/* Title */}
      <div>
        <h1 className="text-xl md:text-2xl font-bold tracking-tight text-forge-text">Start a New Repair</h1>
        <p className="text-xs md:text-sm text-forge-muted mt-1">
          Connect a repository, describe a defect, and let RepairForge investigate, reproduce, and verify.
        </p>
      </div>

      {createMutation.isError && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold">Failed to launch repair</h4>
            <p className="text-xs mt-0.5">{createMutation.error?.message}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* SECTION A: REPOSITORY */}
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderGit2 className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-forge-text uppercase tracking-wide">
                Section A: Target Repository
              </h2>
            </div>
            <span className="text-[11px] text-forge-muted">Server Filesystem Path</span>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-forge-muted mb-1.5">
                Local Repository Path (relative to server root or allowed path)
              </label>
              <input
                type="text"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                required
                className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 text-xs font-mono text-forge-text focus:outline-none focus:border-forge-primary"
                placeholder="e.g. examples/buggy_average"
              />
            </div>

            {knownRepos && knownRepos.length > 0 && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-forge-muted">Quick Presets:</span>
                {knownRepos.map((kr) => (
                  <button
                    key={kr.path}
                    type="button"
                    onClick={() => {
                      setRepoPath(kr.path);
                      if (kr.path.includes('average')) handleSelectTemplate('average');
                    }}
                    className={`px-2.5 py-1 rounded border text-xs font-mono transition-colors ${
                      repoPath === kr.path
                        ? 'bg-forge-primary/20 border-forge-primary text-forge-primary'
                        : 'bg-forge-elevated border-forge-border text-forge-muted hover:text-forge-text'
                    }`}
                  >
                    {kr.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* SECTION B: BUG SPECIFICATION */}
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4">
          <div className="flex items-center gap-2">
            <Bug className="w-4 h-4 text-forge-primary" />
            <h2 className="text-sm font-bold text-forge-text uppercase tracking-wide">
              Section B: Defect Specification
            </h2>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="block font-medium text-forge-muted mb-1.5">Defect Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 text-xs text-forge-text focus:outline-none focus:border-forge-primary"
                placeholder="Brief summary of defect"
              />
            </div>

            <div>
              <label className="block font-medium text-forge-muted mb-1.5">Detailed Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                required
                className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 text-xs text-forge-text focus:outline-none focus:border-forge-primary"
                placeholder="Describe what occurs and steps to reproduce..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block font-medium text-forge-muted mb-1.5">Expected Behavior</label>
                <textarea
                  value={expectedBehavior}
                  onChange={(e) => setExpectedBehavior(e.target.value)}
                  rows={2}
                  className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 text-xs text-forge-text focus:outline-none focus:border-forge-primary"
                />
              </div>
              <div>
                <label className="block font-medium text-forge-muted mb-1.5">Actual Behavior</label>
                <textarea
                  value={actualBehavior}
                  onChange={(e) => setActualBehavior(e.target.value)}
                  rows={2}
                  className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 text-xs text-forge-text focus:outline-none focus:border-forge-primary"
                />
              </div>
            </div>

            <div>
              <label className="block font-medium text-forge-muted mb-1.5">
                Observed Traceback or Error Message (Optional)
              </label>
              <textarea
                value={stackTrace}
                onChange={(e) => setStackTrace(e.target.value)}
                rows={3}
                className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 font-mono text-[11px] text-rose-300 focus:outline-none focus:border-forge-primary"
              />
            </div>

            <div>
              <label className="block font-medium text-forge-muted mb-1.5">
                Targeted Test Command (Optional)
              </label>
              <input
                type="text"
                value={testCommand}
                onChange={(e) => setTestCommand(e.target.value)}
                className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 font-mono text-xs text-forge-text focus:outline-none focus:border-forge-primary"
                placeholder="e.g. python -m pytest test_average.py"
              />
            </div>
          </div>
        </div>

        {/* SECTION C & D: MODEL & EXECUTION POLICY */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Model Config */}
          <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-forge-warning" />
              <h2 className="text-sm font-bold text-forge-text uppercase tracking-wide">
                Section C: Model Provider
              </h2>
            </div>

            <div className="space-y-3 text-xs">
              <div className="space-y-2">
                <label
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    providerType === 'mock'
                      ? 'bg-forge-primary/10 border-forge-primary/40 text-forge-text'
                      : 'bg-forge-elevated border-forge-border text-forge-muted'
                  }`}
                >
                  <input
                    type="radio"
                    name="provider"
                    value="mock"
                    checked={providerType === 'mock'}
                    onChange={() => setProviderType('mock')}
                    className="mt-0.5"
                  />
                  <div>
                    <span className="font-semibold block text-forge-text">Deterministic Mock Adapter</span>
                    <span className="text-[11px] text-forge-muted">
                      Predictable rule-based fixture for offline harness testing. No API key needed.
                    </span>
                  </div>
                </label>

                <label
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    providerType === 'openai_compatible'
                      ? 'bg-forge-primary/10 border-forge-primary/40 text-forge-text'
                      : 'bg-forge-elevated border-forge-border text-forge-muted'
                  }`}
                >
                  <input
                    type="radio"
                    name="provider"
                    value="openai_compatible"
                    checked={providerType === 'openai_compatible'}
                    onChange={() => setProviderType('openai_compatible')}
                    className="mt-0.5"
                  />
                  <div>
                    <span className="font-semibold block text-forge-text">OpenAI-Compatible Endpoint</span>
                    <span className="text-[11px] text-forge-muted">
                      Uses server-configured REPAIRFORGE_API_KEY and base URL (vLLM, Ollama, OpenAI).
                    </span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          {/* Execution Containment */}
          <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-bold text-forge-text uppercase tracking-wide">
                Section D: Execution Policy
              </h2>
            </div>

            <div className="space-y-3 text-xs">
              <label className="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isolateWorkspace}
                  onChange={(e) => setIsolateWorkspace(e.target.checked)}
                  className="rounded bg-forge-elevated border-forge-border text-forge-primary"
                />
                <span className="text-forge-text">Isolate Workspace in Temporary Clone</span>
              </label>
              <p className="text-[11px] text-forge-muted pl-6">
                Leaves your original repository files completely untouched during testing.
              </p>

              <label className="flex items-center gap-2.5 cursor-pointer pt-2">
                <input
                  type="checkbox"
                  checked={autoApprove}
                  onChange={(e) => setAutoApprove(e.target.checked)}
                  className="rounded bg-forge-elevated border-forge-border text-forge-primary"
                />
                <span className="text-forge-text">Auto-Approve Review Gate (Demo Mode)</span>
              </label>
              <p className="text-[11px] text-forge-muted pl-6">
                Automatically transitions from HUMAN_REVIEW to COMPLETED when tests pass.
              </p>
            </div>
          </div>
        </div>

        {/* SECTION E: SUMMARY & SUBMIT */}
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-forge-text">Ready to Investigate</h3>
            <p className="text-xs text-forge-muted mt-0.5">
              Target: <span className="font-mono text-cyan-400">{repoPath}</span> • Model:{' '}
              <span className="font-mono text-forge-primary">{providerType}</span>
            </p>
          </div>

          <button
            type="submit"
            disabled={createMutation.isPending}
            className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-forge-primary hover:bg-forge-primary/90 disabled:opacity-50 text-white text-xs font-semibold shadow-md shadow-forge-primary/20 transition-all"
          >
            {createMutation.isPending ? (
              <span>Initializing Engine...</span>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Initialize Repair</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

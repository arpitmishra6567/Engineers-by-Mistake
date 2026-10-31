import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  FileCode,
  Search,
  AlertCircle,
  Boxes,
  RefreshCw,
} from 'lucide-react';
import { api } from '../api/client';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const RepositoriesPage: React.FC = () => {
  const [selectedPath, setSelectedPath] = useState('.');
  const [inputPath, setInputPath] = useState('.');
  const [fileSearch, setFileSearch] = useState('');

  const { data: knownRepos } = useQuery({
    queryKey: ['known-repos'],
    queryFn: api.listKnownRepositories,
  });

  const {
    data: repoData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['repo-inspect', selectedPath],
    queryFn: () => api.inspectRepository(selectedPath),
  });

  const handleInspect = (e: React.FormEvent) => {
    e.preventDefault();
    setSelectedPath(inputPath);
  };

  const filteredFiles = repoData?.source_files?.filter((f) =>
    f.toLowerCase().includes(fileSearch.toLowerCase())
  ) || [];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-forge bg-forge-surface border border-forge-border">
        <div>
          <h1 className="text-lg md:text-xl font-bold tracking-tight text-forge-text">Repository Explorer</h1>
          <p className="text-xs text-forge-muted mt-0.5">
            Safe inspection and dependency analysis via RepositoryAnalyzer
          </p>
        </div>

        {/* Path Form */}
        <form onSubmit={handleInspect} className="flex items-center gap-2">
          <input
            type="text"
            value={inputPath}
            onChange={(e) => setInputPath(e.target.value)}
            className="bg-forge-elevated border border-forge-border rounded-lg px-3 py-1.5 font-mono text-xs text-forge-text focus:outline-none focus:border-forge-primary"
            placeholder="Repository path (e.g. .)"
          />
          <button
            type="submit"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-forge-primary hover:bg-forge-primary/90 text-white text-xs font-semibold shadow-sm transition-colors shrink-0"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Analyze
          </button>
        </form>
      </div>

      {/* Preset Quick Selectors */}
      {knownRepos && knownRepos.length > 0 && (
        <div className="flex items-center gap-2 text-xs">
          <span className="text-forge-muted">Quick Access:</span>
          {knownRepos.map((kr) => (
            <button
              key={kr.path}
              onClick={() => {
                setInputPath(kr.path);
                setSelectedPath(kr.path);
              }}
              className={`px-2.5 py-1 rounded border text-xs font-mono transition-colors ${
                selectedPath === kr.path
                  ? 'bg-forge-primary/20 border-forge-primary text-forge-primary'
                  : 'bg-forge-elevated border-forge-border text-forge-muted hover:text-forge-text'
              }`}
            >
              {kr.name}
            </button>
          ))}
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold">Inspection Denied / Failed</h4>
            <p className="text-xs mt-0.5 font-mono">{error.message}</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : repoData ? (
        <>
          {/* Metadata Cards Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-forge bg-forge-surface border border-forge-border">
              <span className="text-[10px] uppercase font-mono text-forge-muted block">Total Files</span>
              <span className="text-xl font-bold font-mono text-forge-text mt-1 block">
                {repoData.total_files}
              </span>
            </div>
            <div className="p-4 rounded-forge bg-forge-surface border border-forge-border">
              <span className="text-[10px] uppercase font-mono text-forge-muted block">Languages</span>
              <span className="text-sm font-semibold font-mono text-cyan-400 mt-1 block truncate">
                {repoData.languages.join(', ') || 'N/A'}
              </span>
            </div>
            <div className="p-4 rounded-forge bg-forge-surface border border-forge-border">
              <span className="text-[10px] uppercase font-mono text-forge-muted block">Framework</span>
              <span className="text-sm font-semibold font-mono text-forge-text mt-1 block truncate">
                {repoData.test_framework || 'None'}
              </span>
            </div>
            <div className="p-4 rounded-forge bg-forge-surface border border-forge-border">
              <span className="text-[10px] uppercase font-mono text-forge-muted block">Git Status</span>
              <span className="text-sm font-semibold font-mono text-emerald-400 mt-1 block">
                {repoData.has_git ? 'Git Initialized' : 'None'}
              </span>
            </div>
          </div>

          {/* Dependencies & Configurations */}
          <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted flex items-center gap-2">
              <Boxes className="w-4 h-4 text-forge-primary" /> Dependency & Manifest Files
            </h3>
            <div className="flex flex-wrap gap-2 font-mono text-xs">
              {repoData.dependency_files.length === 0 ? (
                <span className="text-forge-muted text-xs">No standard dependency manifests detected.</span>
              ) : (
                repoData.dependency_files.map((dep, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded bg-forge-elevated border border-forge-border text-forge-text"
                  >
                    {dep}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Source Files Search & List */}
          <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted flex items-center gap-2">
                <FileCode className="w-4 h-4 text-cyan-400" /> Tracked Source Files ({filteredFiles.length})
              </h3>

              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2 top-2 text-forge-muted" />
                <input
                  type="text"
                  placeholder="Filter files..."
                  value={fileSearch}
                  onChange={(e) => setFileSearch(e.target.value)}
                  className="bg-forge-elevated border border-forge-border rounded px-2.5 py-1 pl-7 text-xs font-mono text-forge-text focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 font-mono text-xs max-h-96 overflow-y-auto">
              {filteredFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="p-2 rounded bg-forge-bg border border-forge-border text-forge-text truncate flex items-center gap-2 hover:border-forge-primary/40 transition-colors"
                >
                  <FileCode className="w-3.5 h-3.5 text-forge-muted shrink-0" />
                  <span className="truncate">{file}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Settings as SettingsIcon,
  Cpu,
  Shield,
  Layers,
  Info,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { api } from '../api/client';

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'general' | 'models' | 'execution' | 'security' | 'about'>('general');

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth,
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="p-5 rounded-forge bg-forge-surface border border-forge-border">
        <h1 className="text-lg md:text-xl font-bold tracking-tight text-forge-text">System & Workspace Settings</h1>
        <p className="text-xs text-forge-muted mt-0.5">
          Configure interface preferences, execution boundaries, and inspect security settings
        </p>

        {/* Tab Strip */}
        <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-forge-border text-xs">
          {[
            { id: 'general', label: 'General', icon: SettingsIcon },
            { id: 'models', label: 'Model Providers', icon: Cpu },
            { id: 'execution', label: 'Execution Policy', icon: Layers },
            { id: 'security', label: 'Security & Trust', icon: Shield },
            { id: 'about', label: 'About & Version', icon: Info },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-forge-primary text-white shadow-sm'
                    : 'bg-forge-elevated text-forge-muted hover:text-forge-text border border-forge-border'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* TAB A: GENERAL */}
      {activeTab === 'general' && (
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4 text-xs">
          <h2 className="text-sm font-bold text-forge-text uppercase tracking-wider">Appearance & Preferences</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-forge-elevated/40 border border-forge-border">
              <div>
                <span className="font-semibold text-forge-text block">Workspace Theme</span>
                <span className="text-forge-muted text-[11px]">Toggle between Dark and Light mode</span>
              </div>
              <span className="text-cyan-400 font-mono">Dark (Default) / Light Supported</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-forge-elevated/40 border border-forge-border">
              <div>
                <span className="font-semibold text-forge-text block">Interface Typography</span>
                <span className="text-forge-muted text-[11px]">Inter (UI) + JetBrains Mono (Code/Logs)</span>
              </div>
              <span className="text-forge-muted font-mono">Active</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB B: MODELS */}
      {activeTab === 'models' && (
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4 text-xs">
          <h2 className="text-sm font-bold text-forge-text uppercase tracking-wider">Model Inference Settings</h2>
          <p className="text-forge-muted leading-relaxed">
            RepairForge AI uses environment variables for secure credential injection. Secret tokens are never stored
            in the browser's localStorage.
          </p>

          <div className="p-4 rounded-lg bg-forge-bg border border-forge-border font-mono text-[11px] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">Active Local Provider:</span>
              <span className="text-forge-text font-bold">MockModelAdapter (Deterministic)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">OpenAI / Compatible Provider:</span>
              <span className="text-cyan-400">Supported via REPAIRFORGE_API_KEY</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">Configurable Endpoints:</span>
              <span className="text-forge-text">OpenAI, vLLM, Ollama, LocalAI, TGI</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB C: EXECUTION POLICY */}
      {activeTab === 'execution' && (
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4 text-xs">
          <h2 className="text-sm font-bold text-forge-text uppercase tracking-wider">Execution Policies & Timeouts</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-forge-elevated/40 border border-forge-border space-y-1">
              <span className="text-forge-muted text-[10px] uppercase font-bold block">Execution Timeout</span>
              <span className="text-base font-bold font-mono text-forge-text">60 seconds</span>
              <p className="text-[11px] text-forge-muted">Hard termination for infinite loops</p>
            </div>

            <div className="p-4 rounded-lg bg-forge-elevated/40 border border-forge-border space-y-1">
              <span className="text-forge-muted text-[10px] uppercase font-bold block">Validation Retries</span>
              <span className="text-base font-bold font-mono text-forge-text">3 attempts</span>
              <p className="text-[11px] text-forge-muted">Bounded retry budget prevents runaway loops</p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
            <div>
              <strong className="block">Container Isolation Notice:</strong>
              Docker execution backend is an optional configuration. Local execution currently runs in SAFE_FIXTURE
              mode with whitelisted commands on local test runners.
            </div>
          </div>
        </div>
      )}

      {/* TAB D: SECURITY */}
      {activeTab === 'security' && (
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4 text-xs">
          <h2 className="text-sm font-bold text-forge-text uppercase tracking-wider">Security Boundaries</h2>

          <ul className="space-y-2.5 text-forge-muted">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong className="text-forge-text">Path Traversal Defense:</strong> All file reads and patch writes are
                strictly validated by SafeFileReader to ensure paths never escape workspace boundaries.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong className="text-forge-text">Forbidden Commands:</strong> Destructive operations like{' '}
                <code className="text-rose-400 font-mono">rm -rf</code>,{' '}
                <code className="text-rose-400 font-mono">git push</code>, and system altering calls are blocked by
                ExecutionPolicy.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong className="text-forge-text">Zero Remote Leaks:</strong> API keys, credentials, and environmental
                secrets are never passed to the frontend or written to reports.
              </span>
            </li>
          </ul>
        </div>
      )}

      {/* TAB E: ABOUT */}
      {activeTab === 'about' && (
        <div className="p-6 rounded-forge bg-forge-surface border border-forge-border space-y-4 text-xs">
          <h2 className="text-sm font-bold text-forge-text uppercase tracking-wider">About Forge Command</h2>

          <div className="p-4 rounded-lg bg-forge-bg border border-forge-border font-mono text-[11px] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">Product Name:</span>
              <span className="text-forge-text font-bold">Forge Command</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">Harness Core:</span>
              <span className="text-forge-text">RepairForge AI</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">Backend API Version:</span>
              <span className="text-emerald-400 font-bold">{health?.version || '0.1.0'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">Frontend Version:</span>
              <span className="text-cyan-400 font-bold">v0.1.0</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-forge-muted">License:</span>
              <span className="text-forge-text">MIT License</span>
            </div>
          </div>

          <div className="pt-2">
            <a
              href="https://github.com/arpitmishra6567/Engineers-by-Mistake"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-forge-primary hover:underline font-semibold"
            >
              GitHub Repository: arpitmishra6567/Engineers-by-Mistake <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      )}
    </div>
  );
};


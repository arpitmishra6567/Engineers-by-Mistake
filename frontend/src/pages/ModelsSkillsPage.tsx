import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Cpu,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Shield,
  Layers,
  Check,
  RefreshCw,
} from 'lucide-react';
import { api } from '../api/client';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';

export const ModelsSkillsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'models' | 'skills'>('models');
  const [validationResult, setValidationResult] = useState<{ valid: boolean; message: string } | null>(null);

  const { data: models, isLoading: modelsLoading } = useQuery({
    queryKey: ['models-list'],
    queryFn: api.listModels,
  });

  const { data: skillInfo, isLoading: skillLoading } = useQuery({
    queryKey: ['skill-info'],
    queryFn: api.getSkillInfo,
  });

  const validateMutation = useMutation({
    mutationFn: api.validateSkill,
    onSuccess: (data) => {
      setValidationResult(data);
    },
  });

  if (modelsLoading || skillLoading) {
    return <LoadingSkeleton rows={6} />;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-forge bg-forge-surface border border-forge-border">
        <div>
          <h1 className="text-lg md:text-xl font-bold tracking-tight text-forge-text">Models & Agent Skills</h1>
          <p className="text-xs text-forge-muted mt-0.5">
            Manage model inference adapters and inspect open Agent Skills packages
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center bg-forge-elevated border border-forge-border rounded-lg p-1 text-xs">
          <button
            onClick={() => setActiveTab('models')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'models' ? 'bg-forge-surface text-forge-text shadow-sm' : 'text-forge-muted hover:text-forge-text'
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-forge-primary" /> Model Providers
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'skills' ? 'bg-forge-surface text-forge-text shadow-sm' : 'text-forge-muted hover:text-forge-text'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Agent Skills ({skillInfo?.name || 'bugrepro'})
          </button>
        </div>
      </div>

      {/* TAB A: MODEL PROVIDERS */}
      {activeTab === 'models' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models?.map((model) => (
              <div
                key={model.id}
                className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-sm text-forge-text">{model.name}</span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                        model.status === 'READY'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : model.status === 'CONFIGURED'
                          ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                          : 'bg-forge-elevated text-forge-muted border-forge-border'
                      }`}
                    >
                      {model.status}
                    </span>
                  </div>

                  <p className="text-xs text-forge-muted leading-relaxed mb-3">{model.description}</p>
                </div>

                <div className="pt-3 border-t border-forge-border/60 font-mono text-[11px] space-y-1 text-forge-muted">
                  <div className="flex items-center justify-between">
                    <span>Model ID:</span>
                    <span className="text-forge-text">{model.model_name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Deterministic:</span>
                    <span className="text-forge-text">{model.is_deterministic ? 'True (Mock)' : 'False (LLM)'}</span>
                  </div>
                  {model.base_url && (
                    <div className="flex items-center justify-between">
                      <span>Endpoint:</span>
                      <span className="text-cyan-400 truncate max-w-[180px]">{model.base_url}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB B: AGENT SKILLS */}
      {activeTab === 'skills' && skillInfo && (
        <div className="space-y-6">
          {/* Skill Overview Card */}
          <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-base font-bold text-forge-text">{skillInfo.name}</h2>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    Agent Skills Standard
                  </span>
                </div>
                <p className="text-xs text-forge-muted leading-relaxed max-w-2xl">{skillInfo.description}</p>
              </div>

              <button
                onClick={() => validateMutation.mutate()}
                disabled={validateMutation.isPending}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-forge-primary hover:bg-forge-primary/90 text-white text-xs font-semibold shadow-sm transition-colors shrink-0"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${validateMutation.isPending ? 'animate-spin' : ''}`} />
                <span>Validate Skill Package</span>
              </button>
            </div>

            {/* Live Validation Result Feedback */}
            {validationResult && (
              <div
                className={`p-3.5 rounded-lg border text-xs flex items-center gap-2.5 ${
                  validationResult.valid
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                }`}
              >
                {validationResult.valid ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                )}
                <span>{validationResult.message}</span>
              </div>
            )}
          </div>

          {/* Workflow Phases & Security Rules */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Phases */}
            <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted flex items-center gap-2">
                <Layers className="w-4 h-4 text-forge-primary" /> Standard Workflow Phases
              </h3>
              <ul className="space-y-2 text-xs font-mono">
                {skillInfo.phases.map((ph, idx) => (
                  <li
                    key={idx}
                    className="p-2 rounded bg-forge-elevated/40 border border-forge-border/40 text-forge-text flex items-center gap-2"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-forge-primary" />
                    {ph}
                  </li>
                ))}
              </ul>
            </div>

            {/* Security Boundaries */}
            <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400" /> Embedded Security Constraints
              </h3>
              <ul className="space-y-2 text-xs">
                {skillInfo.security_rules.map((rule, idx) => (
                  <li
                    key={idx}
                    className="p-2 rounded bg-forge-elevated/40 border border-forge-border/40 text-forge-muted flex items-start gap-2"
                  >
                    <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span className="text-forge-text">{rule}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Supporting Resources */}
          <div className="p-5 rounded-forge bg-forge-surface border border-forge-border space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-forge-muted flex items-center gap-2">
              <FileCode className="w-4 h-4 text-cyan-400" /> Supporting Resources in Package
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 font-mono text-xs">
              {skillInfo.supporting_resources.map((res, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-forge-bg border border-forge-border text-forge-text flex items-center gap-2 truncate"
                >
                  <FileCode className="w-3.5 h-3.5 text-forge-muted shrink-0" />
                  <span className="truncate">{res}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

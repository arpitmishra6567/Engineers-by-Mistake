import React from 'react';
import { CheckCircle2, Clock, AlertCircle, CircleDashed, ShieldAlert } from 'lucide-react';

interface Stage {
  key: string;
  label: string;
  description: string;
}

const PHASES: Stage[] = [
  { key: 'REPOSITORY_ANALYZED', label: '1. Repository Analysis', description: 'Structure and dependency mapping' },
  { key: 'ISSUE_UNDERSTOOD', label: '2. Issue Understanding', description: 'Specification and candidate location' },
  { key: 'REPRODUCED', label: '3. Bug Reproduction', description: 'Failure confirmation via test execution' },
  { key: 'ROOT_CAUSE_IDENTIFIED', label: '4. Root Cause Analysis', description: 'Defect diagnosis grounded in traces' },
  { key: 'PATCH_GENERATED', label: '5. Patch Generation', description: 'Minimal unified diff synthesis' },
  { key: 'PATCH_VALIDATED', label: '6. Patch Verification', description: 'AST checks and regression suites' },
  { key: 'HUMAN_REVIEW', label: '7. Human Review Gate', description: 'Evidence inspection & approval' },
];

interface RepairTimelineProps {
  currentState: string;
  status: string;
  history?: Array<{ to_state: string; timestamp: number; reason?: string | null }>;
}

export const RepairTimeline: React.FC<RepairTimelineProps> = ({ currentState, status, history = [] }) => {
  const completedStates = new Set(history.map((h) => h.to_state));
  if (status === 'VERIFIED' || status === 'COMPLETED') {
    PHASES.forEach((p) => completedStates.add(p.key));
  }

  const getStageStatus = (phase: Stage, index: number) => {
    if (completedStates.has(phase.key)) return 'completed';
    if (currentState === phase.key || (currentState === 'INITIALIZED' && index === 0)) return 'running';
    if (status === 'VALIDATION_FAILED' && phase.key === 'PATCH_VALIDATED') return 'failed';
    if (status === 'NOT_REPRODUCED' && phase.key === 'REPRODUCED') return 'failed';
    if (status === 'EXECUTION_BLOCKED' && currentState === phase.key) return 'blocked';
    return 'pending';
  };

  return (
    <div className="space-y-3">
      {PHASES.map((phase, idx) => {
        const stageStatus = getStageStatus(phase, idx);

        return (
          <div
            key={phase.key}
            className={`flex items-start gap-3.5 p-3 rounded-lg border transition-all ${
              stageStatus === 'completed'
                ? 'bg-emerald-500/5 border-emerald-500/20 text-forge-text'
                : stageStatus === 'running'
                ? 'bg-forge-primary/10 border-forge-primary/40 text-forge-text shadow-sm shadow-forge-primary/10'
                : stageStatus === 'failed'
                ? 'bg-rose-500/5 border-rose-500/30 text-rose-300'
                : stageStatus === 'blocked'
                ? 'bg-amber-500/5 border-amber-500/30 text-amber-300'
                : 'bg-forge-elevated/40 border-forge-border/40 text-forge-muted'
            }`}
          >
            <div className="mt-0.5 shrink-0">
              {stageStatus === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
              {stageStatus === 'running' && <Clock className="w-4 h-4 text-forge-primary animate-spin" />}
              {stageStatus === 'failed' && <AlertCircle className="w-4 h-4 text-rose-400" />}
              {stageStatus === 'blocked' && <ShieldAlert className="w-4 h-4 text-amber-400" />}
              {stageStatus === 'pending' && <CircleDashed className="w-4 h-4 text-forge-muted/60" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium tracking-tight truncate">{phase.label}</p>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded border border-forge-border/50 text-forge-muted">
                  {stageStatus}
                </span>
              </div>
              <p className="text-[11px] text-forge-muted mt-0.5 truncate">{phase.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};


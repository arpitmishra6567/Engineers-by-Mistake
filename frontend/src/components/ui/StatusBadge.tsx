import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = status?.toUpperCase() || 'UNKNOWN';

  let bg = 'bg-forge-elevated text-forge-muted border-forge-border';
  let dot = 'bg-forge-muted';

  if (norm === 'VERIFIED' || norm === 'COMPLETED' || norm === 'PASSED') {
    bg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    dot = 'bg-emerald-400';
  } else if (norm === 'RUNNING' || norm === 'IN_PROGRESS') {
    bg = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    dot = 'bg-cyan-400 animate-pulse';
  } else if (norm === 'VALIDATION_FAILED' || norm === 'FAILED' || norm === 'PATCH_GENERATION_FAILED') {
    bg = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    dot = 'bg-rose-400';
  } else if (norm === 'NOT_REPRODUCED') {
    bg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    dot = 'bg-amber-400';
  } else if (norm === 'EXECUTION_BLOCKED' || norm === 'BLOCKED') {
    bg = 'bg-red-500/10 text-red-400 border-red-500/30';
    dot = 'bg-red-400';
  } else if (norm === 'PATCH_GENERATED' || norm === 'PATCH_GENERATED_UNVERIFIED') {
    bg = 'bg-violet-500/10 text-violet-400 border-violet-500/30';
    dot = 'bg-violet-400';
  } else if (norm === 'HUMAN_REVIEW') {
    bg = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
    dot = 'bg-indigo-400 animate-pulse';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-2',
    lg: 'text-sm px-3 py-1.5 gap-2',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-mono font-medium rounded-full border ${bg} ${sizeClasses}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      {norm}
    </span>
  );
};


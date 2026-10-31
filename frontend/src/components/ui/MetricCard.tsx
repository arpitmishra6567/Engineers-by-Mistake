import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: string;
  trendPositive?: boolean;
  highlight?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendPositive,
  highlight = false,
}) => {
  return (
    <div
      className={`rounded-forge p-5 border transition-all ${
        highlight
          ? 'bg-forge-surface border-forge-primary/40 shadow-lg shadow-forge-primary/5'
          : 'bg-forge-surface border-forge-border hover:border-forge-border/80'
      }`}
    >
      <div className="flex items-center justify-between text-forge-muted mb-2">
        <span className="text-xs font-medium uppercase tracking-wider">{title}</span>
        {Icon && <Icon className="w-4 h-4 text-forge-muted" />}
      </div>
      <div className="flex items-baseline gap-3">
        <span className="text-2xl font-bold font-mono tracking-tight text-forge-text">
          {value}
        </span>
        {trend && (
          <span
            className={`text-xs font-mono font-medium ${
              trendPositive ? 'text-emerald-400' : 'text-forge-muted'
            }`}
          >
            {trend}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-forge-muted mt-1.5">{subtitle}</p>}
    </div>
  );
};


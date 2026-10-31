import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = Inbox,
  actionText,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-forge-border rounded-forge bg-forge-surface/40">
      <div className="w-12 h-12 rounded-full bg-forge-elevated flex items-center justify-center mb-4 text-forge-muted">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-forge-text mb-1">{title}</h3>
      <p className="text-xs text-forge-muted max-w-sm mb-4">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-3.5 py-1.5 rounded-lg bg-forge-primary hover:bg-forge-primary/90 text-white text-xs font-medium transition-colors shadow-sm"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};


import React from 'react';

export const LoadingSkeleton: React.FC<{ rows?: number }> = ({ rows = 4 }) => {
  return (
    <div className="space-y-3 animate-pulse">
      <div className="h-4 bg-forge-elevated rounded w-1/3" />
      <div className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-10 bg-forge-elevated/60 rounded w-full" />
        ))}
      </div>
    </div>
  );
};


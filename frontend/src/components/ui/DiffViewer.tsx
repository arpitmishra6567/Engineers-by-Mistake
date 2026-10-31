import React, { useState } from 'react';
import { Copy, Check, FileCode, Split, AlignJustify } from 'lucide-react';

interface DiffViewerProps {
  diffText: string;
  filePath?: string;
  title?: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ diffText, filePath = 'patch.diff', title }) => {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'unified' | 'split'>('unified');

  const handleCopy = () => {
    navigator.clipboard.writeText(diffText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = diffText.trim().split('\n');

  return (
    <div className="bg-forge-bg border border-forge-border rounded-forge overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-forge-surface border-b border-forge-border">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-forge-primary" />
          <span className="font-mono text-xs font-semibold text-forge-text">{filePath}</span>
          {title && <span className="text-xs text-forge-muted font-normal">({title})</span>}
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-forge-elevated border border-forge-border rounded p-0.5 text-xs text-forge-muted">
            <button
              onClick={() => setViewMode('unified')}
              className={`p-1 px-2 rounded flex items-center gap-1 text-[11px] ${
                viewMode === 'unified' ? 'bg-forge-surface text-forge-text font-medium' : 'hover:text-forge-text'
              }`}
            >
              <AlignJustify className="w-3 h-3" /> Unified
            </button>
            <button
              onClick={() => setViewMode('split')}
              className={`p-1 px-2 rounded flex items-center gap-1 text-[11px] ${
                viewMode === 'split' ? 'bg-forge-surface text-forge-text font-medium' : 'hover:text-forge-text'
              }`}
            >
              <Split className="w-3 h-3" /> Split
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-forge-elevated border border-forge-border text-xs text-forge-muted hover:text-forge-text transition-colors"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            <span className="text-[11px]">{copied ? 'Copied' : 'Copy Diff'}</span>
          </button>
        </div>
      </div>

      {/* Code Area */}
      <div className="overflow-x-auto p-4 font-mono text-[12px] leading-relaxed">
        {lines.map((line, idx) => {
          let rowStyle = 'text-forge-muted';

          if (line.startsWith('+') && !line.startsWith('+++')) {
            rowStyle = 'bg-emerald-950/40 text-emerald-300 font-medium';
          } else if (line.startsWith('-') && !line.startsWith('---')) {
            rowStyle = 'bg-rose-950/40 text-rose-300 font-medium';
          } else if (line.startsWith('@@')) {
            rowStyle = 'text-cyan-400/90 bg-cyan-950/20 font-bold';
          } else if (line.startsWith('---') || line.startsWith('+++')) {
            rowStyle = 'text-forge-muted font-bold';
          }

          return (
            <div key={idx} className={`flex items-start px-2 py-0.5 rounded-sm ${rowStyle}`}>
              <span className="w-8 shrink-0 text-right pr-3 select-none text-[10px] text-forge-muted/50">
                {idx + 1}
              </span>
              <span className="w-4 shrink-0 select-none text-center font-bold">{line[0] || ' '}</span>
              <span className="whitespace-pre flex-1">{line.slice(1) || ' '}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

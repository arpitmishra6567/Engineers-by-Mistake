import React, { useState, useEffect, useRef } from 'react';
import { Copy, Pause, Play, Search, Check } from 'lucide-react';
import { LogEntry } from '../../api/types';

interface ExecutionLogProps {
  logs: LogEntry[];
  title?: string;
  isLive?: boolean;
}

export const ExecutionLog: React.FC<ExecutionLogProps> = ({ logs, title = 'Technical Execution Log', isLive = false }) => {
  const [autoScroll, setAutoScroll] = useState(true);
  const [filter, setFilter] = useState('');
  const [copied, setCopied] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const filteredLogs = logs.filter(
    (l) =>
      l.message.toLowerCase().includes(filter.toLowerCase()) ||
      l.stage.toLowerCase().includes(filter.toLowerCase()) ||
      l.level.toLowerCase().includes(filter.toLowerCase())
  );

  const handleCopy = () => {
    const text = logs
      .map((l) => `[${new Date(l.timestamp * 1000).toISOString().split('T')[1].slice(0, 8)}] [${l.level}] [${l.stage}] ${l.message}`)
      .join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-forge-bg border border-forge-border rounded-forge overflow-hidden">
      {/* Log Header Controls */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-forge-surface border-b border-forge-border text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-forge-text">{title}</span>
          {isLive && (
            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
              LIVE STREAM
            </span>
          )}
          <span className="text-forge-muted font-mono">({filteredLogs.length} events)</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2 top-1.5 text-forge-muted" />
            <input
              type="text"
              placeholder="Search logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-forge-elevated border border-forge-border rounded px-2 py-1 pl-7 text-[11px] text-forge-text focus:outline-none focus:border-forge-primary placeholder:text-forge-muted"
            />
          </div>

          {/* Pause / Auto-scroll toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`p-1.5 rounded border text-xs transition-colors ${
              autoScroll
                ? 'bg-forge-primary/10 border-forge-primary/30 text-forge-primary'
                : 'bg-forge-elevated border-forge-border text-forge-muted hover:text-forge-text'
            }`}
            title={autoScroll ? 'Pause auto-scroll' : 'Resume auto-scroll'}
          >
            {autoScroll ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          </button>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 p-1.5 px-2 rounded border border-forge-border bg-forge-elevated text-forge-muted hover:text-forge-text text-xs"
            title="Copy logs to clipboard"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span className="text-[11px]">{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Log Feed */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-1.5 font-mono text-[11px] leading-relaxed selection:bg-forge-primary/30"
      >
        {filteredLogs.length === 0 ? (
          <div className="text-center py-12 text-forge-muted">
            No execution events recorded yet.
          </div>
        ) : (
          filteredLogs.map((log, index) => {
            const timeStr = new Date(log.timestamp * 1000).toLocaleTimeString();
            const isError = log.level === 'ERROR';
            const isWarn = log.level === 'WARNING';

            return (
              <div
                key={index}
                className={`flex items-start gap-2.5 py-0.5 rounded px-1.5 ${
                  isError ? 'bg-rose-500/10 text-rose-300' : isWarn ? 'bg-amber-500/10 text-amber-300' : 'hover:bg-forge-elevated/40'
                }`}
              >
                <span className="text-forge-muted shrink-0 text-[10px]">{timeStr}</span>
                <span
                  className={`px-1 py-0.2 rounded text-[9px] shrink-0 font-bold ${
                    isError
                      ? 'bg-rose-500/20 text-rose-400'
                      : isWarn
                      ? 'bg-amber-500/20 text-amber-400'
                      : 'bg-forge-elevated text-forge-muted'
                  }`}
                >
                  {log.level}
                </span>
                <span className="text-cyan-400/80 shrink-0 text-[10px] max-w-[120px] truncate">
                  [{log.stage}]
                </span>
                <span className="text-forge-text whitespace-pre-wrap break-all">{log.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};


import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  PlayCircle,
  GitPullRequest,
  CheckCircle,
  BarChart3,
  Cpu,
  FolderGit2,
  Settings,
  Search,
  X,
} from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        onClose();
      }
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  const commands = [
    { name: 'Overview Dashboard', path: '/', icon: LayoutDashboard, category: 'Navigation' },
    { name: 'Start New Repair', path: '/new', icon: PlusCircle, category: 'Action' },
    { name: 'Live Execution Workspace', path: '/execution', icon: PlayCircle, category: 'Navigation' },
    { name: 'Patch Review (Code Diff)', path: '/patch-review', icon: GitPullRequest, category: 'Navigation' },
    { name: 'Verification Center', path: '/verification', icon: CheckCircle, category: 'Navigation' },
    { name: 'Model Evaluations (Kaggle Qwen)', path: '/evaluations', icon: BarChart3, category: 'Navigation' },
    { name: 'Models & Agent Skills', path: '/models-skills', icon: Cpu, category: 'Navigation' },
    { name: 'Repository Explorer', path: '/repositories', icon: FolderGit2, category: 'Navigation' },
    { name: 'System Settings', path: '/settings', icon: Settings, category: 'Navigation' },
  ];

  const filtered = commands.filter((c) =>
    c.name.toLowerCase().includes(query.toLowerCase()) || c.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-24 px-4 animate-in fade-in duration-100">
      <div className="w-full max-w-xl bg-forge-surface border border-forge-border rounded-forge shadow-2xl overflow-hidden">
        {/* Input bar */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-forge-border">
          <Search className="w-4 h-4 text-forge-muted shrink-0" />
          <input
            type="text"
            placeholder="Type a command or navigate... (e.g. 'new', 'patch')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="w-full bg-transparent text-sm text-forge-text placeholder:text-forge-muted focus:outline-none"
          />
          <button onClick={onClose} className="p-1 rounded text-forge-muted hover:text-forge-text">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-72 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-xs text-forge-muted">No commands matching "{query}"</div>
          ) : (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    navigate(item.path);
                    onClose();
                  }}
                  className="w-full flex items-center justify-between p-2.5 rounded-lg hover:bg-forge-elevated text-left transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-forge-muted group-hover:text-forge-primary" />
                    <span className="text-xs font-medium text-forge-text">{item.name}</span>
                  </div>
                  <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-forge-elevated text-forge-muted">
                    {item.category}
                  </span>
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-2 bg-forge-bg/60 border-t border-forge-border text-[11px] text-forge-muted">
          <span>Navigate with mouse or arrow keys</span>
          <span className="font-mono">ESC to exit</span>
        </div>
      </div>
    </div>
  );
};


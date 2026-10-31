import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Sun, Moon, Bell, Plus, GitBranch } from 'lucide-react';

interface TopbarProps {
  onOpenCommandPalette: () => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onOpenCommandPalette, theme, onToggleTheme }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const getBreadcrumbs = () => {
    const path = location.pathname;
    if (path === '/') return 'Overview';
    if (path.startsWith('/new')) return 'New Repair';
    if (path.startsWith('/execution')) return 'Live Execution';
    if (path.startsWith('/patch-review')) return 'Patch Review';
    if (path.startsWith('/verification')) return 'Verification Center';
    if (path.startsWith('/evaluations')) return 'Model Evaluations';
    if (path.startsWith('/models-skills')) return 'Models & Skills';
    if (path.startsWith('/repositories')) return 'Repository Explorer';
    if (path.startsWith('/settings')) return 'Settings';
    return 'Dashboard';
  };

  return (
    <header className="h-14 bg-forge-surface border-b border-forge-border px-6 flex items-center justify-between z-20">
      {/* Left: Breadcrumbs & Workspace Selector */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs">
          <span className="text-forge-muted">Forge Command</span>
          <span className="text-forge-muted">/</span>
          <span className="font-semibold text-forge-text">{getBreadcrumbs()}</span>
        </div>

        {/* Workspace Pill */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-forge-elevated border border-forge-border text-xs text-forge-muted">
          <GitBranch className="w-3 h-3 text-cyan-400" />
          <span className="font-mono text-[11px] text-forge-text">Engineers-by-Mistake:main</span>
        </div>
      </div>

      {/* Right: Search, Quick Action, Theme & Notifications */}
      <div className="flex items-center gap-3">
        {/* Command Palette Trigger */}
        <button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-forge-elevated border border-forge-border text-xs text-forge-muted hover:text-forge-text hover:border-forge-border/80 transition-colors"
        >
          <Search className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Search or command...</span>
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-forge-bg text-[10px] font-mono border border-forge-border text-forge-muted">
            Ctrl+K
          </kbd>
        </button>

        {/* Start Repair CTA */}
        <button
          onClick={() => navigate('/new')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-forge-primary hover:bg-forge-primary/90 text-white text-xs font-medium transition-colors shadow-sm"
        >
          <Plus className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">New Repair</span>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={onToggleTheme}
          className="p-2 rounded-lg bg-forge-elevated border border-forge-border text-forge-muted hover:text-forge-text transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-400" />}
        </button>

        {/* Notifications (Functional state) */}
        <div className="relative">
          <button
            className="p-2 rounded-lg bg-forge-elevated border border-forge-border text-forge-muted hover:text-forge-text transition-colors"
            title="Notifications: All systems operational"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-emerald-400" />
          </button>
        </div>
      </div>
    </header>
  );
};


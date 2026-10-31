import React from 'react';
import { NavLink } from 'react-router-dom';
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
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  Wrench,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => {
  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'New Repair', path: '/new', icon: PlusCircle },
    { name: 'Live Execution', path: '/execution', icon: PlayCircle },
    { name: 'Patch Review', path: '/patch-review', icon: GitPullRequest },
    { name: 'Verification', path: '/verification', icon: CheckCircle },
    { name: 'Evaluations', path: '/evaluations', icon: BarChart3 },
    { name: 'Models & Skills', path: '/models-skills', icon: Cpu },
    { name: 'Repositories', path: '/repositories', icon: FolderGit2 },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside
      className={`relative flex flex-col bg-forge-sidebar border-r border-forge-border transition-all duration-200 z-30 select-none ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-4 py-4 border-b border-forge-border">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-forge-primary to-indigo-700 flex items-center justify-center shrink-0 shadow-md shadow-forge-primary/20">
          <Wrench className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0 flex-1">
            <h1 className="text-sm font-bold tracking-tight text-forge-text truncate">Forge Command</h1>
            <p className="text-[10px] text-forge-muted truncate">RepairForge AI Harness</p>
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-2 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              title={collapsed ? item.name : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-forge-primary/15 text-forge-primary border border-forge-primary/30 shadow-sm'
                    : 'text-forge-muted hover:text-forge-text hover:bg-forge-elevated/60'
                } ${collapsed ? 'justify-center px-0' : ''}`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span className="truncate">{item.name}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Metadata & Controls */}
      <div className="p-3 border-t border-forge-border space-y-2 bg-forge-sidebar/50">
        {!collapsed && (
          <div className="p-2.5 rounded-lg bg-forge-elevated/40 border border-forge-border/60 text-[11px] space-y-1.5">
            <div className="flex items-center justify-between text-forge-muted">
              <span>Mode</span>
              <span className="font-mono text-cyan-400 font-semibold flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-cyan-400" /> SAFE_FIXTURE
              </span>
            </div>
            <div className="flex items-center justify-between text-forge-muted">
              <span>Provider</span>
              <span className="font-mono text-forge-text">MockModel</span>
            </div>
            <div className="flex items-center justify-between text-forge-muted pt-1 border-t border-forge-border/40">
              <span>Version</span>
              <span className="font-mono text-forge-muted">v0.1.0</span>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between gap-1">
          <a
            href="https://github.com/arpitmishra6567/Engineers-by-Mistake"
            target="_blank"
            rel="noopener noreferrer"
            title="GitHub Repository"
            className="p-1.5 rounded-lg text-forge-muted hover:text-forge-text hover:bg-forge-elevated transition-colors text-xs flex items-center gap-1.5"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            {!collapsed && <span className="text-[11px]">GitHub</span>}
          </a>

          <button
            onClick={onToggleCollapse}
            className="p-1.5 rounded-lg text-forge-muted hover:text-forge-text hover:bg-forge-elevated transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </aside>
  );
};


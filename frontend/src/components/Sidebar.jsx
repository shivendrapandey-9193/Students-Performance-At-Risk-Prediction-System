import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { 
  Users, 
  BrainCircuit, 
  ExternalLink,
  GraduationCap
} from 'lucide-react';

export default function Sidebar({ mobileOpen, setMobileOpen }) {
  // Exactly two main application sections
  const navItems = [
    {
      name: 'Student Analysis',
      path: '/app/student-analysis',
      icon: Users,
      description: 'Individual & batch cohort screening'
    },
    {
      name: 'Model Insights',
      path: '/app/model-insights',
      icon: BrainCircuit,
      description: 'Performance metrics & explainability'
    }
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside className={`
        fixed top-0 bottom-0 left-0 z-50 w-64 bg-[#111827] border-r border-slate-800 flex flex-col justify-between
        transition-transform duration-300 ease-in-out
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Brand Logo & Title */}
        <div>
          <div className="h-16 flex items-center px-6 border-b border-slate-800">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/20 transition">
                <GraduationCap className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-white text-base tracking-tight flex items-center gap-1.5">
                  Insight AI
                  <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    SaaS
                  </span>
                </span>
                <span className="block text-[11px] text-slate-400 font-normal">Academic Analytics</span>
              </div>
            </Link>
          </div>

          {/* Navigation Links (Exactly 2 items) */}
          <nav className="p-4 space-y-1.5">
            <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              Application Workspace
            </div>
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) => `
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition
                  ${isActive 
                    ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-sm' 
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }
                `}
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <div className="flex-1 truncate">
                  <div className="text-sm font-medium">{item.name}</div>
                  <div className="text-[11px] text-slate-400 truncate">{item.description}</div>
                </div>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Model Status & Footer */}
        <div className="p-4 border-t border-slate-800 space-y-3">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800/80 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Engine Active
              </span>
              <span className="text-[10px] font-mono text-slate-400">RF-Recall</span>
            </div>
            <div className="text-[11px] text-slate-300 font-mono flex justify-between">
              <span className="text-slate-400">Decision Cutoff:</span>
              <span className="text-blue-400 font-medium">0.2457</span>
            </div>
            <div className="text-[11px] text-slate-300 font-mono flex justify-between">
              <span className="text-slate-400">Target Recall:</span>
              <span className="text-emerald-400 font-medium">63.52%</span>
            </div>
          </div>

          <Link
            to="/"
            className="flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition border border-transparent hover:border-slate-700"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Public Welcome Page</span>
          </Link>
        </div>
      </aside>
    </>
  );
}

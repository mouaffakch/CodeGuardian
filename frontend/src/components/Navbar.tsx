import React from 'react';
import { Shield, Play, Terminal, GitBranch, History, AlertTriangle, Layers, Flame } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenScanModal: () => void;
  onOpenCiCdModal: () => void;
  currentBranch?: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenScanModal,
  onOpenCiCdModal,
  currentBranch = 'main'
}) => {
  const tabs = [
    { id: 'dashboard', label: 'Vue d\'ensemble', icon: Shield },
    { id: 'defects', label: 'Bugs & Vulnérabilités', icon: AlertTriangle },
    { id: 'hotspots', label: 'Prédiction des Risques (IA)', icon: Flame },
    { id: 'duplications', label: 'Duplications de Code', icon: Layers },
    { id: 'history', label: 'Historique des Analyses', icon: History },
  ];

  return (
    <header className="border-b border-white/[0.08] bg-[#070b16]/80 backdrop-blur-2xl sticky top-0 z-40 shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3.5">
            <div className="relative group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-cyan-500/25 ring-1 ring-white/20">
                <Shield className="w-5 h-5 text-[#060913] stroke-[2.5]" />
              </div>
              <div className="absolute -inset-1 bg-cyan-500/20 rounded-xl blur-md -z-10 group-hover:bg-cyan-500/40 transition" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                  CodeGuardian
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/20">
                  IA & Static
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Détection intelligente des défauts logiciels</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex space-x-1 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06] backdrop-blur-md">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/20 to-emerald-500/10 text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-slate-300 shadow-inner">
              <GitBranch className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-mono text-[11px] text-emerald-300">{currentBranch}</span>
            </div>

            <button
              onClick={onOpenCiCdModal}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-300 bg-white/[0.04] hover:bg-white/[0.08] hover:text-white border border-white/[0.08] hover:border-cyan-500/30 transition flex items-center space-x-1.5 shadow-sm active:scale-95"
            >
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>CI/CD & CLI</span>
            </button>

            <button
              onClick={onOpenScanModal}
              className="relative group flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 shadow-[0_0_20px_rgba(6,182,212,0.35)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)] transition active:scale-95"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Lancer un Scan</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};

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
    <header className="border-b border-slate-800 bg-[#0c1322]/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-400 bg-clip-text text-transparent">
                  CodeGuardian
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                  IA & Static
                </span>
              </div>
              <p className="text-xs text-slate-400">Détection intelligente des défauts logiciels</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700 text-xs text-slate-300">
              <GitBranch className="w-3.5 h-3.5 text-emerald-400" />
              <span>{currentBranch}</span>
            </div>

            <button
              onClick={onOpenCiCdModal}
              className="px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 transition flex items-center space-x-1.5"
            >
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>CI/CD & CLI</span>
            </button>

            <button
              onClick={onOpenScanModal}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold text-white bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 shadow-lg shadow-cyan-500/25 transition active:scale-95"
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

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
    { id: 'defects', label: 'Défauts & Sécurité', icon: AlertTriangle },
    { id: 'hotspots', label: 'Analyse Prédictive', icon: Flame },
    { id: 'duplications', label: 'Duplications', icon: Layers },
    { id: 'history', label: 'Historique', icon: History },
  ];

  return (
    <header className="border-b border-white/[0.07] bg-[#060a16]/80 backdrop-blur-2xl sticky top-0 z-40 shadow-[0_4px_30px_rgba(0,0,0,0.4)]">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10">
        <div className="flex items-center justify-between h-20">
          
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-cyan-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-cyan-500/20 ring-1 ring-white/15">
              <Shield className="w-5 h-5 text-[#050811] stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <span className="text-xl font-bold tracking-tight text-white font-['Plus_Jakarta_Sans',sans-serif]">
                  CodeGuardian
                </span>
              </div>
              <p className="text-xs text-slate-400 font-normal">Analyse statique & audit de conformité logicielle</p>
            </div>
          </div>

          <nav className="hidden lg:flex items-center space-x-1.5 p-1.5 bg-white/[0.03] rounded-2xl border border-white/[0.06] backdrop-blur-xl">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2.5 px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/20 via-cyan-500/15 to-emerald-500/10 text-cyan-300 border border-cyan-500/35 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="flex items-center space-x-3.5">
            <button
              onClick={onOpenCiCdModal}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 hover:text-white bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] hover:border-cyan-500/30 transition flex items-center space-x-2 shadow-sm active:scale-95"
            >
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>CI/CD & CLI</span>
            </button>

            <button
              onClick={onOpenScanModal}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-cyan-600 via-cyan-500 to-emerald-500 hover:from-cyan-500 hover:to-emerald-400 shadow-lg shadow-cyan-500/25 transition active:scale-95"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Lancer un Scan</span>
            </button>
          </div>

        </div>

        <div className="lg:hidden flex items-center justify-between pb-3 pt-1 border-t border-white/[0.05] overflow-x-auto space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap ${
                  isActive ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

      </div>
    </header>
  );
};

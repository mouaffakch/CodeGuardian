import React from 'react';
import { ShieldAlert, AlertOctagon, Flame, Copy, FileCode2, CheckCircle2 } from 'lucide-react';

interface MetricCardsProps {
  healthScore: number;
  totalIssues: number;
  criticalBugs: number;
  highBugs: number;
  duplicationPercentage: number;
  highRiskFiles: number;
  loc?: number;
  totalFiles?: number;
}

export const MetricCards: React.FC<MetricCardsProps> = ({
  healthScore,
  totalIssues,
  criticalBugs,
  highBugs,
  duplicationPercentage,
  highRiskFiles,
  loc = 0,
  totalFiles = 0,
}) => {
  const getHealthBadge = (score: number) => {
    if (score >= 80) return { label: 'Excellent', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' };
    if (score >= 60) return { label: 'Modéré', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30' };
    return { label: 'Critique', color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/30' };
  };

  const health = getHealthBadge(healthScore);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      {/* Health Score Card */}
      <div className="glass-panel rounded-2xl p-5 relative overflow-hidden transition-all duration-300 group">
        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl -z-10 group-hover:bg-emerald-500/20 transition" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Score de Santé Global</span>
          <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${health.bg} ${health.color} border ${health.border}`}>
            {health.label}
          </span>
        </div>
        <div className="mt-3 flex items-baseline space-x-2">
          <span className={`text-4xl font-black ${health.color} tracking-tight`}>
            {healthScore.toFixed(0)}
          </span>
          <span className="text-slate-500 text-sm font-medium">/ 100</span>
        </div>
        <div className="mt-3 w-full bg-slate-950/70 rounded-full h-2 overflow-hidden border border-white/[0.05]">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              healthScore >= 80 ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : healthScore >= 60 ? 'bg-gradient-to-r from-amber-500 to-yellow-400' : 'bg-gradient-to-r from-rose-500 to-red-400'
            }`}
            style={{ width: `${Math.max(5, healthScore)}%` }}
          />
        </div>
      </div>

      {/* Critical & High Defects */}
      <div className="glass-panel rounded-2xl p-5 relative overflow-hidden transition-all duration-300 group">
        <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/10 rounded-full blur-2xl -z-10 group-hover:bg-rose-500/20 transition" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Défauts & Vulnérabilités</span>
          <AlertOctagon className="w-4 h-4 text-rose-400" />
        </div>
        <div className="mt-3 flex items-baseline space-x-3">
          <span className="text-4xl font-black text-rose-400 tracking-tight">{criticalBugs}</span>
          <span className="text-xs text-rose-300 font-semibold uppercase tracking-wider">Critiques</span>
          <span className="text-2xl font-bold text-amber-400">{highBugs}</span>
          <span className="text-xs text-amber-300 font-medium uppercase tracking-wider">Hauts</span>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Total de <strong className="text-slate-200">{totalIssues}</strong> anomalies détectées
        </p>
      </div>

      {/* Hotspot & Predictive Risk */}
      <div className="glass-panel rounded-2xl p-5 relative overflow-hidden transition-all duration-300 group">
        <div className="absolute top-0 right-0 w-24 h-24 bg-orange-500/10 rounded-full blur-2xl -z-10 group-hover:bg-orange-500/20 transition" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Fichiers à Haut Risque (IA)</span>
          <Flame className="w-4 h-4 text-orange-400" />
        </div>
        <div className="mt-3 flex items-baseline space-x-2">
          <span className="text-4xl font-black text-orange-400 tracking-tight">{highRiskFiles}</span>
          <span className="text-xs text-slate-400 font-medium">points chauds identifiés</span>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Fichiers les plus susceptibles de provoquer un incident en production
        </p>
      </div>

      {/* Duplication & Codebase Volume */}
      <div className="glass-panel rounded-2xl p-5 relative overflow-hidden transition-all duration-300 group">
        <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl -z-10 group-hover:bg-cyan-500/20 transition" />
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Taux de Duplication</span>
          <Copy className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="mt-3 flex items-baseline space-x-2">
          <span className={`text-4xl font-black tracking-tight ${duplicationPercentage > 10 ? 'text-amber-400' : 'text-cyan-400'}`}>
            {duplicationPercentage.toFixed(1)}%
          </span>
          <span className="text-xs text-slate-400">de clones</span>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          {totalFiles} fichiers analysés ({loc.toLocaleString()} lignes de code)
        </p>
      </div>

    </div>
  );
};

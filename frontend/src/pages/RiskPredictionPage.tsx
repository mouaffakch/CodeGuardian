import React from 'react';
import { HotspotRisk } from '../api/client';
import { Flame, GitCommit, GitPullRequest, Wrench, AlertTriangle, ShieldCheck, TrendingUp } from 'lucide-react';

interface RiskPredictionPageProps {
  hotspots: HotspotRisk[];
}

export const RiskPredictionPage: React.FC<RiskPredictionPageProps> = ({ hotspots }) => {
  return (
    <div className="space-y-6">
      
      <div className="bg-gradient-to-r from-orange-950/40 via-slate-900 to-rose-950/30 border border-orange-800/40 rounded-2xl p-6">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-9 h-9 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center">
            <Flame className="w-5 h-5 text-orange-400" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Prédiction des Risques & Hotspots de Bugs</h2>
            <p className="text-xs text-slate-300">
              Modèle combinant l'historique Git (churn, récurrence des correctifs) et la complexité statique (CC, MI).
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {hotspots.map((hotspot, idx) => {
          const isCritical = hotspot.risk_level === 'CRITICAL';
          const isHigh = hotspot.risk_level === 'HIGH';
          const isMedium = hotspot.risk_level === 'MEDIUM';

          const riskBadgeColor = isCritical
            ? 'bg-rose-500/20 text-rose-400 border-rose-500/40'
            : isHigh
            ? 'bg-orange-500/20 text-orange-400 border-orange-500/40'
            : isMedium
            ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
            : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';

          return (
            <div
              key={hotspot.id || idx}
              className="glass-panel hover:bg-slate-900/80 rounded-2xl p-5 space-y-4 transition-all duration-300"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono text-cyan-400 block font-bold truncate max-w-[280px]" title={hotspot.file_path}>
                    {hotspot.file_path}
                  </span>
                  <span className="text-[11px] text-slate-400">
                    Rang #{idx + 1} de susceptibilité aux défauts
                  </span>
                </div>

                <div className="text-right">
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${riskBadgeColor}`}>
                    {hotspot.risk_level} ({hotspot.risk_score}%)
                  </span>
                </div>
              </div>

              <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    isCritical
                      ? 'bg-gradient-to-r from-orange-500 to-rose-500'
                      : isHigh
                      ? 'bg-orange-500'
                      : isMedium
                      ? 'bg-amber-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.max(5, hotspot.risk_score)}%` }}
                />
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 flex items-center space-x-2">
                  <GitCommit className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-400 block">Activité Git (Churn)</span>
                    <span className="font-semibold text-slate-200">
                      {hotspot.commit_count} commits ({hotspot.churn_lines} lignes)
                    </span>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 flex items-center space-x-2">
                  <TrendingUp className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-400 block">Historique Bug-Fixes</span>
                    <span className="font-semibold text-slate-200">
                      {hotspot.bug_fix_count} correctifs passés
                    </span>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 flex items-center space-x-2">
                  <Wrench className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-400 block">Complexité Cyclomatique</span>
                    <span className="font-semibold text-slate-200">CC = {hotspot.cyclomatic_complexity}</span>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 flex items-center space-x-2">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-400 block">Index Maintenabilité (MI)</span>
                    <span className="font-semibold text-slate-200">{hotspot.maintainability_index} / 100</span>
                  </div>
                </div>
              </div>

              {hotspot.reasons && hotspot.reasons.length > 0 && (
                <div className="pt-2 border-t border-slate-800/70">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Facteurs Déclencheurs de Risque :
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {hotspot.reasons.map((reason, i) => (
                      <span
                        key={i}
                        className="text-[11px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700"
                      >
                        • {reason}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {hotspots.length === 0 && (
          <div className="col-span-2 p-12 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
            Aucun fichier analysé pour les prédictions de risque.
          </div>
        )}
      </div>

    </div>
  );
};

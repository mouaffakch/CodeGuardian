import React from 'react';
import { MetricCards } from '../components/MetricCards';
import { AnalysisRun, DashboardStats, Defect } from '../api/client';
import { ShieldCheck, AlertCircle, ArrowUpRight, Flame, Layers, FileCode, CheckCircle, Terminal } from 'lucide-react';

interface DashboardPageProps {
  stats: DashboardStats | null;
  latestRun: AnalysisRun | null;
  onSelectDefect: (defect: Defect) => void;
  onNavigateTab: (tab: string) => void;
  onOpenScanModal: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  stats,
  latestRun,
  onSelectDefect,
  onNavigateTab,
  onOpenScanModal,
}) => {
  if (!latestRun) {
    return (
      <div className="py-16 text-center">
        <div className="w-16 h-16 rounded-2xl bg-cyan-950 border border-cyan-800 flex items-center justify-center mx-auto mb-4">
          <Terminal className="w-8 h-8 text-cyan-400" />
        </div>
        <h3 className="text-xl font-bold text-white">Aucune analyse effectuée pour l'instant</h3>
        <p className="mt-2 text-sm text-slate-400 max-w-md mx-auto">
          Lancez une première analyse statique pour inspecter les bugs, détecter les clones et calculer les risques de régression.
        </p>
        <button
          onClick={onOpenScanModal}
          className="mt-6 px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 font-bold text-white text-xs rounded-xl shadow-lg shadow-cyan-500/25 transition active:scale-95"
        >
          Lancer une première analyse
        </button>
      </div>
    );
  }

  const criticalAndHighDefects = (latestRun.defects || []).filter(
    (d) => d.severity === 'CRITICAL' || d.severity === 'HIGH'
  );

  return (
    <div className="space-y-8">
      {/* Metrics Row */}
      <MetricCards
        healthScore={latestRun.health_score}
        totalIssues={latestRun.total_issues}
        criticalBugs={latestRun.critical_count}
        highBugs={latestRun.high_count}
        duplicationPercentage={latestRun.duplication_percentage}
        highRiskFiles={stats?.high_risk_files_count || (latestRun.hotspots || []).filter(h => h.risk_level === 'CRITICAL' || h.risk_level === 'HIGH').length}
        loc={latestRun.lines_of_code}
        totalFiles={latestRun.total_files}
      />

      {/* Main Grid: Critical Issues & Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Top Priority Defects */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">Défauts Prioritaires à Corriger</h3>
              <p className="text-xs text-slate-400">Failles de sécurité, bugs potentiels et anomalies critiques</p>
            </div>
            <button
              onClick={() => onNavigateTab('defects')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1"
            >
              <span>Voir tout ({latestRun.total_issues})</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {criticalAndHighDefects.slice(0, 5).map((defect) => (
              <div
                key={defect.id || `${defect.file_path}-${defect.line_number}`}
                onClick={() => onSelectDefect(defect)}
                className="group p-3.5 rounded-xl bg-slate-950/50 border border-white/[0.06] hover:border-cyan-500/40 hover:bg-white/[0.04] cursor-pointer transition flex items-start justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        defect.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                      }`}
                    >
                      {defect.severity}
                    </span>
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition">
                      {defect.title}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-1">{defect.description}</p>
                  <p className="text-[11px] font-mono text-slate-500">
                    {defect.file_path}:{defect.line_number}
                  </p>
                </div>

                <div className="text-right">
                  <span className="text-[11px] font-bold text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-md border border-cyan-800/50 group-hover:bg-cyan-500 group-hover:text-black transition shadow-sm">
                    Détails & Correctif →
                  </span>
                </div>
              </div>
            ))}

            {criticalAndHighDefects.length === 0 && (
              <div className="py-8 text-center text-xs text-emerald-400 flex items-center justify-center space-x-2">
                <CheckCircle className="w-4 h-4" />
                <span>Aucune anomalie critique ou haute détectée dans ce scan !</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Predictive Hotspots & Breakdown */}
        <div className="space-y-6">
          
          {/* Top Predictive Hotspots Card */}
          <div className="glass-panel rounded-2xl p-6 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Flame className="w-4 h-4 text-orange-400" />
                <h3 className="text-sm font-bold text-white tracking-tight">Analyse Prédictive des Risques</h3>
              </div>
              <button
                onClick={() => onNavigateTab('hotspots')}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1"
              >
                <span>Détails</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-3">
              {(latestRun.hotspots || []).slice(0, 4).map((h, i) => (
                <div key={i} className="p-3 bg-slate-950/50 rounded-xl border border-white/[0.05]">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-300 truncate max-w-[170px]" title={h.file_path}>
                      {h.file_path}
                    </span>
                    <span
                      className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                        h.risk_level === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                          : h.risk_level === 'HIGH'
                          ? 'bg-orange-500/20 text-orange-400 border border-orange-500/40'
                          : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40'
                      }`}
                    >
                      {h.risk_score}% risque
                    </span>
                  </div>
                  <p className="mt-1 text-[11px] text-slate-400">
                    {h.reasons && h.reasons[0] ? h.reasons[0] : 'Complexité et changements fréquents'}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Issue Categories Breakdown */}
          <div className="glass-panel rounded-2xl p-6 transition-all duration-300">
            <h3 className="text-sm font-bold text-white mb-3">Répartition par Catégorie</h3>
            <div className="space-y-2">
              {Object.entries(stats?.category_breakdown || {}).map(([cat, count]) => (
                <div key={cat} className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-medium capitalize">{cat.toLowerCase().replace('_', ' ')}</span>
                  <span className="font-bold text-slate-200 bg-white/[0.06] border border-white/[0.06] px-2 py-0.5 rounded-full">{count}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

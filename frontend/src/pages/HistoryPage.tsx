import React from 'react';
import { AnalysisRun } from '../api/client';
import { History, GitBranch, GitCommit, Clock, FileDown, CheckCircle2, ArrowRight } from 'lucide-react';

interface HistoryPageProps {
  runs: AnalysisRun[];
  currentRunId?: number;
  onSelectRun: (runId: number) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ runs, currentRunId, onSelectRun }) => {
  const getHealthBadge = (score: number) => {
    if (score >= 80) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 60) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  return (
    <div className="space-y-6">
      
      <div className="glass-panel rounded-2xl p-6 flex items-center justify-between transition-all duration-300">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
            <History className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Historique des Analyses & Évolution</h2>
            <p className="text-xs text-slate-400">
              Traçabilité des exécutions, métriques de santé au fil des commits et rapports d'audit.
            </p>
          </div>
        </div>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden transition-all duration-300">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Scan ID</th>
                <th className="py-3.5 px-4 font-semibold">Branche & Commit</th>
                <th className="py-3.5 px-4 font-semibold">Date & Heure</th>
                <th className="py-3.5 px-4 font-semibold">Santé</th>
                <th className="py-3.5 px-4 font-semibold">Défauts</th>
                <th className="py-3.5 px-4 font-semibold">Duplication</th>
                <th className="py-3.5 px-4 font-semibold">Durée</th>
                <th className="py-3.5 px-4 font-semibold text-right">Rapports d'Export</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {runs.map((run) => {
                const isSelected = run.id === currentRunId;
                return (
                  <tr
                    key={run.id}
                    className={`transition ${
                      isSelected
                        ? 'bg-cyan-950/30 border-l-4 border-cyan-500'
                        : 'hover:bg-slate-800/40'
                    }`}
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-200">
                      #{run.id}
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-1.5 font-mono text-[11px]">
                        <GitBranch className="w-3 h-3 text-emerald-400" />
                        <span className="text-slate-300 font-semibold">{run.branch}</span>
                        <span className="text-slate-500">({run.commit_hash.slice(0, 7)})</span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(run.created_at).toLocaleString('fr-FR')}
                    </td>

                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded-full font-bold border text-[11px] ${getHealthBadge(run.health_score)}`}>
                        {run.health_score.toFixed(0)}/100
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2.5">
                        <span className="flex items-center text-rose-400 font-bold">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5" />
                          {run.critical_count}
                        </span>
                        <span className="flex items-center text-amber-400 font-bold">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5" />
                          {run.high_count}
                        </span>
                        <span className="text-slate-400">({run.total_issues} total)</span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 text-slate-300 font-medium">
                      {run.duplication_percentage}%
                    </td>

                    <td className="py-3.5 px-4 text-slate-400">
                      {run.duration_ms} ms
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => onSelectRun(run.id)}
                          className="px-2.5 py-1 text-xs font-semibold rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 transition"
                        >
                          {isSelected ? 'Actif' : 'Charger'}
                        </button>

                        <a
                          href={`/api/reports/${run.id}/export?format=html`}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2 py-1 text-[11px] font-medium rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                          title="Imprimer / Enregistrer en PDF"
                        >
                          PDF
                        </a>
                        <a
                          href={`/api/reports/${run.id}/export?format=markdown`}
                          download={`codeguardian-report-${run.id}.md`}
                          className="px-2 py-1 text-[11px] font-medium rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                          title="Télécharger en Markdown"
                        >
                          MD
                        </a>
                        <a
                          href={`/api/reports/${run.id}/export?format=json`}
                          download={`codeguardian-report-${run.id}.json`}
                          className="px-2 py-1 text-[11px] font-medium rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                          title="Télécharger en JSON pour CI/CD"
                        >
                          JSON
                        </a>
                        <a
                          href="/api/reports/badge.svg"
                          target="_blank"
                          rel="noreferrer"
                          className="px-2 py-1 text-[11px] font-medium rounded bg-cyan-950/60 hover:bg-cyan-900/60 text-cyan-300 border border-cyan-800/60 transition"
                          title="Voir le badge SVG Shields.io pour le README"
                        >
                          Badge
                        </a>
                      </div>
                    </td>
                  </tr>
                );
              })}

              {runs.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">
                    Aucun historique de scan disponible.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

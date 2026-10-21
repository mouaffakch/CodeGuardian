import React from 'react';
import { DuplicationBlock } from '../api/client';
import { Copy, Layers, FileCode, ArrowRight, Lightbulb } from 'lucide-react';

interface DuplicationPageProps {
  duplications: DuplicationBlock[];
  duplicationPercentage: number;
}

export const DuplicationPage: React.FC<DuplicationPageProps> = ({
  duplications,
  duplicationPercentage
}) => {
  return (
    <div className="space-y-6">
      
      {/* Intro Header */}
      <div className="bg-gradient-to-r from-purple-950/40 via-slate-900 to-indigo-950/30 border border-purple-800/40 rounded-2xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
              <Layers className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">Détection des Duplications de Code (Clones)</h2>
              <p className="text-xs text-slate-300">
                Algorithme Rabin-Karp & hachage glissant identifiant les blocs de logique dupliqués.
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-2xl font-black text-purple-400">{duplicationPercentage}%</span>
            <span className="text-xs text-slate-400 block font-medium">de code dupliqué</span>
          </div>
        </div>
      </div>

      {/* Clones List */}
      <div className="space-y-4">
        {duplications.map((dup, idx) => (
          <div
            key={dup.id || idx}
            className="glass-panel hover:bg-slate-900/80 rounded-2xl p-5 space-y-4 transition-all duration-300"
          >
            {/* Clones Pair Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
              <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                <span className="bg-slate-800 px-2.5 py-1 rounded-md text-cyan-400 border border-slate-700">
                  📄 {dup.file_a}:{dup.start_line_a}-{dup.end_line_a}
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                <span className="bg-slate-800 px-2.5 py-1 rounded-md text-indigo-400 border border-slate-700">
                  📄 {dup.file_b}:{dup.start_line_b}-{dup.end_line_b}
                </span>
              </div>

              <div className="flex items-center space-x-2 text-xs">
                <span className="font-bold text-purple-400 bg-purple-950/60 border border-purple-800/60 px-2.5 py-1 rounded-md">
                  {dup.line_count} lignes identiques
                </span>
              </div>
            </div>

            {/* Snippet */}
            {dup.snippet && (
              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-1.5 uppercase tracking-wider">
                  Extrait du bloc dupliqué :
                </span>
                <div className="bg-[#070b14] border border-slate-800 rounded-xl p-3.5 font-mono text-xs text-slate-300 overflow-x-auto">
                  <pre>{dup.snippet}</pre>
                </div>
              </div>
            )}

            {/* Refactoring recommendation */}
            <div className="bg-purple-950/20 border border-purple-900/40 rounded-xl p-3 flex items-start space-x-2.5 text-xs text-purple-200">
              <Lightbulb className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-white block mb-0.5">Recommandation Clean Code :</strong>
                <span>
                  Extraire cette portion de code dans un module partagé (ex: <code>utils.py</code> ou <code>services/common.py</code>) pour respecter le principe DRY (Don't Repeat Yourself) et éviter les divergences de comportement lors des futures évolutions.
                </span>
              </div>
            </div>
          </div>
        ))}

        {duplications.length === 0 && (
          <div className="p-12 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
            Félicitations ! Aucune duplication significative détectée dans ce projet.
          </div>
        )}
      </div>

    </div>
  );
};

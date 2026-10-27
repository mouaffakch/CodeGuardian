import React, { useState } from 'react';
import { X, Play, Folder, Sparkles, CheckCircle, RefreshCw } from 'lucide-react';

interface ScanFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartScan: (targetPath: string, projectName: string) => Promise<void>;
}

export const ScanFormModal: React.FC<ScanFormModalProps> = ({ isOpen, onClose, onStartScan }) => {
  if (!isOpen) return null;

  const [targetPath, setTargetPath] = useState('');
  const [projectName, setProjectName] = useState('Mon Projet');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onStartScan(targetPath, projectName);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSample = (path: string, name: string) => {
    setTargetPath(path);
    setProjectName(name);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-[#0f172a] border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center space-x-2 text-white font-bold">
            <Play className="w-4 h-4 text-cyan-400 fill-current" />
            <span>Lancer une Analyse CodeGuardian</span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Nom du Projet
            </label>
            <input
              type="text"
              required
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
              placeholder="Ex: API Backend, Service Paiement"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Chemin du Répertoire (relatif ou absolu)
            </label>
            <div className="relative">
              <Folder className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                value={targetPath}
                onChange={(e) => setTargetPath(e.target.value)}
                placeholder="Laissez vide pour analyser tout le projet actuel"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3.5 py-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
            <p className="mt-1 text-[11px] text-slate-400">
              Chemin vide = analyse du workspace courant.
            </p>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 space-y-2">
            <span className="text-[11px] font-semibold text-slate-400 block uppercase tracking-wider">
              Scénarios Prédéfinis Rapides :
            </span>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => handleSelectSample('sample_project', 'Sample Test Suite')}
                className="text-xs px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 transition"
              >
                Projet d'exemple (sample_project)
              </button>
              <button
                type="button"
                onClick={() => handleSelectSample('backend', 'CodeGuardian Backend')}
                className="text-xs px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-slate-700 transition"
              >
                Backend CodeGuardian
              </button>
            </div>
          </div>

          <div className="bg-cyan-950/20 border border-cyan-800/30 p-3 rounded-xl flex items-center space-x-2 text-xs text-cyan-300">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>L'analyse statique AST, le calcul des risques Git et les suggestions IA seront exécutés.</span>
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white bg-slate-800 rounded-lg transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-5 py-2 text-xs font-bold text-white bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 rounded-lg shadow-lg shadow-cyan-500/20 transition active:scale-95 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Analyse en cours...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Démarrer le Scan</span>
                </>
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
};

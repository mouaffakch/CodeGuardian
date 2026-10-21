import React, { useState } from 'react';
import { X, Sparkles, Check, Copy, AlertTriangle, ShieldCheck, Wrench, RefreshCw, ArrowRight } from 'lucide-react';
import { Defect, requestAIFix } from '../api/client';

interface DefectDetailModalProps {
  defect: Defect | null;
  onClose: () => void;
}

export const DefectDetailModal: React.FC<DefectDetailModalProps> = ({ defect, onClose }) => {
  if (!defect) return null;

  const [copied, setCopied] = useState(false);
  const [loadingFix, setLoadingFix] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');
  const [aiFixData, setAiFixData] = useState<{
    explanation: string;
    rootCause: string;
    remediation: string;
    fixedCode: string;
    diff: string;
    bestPractices: string[];
  }>({
    explanation: defect.ai_explanation || defect.description,
    rootCause: "Vulnérabilité ou non-respect des règles de qualité détecté par l'analyseur statique AST.",
    remediation: "Refactorisation automatisée sécurisée recommandée.",
    fixedCode: defect.ai_suggested_fix || defect.code_snippet || '',
    diff: defect.ai_diff || '',
    bestPractices: [
      'Valider et assainir toutes les entrées utilisateurs.',
      'Ne jamais exposer de secrets ou clés sensibles dans le code source.',
      'Écrire des tests unitaires pour valider les cas limites.'
    ]
  });

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCustomAiRequest = async () => {
    if (!defect.code_snippet) return;
    setLoadingFix(true);
    try {
      const res = await requestAIFix({
        defect_id: defect.id,
        code_snippet: defect.code_snippet,
        rule_id: defect.rule_id,
        description: defect.description,
        file_path: defect.file_path,
        user_instructions: customPrompt
      });
      setAiFixData({
        explanation: res.explanation,
        rootCause: res.root_cause,
        remediation: res.remediation_summary,
        fixedCode: res.fixed_code,
        diff: res.diff,
        bestPractices: res.best_practices.length ? res.best_practices : aiFixData.bestPractices
      });
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFix(false);
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm overflow-y-auto">
      <div className="bg-[#0f172a] border border-slate-800 rounded-2xl w-full max-w-4xl shadow-2xl overflow-hidden my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center space-x-3">
            <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${getSeverityBadge(defect.severity)}`}>
              {defect.severity}
            </span>
            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-md border border-cyan-800/50">
              {defect.rule_id}
            </span>
            <span className="text-xs text-slate-400">
              {defect.file_path}:{defect.line_number}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
          
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">{defect.title}</h2>
            <p className="mt-1 text-sm text-slate-300">{defect.description}</p>
          </div>

          {/* Original Snippet */}
          {defect.code_snippet && (
            <div>
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                <span>Code Détecté (Ligne {defect.line_number})</span>
              </div>
              <div className="bg-[#070b14] border border-slate-800 rounded-xl p-4 font-mono text-xs text-rose-300 overflow-x-auto">
                <pre>{defect.code_snippet}</pre>
              </div>
            </div>
          )}

          {/* AI Diagnostic Card */}
          <div className="bg-gradient-to-br from-cyan-950/40 via-slate-900 to-emerald-950/20 border border-cyan-800/40 rounded-xl p-5 relative">
            <div className="flex items-center space-x-2 text-cyan-400 font-bold text-sm mb-3">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Analyse & Diagnostic IA</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-900/60 p-3.5 rounded-lg border border-slate-800">
                <span className="font-semibold text-slate-300 block mb-1">Cause racine :</span>
                <p className="text-slate-400 leading-relaxed">{aiFixData.rootCause}</p>
              </div>
              <div className="bg-slate-900/60 p-3.5 rounded-lg border border-slate-800">
                <span className="font-semibold text-slate-300 block mb-1">Explication technique :</span>
                <p className="text-slate-400 leading-relaxed">{aiFixData.explanation}</p>
              </div>
            </div>

            {/* Best Practices */}
            {aiFixData.bestPractices.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-800/60">
                <span className="text-xs font-semibold text-slate-300 block mb-2">Recommandations de sécurité & qualité :</span>
                <ul className="space-y-1.5 text-xs text-slate-400">
                  {aiFixData.bestPractices.map((bp, i) => (
                    <li key={i} className="flex items-center space-x-2">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{bp}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Suggested Fix & Diff */}
          {aiFixData.fixedCode && (
            <div>
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                <div className="flex items-center space-x-2">
                  <Wrench className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Code Corrigé Proposé</span>
                </div>
                <button
                  onClick={() => handleCopy(aiFixData.fixedCode)}
                  className="flex items-center space-x-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded-md transition"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copié !' : 'Copier le code'}</span>
                </button>
              </div>

              <div className="bg-[#070b14] border border-emerald-900/50 rounded-xl p-4 font-mono text-xs text-emerald-300 overflow-x-auto">
                <pre>{aiFixData.fixedCode}</pre>
              </div>

              {/* Unified Diff View */}
              {aiFixData.diff && (
                <div className="mt-3">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Différence (Unified Diff)
                  </span>
                  <div className="bg-[#070b14] border border-slate-800 rounded-xl p-3 font-mono text-[11px] overflow-x-auto text-slate-300 max-h-48 overflow-y-auto">
                    {aiFixData.diff.split('\n').map((line, idx) => {
                      const isAdded = line.startsWith('+');
                      const isRemoved = line.startsWith('-');
                      return (
                        <div
                          key={idx}
                          className={`${
                            isAdded ? 'text-emerald-400 bg-emerald-950/20' : isRemoved ? 'text-rose-400 bg-rose-950/20' : 'text-slate-400'
                          }`}
                        >
                          {line}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Custom Instruction Box for AI */}
          <div className="pt-2 border-t border-slate-800">
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Demander un ajustement spécifique à l'IA :
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Ex: Utiliser SQLAlchemy 2.0 select() ou adapter pour async/await..."
                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <button
                onClick={handleCustomAiRequest}
                disabled={loadingFix}
                className="flex items-center space-x-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition shadow"
              >
                {loadingFix ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                <span>Générer</span>
              </button>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 rounded-lg hover:bg-slate-700 transition"
          >
            Fermer
          </button>
        </div>

      </div>
    </div>
  );
};

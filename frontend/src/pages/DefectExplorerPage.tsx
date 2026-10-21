import React, { useState, useMemo } from 'react';
import { Defect } from '../api/client';
import { Search, Filter, Sparkles, ChevronRight, AlertTriangle, Bug, Shield, Wrench, Layers } from 'lucide-react';

interface DefectExplorerPageProps {
  defects: Defect[];
  onSelectDefect: (defect: Defect) => void;
}

export const DefectExplorerPage: React.FC<DefectExplorerPageProps> = ({ defects, onSelectDefect }) => {
  const [search, setSearch] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const filteredDefects = useMemo(() => {
    return defects.filter((d) => {
      const matchSearch =
        d.title.toLowerCase().includes(search.toLowerCase()) ||
        d.description.toLowerCase().includes(search.toLowerCase()) ||
        d.file_path.toLowerCase().includes(search.toLowerCase()) ||
        d.rule_id.toLowerCase().includes(search.toLowerCase());

      const matchSeverity = selectedSeverity === 'ALL' || d.severity === selectedSeverity;
      const matchCategory = selectedCategory === 'ALL' || d.category === selectedCategory;

      return matchSearch && matchSeverity && matchCategory;
    });
  }, [defects, search, selectedSeverity, selectedCategory]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'SECURITY':
        return <Shield className="w-3.5 h-3.5 text-rose-400" />;
      case 'BUG':
        return <Bug className="w-3.5 h-3.5 text-amber-400" />;
      case 'COMPLEXITY':
        return <Wrench className="w-3.5 h-3.5 text-cyan-400" />;
      case 'DUPLICATION':
        return <Layers className="w-3.5 h-3.5 text-purple-400" />;
      default:
        return <AlertTriangle className="w-3.5 h-3.5 text-slate-400" />;
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
    <div className="space-y-6">
      
      {/* Search & Filters */}
      <div className="glass-panel rounded-2xl p-4 flex flex-col md:flex-row gap-4 justify-between items-center transition-all duration-300">
        
        {/* Search */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher par règle, titre, fichier ou mot-clé..."
            className="w-full bg-slate-950/70 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Severity selector */}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="bg-slate-950/80 border border-white/[0.08] text-xs text-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">Toutes Sévérités</option>
            <option value="CRITICAL">🔴 Critique</option>
            <option value="HIGH">🟠 Haute</option>
            <option value="MEDIUM">🟡 Moyenne</option>
            <option value="LOW">🔵 Basse</option>
          </select>

          {/* Category selector */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-950/80 border border-white/[0.08] text-xs text-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">Toutes Catégories</option>
            <option value="SECURITY">Sécurité</option>
            <option value="BUG">Bugs Fonctionnels</option>
            <option value="BAD_PRACTICE">Mauvaises Pratiques</option>
            <option value="COMPLEXITY">Complexité / Code Smell</option>
            <option value="DUPLICATION">Duplication</option>
          </select>

          <span className="text-xs text-slate-400 ml-2 font-medium">
            <strong>{filteredDefects.length}</strong> / {defects.length} défauts
          </span>
        </div>

      </div>

      {/* Defects List */}
      <div className="space-y-3">
        {filteredDefects.map((defect) => (
          <div
            key={defect.id || `${defect.file_path}-${defect.line_number}-${defect.rule_id}`}
            onClick={() => onSelectDefect(defect)}
            className="group glass-panel hover:bg-slate-900/80 p-5 rounded-2xl cursor-pointer transition-all duration-300 flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div className="space-y-2 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-md border ${getSeverityBadge(defect.severity)}`}>
                  {defect.severity}
                </span>

                <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-800 px-2 py-0.5 rounded-md">
                  {getCategoryIcon(defect.category)}
                  <span>{defect.category}</span>
                </div>

                <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded-md border border-cyan-800/50">
                  {defect.rule_id}
                </span>
              </div>

              <h4 className="text-sm font-bold text-white group-hover:text-cyan-300 transition">
                {defect.title}
              </h4>
              <p className="text-xs text-slate-400 line-clamp-2">{defect.description}</p>

              <div className="flex items-center space-x-3 text-xs text-slate-500 font-mono">
                <span>📁 {defect.file_path}:{defect.line_number}</span>
              </div>
            </div>

            <div className="flex items-center space-x-3 shrink-0">
              <button
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 text-xs font-semibold group-hover:bg-cyan-600 group-hover:text-white transition"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Diagnostic & Fix IA</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}

        {filteredDefects.length === 0 && (
          <div className="p-12 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
            Aucun défaut ne correspond à vos filtres.
          </div>
        )}
      </div>

    </div>
  );
};

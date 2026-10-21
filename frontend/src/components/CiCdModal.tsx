import React, { useState } from 'react';
import { X, Copy, Check, Terminal, GitBranch, Shield, Cpu } from 'lucide-react';

interface CiCdModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CiCdModal: React.FC<CiCdModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const [activeTab, setActiveTab] = useState<'cli' | 'github' | 'gitlab' | 'precommit'>('cli');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const cliSnippet = `# 1. Activer l'environnement virtuel
cd backend
.venv\\Scripts\\activate  # Sur Windows
# source .venv/bin/activate  # Sur Linux/macOS

# 2. Lancer une analyse sur un projet
python app/cli.py scan ../sample_project --fail-on-critical --output report.md

# 3. Lancer la suite de tests automatisés
pytest tests -v`;

  const githubActionsSnippet = `name: CodeGuardian CI Quality Gate

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]

jobs:
  code-guardian:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Historique Git complet pour l'analyse des risques

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Dependencies
        run: pip install -r backend/requirements.txt

      - name: Static & AI Defect Analysis
        run: python backend/app/cli.py scan . --fail-on-critical --output report.md

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: codeguardian-report
          path: report.md`;

  const gitlabSnippet = `stages:
  - test
  - quality-gate

codeguardian-scan:
  stage: quality-gate
  image: python:3.12-slim
  before_script:
    - apt-get update && apt-get install -y git
  script:
    - pip install -r backend/requirements.txt
    - python backend/app/cli.py scan . --fail-on-critical --output report.json
  artifacts:
    paths:
      - report.json
    expire_in: 14 days`;

  const precommitSnippet = `# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: codeguardian-scan
        name: CodeGuardian Pre-Commit Defect Scanner
        entry: python backend/app/cli.py scan . --fail-on-critical
        language: python
        types: [python, javascript]
        pass_filenames: false`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-[#0f172a] border border-slate-800 rounded-2xl w-full max-w-3xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center space-x-2 text-white font-bold">
            <Terminal className="w-5 h-5 text-cyan-400" />
            <span>Intégration Génie Logiciel : CLI & Pipelines CI/CD</span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-800 bg-slate-900/30 px-6 pt-3 space-x-6 text-xs font-semibold">
          {[
            { id: 'cli', label: 'CLI & Terminal' },
            { id: 'github', label: 'GitHub Actions' },
            { id: 'gitlab', label: 'GitLab CI' },
            { id: 'precommit', label: 'Git Pre-commit Hook' },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`pb-3 transition-colors ${
                activeTab === t.id
                  ? 'border-b-2 border-cyan-400 text-cyan-400 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'cli' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400 font-medium">Exécution locale via la ligne de commande CodeGuardian :</span>
                <button
                  onClick={() => handleCopy(cliSnippet, 'cli')}
                  className="flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300"
                >
                  {copiedKey === 'cli' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey === 'cli' ? 'Copié !' : 'Copier'}</span>
                </button>
              </div>
              <pre className="bg-[#070b14] border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 overflow-x-auto">
                {cliSnippet}
              </pre>
              <div className="mt-3 text-xs text-slate-400 space-y-1">
                <p>• Code de retour <code>0</code> : Analyse validée, aucun bug critique.</p>
                <p>• Code de retour <code>1</code> : Échec de la Quality Gate (défauts critiques détectés).</p>
              </div>
            </div>
          )}

          {activeTab === 'github' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400 font-medium">Workflow <code>.github/workflows/codeguardian-ci.yml</code> :</span>
                <button
                  onClick={() => handleCopy(githubActionsSnippet, 'gh')}
                  className="flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300"
                >
                  {copiedKey === 'gh' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey === 'gh' ? 'Copié !' : 'Copier'}</span>
                </button>
              </div>
              <pre className="bg-[#070b14] border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 overflow-x-auto max-h-72 overflow-y-auto">
                {githubActionsSnippet}
              </pre>
            </div>
          )}

          {activeTab === 'gitlab' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400 font-medium">Pipeline <code>.gitlab-ci.yml</code> :</span>
                <button
                  onClick={() => handleCopy(gitlabSnippet, 'gl')}
                  className="flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300"
                >
                  {copiedKey === 'gl' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey === 'gl' ? 'Copié !' : 'Copier'}</span>
                </button>
              </div>
              <pre className="bg-[#070b14] border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 overflow-x-auto max-h-72 overflow-y-auto">
                {gitlabSnippet}
              </pre>
            </div>
          )}

          {activeTab === 'precommit' && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400 font-medium">Hook Git local <code>.pre-commit-config.yaml</code> :</span>
                <button
                  onClick={() => handleCopy(precommitSnippet, 'pc')}
                  className="flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300"
                >
                  {copiedKey === 'pc' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey === 'pc' ? 'Copié !' : 'Copier'}</span>
                </button>
              </div>
              <pre className="bg-[#070b14] border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 overflow-x-auto">
                {precommitSnippet}
              </pre>
              <p className="mt-2 text-xs text-slate-400">
                Bloque automatiquement les commits locaux si des failles ou secrets non masqués sont détectés.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 rounded-lg hover:bg-slate-700 transition"
          >
            Fermer
          </button>
        </div>

      </div>
    </div>
  );
};

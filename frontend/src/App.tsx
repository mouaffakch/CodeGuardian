import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { DefectExplorerPage } from './pages/DefectExplorerPage';
import { RiskPredictionPage } from './pages/RiskPredictionPage';
import { DuplicationPage } from './pages/DuplicationPage';
import { HistoryPage } from './pages/HistoryPage';
import { DefectDetailModal } from './components/DefectDetailModal';
import { ScanFormModal } from './components/ScanFormModal';
import { CiCdModal } from './components/CiCdModal';
import {
  AnalysisRun,
  DashboardStats,
  Defect,
  fetchDashboardStats,
  fetchScans,
  fetchScanDetail,
  triggerScan
} from './api/client';
import { RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [runs, setRuns] = useState<AnalysisRun[]>([]);
  const [currentRun, setCurrentRun] = useState<AnalysisRun | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  // Modals state
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);
  const [isScanModalOpen, setIsScanModalOpen] = useState<boolean>(false);
  const [isCiCdModalOpen, setIsCiCdModalOpen] = useState<boolean>(false);

  // Load initial data
  const loadData = async () => {
    setLoading(true);
    try {
      const statsData = await fetchDashboardStats();
      setStats(statsData);

      const runsData = await fetchScans();
      setRuns(runsData);

      if (runsData.length > 0) {
        // Fetch full detail of the latest run
        const latestDetail = await fetchScanDetail(runsData[0].id);
        setCurrentRun(latestDetail);
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectRun = async (runId: number) => {
    try {
      const detail = await fetchScanDetail(runId);
      setCurrentRun(detail);
      setActiveTab('dashboard');
    } catch (err) {
      console.error('Failed to switch run:', err);
    }
  };

  const handleStartScan = async (targetPath: string, projectName: string) => {
    const newRun = await triggerScan(targetPath, projectName);
    setCurrentRun(newRun);
    await loadData();
    setActiveTab('dashboard');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0a0f1d] text-slate-100">
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenScanModal={() => setIsScanModalOpen(true)}
        onOpenCiCdModal={() => setIsCiCdModalOpen(true)}
        currentBranch={currentRun?.branch || 'main'}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && !currentRun ? (
          <div className="flex flex-col items-center justify-center py-24 space-y-3">
            <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
            <span className="text-sm text-slate-400 font-medium">Chargement des données CodeGuardian...</span>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && (
              <DashboardPage
                stats={stats}
                latestRun={currentRun}
                onSelectDefect={(d) => setSelectedDefect(d)}
                onNavigateTab={(tab) => setActiveTab(tab)}
                onOpenScanModal={() => setIsScanModalOpen(true)}
              />
            )}

            {activeTab === 'defects' && (
              <DefectExplorerPage
                defects={currentRun?.defects || []}
                onSelectDefect={(d) => setSelectedDefect(d)}
              />
            )}

            {activeTab === 'hotspots' && (
              <RiskPredictionPage
                hotspots={currentRun?.hotspots || []}
              />
            )}

            {activeTab === 'duplications' && (
              <DuplicationPage
                duplications={currentRun?.duplications || []}
                duplicationPercentage={currentRun?.duplication_percentage || 0}
              />
            )}

            {activeTab === 'history' && (
              <HistoryPage
                runs={runs}
                currentRunId={currentRun?.id}
                onSelectRun={handleSelectRun}
              />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#090d19] py-5 text-center text-xs text-slate-500">
        <p>
          🛡️ <strong className="text-slate-400">CodeGuardian</strong> — Plateforme Intelligente d'Analyse Statique, Détection de Défauts & Prédiction de Risques.
        </p>
      </footer>

      {/* Modals */}
      <DefectDetailModal
        defect={selectedDefect}
        onClose={() => setSelectedDefect(null)}
      />

      <ScanFormModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        onStartScan={handleStartScan}
      />

      <CiCdModal
        isOpen={isCiCdModalOpen}
        onClose={() => setIsCiCdModalOpen(false)}
      />

    </div>
  );
};

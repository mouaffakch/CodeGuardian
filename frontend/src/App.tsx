import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { AnimatedBackground } from './components/AnimatedBackground';
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
  
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);
  const [isScanModalOpen, setIsScanModalOpen] = useState<boolean>(false);
  const [isCiCdModalOpen, setIsCiCdModalOpen] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const statsData = await fetchDashboardStats();
      setStats(statsData);

      const runsData = await fetchScans();
      setRuns(runsData);

      if (runsData.length > 0) {
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
    <div className="min-h-screen flex flex-col bg-[#040711] text-slate-100 relative overflow-hidden">
      
      <AnimatedBackground />

      <div className="relative z-20">
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onOpenScanModal={() => setIsScanModalOpen(true)}
          onOpenCiCdModal={() => setIsCiCdModalOpen(true)}
          currentBranch={currentRun?.branch || 'main'}
        />
      </div>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {loading && !currentRun ? (
          <div className="flex flex-col items-center justify-center py-28 space-y-4">
            <div className="relative">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center animate-pulse">
                <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin" />
              </div>
              <div className="absolute -inset-1 bg-cyan-500/20 rounded-2xl blur-lg -z-10 animate-pulse" />
            </div>
            <span className="text-sm text-slate-300 font-medium tracking-wide">Chargement de l'environnement CodeGuardian...</span>
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

      <footer className="border-t border-white/[0.07] bg-[#070b16]/70 backdrop-blur-md py-5 text-center text-xs text-slate-400 relative z-10">
        <p className="flex items-center justify-center space-x-2">
          <span className="font-semibold text-slate-200">CodeGuardian</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">Plateforme d'Analyse Statique, Détection de Vulnérabilités & Audit Logiciel</span>
        </p>
      </footer>

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

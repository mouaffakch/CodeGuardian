export interface Defect {
  id: number;
  file_path: string;
  line_number: number;
  end_line?: number;
  rule_id: string;
  title: string;
  description: string;
  category: 'BUG' | 'SECURITY' | 'BAD_PRACTICE' | 'COMPLEXITY' | 'DUPLICATION';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  code_snippet?: string;
  ai_explanation?: string;
  ai_suggested_fix?: string;
  ai_diff?: string;
  status: string;
}

export interface HotspotRisk {
  id: number;
  file_path: string;
  risk_score: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  churn_lines: number;
  commit_count: number;
  bug_fix_count: number;
  cyclomatic_complexity: number;
  maintainability_index: number;
  reasons: string[];
}

export interface DuplicationBlock {
  id: number;
  content_hash: string;
  file_a: string;
  start_line_a: number;
  end_line_a: number;
  file_b: string;
  start_line_b: number;
  end_line_b: number;
  line_count: number;
  snippet?: string;
}

export interface AnalysisRun {
  id: number;
  project_id: number;
  branch: string;
  commit_hash: string;
  status: string;
  total_files: number;
  lines_of_code: number;
  total_issues: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  duplication_percentage: number;
  health_score: number;
  duration_ms: number;
  created_at: string;
  defects?: Defect[];
  hotspots?: HotspotRisk[];
  duplications?: DuplicationBlock[];
}

export interface DashboardStats {
  total_projects: number;
  total_scans: number;
  latest_health_score: number;
  total_critical_bugs: number;
  total_high_bugs: number;
  total_duplications: number;
  high_risk_files_count: number;
  category_breakdown: Record<string, number>;
  severity_breakdown: Record<string, number>;
  recent_runs: AnalysisRun[];
}

export interface AIFixResponse {
  explanation: string;
  root_cause: string;
  remediation_summary: string;
  fixed_code: string;
  diff: string;
  confidence_score: number;
  best_practices: string[];
}

export interface ApplyFixResult {
  success: boolean;
  message: string;
  file_path: string;
  backup_path?: string;
}

const API_BASE = '/api';

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/scans/dashboard/stats`);
  if (!res.ok) throw new Error('Failed to fetch dashboard stats');
  return res.json();
}

export async function fetchScans(): Promise<AnalysisRun[]> {
  const res = await fetch(`${API_BASE}/scans`);
  if (!res.ok) throw new Error('Failed to fetch scans');
  return res.json();
}

export async function fetchScanDetail(id: number): Promise<AnalysisRun> {
  const res = await fetch(`${API_BASE}/scans/${id}`);
  if (!res.ok) throw new Error('Failed to fetch scan detail');
  return res.json();
}

export async function triggerScan(targetPath?: string, projectName?: string, diffOnly: boolean = false): Promise<AnalysisRun> {
  const res = await fetch(`${API_BASE}/scans/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      target_path: targetPath || '',
      project_name: projectName || 'CodeGuardian Project',
      include_ai_fixes: true,
      diff_only: diffOnly,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Scan failed' }));
    throw new Error(err.detail || 'Scan failed');
  }
  return res.json();
}

export async function requestAIFix(params: {
  defect_id?: number;
  code_snippet: string;
  rule_id: string;
  description: string;
  file_path?: string;
  user_instructions?: string;
}): Promise<AIFixResponse> {
  const res = await fetch(`${API_BASE}/ai/fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to generate AI fix');
  return res.json();
}

export async function applyAIFix(defectId: number, fixedCode?: string): Promise<ApplyFixResult> {
  const res = await fetch(`${API_BASE}/ai/apply-fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      defect_id: defectId,
      fixed_code: fixedCode,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to apply fix' }));
    throw new Error(err.detail || 'Failed to apply fix');
  }
  return res.json();
}

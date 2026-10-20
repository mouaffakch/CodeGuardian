from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field

class ProjectCreate(BaseModel):
    name: str
    root_path: str
    git_remote: Optional[str] = None

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    root_path: str
    git_remote: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class DefectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    file_path: str
    line_number: int
    end_line: Optional[int] = None
    rule_id: str
    title: str
    description: str
    category: str
    severity: str
    code_snippet: Optional[str] = None
    ai_explanation: Optional[str] = None
    ai_suggested_fix: Optional[str] = None
    ai_diff: Optional[str] = None
    status: str = "OPEN"

class HotspotRiskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    file_path: str
    risk_score: float
    risk_level: str
    churn_lines: int
    commit_count: int
    bug_fix_count: int
    cyclomatic_complexity: int
    maintainability_index: float
    reasons: List[str] = []

class DuplicationBlockSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    content_hash: str
    file_a: str
    start_line_a: int
    end_line_a: int
    file_b: str
    start_line_b: int
    end_line_b: int
    line_count: int
    snippet: Optional[str] = None

class AnalysisRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    branch: str
    commit_hash: str
    status: str
    total_files: int
    lines_of_code: int
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    duplication_percentage: float
    health_score: float
    duration_ms: int
    created_at: datetime
    error_message: Optional[str] = None

class AnalysisRunDetailResponse(AnalysisRunResponse):
    defects: List[DefectSchema] = []
    hotspots: List[HotspotRiskSchema] = []
    duplications: List[DuplicationBlockSchema] = []

class ScanRequest(BaseModel):
    target_path: Optional[str] = None
    project_name: Optional[str] = "CodeGuardian Target"
    include_ai_fixes: bool = True

class AIFixRequest(BaseModel):
    defect_id: Optional[int] = None
    code_snippet: str
    rule_id: str
    description: str
    file_path: Optional[str] = ""
    language: Optional[str] = "python"
    user_instructions: Optional[str] = None

class AIFixResponse(BaseModel):
    explanation: str
    root_cause: str
    remediation_summary: str
    fixed_code: str
    diff: str
    confidence_score: float
    best_practices: List[str] = []

class DashboardSummaryResponse(BaseModel):
    total_projects: int
    total_scans: int
    latest_health_score: float
    total_critical_bugs: int
    total_high_bugs: int
    total_duplications: int
    high_risk_files_count: int
    category_breakdown: dict
    severity_breakdown: dict
    recent_runs: List[AnalysisRunResponse]

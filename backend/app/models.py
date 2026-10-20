import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    root_path = Column(String(1024), nullable=False)
    git_remote = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    runs = relationship("AnalysisRun", back_populates="project", cascade="all, delete-orphan")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    branch = Column(String(128), default="main")
    commit_hash = Column(String(64), default="HEAD")
    status = Column(String(32), default="COMPLETED") # PENDING, RUNNING, COMPLETED, FAILED
    
    total_files = Column(Integer, default=0)
    lines_of_code = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    duplication_percentage = Column(Float, default=0.0)
    health_score = Column(Float, default=100.0) # 0 to 100
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="runs")
    defects = relationship("Defect", back_populates="run", cascade="all, delete-orphan")
    hotspots = relationship("HotspotRisk", back_populates="run", cascade="all, delete-orphan")
    duplications = relationship("DuplicationBlock", back_populates="run", cascade="all, delete-orphan")


class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False)
    file_path = Column(String(1024), nullable=False)
    line_number = Column(Integer, default=1)
    end_line = Column(Integer, nullable=True)
    rule_id = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(32), default="BUG") # BUG, SECURITY, BAD_PRACTICE, COMPLEXITY, DUPLICATION
    severity = Column(String(32), default="MEDIUM") # CRITICAL, HIGH, MEDIUM, LOW
    code_snippet = Column(Text, nullable=True)
    
    # AI Assistance fields
    ai_explanation = Column(Text, nullable=True)
    ai_suggested_fix = Column(Text, nullable=True)
    ai_diff = Column(Text, nullable=True)
    
    status = Column(String(32), default="OPEN") # OPEN, RESOLVED, IGNORED

    run = relationship("AnalysisRun", back_populates="defects")


class HotspotRisk(Base):
    __tablename__ = "hotspot_risks"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False)
    file_path = Column(String(1024), nullable=False)
    risk_score = Column(Float, default=0.0) # 0.0 to 100.0
    risk_level = Column(String(32), default="LOW") # CRITICAL, HIGH, MEDIUM, LOW
    churn_lines = Column(Integer, default=0)
    commit_count = Column(Integer, default=0)
    bug_fix_count = Column(Integer, default=0)
    cyclomatic_complexity = Column(Integer, default=1)
    maintainability_index = Column(Float, default=100.0)
    reasons_json = Column(Text, default="[]") # JSON list of strings

    run = relationship("AnalysisRun", back_populates="hotspots")


class DuplicationBlock(Base):
    __tablename__ = "duplication_blocks"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False)
    content_hash = Column(String(64), nullable=False)
    file_a = Column(String(1024), nullable=False)
    start_line_a = Column(Integer, nullable=False)
    end_line_a = Column(Integer, nullable=False)
    file_b = Column(String(1024), nullable=False)
    start_line_b = Column(Integer, nullable=False)
    end_line_b = Column(Integer, nullable=False)
    line_count = Column(Integer, default=0)
    snippet = Column(Text, nullable=True)

    run = relationship("AnalysisRun", back_populates="duplications")

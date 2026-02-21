from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from backend.app.models.database import Base
from backend.app.models.enums import Role, JobStatus, PipelineStatus, StageStatus

def generate_uuid():
    return uuid.uuid4().hex

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    users = relationship("User", back_populates="organization")
    api_keys = relationship("ApiKey", back_populates="organization")
    jobs = relationship("JobPosting", back_populates="organization")
    pipeline_runs = relationship("PipelineRun", back_populates="organization")
    usage_records = relationship("UsageRecord", back_populates="organization")
    file_uploads = relationship("FileUpload", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(Role), default=Role.VIEWER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="users")

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, unique=True, index=True, nullable=False)
    permissions = Column(JSON, default=list)
    rate_limit = Column(Integer, default=60) # requests per min
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="api_keys")

class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="jobs")
    pipeline_runs = relationship("PipelineRun", back_populates="job")

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("job_postings.id"), nullable=True, index=True)
    candidate_id = Column(String, index=True) # ID referencing zynd/candidates logic
    status = Column(SQLEnum(PipelineStatus), default=PipelineStatus.PENDING, nullable=False)
    timing = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="pipeline_runs")
    job = relationship("JobPosting", back_populates="pipeline_runs")
    stages = relationship("PipelineStageResult", back_populates="run", cascade="all, delete-orphan")

class PipelineStageResult(Base):
    __tablename__ = "pipeline_stage_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("pipeline_runs.id"), nullable=False, index=True)
    stage = Column(String, nullable=False) # e.g. 'gatekeeper'
    status = Column(SQLEnum(StageStatus), default=StageStatus.PENDING, nullable=False)
    output = Column(JSON, default=dict)
    score = Column(Float, nullable=True)
    duration_ms = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("PipelineRun", back_populates="stages")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    action = Column(String, nullable=False) # e.g 'pipeline_run', 'file_upload'
    tokens = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    organization = relationship("Organization", back_populates="usage_records")

class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    storage_key = Column(String, unique=True, nullable=False)
    original_filename = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="file_uploads")

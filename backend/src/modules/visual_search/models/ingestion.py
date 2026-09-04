# from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
# from sqlalchemy.sql import func
# from backend.src.shared.db.base import Base

# class IngestionJob(Base):
#     __tablename__ = "ingestion_jobs"

#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(String, index=True)  # User ka Session ID
    
#     # --- JOB TYPE ---
#     # "visual_sync" (Store sync) ya "file_upload" (CSV/JSON upload)
#     ingestion_type = Column(String, default="visual_sync", nullable=False)
    
#     source_name = Column(String, nullable=False)  # Store name ya filename
    
#     # --- STATUS ---
#     # "pending", "processing", "completed", "failed"
#     status = Column(String, default="pending", nullable=False)
    
#     # --- PROGRESS TRACKING ---
#     items_processed = Column(Integer, default=0)
#     total_items = Column(Integer, default=0)
    
#     # --- DETAILS / ERRORS ---
#     details = Column(JSON, default=[])
#     error_message = Column(Text, nullable=True)
    
#     # --- TIMESTAMPS ---
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from backend.src.shared.db.base import Base

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)  # User ka Session ID
    
    # --- JOB TYPE ---
    ingestion_type = Column(String, default="visual_sync", nullable=False)
    
    source_name = Column(String, nullable=False)  # Store name ya filename
    
    # --- STATUS ---
    status = Column(String, default="pending", nullable=False)
    
    # --- PROGRESS TRACKING ---
    items_processed = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
    
    # --- DETAILS / ERRORS ---
    details = Column(JSON, nullable=True, default=None)   # 🔥 FIX: list ki jagah None
    error_message = Column(Text, nullable=True)
    
    # --- TIMESTAMPS ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
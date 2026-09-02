from pydantic import BaseModel
from typing import Optional, Dict, List


# --- FILE UPLOAD SCHEMAS ---
class FilePreviewResponse(BaseModel):
    """File upload ke baad headers/keys return karne ke liye."""
    filename: str
    headers: List[str]
    message: str


class FileProcessRequest(BaseModel):
    """File process start karne ke liye field mapping."""
    filename: str
    field_mapping: Dict[str, str]  # {"title": "...", "slug": "...", "image_url": "..."}


# --- SEARCH SCHEMAS ---
class VisualSearchResponse(BaseModel):
    """Visual search results ka format."""
    results: List[Dict]  # [{"id": "...", "score": 0.89, "payload": {...}}]


# --- JOB STATUS SCHEMAS ---
class JobStatusResponse(BaseModel):
    """Sync/file processing job ki status dikhane ke liye."""
    job_id: int
    status: str
    items_processed: int
    total_items: int
    error_message: Optional[str] = None


class JobStartResponse(BaseModel):
    """Job start hone par response."""
    status: str
    message: str
    job_id: int
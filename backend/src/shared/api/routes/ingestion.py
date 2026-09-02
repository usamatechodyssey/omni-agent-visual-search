from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from backend.src.shared.db.session import get_db
from backend.src.shared.api.routes.deps import get_current_user
from backend.src.shared.models.user import User
from backend.src.modules.visual_search.models.ingestion import IngestionJob

router = APIRouter()


class JobStatusResponse(BaseModel):
    job_id: int
    ingestion_type: str  # "visual_sync" ya "file_upload"
    source_name: str
    status: str  # "pending", "processing", "completed", "failed"
    items_processed: int
    total_items: int
    error_message: Optional[str] = None
    details: Optional[dict] = None  # 🔥 NAYA FIELD ADD KIYA


@router.get("/ingestion/jobs", response_model=List[JobStatusResponse])
async def get_all_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[JobStatusResponse]:
    """Dashboard ke liye user ke saare ingestion jobs ki list return karta hai."""
    # Session ID format: "visual_sync_{user_id}" ya "file_upload_{user_id}"
    query = select(IngestionJob).where(
        IngestionJob.session_id.contains(str(current_user.id))
    )
    result = await db.execute(query)
    jobs = result.scalars().all()

    if not jobs:
        return []

    return [
        JobStatusResponse(
            job_id=job.id,
            ingestion_type=job.ingestion_type,
            source_name=job.source_name,
            status=job.status,
            items_processed=job.items_processed,
            total_items=job.total_items,
            error_message=job.error_message,
            details=job.details  # 🔥 YAHAN DETAILS PASS KI
        )
        for job in jobs
    ]


@router.get("/ingestion/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobStatusResponse:
    """Ek specific job ki status return karta hai (sirf user ka apna)."""
    query = select(IngestionJob).where(
        IngestionJob.id == job_id,
        IngestionJob.session_id.contains(str(current_user.id)),  # Security: User apna hi dekh sake
    )
    result = await db.execute(query)
    job = result.scalars().first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return JobStatusResponse(
        job_id=job.id,
        ingestion_type=job.ingestion_type,
        source_name=job.source_name,
        status=job.status,
        items_processed=job.items_processed,
        total_items=job.total_items,
        error_message=job.error_message,
        details=job.details  # 🔥 YAHAN DETAILS PASS KI
    )
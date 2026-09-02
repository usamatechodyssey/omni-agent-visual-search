import json
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    BackgroundTasks,
    Request,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Internal Imports
from backend.src.shared.api.routes.deps import get_current_user, get_current_user_by_api_key
from backend.src.shared.db.session import get_db, AsyncSessionLocal
from backend.src.shared.models.user import User
from backend.src.shared.models.integration import UserIntegration
from backend.src.modules.visual_search.models.ingestion import IngestionJob
from backend.src.modules.visual_search.schemas.visual import (
    FilePreviewResponse,
    JobStartResponse,
    JobStatusResponse,
    VisualSearchResponse,
)

# Visual Services
from backend.src.modules.visual_search.services.visual.engine import get_image_embedding
from backend.src.modules.visual_search.services.visual.agent import run_visual_sync
from backend.src.modules.visual_search.services.visual.file_ingestion import (
    parse_file_headers,
    process_file_upload,
)
from backend.src.modules.visual_search.services.vector_store.factory import get_visual_vector_store

router = APIRouter()


def check_domain_authorization(user: User, request: Request) -> None:
    client_origin = request.headers.get("origin") or request.headers.get("referer") or ""
    if user.allowed_domains == "*":
        return
    allowed = [d.strip() for d in user.allowed_domains.split(",")]
    is_authorized = any(domain in client_origin for domain in allowed)
    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Domain not authorized to use this API.")


@router.post("/visual/sync", response_model=JobStartResponse)
async def trigger_visual_sync(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobStartResponse:
    try:
        job = IngestionJob(
            session_id=f"visual_sync_{current_user.id}",
            ingestion_type="visual_sync",
            source_name="Store Integration (Visual)",
            status="pending",
            total_items=0,
            items_processed=0,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        background_tasks.add_task(run_visual_sync, str(current_user.id), job.id, AsyncSessionLocal)
        return JobStartResponse(status="processing", message="Visual Sync started successfully.", job_id=job.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visual/search", response_model=VisualSearchResponse)
async def search_visual_products(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_by_api_key),
) -> VisualSearchResponse:
    check_domain_authorization(current_user, request)

    # 🔥 Check if user selected a vector DB
    if not current_user.selected_vector_provider:
        raise HTTPException(status_code=400, detail="No vector DB selected. Please select one in Settings.")

    stmt = select(UserIntegration).where(
        UserIntegration.user_id == str(current_user.id),
        UserIntegration.is_active == True,
        UserIntegration.provider == current_user.selected_vector_provider
    )
    result = await db.execute(stmt)
    integration = result.scalars().first()

    if not integration:
        raise HTTPException(status_code=400, detail="Selected vector database integration not found.")

    try:
        creds = json.loads(integration.credentials)
        creds['provider'] = current_user.selected_vector_provider
        collection_name = current_user.selected_collection_name or "visual_search_products"
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid vector DB credentials format.")

    try:
        image_bytes = await file.read()
        vector = get_image_embedding(image_bytes)
        if not vector or len(vector) != 512:
            raise ValueError("Empty or invalid embedding returned (expected 512 dims)")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing failed: {e}")

    try:
        vector_store = get_visual_vector_store(credentials=creds)
        results = await vector_store.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=10,
            filters={"user_id": str(current_user.id)},
            score_threshold=0.50,
        )
        return VisualSearchResponse(results=results)
    except Exception as e:
        print(f"❌ Visual Search Failed: {e}")
        msg = str(e)
        if "dimension" in msg.lower():
            msg = "Vector dimension mismatch. Please re-run Visual Sync."
        if "not found" in msg.lower():
            msg = "Visual search collection not found. Run Sync first."
        raise HTTPException(status_code=500, detail=msg)


@router.post("/visual/file/preview", response_model=FilePreviewResponse)
async def file_preview(
    file: UploadFile = File(...),
    _current_user: User = Depends(get_current_user),
) -> FilePreviewResponse:
    try:
        file_content = await file.read()
        filename = file.filename or ""
        headers = await parse_file_headers(file_content, filename)
        if not headers:
            raise HTTPException(status_code=400, detail="No headers/keys found in file.")
        return FilePreviewResponse(filename=filename, headers=headers, message="File parsed successfully. Please map fields.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File parsing failed: {e}")


@router.post("/visual/file/process", response_model=JobStartResponse)
async def file_process(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    field_mapping: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobStartResponse:
    try:
        try:
            mapping_dict = json.loads(field_mapping)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid field_mapping JSON format.")

        required_fields = ["title", "slug", "image_url"]
        for field in required_fields:
            if field not in mapping_dict:
                raise HTTPException(status_code=400, detail=f"Missing required field mapping: {field}")

        file_content = await file.read()
        filename = file.filename or "uploaded_file"
        job = IngestionJob(
            session_id=f"file_upload_{current_user.id}",
            ingestion_type="file_upload",
            source_name=filename,
            status="pending",
            total_items=0,
            items_processed=0,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        background_tasks.add_task(process_file_upload, str(current_user.id), job.id, file_content, filename, mapping_dict, AsyncSessionLocal)
        return JobStartResponse(status="processing", message="File processing started successfully.", job_id=job.id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {e}")


@router.get("/visual/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobStatusResponse:
    try:
        result = await db.execute(
            select(IngestionJob).where(
                IngestionJob.id == job_id,
                IngestionJob.session_id == f"visual_sync_{current_user.id}",
            )
        )
        job = result.scalars().first()
        if not job:
            result = await db.execute(
                select(IngestionJob).where(
                    IngestionJob.id == job_id,
                    IngestionJob.session_id == f"file_upload_{current_user.id}",
                )
            )
            job = result.scalars().first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            items_processed=job.items_processed,
            total_items=job.total_items,
            error_message=job.error_message,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job status: {e}")
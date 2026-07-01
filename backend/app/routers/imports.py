# ============================================================
# Router — PDF Imports & Preview Editor
# ============================================================

import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DBSession
from app.models.import_job import PdfImportJob
from app.services.pdf_parser_service import PdfParserService
from app.schemas.pdf_import import (
    PreviewResponse, 
    ImportStatusResponse, 
    ImportJobResponse,
    ParsedTopicNode,
    PreviewNodePatch,
    ValidationResponse
)

router = APIRouter(tags=["Imports"])

MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def validate_pdf(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid mime type. Must be application/pdf.")

async def validate_pdf_size(file: UploadFile) -> bytes:
    """Read file bytes and enforce max size to prevent OOM on malicious uploads."""
    file_bytes = await file.read()
    if len(file_bytes) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF file exceeds maximum size of {MAX_PDF_SIZE_BYTES // (1024*1024)}MB."
        )
    return file_bytes

async def _get_job_or_404(db, import_id: uuid.UUID, user_id: uuid.UUID) -> PdfImportJob:
    stmt = select(PdfImportJob).where(PdfImportJob.id == import_id, PdfImportJob.user_id == user_id)
    job = (await db.execute(stmt)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Import session not found")
    return job

@router.post(
    "/skills/{skill_id}/import/pdf/preview",
    response_model=PreviewResponse,
    summary="Preview parsed topics without saving to DB",
)
async def preview_pdf_import(
    skill_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    file: UploadFile = File(...)
):
    validate_pdf(file)
    file_bytes = await validate_pdf_size(file)
    svc = PdfParserService(db)
    text = svc.extract_text_from_pdf(file_bytes)
    parsed_nodes = svc.parse_hierarchy_from_text(text)
    tree_data = svc.build_preview_tree(parsed_nodes)
    return {"success": True, "topics": tree_data}

@router.post(
    "/skills/{skill_id}/import/pdf",
    response_model=ImportJobResponse,
    summary="Upload and start a PDF import session",
)
async def start_pdf_import(
    skill_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    validate_pdf(file)
    file_bytes = await file.read()
    
    job_id = uuid.uuid4()
    job = PdfImportJob(
        id=job_id,
        user_id=current_user.id,
        skill_id=skill_id,
        filename=file.filename,
        status="pending"
    )
    db.add(job)
    await db.commit()
    
    from app.database.session import async_session_factory
    async def bg_runner():
        async with async_session_factory() as session:
            svc = PdfParserService(session)
            await svc.execute_import_job(job_id, file_bytes)

    background_tasks.add_task(bg_runner)
    
    return {
        "success": True, 
        "importId": job_id, 
        "skillId": skill_id,
        "totalTopics": 0,
        "createdTopics": 0,
        "durationMs": 0
    }

@router.get(
    "/imports/{import_id}",
    response_model=ImportStatusResponse,
    summary="Get import session state including tree data",
)
async def get_import_session(
    import_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    job = await _get_job_or_404(db, import_id, current_user.id)
    return {
        "id": job.id,
        "status": job.status,
        "totalTopics": job.total_topics,
        "createdTopics": job.created_topics,
        "failedTopics": job.failed_topics,
        "errorMessage": job.error_message,
        "treeData": job.tree_data
    }

@router.patch(
    "/imports/{import_id}/tree",
    summary="Overwrite entire preview tree",
)
async def update_entire_tree(
    import_id: uuid.UUID,
    tree_data: List[ParsedTopicNode],
    current_user: CurrentUser,
    db: DBSession,
):
    job = await _get_job_or_404(db, import_id, current_user.id)
    job.tree_data = [node.model_dump() for node in tree_data]
    await db.commit()
    return {"success": True}

@router.patch(
    "/imports/{import_id}/node/{node_id}",
    summary="Update a specific node in the preview tree",
)
async def update_tree_node(
    import_id: uuid.UUID,
    node_id: str,
    patch: PreviewNodePatch,
    current_user: CurrentUser,
    db: DBSession,
):
    job = await _get_job_or_404(db, import_id, current_user.id)
    if not job.tree_data:
        raise HTTPException(status_code=400, detail="No tree data exists.")
        
    tree = job.tree_data.copy()
    node_found = False
    for node in tree:
        if node["id"] == node_id:
            if patch.title is not None:
                node["title"] = patch.title
            if patch.parent_id is not None:
                node["parent_id"] = patch.parent_id
            if patch.order_index is not None:
                node["order_index"] = patch.order_index
            node_found = True
            break
            
    if not node_found:
        raise HTTPException(status_code=404, detail="Node not found in tree")
        
    # Re-assign to trigger SQLAlchemy JSON mutation detection, though .copy() helps
    job.tree_data = tree
    await db.commit()
    return {"success": True}

@router.delete(
    "/imports/{import_id}/node/{node_id}",
    summary="Delete a node and its descendants from the preview tree",
)
async def delete_tree_node(
    import_id: uuid.UUID,
    node_id: str,
    current_user: CurrentUser,
    db: DBSession,
):
    job = await _get_job_or_404(db, import_id, current_user.id)
    if not job.tree_data:
        raise HTTPException(status_code=400, detail="No tree data exists.")
        
    tree = job.tree_data.copy()
    
    # Need to delete the node and all descendants recursively
    to_delete = {node_id}
    # Loop to find all descendants (may require multiple passes for deep trees)
    # Better: build an adjacency list to find descendants
    children_map = {}
    for n in tree:
        pid = n.get("parent_id")
        if pid not in children_map:
            children_map[pid] = []
        children_map[pid].append(n["id"])
        
    def collect_descendants(curr_id):
        if curr_id in children_map:
            for child_id in children_map[curr_id]:
                to_delete.add(child_id)
                collect_descendants(child_id)
                
    collect_descendants(node_id)
    
    new_tree = [n for n in tree if n["id"] not in to_delete]
    job.tree_data = new_tree
    await db.commit()
    return {"success": True, "deletedCount": len(to_delete)}

@router.post(
    "/imports/{import_id}/validate",
    response_model=ValidationResponse,
    summary="Validate current preview tree state",
)
async def validate_import_tree(
    import_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    job = await _get_job_or_404(db, import_id, current_user.id)
    svc = PdfParserService(db)
    errors = svc.validate_preview_tree(job.tree_data or [])
    return {"success": len(errors) == 0, "errors": errors}

@router.post(
    "/imports/{import_id}/save",
    summary="Commit the preview tree to the database",
)
async def save_import_session(
    import_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    svc = PdfParserService(db)
    # The service method validates and inserts
    await svc.commit_import_session(import_id)
    return {"success": True}

@router.delete(
    "/imports/{import_id}",
    summary="Discard an import session",
)
async def delete_import_session(
    import_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    job = await _get_job_or_404(db, import_id, current_user.id)
    await db.delete(job)
    await db.commit()
    return {"success": True}

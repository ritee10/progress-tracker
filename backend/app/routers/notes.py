# ============================================================
# Router — Notes
# ============================================================

import uuid
from typing import List

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.services.note_service import NoteService
from app.utils.response import success_response

router = APIRouter(tags=["Notes"])


@router.post(
    "/notes",
    response_model=dict,
    status_code=201,
    summary="Create Note",
)
async def create_note(data: NoteCreate, current_user: CurrentUser, db: DBSession):
    service = NoteService(db)
    note = await service.create_note(current_user, data)
    return success_response(data=NoteResponse.model_validate(note).model_dump(mode="json"))


@router.get(
    "/notes/{note_id}",
    response_model=dict,
    summary="Get Note",
)
async def get_note(note_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = NoteService(db)
    note = await service.get_note(current_user, note_id)
    return success_response(data=NoteResponse.model_validate(note).model_dump(mode="json"))


@router.put(
    "/notes/{note_id}",
    response_model=dict,
    summary="Update Note",
)
async def update_note(note_id: uuid.UUID, data: NoteUpdate, current_user: CurrentUser, db: DBSession):
    service = NoteService(db)
    note = await service.update_note(current_user, note_id, data)
    return success_response(data=NoteResponse.model_validate(note).model_dump(mode="json"))


@router.delete(
    "/notes/{note_id}",
    response_model=dict,
    summary="Delete Note",
)
async def delete_note(note_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = NoteService(db)
    await service.delete_note(current_user, note_id)
    return success_response(message="Note deleted successfully.")


@router.get(
    "/skills/{skill_id}/notes",
    response_model=dict,
    summary="List Notes for Skill",
)
async def list_skill_notes(
    skill_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    service = NoteService(db)
    notes = await service.list_skill_notes(current_user, skill_id, skip, limit)
    return success_response(data=[NoteResponse.model_validate(n).model_dump(mode="json") for n in notes])


@router.get(
    "/topics/{topic_id}/notes",
    response_model=dict,
    summary="List Notes for Topic",
)
async def list_topic_notes(
    topic_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    service = NoteService(db)
    notes = await service.list_topic_notes(current_user, topic_id, skip, limit)
    return success_response(data=[NoteResponse.model_validate(n).model_dump(mode="json") for n in notes])

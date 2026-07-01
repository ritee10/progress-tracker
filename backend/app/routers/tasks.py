# ============================================================
# Router — Tasks
# ============================================================

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import CurrentUser, DBSession
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.utils.pagination import PaginationParams, paginate
from app.utils.response import success_response

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=dict,
    status_code=201,
    summary="Create a new study task",
)
async def create_task(
    data: TaskCreate, current_user: CurrentUser, db: DBSession
):
    """Add a new task to the user's study plan."""
    repo = TaskRepository(db)
    task = Task(
        user_id=current_user.id,
        skill_id=data.skill_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        estimated_minutes=data.estimated_minutes,
        is_recurring=data.is_recurring,
    )
    task = await repo.create(task)
    return success_response(
        data=TaskResponse.model_validate(task).model_dump(mode="json"),
        message="Task created",
    )


@router.get(
    "",
    response_model=dict,
    summary="List study tasks",
)
async def get_tasks(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    skill_id: Optional[uuid.UUID] = Query(None),
):
    """Fetch the user's tasks with optional filters and pagination."""
    repo = TaskRepository(db)
    pagination = PaginationParams(page=page, page_size=page_size)

    items = await repo.get_all_by_user(
        user_id=current_user.id,
        offset=pagination.offset,
        limit=pagination.limit,
        status=status,
        skill_id=skill_id,
    )
    total = await repo.count_by_user(
        user_id=current_user.id, status=status, skill_id=skill_id
    )
    result = paginate(
        items=[TaskResponse.model_validate(t).model_dump(mode="json") for t in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return success_response(data=result.model_dump())


@router.put(
    "/{task_id}",
    response_model=dict,
    summary="Update a task",
)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update an existing study task."""
    repo = TaskRepository(db)
    task = await repo.get_by_id(task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = data.model_dump(exclude_unset=True)

    # Auto-set completed_at when status changes to completed
    if update_data.get("status") == "completed" and task.status != "completed":
        from app.utils.date_utils import today_utc
        update_data["completed_at"] = today_utc()

    for field, value in update_data.items():
        setattr(task, field, value)

    task = await repo.update(task)
    return success_response(
        data=TaskResponse.model_validate(task).model_dump(mode="json"),
        message="Task updated",
    )


@router.delete(
    "/{task_id}",
    response_model=dict,
    summary="Delete a task",
)
async def delete_task(
    task_id: uuid.UUID, current_user: CurrentUser, db: DBSession
):
    """Hard-delete a study task."""
    repo = TaskRepository(db)
    task = await repo.get_by_id(task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await repo.delete(task)
    return success_response(message="Task deleted")

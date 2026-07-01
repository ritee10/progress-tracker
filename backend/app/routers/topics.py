# ============================================================
# Router — Topics
# ============================================================

import uuid

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.topic import (
    TopicCreate, TopicUpdate, TopicResponse, TopicTreeResponse,
    TopicMoveRequest, TopicReorderRequest, TopicSearchResponse
)
from app.services.topic_service import TopicService
from app.utils.response import success_response

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.post(
    "",
    response_model=dict,
    status_code=201,
    summary="Create Root Topic",
)
async def create_root_topic(data: TopicCreate, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.create_root_topic(current_user, data)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.post(
    "/{parent_id}/children",
    response_model=dict,
    status_code=201,
    summary="Create Child Topic",
)
async def create_child_topic(parent_id: uuid.UUID, data: TopicCreate, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.create_child_topic(current_user, parent_id, data)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.get(
    "/tree",
    response_model=dict,
    summary="Get Full Tree",
)
async def get_tree(current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    tree = await service.get_tree(current_user)
    return success_response(data=[t.model_dump(mode="json") for t in tree])


@router.get(
    "/search",
    response_model=dict,
    summary="Search Topics",
)
async def search_topics(
    current_user: CurrentUser, 
    db: DBSession,
    q: str = Query(..., min_length=1)
):
    service = TopicService(db)
    results = await service.search_topics(current_user, q)
    return success_response(data=[TopicSearchResponse(**r).model_dump(mode="json") for r in results])


@router.post(
    "/reorder",
    response_model=dict,
    summary="Reorder Siblings",
)
async def reorder_topics(data: TopicReorderRequest, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    await service.reorder_topics(current_user, data.parent_id, data.topic_ids)
    return success_response(message="Topics reordered successfully")


@router.get(
    "/{topic_id}",
    response_model=dict,
    summary="Get Topic",
)
async def get_topic(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.get_topic(current_user, topic_id)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.put(
    "/{topic_id}",
    response_model=dict,
    summary="Update Topic",
)
async def update_topic(topic_id: uuid.UUID, data: TopicUpdate, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.update_topic(current_user, topic_id, data)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.delete(
    "/{topic_id}",
    response_model=dict,
    summary="Soft Delete Topic",
)
async def delete_topic(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    await service.soft_delete_topic(current_user, topic_id)
    return success_response(message="Topic and descendants deleted")


@router.post(
    "/{topic_id}/restore",
    response_model=dict,
    summary="Restore Topic",
)
async def restore_topic(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    await service.restore_topic(current_user, topic_id)
    return success_response(message="Topic and descendants restored")


@router.get(
    "/{topic_id}/subtree",
    response_model=dict,
    summary="Get Subtree",
)
async def get_subtree(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    subtree = await service.get_subtree(current_user, topic_id)
    return success_response(data=subtree.model_dump(mode="json") if subtree else None)


@router.get(
    "/{topic_id}/ancestors",
    response_model=dict,
    summary="Get Ancestors",
)
async def get_ancestors(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    ancestors = await service.get_ancestors(current_user, topic_id)
    return success_response(data=[TopicResponse.model_validate(a).model_dump(mode="json") for a in ancestors])


@router.get(
    "/{topic_id}/descendants",
    response_model=dict,
    summary="Get Descendants",
)
async def get_descendants(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    descendants = await service.get_descendants(current_user, topic_id)
    return success_response(data=[TopicResponse.model_validate(d).model_dump(mode="json") for d in descendants])


@router.post(
    "/{topic_id}/move",
    response_model=dict,
    summary="Move Node",
)
async def move_topic(topic_id: uuid.UUID, data: TopicMoveRequest, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.move_topic(current_user, topic_id, data.new_parent_id)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.post(
    "/{topic_id}/pin",
    response_model=dict,
    summary="Pin Topic",
)
async def pin_topic(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.pin_topic(current_user, topic_id)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.post(
    "/{topic_id}/unpin",
    response_model=dict,
    summary="Unpin Topic",
)
async def unpin_topic(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.unpin_topic(current_user, topic_id)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.post(
    "/{topic_id}/archive",
    response_model=dict,
    summary="Archive Topic",
)
async def archive_topic(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.archive_topic(current_user, topic_id)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))


@router.post(
    "/{topic_id}/unarchive",
    response_model=dict,
    summary="Unarchive Topic",
)
async def unarchive_topic(topic_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    service = TopicService(db)
    topic = await service.unarchive_topic(current_user, topic_id)
    return success_response(data=TopicResponse.model_validate(topic).model_dump(mode="json"))

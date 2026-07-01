# ============================================================
# Schemas — PDF Import
# ============================================================

from typing import List, Optional
from pydantic import BaseModel, UUID4

class ParsedTopicNode(BaseModel):
    id: str
    parent_id: Optional[str]
    title: str
    number: str
    depth: int
    order_index: int

class PreviewResponse(BaseModel):
    success: bool
    topics: List[ParsedTopicNode]

class ImportStatusResponse(BaseModel):
    id: UUID4
    status: str
    totalTopics: int
    createdTopics: int
    failedTopics: int
    errorMessage: Optional[str] = None
    treeData: Optional[List[ParsedTopicNode]] = None

class ImportJobResponse(BaseModel):
    success: bool
    importId: UUID4
    skillId: UUID4
    totalTopics: int
    createdTopics: int
    durationMs: int

class PreviewNodePatch(BaseModel):
    title: Optional[str] = None
    parent_id: Optional[str] = None
    order_index: Optional[int] = None

class ValidationResponse(BaseModel):
    success: bool
    errors: List[str]

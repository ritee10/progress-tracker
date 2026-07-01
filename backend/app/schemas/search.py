from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Any, Literal
from datetime import datetime

class SearchResult(BaseModel):
    id: UUID4
    type: Literal["skill", "topic", "note"]
    name: str
    skill_id: UUID4
    matched_field: str
    parent_id: Optional[UUID4] = None
    path: Optional[str] = None
    depth: Optional[int] = None
    url: Optional[str] = None

class GlobalSearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[SearchResult]

class TopicSearchResult(BaseModel):
    id: UUID4
    title: str
    skill_id: UUID4
    parent_id: Optional[UUID4] = None
    depth: int
    path: str
    level: int

class TopicSearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[TopicSearchResult]

class SkillSearchResult(BaseModel):
    id: UUID4
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: str
    status: str

class SkillSearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[SkillSearchResult]

class NoteSearchResult(BaseModel):
    id: UUID4
    skill_id: UUID4
    topic_id: UUID4
    content_preview: str
    urls: List[str]

class NoteSearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[NoteSearchResult]

class CrossSkillResultGroup(BaseModel):
    skill_id: UUID4
    skill_title: str
    results: List[SearchResult]

class CrossSkillSearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[CrossSkillResultGroup]

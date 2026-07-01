# ============================================================
# Schemas — Dashboard (Phase 13)
# ============================================================

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, UUID4

class SkillCardDTO(BaseModel):
    skillId: UUID4
    skillName: str
    skillIcon: Optional[str] = None
    progress: float
    topicsCount: int
    completedTopics: int
    remainingTopics: int
    currentStreak: int
    lastActivityDate: Optional[datetime] = None

class OverdueSkillDTO(BaseModel):
    skillId: UUID4
    skillName: str
    inactiveDays: int
    progress: float

class LastSeenDTO(BaseModel):
    skillId: Optional[UUID4] = None
    skillName: Optional[str] = None
    topicId: Optional[UUID4] = None
    topicName: Optional[str] = None
    lastSeenAt: Optional[datetime] = None

class ActivityDTO(BaseModel):
    id: UUID4
    activityType: str
    entityId: Optional[UUID4] = None
    metadataJson: Optional[Dict[str, Any]] = None
    createdAt: datetime

class DashboardStatisticsDTO(BaseModel):
    totalSkills: int
    totalTopics: int
    completedTopics: int
    pendingTopics: int
    completionPercentage: float
    totalNotes: int
    totalStudySessions: int
    currentStreak: int
    longestStreak: int
    pinnedSkillsCount: int
    overdueSkillsCount: int

class RecentAchievement(BaseModel):
    id: UUID4
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    rarity: Optional[str] = None
    earned_at: Optional[str] = None

class DashboardResponse(BaseModel):
    statistics: DashboardStatisticsDTO
    pinnedSkills: List[SkillCardDTO]
    overdueSkills: List[OverdueSkillDTO]
    lastSeen: LastSeenDTO
    recentActivity: List[ActivityDTO]
    skillCards: List[SkillCardDTO]

class LastSeenRequest(BaseModel):
    skillId: UUID4
    topicId: Optional[UUID4] = None

class ActivityFeedResponse(BaseModel):
    activities: List[ActivityDTO]
    total: int

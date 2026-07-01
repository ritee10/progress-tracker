# ============================================================
# Service — Dashboard (Phase 13)
# ============================================================

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from fastapi import HTTPException

from app.models.skill import Skill
from app.models.topic import Topic
from app.models.user import UserDashboardState
from app.models.activity import ActivityLog
from app.models.note import Note
from app.models.progress import Progress
from app.services.streak_service import StreakService
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardStatisticsDTO,
    SkillCardDTO,
    OverdueSkillDTO,
    LastSeenDTO,
    ActivityDTO,
)
from app.utils.date_utils import utc_now

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_activity(
        self, user_id: uuid.UUID, activity_type: str, entity_id: uuid.UUID = None, metadata: dict = None
    ) -> None:
        """Helper to asynchronously record an activity in the DB without breaking flows."""
        log = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            entity_id=entity_id,
            metadata_json=metadata or {}
        )
        self.db.add(log)
        # Note: flush/commit should generally be handled by the caller transaction

    async def update_last_seen(self, user_id: uuid.UUID, skill_id: uuid.UUID, topic_id: uuid.UUID = None) -> None:
        stmt = select(UserDashboardState).where(UserDashboardState.user_id == user_id)
        state = (await self.db.execute(stmt)).scalar_one_or_none()
        if not state:
            state = UserDashboardState(user_id=user_id)
            self.db.add(state)
        state.last_seen_skill_id = skill_id
        state.last_seen_topic_id = topic_id
        state.last_seen_at = utc_now()
        # Do NOT call commit() here — session lifecycle is managed by get_db() dependency
        await self.db.flush()

    async def get_activities(self, user_id: uuid.UUID, limit: int = 20, offset: int = 0) -> List[ActivityDTO]:
        stmt = select(ActivityLog).where(ActivityLog.user_id == user_id).order_by(desc(ActivityLog.created_at)).limit(limit).offset(offset)
        records = (await self.db.execute(stmt)).scalars().all()
        return [
            ActivityDTO(
                id=r.id,
                activityType=r.activity_type,
                entityId=r.entity_id,
                metadataJson=r.metadata_json,
                createdAt=r.created_at
            )
            for r in records
        ]

    async def get_full_dashboard(self, user_id: uuid.UUID) -> DashboardResponse:
        """
        Executes concurrent optimized queries to build the comprehensive Phase 13 dashboard.
        """
        # 1. Fetch Skills Data
        stmt_skills = select(Skill).where(Skill.user_id == user_id, Skill.deleted_at == None).order_by(desc(Skill.updated_at))
        skills_raw = (await self.db.execute(stmt_skills)).scalars().all()

        # Build Skill Cards & Classify them
        skill_cards = []
        pinned_skills = []
        overdue_skills = []
        
        now = utc_now()
        seven_days_ago = now - timedelta(days=7)
        
        for s in skills_raw:
            card = SkillCardDTO(
                skillId=s.id,
                skillName=s.title,
                skillIcon=s.icon,
                progress=float(s.progress_percent),
                topicsCount=s.total_nodes,
                completedTopics=s.completed_nodes,
                remainingTopics=s.total_nodes - s.completed_nodes,
                currentStreak=0, # Need advanced logic or streak model if tracked per skill, defaulting to 0 for DTO mapping
                lastActivityDate=s.last_activity_at or s.created_at
            )
            skill_cards.append(card)
            
            if s.is_pinned:
                pinned_skills.append(card)
                
            # Overdue Logic
            last_act = s.last_activity_at or s.created_at
            if last_act < seven_days_ago and s.status != "completed":
                inactive_days = (now - last_act).days
                overdue_skills.append(
                    OverdueSkillDTO(
                        skillId=s.id,
                        skillName=s.title,
                        inactiveDays=inactive_days,
                        progress=float(s.progress_percent)
                    )
                )

        # Sort overdue
        overdue_skills.sort(key=lambda x: x.inactiveDays, reverse=True)

        # 2. Fetch Last Seen
        stmt_state = select(UserDashboardState).where(UserDashboardState.user_id == user_id)
        state = (await self.db.execute(stmt_state)).scalar_one_or_none()
        
        last_seen = LastSeenDTO()
        if state and state.last_seen_skill_id:
            last_seen.skillId = state.last_seen_skill_id
            last_seen.lastSeenAt = state.last_seen_at
            # Fast inner query for titles
            skill_obj = next((s for s in skills_raw if s.id == state.last_seen_skill_id), None)
            if skill_obj:
                last_seen.skillName = skill_obj.title
            
            if state.last_seen_topic_id:
                last_seen.topicId = state.last_seen_topic_id
                stmt_t = select(Topic.title).where(Topic.id == state.last_seen_topic_id)
                last_seen.topicName = (await self.db.execute(stmt_t)).scalar_one_or_none()

        # 3. Fetch Recent Activity
        recent_activity = await self.get_activities(user_id, limit=20)

        # 4. Fetch Statistics (Aggregated safely)
        stmt_topics = select(func.count(Topic.id)).where(Topic.user_id == user_id, Topic.deleted_at == None)
        stmt_topics_completed = select(func.count(Topic.id)).where(Topic.user_id == user_id, Topic.deleted_at == None, Topic.progress_percent == 100)
        stmt_notes = select(func.count(Note.id)).where(Note.user_id == user_id, Note.deleted_at == None)
        stmt_sessions = select(func.count(Progress.id)).where(Progress.user_id == user_id)

        # Run aggregated metrics sequentially on the shared AsyncSession.
        # AsyncSession is NOT safe for concurrent use via asyncio.gather on a single session.
        total_topics = (await self.db.scalar(stmt_topics)) or 0
        completed_topics = (await self.db.scalar(stmt_topics_completed)) or 0
        total_notes = (await self.db.scalar(stmt_notes)) or 0
        total_sessions = (await self.db.scalar(stmt_sessions)) or 0

        total_topics = total_topics or 0
        completed_topics = completed_topics or 0
        total_notes = total_notes or 0
        total_sessions = total_sessions or 0

        completion_pct = (completed_topics / total_topics * 100) if total_topics > 0 else 0.0

        # Streak System
        streak_svc = StreakService(self.db)
        streak_stats = await streak_svc.getStats(user_id)

        statistics = DashboardStatisticsDTO(
            totalSkills=len(skills_raw),
            totalTopics=total_topics,
            completedTopics=completed_topics,
            pendingTopics=total_topics - completed_topics,
            completionPercentage=float(completion_pct),
            totalNotes=total_notes,
            totalStudySessions=total_sessions,
            currentStreak=streak_stats["currentStreak"],
            longestStreak=streak_stats["longestStreak"],
            pinnedSkillsCount=len(pinned_skills),
            overdueSkillsCount=len(overdue_skills)
        )

        return DashboardResponse(
            statistics=statistics,
            pinnedSkills=pinned_skills,
            overdueSkills=overdue_skills,
            lastSeen=last_seen,
            recentActivity=recent_activity,
            skillCards=skill_cards
        )

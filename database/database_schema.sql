-- ============================================================
-- SKILL PROGRESS TRACKER — COMPLETE DATABASE SCHEMA
-- PostgreSQL 16 | Production-Ready
-- ============================================================
-- Version  : 1.0.0
-- Created  : 2026-06-22
-- Author   : Database Architecture Team
-- License  : Proprietary
-- ============================================================
--
-- This file contains the COMPLETE database schema including:
--   • Custom ENUM types
--   • Extension activation
--   • 28+ tables with full constraints
--   • Foreign key relationships
--   • Indexes (B-tree, composite, partial, unique, GIN)
--   • Triggers for audit logging and automation
--   • Row Level Security (RLS) policies
--   • Materialized views for analytics
--   • Seed data for categories, skills, topics, and achievements
--
-- EXECUTION ORDER: Run this file top-to-bottom in a single
-- transaction against a fresh PostgreSQL 16 database.
-- ============================================================

BEGIN;

-- ============================================================
-- 0. EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";         -- Trigram fuzzy search
CREATE EXTENSION IF NOT EXISTS "btree_gin";       -- GIN index support for scalars

-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

-- 1.1 Difficulty levels for skills, topics, and problems
CREATE TYPE difficulty_level AS ENUM (
    'beginner',
    'intermediate',
    'advanced',
    'expert'
);

-- 1.2 Status for skills and topic progress
CREATE TYPE skill_status AS ENUM (
    'not_started',
    'in_progress',
    'completed',
    'mastered',
    'archived'
);

-- 1.3 Goal lifecycle status
CREATE TYPE goal_status AS ENUM (
    'not_started',
    'in_progress',
    'completed',
    'paused',
    'abandoned'
);

-- 1.4 Roadmap lifecycle status
CREATE TYPE roadmap_status AS ENUM (
    'draft',
    'active',
    'paused',
    'completed',
    'archived'
);

-- 1.5 Project lifecycle status
CREATE TYPE project_status AS ENUM (
    'ideation',
    'planning',
    'in_progress',
    'testing',
    'deployed',
    'completed',
    'on_hold',
    'abandoned'
);

-- 1.6 Notification types
CREATE TYPE notification_type AS ENUM (
    'reminder',
    'achievement',
    'streak_alert',
    'recommendation',
    'system',
    'social',
    'milestone',
    'weekly_digest'
);

-- 1.7 Resource types for learning materials
CREATE TYPE resource_type AS ENUM (
    'article',
    'video',
    'course',
    'book',
    'documentation',
    'tutorial',
    'podcast',
    'github_repo',
    'tool',
    'other'
);

-- 1.8 Achievement/badge types
CREATE TYPE achievement_type AS ENUM (
    'streak',
    'milestone',
    'skill_mastery',
    'consistency',
    'speed',
    'community',
    'special',
    'seasonal'
);

-- 1.9 Visibility levels for shared content
CREATE TYPE visibility_level AS ENUM (
    'private',
    'friends',
    'public'
);

-- 1.10 User roles
CREATE TYPE user_role AS ENUM (
    'user',
    'premium',
    'mentor',
    'admin',
    'super_admin'
);

-- 1.11 Auth provider
CREATE TYPE auth_provider AS ENUM (
    'email',
    'google',
    'github',
    'linkedin'
);

-- 1.12 Study session activity types
CREATE TYPE activity_type AS ENUM (
    'reading',
    'watching',
    'coding',
    'practicing',
    'revising',
    'project_work',
    'assessment',
    'note_taking',
    'discussion'
);

-- 1.13 Certification status
CREATE TYPE certification_status AS ENUM (
    'planned',
    'in_progress',
    'earned',
    'expired',
    'renewed'
);

-- 1.14 Note types
CREATE TYPE note_type AS ENUM (
    'topic_note',
    'study_note',
    'revision_note',
    'project_note',
    'journal',
    'general'
);

-- 1.15 Audit action types
CREATE TYPE audit_action AS ENUM (
    'create',
    'update',
    'delete',
    'login',
    'logout',
    'export',
    'import',
    'admin_action'
);


-- ============================================================
-- 2. CORE TABLES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 2.1  users
-- Purpose: Core identity table for all registered users
-- ──────────────────────────────────────────────────────────────
CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email               VARCHAR(255) NOT NULL,
    password_hash       VARCHAR(255),                         -- NULL for OAuth-only accounts
    display_name        VARCHAR(50)  NOT NULL,
    avatar_url          TEXT,
    role                user_role    NOT NULL DEFAULT 'user',
    auth_provider       auth_provider NOT NULL DEFAULT 'email',
    auth_provider_id    VARCHAR(255),                         -- External provider user ID
    email_verified      BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    last_login_at       TIMESTAMPTZ,
    last_active_at      TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,                          -- Soft delete

    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_display_name_length CHECK (char_length(display_name) BETWEEN 2 AND 50)
);

-- ──────────────────────────────────────────────────────────────
-- 2.2  profiles
-- Purpose: Extended user profile for personalization & portfolio
-- One-to-one relationship with users
-- ──────────────────────────────────────────────────────────────
CREATE TABLE profiles (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    bio                 TEXT,
    primary_goal        VARCHAR(100),
    target_role         VARCHAR(100),
    target_companies    JSONB        DEFAULT '[]'::JSONB,     -- ["Google", "Microsoft"]
    target_timeline     DATE,
    daily_study_hours   NUMERIC(4,2) DEFAULT 2.0,
    preferred_study_time VARCHAR(20)  DEFAULT 'evening',
    preferred_content   JSONB        DEFAULT '["video","article"]'::JSONB,
    education           JSONB        DEFAULT '[]'::JSONB,     -- [{institution, degree, year}]
    work_experience     JSONB        DEFAULT '[]'::JSONB,     -- [{company, role, years}]
    github_url          VARCHAR(500),
    linkedin_url        VARCHAR(500),
    leetcode_url        VARCHAR(500),
    portfolio_url       VARCHAR(500),
    timezone            VARCHAR(50)  DEFAULT 'Asia/Kolkata',
    profile_visibility  visibility_level NOT NULL DEFAULT 'private',
    onboarding_completed BOOLEAN     NOT NULL DEFAULT FALSE,
    xp_total            INTEGER      NOT NULL DEFAULT 0,
    current_level       INTEGER      NOT NULL DEFAULT 1,
    current_streak      INTEGER      NOT NULL DEFAULT 0,
    longest_streak      INTEGER      NOT NULL DEFAULT 0,
    streak_last_date    DATE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_profiles_user UNIQUE (user_id),
    CONSTRAINT ck_profiles_daily_hours CHECK (daily_study_hours BETWEEN 0.5 AND 16.0),
    CONSTRAINT ck_profiles_xp CHECK (xp_total >= 0),
    CONSTRAINT ck_profiles_level CHECK (current_level BETWEEN 1 AND 100),
    CONSTRAINT ck_profiles_streak CHECK (current_streak >= 0 AND longest_streak >= 0)
);

-- ──────────────────────────────────────────────────────────────
-- 2.3  categories
-- Purpose: Top-level grouping for skills (e.g., "DSA", "AI/ML",
--          "Core CS", "Cloud", "DevOps")
-- Self-referencing hierarchy via parent_id
-- ──────────────────────────────────────────────────────────────
CREATE TABLE categories (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(100) NOT NULL,
    slug                VARCHAR(100) NOT NULL,
    description         TEXT,
    icon_url            TEXT,
    parent_id           UUID,
    display_order       INTEGER      NOT NULL DEFAULT 0,
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_categories_slug UNIQUE (slug),
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- ──────────────────────────────────────────────────────────────
-- 2.4  skills
-- Purpose: Individual trackable skills within a category
--          (e.g., "Dynamic Programming", "Neural Networks")
-- ──────────────────────────────────────────────────────────────
CREATE TABLE skills (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id         UUID NOT NULL,
    name                VARCHAR(150) NOT NULL,
    slug                VARCHAR(150) NOT NULL,
    description         TEXT,
    difficulty          difficulty_level NOT NULL DEFAULT 'beginner',
    estimated_hours     NUMERIC(6,1),                         -- Approx hours to learn
    icon_url            TEXT,
    is_custom           BOOLEAN      NOT NULL DEFAULT FALSE,
    created_by          UUID,                                 -- user_id for custom skills
    prerequisite_ids    UUID[]       DEFAULT '{}',            -- Array of prerequisite skill IDs
    tags                TEXT[]       DEFAULT '{}',            -- Flexible tagging
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_skills_slug UNIQUE (slug),
    CONSTRAINT fk_skills_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    CONSTRAINT fk_skills_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT ck_skills_name_length CHECK (char_length(name) BETWEEN 2 AND 150)
);

-- ──────────────────────────────────────────────────────────────
-- 2.5  topics
-- Purpose: Specific topics within a skill
--          (e.g., Skill="Arrays" → Topics: "Two Pointer",
--           "Sliding Window", "Kadane's Algorithm")
-- ──────────────────────────────────────────────────────────────
CREATE TABLE topics (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id            UUID NOT NULL,
    name                VARCHAR(200) NOT NULL,
    slug                VARCHAR(200) NOT NULL,
    description         TEXT,
    difficulty          difficulty_level NOT NULL DEFAULT 'beginner',
    estimated_hours     NUMERIC(5,1),
    display_order       INTEGER      NOT NULL DEFAULT 0,
    importance          VARCHAR(20)  DEFAULT 'medium',        -- low, medium, high, critical
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_topics_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    CONSTRAINT uq_topics_skill_slug UNIQUE (skill_id, slug),
    CONSTRAINT ck_topics_importance CHECK (importance IN ('low', 'medium', 'high', 'critical'))
);

-- ──────────────────────────────────────────────────────────────
-- 2.6  subtopics
-- Purpose: Granular breakdown within a topic
--          (e.g., Topic="Sorting" → Subtopics: "Merge Sort",
--           "Quick Sort", "Heap Sort")
-- ──────────────────────────────────────────────────────────────
CREATE TABLE subtopics (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id            UUID NOT NULL,
    name                VARCHAR(200) NOT NULL,
    slug                VARCHAR(200) NOT NULL,
    description         TEXT,
    display_order       INTEGER      NOT NULL DEFAULT 0,
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_subtopics_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT uq_subtopics_topic_slug UNIQUE (topic_id, slug)
);


-- ============================================================
-- 3. ROADMAP TABLES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 3.1  roadmaps
-- Purpose: Learning path templates and user-created roadmaps
-- ──────────────────────────────────────────────────────────────
CREATE TABLE roadmaps (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title               VARCHAR(200) NOT NULL,
    slug                VARCHAR(200) NOT NULL,
    description         TEXT,
    category_id         UUID,
    difficulty          difficulty_level NOT NULL DEFAULT 'beginner',
    estimated_days      INTEGER,
    estimated_hours     NUMERIC(7,1),
    is_template         BOOLEAN      NOT NULL DEFAULT FALSE,  -- TRUE = system/community template
    is_ai_generated     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_by          UUID,                                 -- NULL for system templates
    forked_from_id      UUID,
    visibility          visibility_level NOT NULL DEFAULT 'private',
    status              roadmap_status   NOT NULL DEFAULT 'draft',
    tags                TEXT[]       DEFAULT '{}',
    total_sections      INTEGER      NOT NULL DEFAULT 0,
    total_topics        INTEGER      NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,

    CONSTRAINT uq_roadmaps_slug UNIQUE (slug),
    CONSTRAINT fk_roadmaps_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT fk_roadmaps_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_roadmaps_forked_from FOREIGN KEY (forked_from_id) REFERENCES roadmaps(id) ON DELETE SET NULL,
    CONSTRAINT ck_roadmaps_title_length CHECK (char_length(title) BETWEEN 3 AND 200)
);

-- ──────────────────────────────────────────────────────────────
-- 3.2  roadmap_sections
-- Purpose: Ordered phases/stages within a roadmap
-- ──────────────────────────────────────────────────────────────
CREATE TABLE roadmap_sections (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id          UUID NOT NULL,
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    section_order       INTEGER      NOT NULL DEFAULT 0,
    estimated_days      INTEGER,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_rsections_roadmap FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id) ON DELETE CASCADE,
    CONSTRAINT uq_rsections_order UNIQUE (roadmap_id, section_order)
);

-- ──────────────────────────────────────────────────────────────
-- 3.3  roadmap_topics
-- Purpose: Topics assigned to a roadmap section (many-to-many
--          bridge between sections and topics/skills)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE roadmap_topics (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id          UUID NOT NULL,
    topic_id            UUID,                                 -- Reference to topics table
    skill_id            UUID,                                 -- OR reference to skills table
    custom_title        VARCHAR(200),                         -- For non-cataloged items
    topic_order         INTEGER      NOT NULL DEFAULT 0,
    estimated_hours     NUMERIC(5,1),
    is_milestone        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_rtopics_section FOREIGN KEY (section_id) REFERENCES roadmap_sections(id) ON DELETE CASCADE,
    CONSTRAINT fk_rtopics_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL,
    CONSTRAINT fk_rtopics_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    CONSTRAINT ck_rtopics_has_reference CHECK (
        topic_id IS NOT NULL OR skill_id IS NOT NULL OR custom_title IS NOT NULL
    )
);

-- ──────────────────────────────────────────────────────────────
-- 3.4  user_roadmaps
-- Purpose: Tracks a user's enrollment/progress on a roadmap
-- ──────────────────────────────────────────────────────────────
CREATE TABLE user_roadmaps (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    roadmap_id          UUID NOT NULL,
    status              roadmap_status   NOT NULL DEFAULT 'active',
    progress_percentage NUMERIC(5,2)     NOT NULL DEFAULT 0.00,
    started_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    target_completion   DATE,
    completed_at        TIMESTAMPTZ,
    last_activity_at    TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_uroadmaps_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_uroadmaps_roadmap FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id) ON DELETE CASCADE,
    CONSTRAINT uq_uroadmaps_user_roadmap UNIQUE (user_id, roadmap_id),
    CONSTRAINT ck_uroadmaps_progress CHECK (progress_percentage BETWEEN 0 AND 100)
);


-- ============================================================
-- 4. PROGRESS TRACKING TABLES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 4.1  user_topic_progress
-- Purpose: Per-user, per-topic progress tracking
--          The core progress table linking users to topics
-- ──────────────────────────────────────────────────────────────
CREATE TABLE user_topic_progress (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    topic_id            UUID NOT NULL,
    skill_id            UUID NOT NULL,                        -- Denormalized for faster queries
    status              skill_status     NOT NULL DEFAULT 'not_started',
    progress_percentage NUMERIC(5,2)     NOT NULL DEFAULT 0.00,
    proficiency_level   INTEGER          NOT NULL DEFAULT 0,  -- 0=none, 1=beginner, ..., 5=expert
    confidence_score    NUMERIC(5,2)     DEFAULT 0.00,
    total_time_minutes  INTEGER          NOT NULL DEFAULT 0,
    revision_count      INTEGER          NOT NULL DEFAULT 0,
    last_studied_at     TIMESTAMPTZ,
    last_revised_at     TIMESTAMPTZ,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_utprogress_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_utprogress_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_utprogress_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    CONSTRAINT uq_utprogress_user_topic UNIQUE (user_id, topic_id),
    CONSTRAINT ck_utprogress_progress CHECK (progress_percentage BETWEEN 0 AND 100),
    CONSTRAINT ck_utprogress_proficiency CHECK (proficiency_level BETWEEN 0 AND 5),
    CONSTRAINT ck_utprogress_confidence CHECK (confidence_score BETWEEN 0 AND 100),
    CONSTRAINT ck_utprogress_time CHECK (total_time_minutes >= 0),
    CONSTRAINT ck_utprogress_revision CHECK (revision_count >= 0)
);

-- ──────────────────────────────────────────────────────────────
-- 4.2  study_sessions
-- Purpose: Individual study activity logs with duration, type,
--          and quality rating
-- ──────────────────────────────────────────────────────────────
CREATE TABLE study_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    topic_id            UUID,
    skill_id            UUID,
    roadmap_id          UUID,                                 -- Optional: linked roadmap
    activity            activity_type    NOT NULL DEFAULT 'reading',
    title               VARCHAR(300),
    duration_minutes    INTEGER          NOT NULL,
    quality_rating      INTEGER,                              -- 1-5 self-assessment
    focus_score         INTEGER,                              -- 1-5
    notes               TEXT,
    session_date        DATE             NOT NULL DEFAULT CURRENT_DATE,
    started_at          TIMESTAMPTZ,
    ended_at            TIMESTAMPTZ,
    xp_earned           INTEGER          NOT NULL DEFAULT 0,
    is_timed            BOOLEAN          NOT NULL DEFAULT FALSE, -- TRUE = timer was used
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_sessions_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL,
    CONSTRAINT fk_sessions_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    CONSTRAINT fk_sessions_roadmap FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id) ON DELETE SET NULL,
    CONSTRAINT ck_sessions_duration CHECK (duration_minutes BETWEEN 1 AND 720),
    CONSTRAINT ck_sessions_quality CHECK (quality_rating IS NULL OR quality_rating BETWEEN 1 AND 5),
    CONSTRAINT ck_sessions_focus CHECK (focus_score IS NULL OR focus_score BETWEEN 1 AND 5),
    CONSTRAINT ck_sessions_xp CHECK (xp_earned >= 0),
    CONSTRAINT ck_sessions_date_not_future CHECK (session_date <= CURRENT_DATE + INTERVAL '1 day')
);

-- ──────────────────────────────────────────────────────────────
-- 4.3  revision_sessions
-- Purpose: Track spaced repetition revision cycles for topics
-- ──────────────────────────────────────────────────────────────
CREATE TABLE revision_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    topic_id            UUID NOT NULL,
    revision_number     INTEGER      NOT NULL DEFAULT 1,      -- 1st, 2nd, 3rd revision etc.
    quality_rating      INTEGER,                              -- 1-5 how well remembered
    confidence_before   NUMERIC(5,2),                         -- Confidence before revision
    confidence_after    NUMERIC(5,2),                         -- Confidence after revision
    duration_minutes    INTEGER,
    notes               TEXT,
    next_revision_date  DATE,                                 -- Calculated via spaced repetition
    revised_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_revisions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_revisions_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT ck_revisions_number CHECK (revision_number >= 1),
    CONSTRAINT ck_revisions_quality CHECK (quality_rating IS NULL OR quality_rating BETWEEN 1 AND 5),
    CONSTRAINT ck_revisions_confidence CHECK (
        (confidence_before IS NULL OR confidence_before BETWEEN 0 AND 100) AND
        (confidence_after IS NULL OR confidence_after BETWEEN 0 AND 100)
    )
);


-- ============================================================
-- 5. PROJECT & CERTIFICATION TABLES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 5.1  projects
-- Purpose: Personal, academic, or portfolio projects
-- ──────────────────────────────────────────────────────────────
CREATE TABLE projects (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    tech_stack          TEXT[]       DEFAULT '{}',             -- ["Python", "React", "PostgreSQL"]
    status              project_status   NOT NULL DEFAULT 'ideation',
    complexity          difficulty_level DEFAULT 'beginner',
    github_url          VARCHAR(500),
    deployment_url      VARCHAR(500),
    demo_url            VARCHAR(500),
    screenshot_urls     JSONB        DEFAULT '[]'::JSONB,
    progress_percentage NUMERIC(5,2)     NOT NULL DEFAULT 0.00,
    start_date          DATE,
    target_date         DATE,
    completed_at        TIMESTAMPTZ,
    is_featured         BOOLEAN      NOT NULL DEFAULT FALSE,
    skills_used         UUID[]       DEFAULT '{}',            -- Array of skill IDs
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,

    CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT ck_projects_progress CHECK (progress_percentage BETWEEN 0 AND 100),
    CONSTRAINT ck_projects_title_length CHECK (char_length(title) BETWEEN 3 AND 200),
    CONSTRAINT ck_projects_dates CHECK (target_date IS NULL OR start_date IS NULL OR target_date >= start_date)
);

-- ──────────────────────────────────────────────────────────────
-- 5.2  project_milestones
-- Purpose: Checkpoints within a project
-- ──────────────────────────────────────────────────────────────
CREATE TABLE project_milestones (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL,
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    milestone_order     INTEGER      NOT NULL DEFAULT 0,
    target_date         DATE,
    is_completed        BOOLEAN      NOT NULL DEFAULT FALSE,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_pmilestones_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────────────────
-- 5.3  certifications
-- Purpose: Professional certifications and course credentials
-- ──────────────────────────────────────────────────────────────
CREATE TABLE certifications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    name                VARCHAR(300) NOT NULL,
    issuing_body        VARCHAR(200) NOT NULL,
    category            VARCHAR(100),                         -- Cloud, Data, AI, Security, etc.
    status              certification_status NOT NULL DEFAULT 'planned',
    credential_id       VARCHAR(200),
    credential_url      VARCHAR(500),
    certificate_image_url TEXT,
    date_earned         DATE,
    expiry_date         DATE,
    course_total_modules INTEGER     DEFAULT 0,
    course_completed    INTEGER      DEFAULT 0,
    skills_mapped       UUID[]       DEFAULT '{}',
    cost                NUMERIC(10,2),
    notes               TEXT,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,

    CONSTRAINT fk_certs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT ck_certs_modules CHECK (course_completed <= course_total_modules),
    CONSTRAINT ck_certs_dates CHECK (expiry_date IS NULL OR date_earned IS NULL OR expiry_date > date_earned),
    CONSTRAINT ck_certs_cost CHECK (cost IS NULL OR cost >= 0)
);


-- ============================================================
-- 6. GOALS & MILESTONES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 6.1  goals
-- Purpose: User-defined learning or career goals with deadlines
-- ──────────────────────────────────────────────────────────────
CREATE TABLE goals (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    title               VARCHAR(300) NOT NULL,
    description         TEXT,
    category            VARCHAR(100),                         -- e.g., "Placement", "Upskilling"
    status              goal_status      NOT NULL DEFAULT 'not_started',
    priority            INTEGER          NOT NULL DEFAULT 3,  -- 1=highest, 5=lowest
    target_date         DATE,
    progress_percentage NUMERIC(5,2)     NOT NULL DEFAULT 0.00,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    linked_roadmap_id   UUID,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,

    CONSTRAINT fk_goals_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_goals_roadmap FOREIGN KEY (linked_roadmap_id) REFERENCES roadmaps(id) ON DELETE SET NULL,
    CONSTRAINT ck_goals_progress CHECK (progress_percentage BETWEEN 0 AND 100),
    CONSTRAINT ck_goals_priority CHECK (priority BETWEEN 1 AND 5)
);

-- ──────────────────────────────────────────────────────────────
-- 6.2  goal_milestones
-- Purpose: Measurable checkpoints within a goal
-- ──────────────────────────────────────────────────────────────
CREATE TABLE goal_milestones (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goal_id             UUID NOT NULL,
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    milestone_order     INTEGER      NOT NULL DEFAULT 0,
    target_date         DATE,
    target_value        NUMERIC(10,2),                        -- e.g., "100 problems"
    current_value       NUMERIC(10,2) DEFAULT 0,
    unit                VARCHAR(50),                          -- e.g., "problems", "hours", "topics"
    is_completed        BOOLEAN      NOT NULL DEFAULT FALSE,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_gmilestones_goal FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
    CONSTRAINT ck_gmilestones_values CHECK (current_value IS NULL OR current_value >= 0)
);


-- ============================================================
-- 7. NOTES & RESOURCES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 7.1  notes
-- Purpose: Flexible note-taking linked to any entity
--          (topic, project, study session, or standalone)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE notes (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    note_kind           note_type        NOT NULL DEFAULT 'general',
    title               VARCHAR(300),
    content             TEXT NOT NULL,
    -- Polymorphic references (only one should be non-null)
    topic_id            UUID,
    project_id          UUID,
    skill_id            UUID,
    session_id          UUID,
    tags                TEXT[]       DEFAULT '{}',
    is_pinned           BOOLEAN      NOT NULL DEFAULT FALSE,
    note_date           DATE         DEFAULT CURRENT_DATE,
    mood                VARCHAR(20),                          -- For journal entries
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,

    CONSTRAINT fk_notes_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_notes_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL,
    CONSTRAINT fk_notes_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    CONSTRAINT fk_notes_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    CONSTRAINT fk_notes_session FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE SET NULL,
    CONSTRAINT ck_notes_content_length CHECK (char_length(content) BETWEEN 1 AND 50000),
    CONSTRAINT ck_notes_mood CHECK (mood IS NULL OR mood IN ('great','good','neutral','struggling','frustrated'))
);

-- ──────────────────────────────────────────────────────────────
-- 7.2  resources
-- Purpose: Learning resources linked to topics or skills
-- ──────────────────────────────────────────────────────────────
CREATE TABLE resources (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID,                                 -- NULL for system resources
    topic_id            UUID,
    skill_id            UUID,
    title               VARCHAR(300) NOT NULL,
    url                 TEXT NOT NULL,
    resource_kind       resource_type    NOT NULL DEFAULT 'article',
    description         TEXT,
    difficulty          difficulty_level,
    is_free             BOOLEAN      DEFAULT TRUE,
    is_recommended      BOOLEAN      DEFAULT FALSE,           -- System/AI recommended
    rating              NUMERIC(3,1),                         -- User rating 1.0-5.0
    tags                TEXT[]       DEFAULT '{}',
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_resources_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_resources_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL,
    CONSTRAINT fk_resources_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    CONSTRAINT ck_resources_rating CHECK (rating IS NULL OR rating BETWEEN 1.0 AND 5.0)
);


-- ============================================================
-- 8. GAMIFICATION TABLES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 8.1  achievements
-- Purpose: Badge/achievement definitions (system-managed catalog)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE achievements (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(200) NOT NULL,
    slug                VARCHAR(200) NOT NULL,
    description         TEXT NOT NULL,
    icon_url            TEXT,
    achievement_kind    achievement_type NOT NULL DEFAULT 'milestone',
    category            VARCHAR(100),                         -- Grouping: "DSA", "Consistency", etc.
    criteria_type       VARCHAR(100) NOT NULL,                -- e.g., "dsa_problems_solved"
    criteria_value      INTEGER      NOT NULL,                -- Threshold: e.g., 100
    xp_reward           INTEGER      NOT NULL DEFAULT 0,
    rarity              VARCHAR(20)  NOT NULL DEFAULT 'common',
    is_repeatable       BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_achievements_slug UNIQUE (slug),
    CONSTRAINT ck_achievements_xp CHECK (xp_reward >= 0),
    CONSTRAINT ck_achievements_rarity CHECK (rarity IN ('common','uncommon','rare','epic','legendary')),
    CONSTRAINT ck_achievements_criteria CHECK (criteria_value > 0)
);

-- ──────────────────────────────────────────────────────────────
-- 8.2  user_achievements
-- Purpose: Records which users earned which achievements, when
-- ──────────────────────────────────────────────────────────────
CREATE TABLE user_achievements (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    achievement_id      UUID NOT NULL,
    earned_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    earn_count          INTEGER      NOT NULL DEFAULT 1,      -- For repeatable achievements
    notified            BOOLEAN      NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_uachievements_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_uachievements_achievement FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    CONSTRAINT uq_uachievements_non_repeatable UNIQUE (user_id, achievement_id),
    CONSTRAINT ck_uachievements_count CHECK (earn_count >= 1)
);

-- ──────────────────────────────────────────────────────────────
-- 8.3  daily_streaks
-- Purpose: Per-day activity record for streak calculation
--          One row per user per active day
-- ──────────────────────────────────────────────────────────────
CREATE TABLE daily_streaks (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    streak_date         DATE NOT NULL,
    total_minutes       INTEGER      NOT NULL DEFAULT 0,
    activities_count    INTEGER      NOT NULL DEFAULT 0,
    topics_touched      INTEGER      NOT NULL DEFAULT 0,
    xp_earned           INTEGER      NOT NULL DEFAULT 0,
    is_streak_day       BOOLEAN      NOT NULL DEFAULT TRUE,   -- FALSE if freeze used
    streak_freeze_used  BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_dstreaks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_dstreaks_user_date UNIQUE (user_id, streak_date),
    CONSTRAINT ck_dstreaks_minutes CHECK (total_minutes >= 0),
    CONSTRAINT ck_dstreaks_xp CHECK (xp_earned >= 0)
);


-- ============================================================
-- 9. ANALYTICS TABLES
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 9.1  analytics_snapshots
-- Purpose: Pre-computed daily analytics snapshots per user
--          for fast dashboard rendering and trend analysis
-- ──────────────────────────────────────────────────────────────
CREATE TABLE analytics_snapshots (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    snapshot_date       DATE NOT NULL,
    snapshot_type       VARCHAR(20)  NOT NULL DEFAULT 'daily', -- daily, weekly, monthly

    -- Study metrics
    total_study_minutes INTEGER      NOT NULL DEFAULT 0,
    sessions_count      INTEGER      NOT NULL DEFAULT 0,
    avg_session_minutes NUMERIC(6,1) DEFAULT 0,
    avg_quality_rating  NUMERIC(3,1),

    -- Progress metrics
    topics_started      INTEGER      NOT NULL DEFAULT 0,
    topics_completed    INTEGER      NOT NULL DEFAULT 0,
    topics_revised      INTEGER      NOT NULL DEFAULT 0,
    skills_improved     INTEGER      NOT NULL DEFAULT 0,

    -- DSA metrics (denormalized for fast reads)
    dsa_problems_solved INTEGER      DEFAULT 0,
    dsa_easy_count      INTEGER      DEFAULT 0,
    dsa_medium_count    INTEGER      DEFAULT 0,
    dsa_hard_count      INTEGER      DEFAULT 0,

    -- Readiness metrics
    overall_readiness   NUMERIC(5,2),                         -- 0-100 composite score
    dsa_readiness       NUMERIC(5,2),
    core_cs_readiness   NUMERIC(5,2),
    aptitude_readiness  NUMERIC(5,2),
    project_readiness   NUMERIC(5,2),

    -- Gamification metrics
    xp_earned           INTEGER      NOT NULL DEFAULT 0,
    current_level       INTEGER      DEFAULT 1,
    current_streak      INTEGER      DEFAULT 0,
    badges_earned       INTEGER      DEFAULT 0,

    -- Velocity metrics
    learning_velocity   NUMERIC(6,2),                         -- topics/week normalized
    consistency_score   NUMERIC(5,2),                         -- % of planned days active

    model_version       VARCHAR(20),                          -- Version of scoring model
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_snapshots_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_snapshots_user_date_type UNIQUE (user_id, snapshot_date, snapshot_type),
    CONSTRAINT ck_snapshots_type CHECK (snapshot_type IN ('daily', 'weekly', 'monthly')),
    CONSTRAINT ck_snapshots_readiness CHECK (
        (overall_readiness IS NULL OR overall_readiness BETWEEN 0 AND 100) AND
        (dsa_readiness IS NULL OR dsa_readiness BETWEEN 0 AND 100) AND
        (core_cs_readiness IS NULL OR core_cs_readiness BETWEEN 0 AND 100)
    )
);


-- ============================================================
-- 10. NOTIFICATIONS
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 10.1  notifications
-- Purpose: All in-app, email, and push notifications for a user
-- ──────────────────────────────────────────────────────────────
CREATE TABLE notifications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,
    notification_kind   notification_type NOT NULL DEFAULT 'system',
    title               VARCHAR(300) NOT NULL,
    body                TEXT,
    action_url          TEXT,                                  -- Deep link
    is_read             BOOLEAN      NOT NULL DEFAULT FALSE,
    read_at             TIMESTAMPTZ,
    priority            VARCHAR(10)  NOT NULL DEFAULT 'normal',
    channel             VARCHAR(20)  NOT NULL DEFAULT 'in_app', -- in_app, email, push
    metadata            JSONB        DEFAULT '{}'::JSONB,      -- Flexible extra data
    expires_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT ck_notif_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    CONSTRAINT ck_notif_channel CHECK (channel IN ('in_app', 'email', 'push'))
);


-- ============================================================
-- 11. USER SETTINGS
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 11.1  user_settings
-- Purpose: Per-user application preferences and notification config
-- One-to-one with users
-- ──────────────────────────────────────────────────────────────
CREATE TABLE user_settings (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL,

    -- Theme & UI
    theme               VARCHAR(20)  NOT NULL DEFAULT 'system',  -- light, dark, system
    language            VARCHAR(10)  NOT NULL DEFAULT 'en',
    compact_mode        BOOLEAN      NOT NULL DEFAULT FALSE,

    -- Notifications
    email_notifications BOOLEAN      NOT NULL DEFAULT TRUE,
    push_notifications  BOOLEAN      NOT NULL DEFAULT TRUE,
    weekly_digest       BOOLEAN      NOT NULL DEFAULT TRUE,
    streak_alerts       BOOLEAN      NOT NULL DEFAULT TRUE,
    achievement_alerts  BOOLEAN      NOT NULL DEFAULT TRUE,
    recommendation_alerts BOOLEAN    NOT NULL DEFAULT TRUE,
    dnd_start_time      TIME,                                   -- Do Not Disturb start
    dnd_end_time        TIME,                                   -- Do Not Disturb end

    -- Privacy
    show_profile_public BOOLEAN      NOT NULL DEFAULT FALSE,
    show_on_leaderboard BOOLEAN      NOT NULL DEFAULT TRUE,
    allow_mentor_view   BOOLEAN      NOT NULL DEFAULT FALSE,

    -- Study preferences
    pomodoro_work_min   INTEGER      NOT NULL DEFAULT 25,
    pomodoro_break_min  INTEGER      NOT NULL DEFAULT 5,
    daily_goal_minutes  INTEGER      NOT NULL DEFAULT 120,
    reminder_time       TIME         DEFAULT '09:00:00',

    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_settings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_settings_user UNIQUE (user_id),
    CONSTRAINT ck_settings_theme CHECK (theme IN ('light', 'dark', 'system')),
    CONSTRAINT ck_settings_pomodoro CHECK (pomodoro_work_min BETWEEN 5 AND 120 AND pomodoro_break_min BETWEEN 1 AND 30),
    CONSTRAINT ck_settings_daily_goal CHECK (daily_goal_minutes BETWEEN 5 AND 960)
);


-- ============================================================
-- 12. AUDIT & ACTIVITY LOGGING
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 12.1  activity_logs
-- Purpose: Immutable audit trail of all state-changing actions
--          Supports security review, compliance, and debugging
-- ──────────────────────────────────────────────────────────────
CREATE TABLE activity_logs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID,                                 -- NULL for system actions
    action              audit_action     NOT NULL,
    entity_type         VARCHAR(100) NOT NULL,                -- e.g., 'study_session', 'goal'
    entity_id           UUID,
    description         TEXT,
    old_values          JSONB,                                -- State before change
    new_values          JSONB,                                -- State after change
    ip_address          INET,
    user_agent          TEXT,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
    -- NOTE: No updated_at or deleted_at — this table is APPEND-ONLY
);

-- Prevent UPDATE and DELETE on activity_logs via a trigger
CREATE OR REPLACE FUNCTION prevent_activity_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'activity_logs table is append-only. UPDATE and DELETE are not permitted.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_activity_logs_immutable
    BEFORE UPDATE OR DELETE ON activity_logs
    FOR EACH ROW
    EXECUTE FUNCTION prevent_activity_log_modification();


-- ============================================================
-- 13. TRIGGERS — AUTOMATED LOGIC
-- ============================================================

-- 13.1  Auto-update updated_at timestamp on any table modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT table_name FROM information_schema.columns
        WHERE column_name = 'updated_at'
          AND table_schema = 'public'
          AND table_name NOT IN ('activity_logs')
    LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%I_updated_at
             BEFORE UPDATE ON %I
             FOR EACH ROW
             EXECUTE FUNCTION update_updated_at_column()',
            t, t
        );
    END LOOP;
END;
$$;

-- 13.2  Auto-create profile and settings when a new user is created
CREATE OR REPLACE FUNCTION create_user_defaults()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (user_id) VALUES (NEW.id);
    INSERT INTO user_settings (user_id) VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_create_defaults
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION create_user_defaults();

-- 13.3  Update streak on daily_streaks insert
CREATE OR REPLACE FUNCTION update_user_streak()
RETURNS TRIGGER AS $$
DECLARE
    v_prev_date DATE;
    v_current_streak INTEGER;
BEGIN
    -- Get the most recent streak date before this one
    SELECT streak_date INTO v_prev_date
    FROM daily_streaks
    WHERE user_id = NEW.user_id
      AND streak_date < NEW.streak_date
      AND is_streak_day = TRUE
    ORDER BY streak_date DESC
    LIMIT 1;

    -- Calculate current streak
    IF v_prev_date IS NULL OR (NEW.streak_date - v_prev_date) > 1 THEN
        -- Streak broken or first day
        v_current_streak := 1;
    ELSE
        -- Continuing streak
        SELECT current_streak + 1 INTO v_current_streak
        FROM profiles WHERE user_id = NEW.user_id;
    END IF;

    -- Update profile
    UPDATE profiles
    SET current_streak = v_current_streak,
        longest_streak = GREATEST(longest_streak, v_current_streak),
        streak_last_date = NEW.streak_date
    WHERE user_id = NEW.user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_daily_streaks_update
    AFTER INSERT ON daily_streaks
    FOR EACH ROW
    WHEN (NEW.is_streak_day = TRUE)
    EXECUTE FUNCTION update_user_streak();

-- 13.4  Auto-update user_topic_progress on study_session insert
CREATE OR REPLACE FUNCTION update_topic_progress_on_session()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.topic_id IS NOT NULL THEN
        INSERT INTO user_topic_progress (user_id, topic_id, skill_id, status, total_time_minutes, last_studied_at, started_at)
        SELECT NEW.user_id, NEW.topic_id, t.skill_id, 'in_progress', NEW.duration_minutes, NOW(), NOW()
        FROM topics t WHERE t.id = NEW.topic_id
        ON CONFLICT (user_id, topic_id)
        DO UPDATE SET
            total_time_minutes = user_topic_progress.total_time_minutes + NEW.duration_minutes,
            last_studied_at = NOW(),
            status = CASE
                WHEN user_topic_progress.status = 'not_started' THEN 'in_progress'::skill_status
                ELSE user_topic_progress.status
            END,
            updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_session_update_progress
    AFTER INSERT ON study_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_topic_progress_on_session();

-- 13.5  Update XP on study session and achievement earnings
CREATE OR REPLACE FUNCTION award_session_xp()
RETURNS TRIGGER AS $$
DECLARE
    v_xp INTEGER;
BEGIN
    -- Base XP: 1 XP per minute, bonus for quality
    v_xp := NEW.duration_minutes + COALESCE(NEW.quality_rating, 3) * 2;
    NEW.xp_earned := v_xp;

    -- Update profile XP
    UPDATE profiles
    SET xp_total = xp_total + v_xp,
        current_level = GREATEST(1, FLOOR(SQRT(xp_total + v_xp) / 5)::INTEGER + 1)
    WHERE user_id = NEW.user_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_session_award_xp
    BEFORE INSERT ON study_sessions
    FOR EACH ROW
    EXECUTE FUNCTION award_session_xp();


-- ============================================================
-- 14. INDEXES
-- ============================================================

-- ── 14.1  USER & PROFILE INDEXES ─────────────────────────────

-- Login lookups (email is already UNIQUE → has implicit index)
CREATE INDEX idx_users_auth_provider ON users (auth_provider, auth_provider_id)
    WHERE auth_provider_id IS NOT NULL;
CREATE INDEX idx_users_active ON users (is_active, last_active_at DESC)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_users_role ON users (role)
    WHERE deleted_at IS NULL;

-- ── 14.2  SKILL TAXONOMY INDEXES ──────────────────────────────

CREATE INDEX idx_categories_parent ON categories (parent_id)
    WHERE parent_id IS NOT NULL;
CREATE INDEX idx_categories_active ON categories (is_active, display_order);

CREATE INDEX idx_skills_category ON skills (category_id, is_active);
CREATE INDEX idx_skills_name_trgm ON skills USING GIN (name gin_trgm_ops);  -- Fuzzy search
CREATE INDEX idx_skills_tags ON skills USING GIN (tags);
CREATE INDEX idx_skills_active ON skills (is_active) WHERE is_active = TRUE;

CREATE INDEX idx_topics_skill ON topics (skill_id, display_order);
CREATE INDEX idx_topics_difficulty ON topics (skill_id, difficulty);

CREATE INDEX idx_subtopics_topic ON subtopics (topic_id, display_order);

-- ── 14.3  ROADMAP INDEXES ──────────────────────────────────────

CREATE INDEX idx_roadmaps_created_by ON roadmaps (created_by)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_roadmaps_template ON roadmaps (is_template, category_id)
    WHERE is_template = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_roadmaps_visibility ON roadmaps (visibility)
    WHERE visibility = 'public' AND deleted_at IS NULL;

CREATE INDEX idx_rsections_roadmap ON roadmap_sections (roadmap_id, section_order);
CREATE INDEX idx_rtopics_section ON roadmap_topics (section_id, topic_order);

CREATE INDEX idx_uroadmaps_user ON user_roadmaps (user_id, status);
CREATE INDEX idx_uroadmaps_roadmap ON user_roadmaps (roadmap_id);

-- ── 14.4  PROGRESS TRACKING INDEXES ────────────────────────────

CREATE INDEX idx_utprogress_user_skill ON user_topic_progress (user_id, skill_id);
CREATE INDEX idx_utprogress_user_status ON user_topic_progress (user_id, status);
CREATE INDEX idx_utprogress_last_studied ON user_topic_progress (user_id, last_studied_at DESC)
    WHERE status != 'not_started';
-- Partial index for revision due topics
CREATE INDEX idx_utprogress_revision_due ON user_topic_progress (user_id, last_revised_at)
    WHERE status IN ('completed', 'mastered') AND revision_count < 5;

-- ── 14.5  STUDY SESSION INDEXES ────────────────────────────────

CREATE INDEX idx_sessions_user_date ON study_sessions (user_id, session_date DESC);
CREATE INDEX idx_sessions_user_skill ON study_sessions (user_id, skill_id)
    WHERE skill_id IS NOT NULL;
CREATE INDEX idx_sessions_user_topic ON study_sessions (user_id, topic_id)
    WHERE topic_id IS NOT NULL;
-- Dashboard query: recent sessions
CREATE INDEX idx_sessions_user_recent ON study_sessions (user_id, created_at DESC);
-- Analytics: time aggregation by date
CREATE INDEX idx_sessions_date_user ON study_sessions (session_date, user_id);

-- ── 14.6  REVISION SESSION INDEXES ─────────────────────────────

CREATE INDEX idx_revisions_user_topic ON revision_sessions (user_id, topic_id);
CREATE INDEX idx_revisions_next_date ON revision_sessions (user_id, next_revision_date)
    WHERE next_revision_date IS NOT NULL;

-- ── 14.7  PROJECT & CERTIFICATION INDEXES ───────────────────────

CREATE INDEX idx_projects_user ON projects (user_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_projects_featured ON projects (user_id, is_featured)
    WHERE is_featured = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_pmilestones_project ON project_milestones (project_id, milestone_order);

CREATE INDEX idx_certs_user ON certifications (user_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_certs_expiry ON certifications (user_id, expiry_date)
    WHERE expiry_date IS NOT NULL AND status = 'earned';

-- ── 14.8  GOAL INDEXES ─────────────────────────────────────────

CREATE INDEX idx_goals_user ON goals (user_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_goals_priority ON goals (user_id, priority, status)
    WHERE deleted_at IS NULL AND status NOT IN ('completed', 'abandoned');
CREATE INDEX idx_gmilestones_goal ON goal_milestones (goal_id, milestone_order);

-- ── 14.9  NOTES & RESOURCES INDEXES ────────────────────────────

CREATE INDEX idx_notes_user ON notes (user_id, note_kind, created_at DESC)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_notes_topic ON notes (topic_id)
    WHERE topic_id IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX idx_notes_pinned ON notes (user_id, is_pinned)
    WHERE is_pinned = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_notes_tags ON notes USING GIN (tags);

CREATE INDEX idx_resources_topic ON resources (topic_id)
    WHERE topic_id IS NOT NULL;
CREATE INDEX idx_resources_skill ON resources (skill_id)
    WHERE skill_id IS NOT NULL;
CREATE INDEX idx_resources_type ON resources (resource_kind);

-- ── 14.10  GAMIFICATION INDEXES ────────────────────────────────

CREATE INDEX idx_uachievements_user ON user_achievements (user_id, earned_at DESC);
CREATE INDEX idx_dstreaks_user_date ON daily_streaks (user_id, streak_date DESC);
-- Leaderboard query (XP-based)
CREATE INDEX idx_profiles_leaderboard ON profiles (xp_total DESC, current_level DESC)
    WHERE (SELECT is_active FROM users WHERE users.id = profiles.user_id) = TRUE;

-- ── 14.11  ANALYTICS INDEXES ───────────────────────────────────

CREATE INDEX idx_snapshots_user_date ON analytics_snapshots (user_id, snapshot_date DESC);
CREATE INDEX idx_snapshots_type ON analytics_snapshots (snapshot_type, snapshot_date DESC);
-- Weekly/monthly analytics lookups
CREATE INDEX idx_snapshots_weekly ON analytics_snapshots (user_id, snapshot_date DESC)
    WHERE snapshot_type = 'weekly';
CREATE INDEX idx_snapshots_monthly ON analytics_snapshots (user_id, snapshot_date DESC)
    WHERE snapshot_type = 'monthly';

-- ── 14.12  NOTIFICATION INDEXES ────────────────────────────────

CREATE INDEX idx_notif_user_unread ON notifications (user_id, is_read, created_at DESC)
    WHERE is_read = FALSE;
CREATE INDEX idx_notif_user_type ON notifications (user_id, notification_kind, created_at DESC);
-- Cleanup: find expired notifications
CREATE INDEX idx_notif_expires ON notifications (expires_at)
    WHERE expires_at IS NOT NULL;

-- ── 14.13  AUDIT LOG INDEXES ───────────────────────────────────

CREATE INDEX idx_logs_user ON activity_logs (user_id, created_at DESC)
    WHERE user_id IS NOT NULL;
CREATE INDEX idx_logs_entity ON activity_logs (entity_type, entity_id);
CREATE INDEX idx_logs_action ON activity_logs (action, created_at DESC);


-- ============================================================
-- 15. ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on user-owned tables.
-- Application connects as 'app_user' role with user_id set via:
--   SET LOCAL app.current_user_id = '<uuid>';

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_topic_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE revision_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see/modify their own data
-- (Admin bypass handled at application layer by not setting app.current_user_id)

CREATE POLICY users_own_data ON users
    USING (id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY profiles_own_data ON profiles
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY progress_own_data ON user_topic_progress
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY sessions_own_data ON study_sessions
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY revisions_own_data ON revision_sessions
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY projects_own_data ON projects
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY certs_own_data ON certifications
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY goals_own_data ON goals
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY notes_own_data ON notes
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY notif_own_data ON notifications
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY settings_own_data ON user_settings
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY streaks_own_data ON daily_streaks
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY uroadmaps_own_data ON user_roadmaps
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);

CREATE POLICY uachievements_own_data ON user_achievements
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID OR
           current_setting('app.current_user_id', TRUE) IS NULL);


-- ============================================================
-- 16. MATERIALIZED VIEWS — ANALYTICS
-- ============================================================

-- 16.1  Weekly progress aggregation per user
CREATE MATERIALIZED VIEW mv_weekly_progress AS
SELECT
    s.user_id,
    DATE_TRUNC('week', s.session_date)::DATE AS week_start,
    COUNT(*)                           AS total_sessions,
    SUM(s.duration_minutes)            AS total_minutes,
    ROUND(AVG(s.duration_minutes), 1)  AS avg_session_minutes,
    ROUND(AVG(s.quality_rating), 1)    AS avg_quality,
    COUNT(DISTINCT s.topic_id)         AS unique_topics,
    COUNT(DISTINCT s.skill_id)         AS unique_skills,
    SUM(s.xp_earned)                   AS total_xp
FROM study_sessions s
GROUP BY s.user_id, DATE_TRUNC('week', s.session_date)
WITH DATA;

CREATE UNIQUE INDEX idx_mv_weekly_user_week ON mv_weekly_progress (user_id, week_start);

-- 16.2  Monthly progress aggregation per user
CREATE MATERIALIZED VIEW mv_monthly_progress AS
SELECT
    s.user_id,
    DATE_TRUNC('month', s.session_date)::DATE AS month_start,
    COUNT(*)                           AS total_sessions,
    SUM(s.duration_minutes)            AS total_minutes,
    ROUND(AVG(s.quality_rating), 1)    AS avg_quality,
    COUNT(DISTINCT s.topic_id)         AS unique_topics,
    COUNT(DISTINCT s.skill_id)         AS unique_skills,
    SUM(s.xp_earned)                   AS total_xp,
    COUNT(DISTINCT s.session_date)     AS active_days
FROM study_sessions s
GROUP BY s.user_id, DATE_TRUNC('month', s.session_date)
WITH DATA;

CREATE UNIQUE INDEX idx_mv_monthly_user_month ON mv_monthly_progress (user_id, month_start);

-- 16.3  Skill mastery summary per user
CREATE MATERIALIZED VIEW mv_skill_mastery AS
SELECT
    utp.user_id,
    s.id AS skill_id,
    s.name AS skill_name,
    c.name AS category_name,
    COUNT(utp.id) AS total_topics,
    COUNT(CASE WHEN utp.status = 'completed' THEN 1 END) AS completed_topics,
    COUNT(CASE WHEN utp.status = 'mastered' THEN 1 END) AS mastered_topics,
    ROUND(
        COUNT(CASE WHEN utp.status IN ('completed', 'mastered') THEN 1 END)::NUMERIC
        / NULLIF(COUNT(utp.id), 0) * 100, 2
    ) AS completion_percentage,
    SUM(utp.total_time_minutes) AS total_time_minutes,
    MAX(utp.last_studied_at) AS last_studied_at
FROM user_topic_progress utp
JOIN topics t ON t.id = utp.topic_id
JOIN skills s ON s.id = t.skill_id
JOIN categories c ON c.id = s.category_id
GROUP BY utp.user_id, s.id, s.name, c.name
WITH DATA;

CREATE UNIQUE INDEX idx_mv_skill_mastery_user_skill ON mv_skill_mastery (user_id, skill_id);

-- 16.4  Leaderboard view
CREATE MATERIALIZED VIEW mv_leaderboard AS
SELECT
    p.user_id,
    u.display_name,
    u.avatar_url,
    p.xp_total,
    p.current_level,
    p.current_streak,
    p.longest_streak,
    RANK() OVER (ORDER BY p.xp_total DESC) AS global_rank
FROM profiles p
JOIN users u ON u.id = p.user_id
WHERE u.is_active = TRUE AND u.deleted_at IS NULL
WITH DATA;

CREATE UNIQUE INDEX idx_mv_leaderboard_user ON mv_leaderboard (user_id);
CREATE INDEX idx_mv_leaderboard_rank ON mv_leaderboard (global_rank);


-- ============================================================
-- 17. GDPR / ACCOUNT DELETION SUPPORT
-- ============================================================

-- Function to anonymize user data (GDPR Right to Erasure)
-- Called after 30-day grace period post account deletion request
CREATE OR REPLACE FUNCTION anonymize_user_data(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Anonymize user record
    UPDATE users
    SET email = 'deleted_' || id::TEXT || '@anonymized.local',
        password_hash = NULL,
        display_name = 'Deleted User',
        avatar_url = NULL,
        auth_provider_id = NULL,
        email_verified = FALSE,
        is_active = FALSE,
        deleted_at = COALESCE(deleted_at, NOW())
    WHERE id = p_user_id;

    -- Anonymize profile
    UPDATE profiles
    SET bio = NULL,
        primary_goal = NULL,
        target_role = NULL,
        target_companies = '[]'::JSONB,
        education = '[]'::JSONB,
        work_experience = '[]'::JSONB,
        github_url = NULL,
        linkedin_url = NULL,
        leetcode_url = NULL,
        portfolio_url = NULL
    WHERE user_id = p_user_id;

    -- Delete notifications
    DELETE FROM notifications WHERE user_id = p_user_id;

    -- Delete notes (user content)
    DELETE FROM notes WHERE user_id = p_user_id;

    -- Anonymize activity logs (retain for audit but remove PII)
    UPDATE activity_logs
    SET ip_address = NULL,
        user_agent = NULL
    WHERE user_id = p_user_id;

    -- Study sessions, progress, projects etc. are retained but
    -- no longer linkable to a real identity

    RAISE NOTICE 'User % data anonymized successfully', p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ============================================================
-- 18. SEED DATA
-- ============================================================

-- ── 18.1  Categories ────────────────────────────────────────────

INSERT INTO categories (id, name, slug, description, display_order) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Data Structures & Algorithms', 'dsa', 'Core DSA concepts and problem-solving', 1),
    ('a0000000-0000-0000-0000-000000000002', 'Core Computer Science', 'core-cs', 'Fundamental CS subjects: OS, DBMS, CN, OOP', 2),
    ('a0000000-0000-0000-0000-000000000003', 'Aptitude & Reasoning', 'aptitude', 'Quantitative, logical, and verbal reasoning', 3),
    ('a0000000-0000-0000-0000-000000000004', 'AI & Machine Learning', 'ai-ml', 'Artificial Intelligence and Machine Learning', 4),
    ('a0000000-0000-0000-0000-000000000005', 'Web Development', 'web-dev', 'Frontend, backend, and full-stack development', 5),
    ('a0000000-0000-0000-0000-000000000006', 'Cloud & DevOps', 'cloud-devops', 'Cloud platforms, CI/CD, infrastructure', 6),
    ('a0000000-0000-0000-0000-000000000007', 'System Design', 'system-design', 'Scalable system design and architecture', 7),
    ('a0000000-0000-0000-0000-000000000008', 'Programming Languages', 'languages', 'Language-specific proficiency', 8),
    ('a0000000-0000-0000-0000-000000000009', 'Databases', 'databases', 'SQL, NoSQL, and database management', 9),
    ('a0000000-0000-0000-0000-000000000010', 'Soft Skills', 'soft-skills', 'Communication, leadership, teamwork', 10);

-- Sub-categories for AI/ML
INSERT INTO categories (name, slug, description, parent_id, display_order) VALUES
    ('Mathematics for AI', 'ai-math', 'Linear algebra, calculus, probability, statistics', 'a0000000-0000-0000-0000-000000000004', 1),
    ('Machine Learning', 'ml', 'Classical ML algorithms and techniques', 'a0000000-0000-0000-0000-000000000004', 2),
    ('Deep Learning', 'dl', 'Neural networks and deep learning architectures', 'a0000000-0000-0000-0000-000000000004', 3),
    ('Natural Language Processing', 'nlp', 'Text processing, transformers, LLMs', 'a0000000-0000-0000-0000-000000000004', 4),
    ('Computer Vision', 'cv', 'Image and video analysis', 'a0000000-0000-0000-0000-000000000004', 5),
    ('Generative AI', 'gen-ai', 'LLMs, diffusion models, generative techniques', 'a0000000-0000-0000-0000-000000000004', 6),
    ('Agentic AI', 'agentic-ai', 'AI agents, tool use, multi-agent systems', 'a0000000-0000-0000-0000-000000000004', 7),
    ('Prompt Engineering', 'prompt-eng', 'Prompt design and optimization', 'a0000000-0000-0000-0000-000000000004', 8);

-- Sub-categories for Core CS
INSERT INTO categories (name, slug, description, parent_id, display_order) VALUES
    ('Operating Systems', 'os', 'Process management, memory, file systems', 'a0000000-0000-0000-0000-000000000002', 1),
    ('Database Management Systems', 'dbms', 'RDBMS concepts, normalization, transactions', 'a0000000-0000-0000-0000-000000000002', 2),
    ('Computer Networks', 'cn', 'OSI model, TCP/IP, protocols', 'a0000000-0000-0000-0000-000000000002', 3),
    ('Object-Oriented Programming', 'oop', 'OOP principles, design patterns', 'a0000000-0000-0000-0000-000000000002', 4),
    ('SQL', 'sql', 'SQL queries, optimization, advanced concepts', 'a0000000-0000-0000-0000-000000000002', 5);

-- ── 18.2  Skills (DSA) ──────────────────────────────────────────

INSERT INTO skills (id, category_id, name, slug, difficulty, estimated_hours) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Arrays', 'arrays', 'beginner', 40),
    ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'Strings', 'strings', 'beginner', 35),
    ('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'Linked Lists', 'linked-lists', 'intermediate', 30),
    ('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 'Stacks & Queues', 'stacks-queues', 'intermediate', 25),
    ('b0000000-0000-0000-0000-000000000005', 'a0000000-0000-0000-0000-000000000001', 'Trees', 'trees', 'intermediate', 50),
    ('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000001', 'Graphs', 'graphs', 'advanced', 60),
    ('b0000000-0000-0000-0000-000000000007', 'a0000000-0000-0000-0000-000000000001', 'Dynamic Programming', 'dynamic-programming', 'advanced', 80),
    ('b0000000-0000-0000-0000-000000000008', 'a0000000-0000-0000-0000-000000000001', 'Sorting & Searching', 'sorting-searching', 'beginner', 30),
    ('b0000000-0000-0000-0000-000000000009', 'a0000000-0000-0000-0000-000000000001', 'Recursion & Backtracking', 'recursion-backtracking', 'intermediate', 45),
    ('b0000000-0000-0000-0000-000000000010', 'a0000000-0000-0000-0000-000000000001', 'Greedy Algorithms', 'greedy', 'intermediate', 25),
    ('b0000000-0000-0000-0000-000000000011', 'a0000000-0000-0000-0000-000000000001', 'Hashing', 'hashing', 'beginner', 20),
    ('b0000000-0000-0000-0000-000000000012', 'a0000000-0000-0000-0000-000000000001', 'Heaps', 'heaps', 'intermediate', 20),
    ('b0000000-0000-0000-0000-000000000013', 'a0000000-0000-0000-0000-000000000001', 'Tries', 'tries', 'advanced', 15),
    ('b0000000-0000-0000-0000-000000000014', 'a0000000-0000-0000-0000-000000000001', 'Bit Manipulation', 'bit-manipulation', 'intermediate', 15),
    ('b0000000-0000-0000-0000-000000000015', 'a0000000-0000-0000-0000-000000000001', 'Segment Trees', 'segment-trees', 'expert', 25);

-- ── 18.3  Topics (sample for Arrays skill) ────────────────────

INSERT INTO topics (skill_id, name, slug, difficulty, display_order, importance) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'Two Pointer Technique', 'two-pointer', 'beginner', 1, 'critical'),
    ('b0000000-0000-0000-0000-000000000001', 'Sliding Window', 'sliding-window', 'intermediate', 2, 'critical'),
    ('b0000000-0000-0000-0000-000000000001', 'Kadane''s Algorithm', 'kadanes-algorithm', 'intermediate', 3, 'high'),
    ('b0000000-0000-0000-0000-000000000001', 'Prefix Sum', 'prefix-sum', 'beginner', 4, 'high'),
    ('b0000000-0000-0000-0000-000000000001', 'Matrix Problems', 'matrix-problems', 'intermediate', 5, 'medium'),
    ('b0000000-0000-0000-0000-000000000001', 'Array Rotation', 'array-rotation', 'beginner', 6, 'medium'),
    ('b0000000-0000-0000-0000-000000000001', 'Merge Intervals', 'merge-intervals', 'intermediate', 7, 'critical'),
    ('b0000000-0000-0000-0000-000000000001', 'Dutch National Flag', 'dutch-national-flag', 'beginner', 8, 'high'),
    ('b0000000-0000-0000-0000-000000000001', 'Subarray Problems', 'subarray-problems', 'intermediate', 9, 'high'),
    ('b0000000-0000-0000-0000-000000000001', 'Binary Search on Arrays', 'binary-search-arrays', 'intermediate', 10, 'critical');

-- Topics for Dynamic Programming
INSERT INTO topics (skill_id, name, slug, difficulty, display_order, importance) VALUES
    ('b0000000-0000-0000-0000-000000000007', '1D DP', 'dp-1d', 'intermediate', 1, 'critical'),
    ('b0000000-0000-0000-0000-000000000007', '2D DP', 'dp-2d', 'advanced', 2, 'critical'),
    ('b0000000-0000-0000-0000-000000000007', 'DP on Strings', 'dp-strings', 'advanced', 3, 'high'),
    ('b0000000-0000-0000-0000-000000000007', 'DP on Trees', 'dp-trees', 'expert', 4, 'medium'),
    ('b0000000-0000-0000-0000-000000000007', 'Knapsack Variants', 'knapsack', 'advanced', 5, 'critical'),
    ('b0000000-0000-0000-0000-000000000007', 'LIS / LCS', 'lis-lcs', 'advanced', 6, 'high'),
    ('b0000000-0000-0000-0000-000000000007', 'Matrix Chain Multiplication', 'mcm', 'advanced', 7, 'medium'),
    ('b0000000-0000-0000-0000-000000000007', 'Partition DP', 'partition-dp', 'expert', 8, 'medium'),
    ('b0000000-0000-0000-0000-000000000007', 'Digit DP', 'digit-dp', 'expert', 9, 'low'),
    ('b0000000-0000-0000-0000-000000000007', 'Bitmask DP', 'bitmask-dp', 'expert', 10, 'low');

-- ── 18.4  Achievements ──────────────────────────────────────────

INSERT INTO achievements (name, slug, description, achievement_kind, criteria_type, criteria_value, xp_reward, rarity) VALUES
    -- Streak achievements
    ('First Spark',         'first-spark',          'Log your first study session',          'milestone',    'sessions_logged',      1,      10,   'common'),
    ('Week Warrior',        'week-warrior',         'Maintain a 7-day study streak',         'streak',       'streak_days',          7,      50,   'common'),
    ('Fortnight Focus',     'fortnight-focus',      'Maintain a 14-day study streak',        'streak',       'streak_days',          14,     100,  'uncommon'),
    ('Monthly Master',      'monthly-master',       'Maintain a 30-day study streak',        'streak',       'streak_days',          30,     250,  'rare'),
    ('Century Streak',      'century-streak',       'Maintain a 100-day study streak',       'streak',       'streak_days',          100,    1000, 'epic'),
    ('Year of Growth',      'year-of-growth',       'Maintain a 365-day study streak',       'streak',       'streak_days',          365,    5000, 'legendary'),

    -- DSA milestones
    ('DSA Starter',         'dsa-starter',          'Complete 10 DSA topics',                'milestone',    'dsa_topics_completed', 10,     50,   'common'),
    ('DSA Century',         'dsa-century',          'Complete 100 DSA topics',               'milestone',    'dsa_topics_completed', 100,    500,  'rare'),
    ('Problem Solver',      'problem-solver',       'Log 50 study sessions',                 'milestone',    'sessions_logged',      50,     100,  'uncommon'),
    ('Dedicated Learner',   'dedicated-learner',    'Log 200 study sessions',                'milestone',    'sessions_logged',      200,    400,  'rare'),

    -- Time-based
    ('Deep Focus',          'deep-focus',           'Complete a 2+ hour study session',      'consistency',  'session_minutes',      120,    30,   'uncommon'),
    ('Marathon Session',    'marathon-session',     'Complete a 4+ hour study session',      'consistency',  'session_minutes',      240,    75,   'rare'),
    ('100 Hour Club',       'hundred-hour-club',    'Accumulate 100 hours of study time',    'milestone',    'total_hours',          100,    500,  'rare'),
    ('500 Hour Club',       'five-hundred-hours',   'Accumulate 500 hours of study time',    'milestone',    'total_hours',          500,    2000, 'epic'),

    -- Skill mastery
    ('First Mastery',       'first-mastery',        'Master your first skill topic',         'skill_mastery','topics_mastered',      1,      25,   'common'),
    ('Skill Explorer',      'skill-explorer',       'Track skills in 5 different categories','skill_mastery','categories_tracked',   5,      100,  'uncommon'),

    -- Projects
    ('Builder',             'builder',              'Create your first project',             'milestone',    'projects_created',     1,      30,   'common'),
    ('Ship It',             'ship-it',              'Deploy your first project',             'milestone',    'projects_deployed',    1,      75,   'uncommon'),

    -- Certifications
    ('Certified',           'certified',            'Earn your first certification',         'milestone',    'certs_earned',         1,      50,   'uncommon'),

    -- Special
    ('Early Adopter',       'early-adopter',        'Join during the beta period',           'special',      'beta_signup',          1,      100,  'rare');

-- ── 18.5  Sample Roadmap Template ───────────────────────────────

INSERT INTO roadmaps (id, title, slug, description, category_id, difficulty, estimated_days, estimated_hours, is_template, visibility, status, total_sections, total_topics) VALUES
    ('c0000000-0000-0000-0000-000000000001',
     'DSA Mastery in 90 Days',
     'dsa-mastery-90-days',
     'A structured 90-day roadmap to master Data Structures and Algorithms for placement preparation. Covers all major topics from arrays to dynamic programming.',
     'a0000000-0000-0000-0000-000000000001',
     'intermediate',
     90, 300, TRUE, 'public', 'active', 4, 15);

INSERT INTO roadmap_sections (id, roadmap_id, title, description, section_order, estimated_days) VALUES
    ('d0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'Phase 1: Foundations', 'Arrays, Strings, Hashing, Sorting & Searching', 1, 20),
    ('d0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000001', 'Phase 2: Core Data Structures', 'Linked Lists, Stacks, Queues, Trees, Heaps', 2, 25),
    ('d0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000001', 'Phase 3: Advanced Algorithms', 'Graphs, Recursion, Backtracking, Greedy', 3, 25),
    ('d0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000001', 'Phase 4: Dynamic Programming & Mastery', 'DP, Tries, Segment Trees, Revision', 4, 20);

INSERT INTO roadmap_topics (section_id, skill_id, topic_order, estimated_hours, is_milestone) VALUES
    ('d0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 1, 40, FALSE),  -- Arrays
    ('d0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000002', 2, 35, FALSE),  -- Strings
    ('d0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000011', 3, 20, FALSE),  -- Hashing
    ('d0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000008', 4, 30, TRUE),   -- Sorting (milestone)
    ('d0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000003', 1, 30, FALSE),  -- Linked Lists
    ('d0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000004', 2, 25, FALSE),  -- Stacks & Queues
    ('d0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000005', 3, 50, FALSE),  -- Trees
    ('d0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000012', 4, 20, TRUE),   -- Heaps (milestone)
    ('d0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000006', 1, 60, FALSE),  -- Graphs
    ('d0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000009', 2, 45, FALSE),  -- Recursion
    ('d0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000010', 3, 25, TRUE),   -- Greedy (milestone)
    ('d0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000007', 1, 80, FALSE),  -- DP
    ('d0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000013', 2, 15, FALSE),  -- Tries
    ('d0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000014', 3, 15, FALSE),  -- Bit Manipulation
    ('d0000000-0000-0000-0000-000000000004', 'b0000000-0000-0000-0000-000000000015', 4, 25, TRUE);   -- Segment Trees (milestone)


-- ============================================================
-- 19. REFRESH FUNCTIONS FOR MATERIALIZED VIEWS
-- ============================================================

-- Call these via background job (e.g., pg_cron or application scheduler)

CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_weekly_progress;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_progress;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_mastery;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_leaderboard;
    RAISE NOTICE 'All analytics materialized views refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 20. UTILITY: SOFT DELETE HELPERS
-- ============================================================

-- View that filters out soft-deleted records for common tables
CREATE OR REPLACE VIEW v_active_users AS
    SELECT * FROM users WHERE deleted_at IS NULL AND is_active = TRUE;

CREATE OR REPLACE VIEW v_active_projects AS
    SELECT * FROM projects WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_goals AS
    SELECT * FROM goals WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_roadmaps AS
    SELECT * FROM roadmaps WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_certifications AS
    SELECT * FROM certifications WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW v_active_notes AS
    SELECT * FROM notes WHERE deleted_at IS NULL;


-- ============================================================
-- SCHEMA COMPLETE
-- ============================================================

COMMIT;

-- Post-commit: Verify table count
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE';
    RAISE NOTICE '✅ Schema creation complete. Total tables: %', v_count;
END;
$$;

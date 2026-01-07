"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-01-07

"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep the MVP schema close to the SQL you provided (enums + tables + indexes)
    op.execute(
        """
DO $$ BEGIN
  CREATE TYPE platform_type AS ENUM ('tiktok','instagram','youtube','linkedin','x','facebook','reddit','other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE lead_status AS ENUM ('new','contacted','qualified','proposal','won','lost','nurture');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE lead_intent AS ENUM ('student','small_business','ecommerce','internal_tool','agency_client','unknown');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE post_status AS ENUM ('draft','approved','scheduled','published','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE handoff_target AS ENUM ('codlearn','splendid');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS trend_sources (
  id              BIGSERIAL PRIMARY KEY,
  name            TEXT NOT NULL,
  details         JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS trend_items (
  id              BIGSERIAL PRIMARY KEY,
  source_id       BIGINT NOT NULL REFERENCES trend_sources(id) ON DELETE RESTRICT,
  region          TEXT NOT NULL,
  language        TEXT,
  topic           TEXT NOT NULL,
  url             TEXT,
  category        TEXT,
  score           NUMERIC(6,3) NOT NULL DEFAULT 0,
  features        JSONB NOT NULL DEFAULT '{}'::jsonb,
  first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trend_items_region_score ON trend_items(region, score DESC);
CREATE INDEX IF NOT EXISTS idx_trend_items_last_seen ON trend_items(last_seen_at DESC);

CREATE TABLE IF NOT EXISTS trend_snapshots (
  id              BIGSERIAL PRIMARY KEY,
  trend_item_id   BIGINT NOT NULL REFERENCES trend_items(id) ON DELETE CASCADE,
  snapshot_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  metrics         JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_trend_snapshots_item_time ON trend_snapshots(trend_item_id, snapshot_at DESC);

CREATE TABLE IF NOT EXISTS campaigns (
  id              BIGSERIAL PRIMARY KEY,
  name            TEXT NOT NULL,
  region          TEXT NOT NULL,
  objective       TEXT NOT NULL DEFAULT 'lead_gen',
  target          handoff_target NOT NULL DEFAULT 'codlearn',
  offer           TEXT,
  niche           TEXT,
  status          TEXT NOT NULL DEFAULT 'active',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_campaigns_region_status ON campaigns(region, status);

CREATE TABLE IF NOT EXISTS content_packs (
  id              BIGSERIAL PRIMARY KEY,
  campaign_id     BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  trend_item_id   BIGINT REFERENCES trend_items(id) ON DELETE SET NULL,
  platform        platform_type NOT NULL,
  title           TEXT,
  content_json    JSONB NOT NULL,
  quality_score   NUMERIC(5,2) NOT NULL DEFAULT 0,
  is_approved     BOOLEAN NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_content_packs_campaign_platform ON content_packs(campaign_id, platform);
CREATE INDEX IF NOT EXISTS idx_content_packs_approved ON content_packs(is_approved);

CREATE TABLE IF NOT EXISTS social_posts (
  id              BIGSERIAL PRIMARY KEY,
  campaign_id     BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  content_pack_id BIGINT REFERENCES content_packs(id) ON DELETE SET NULL,
  platform        platform_type NOT NULL,
  status          post_status NOT NULL DEFAULT 'draft',
  scheduled_at    TIMESTAMPTZ,
  published_at    TIMESTAMPTZ,
  external_post_id TEXT,
  post_url        TEXT,
  metrics         JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_social_posts_campaign_status ON social_posts(campaign_id, status);
CREATE INDEX IF NOT EXISTS idx_social_posts_platform_time ON social_posts(platform, scheduled_at DESC);

CREATE TABLE IF NOT EXISTS leads (
  id              BIGSERIAL PRIMARY KEY,
  email           TEXT,
  phone           TEXT,
  full_name       TEXT,
  company         TEXT,
  region          TEXT,
  source_platform platform_type NOT NULL DEFAULT 'other',
  source_detail   TEXT,
  intent          lead_intent NOT NULL DEFAULT 'unknown',
  status          lead_status NOT NULL DEFAULT 'new',
  score           INTEGER NOT NULL DEFAULT 0,
  attributes      JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_leads_email ON leads(email) WHERE email IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_leads_status_score ON leads(status, score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_region ON leads(region);

CREATE TABLE IF NOT EXISTS lead_events (
  id              BIGSERIAL PRIMARY KEY,
  lead_id         BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  event_type      TEXT NOT NULL,
  event_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata        JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_lead_events_lead_time ON lead_events(lead_id, event_at DESC);
CREATE INDEX IF NOT EXISTS idx_lead_events_type_time ON lead_events(event_type, event_at DESC);

CREATE TABLE IF NOT EXISTS lead_notes (
  id              BIGSERIAL PRIMARY KEY,
  lead_id         BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  note            TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS lead_tasks (
  id              BIGSERIAL PRIMARY KEY,
  lead_id         BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  due_at          TIMESTAMPTZ,
  is_done         BOOLEAN NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lead_tasks_due ON lead_tasks(due_at) WHERE is_done = false;

CREATE TABLE IF NOT EXISTS handoff_requests (
  id              BIGSERIAL PRIMARY KEY,
  lead_id         BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  target          handoff_target NOT NULL DEFAULT 'splendid',
  reason          TEXT,
  payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_handoff_requests_created ON handoff_requests(created_at DESC);
        """
    )


def downgrade() -> None:
    # MVP: no destructive downgrade by default (safe for early iterations)
    pass

"""add campaign slug

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-07

"""

from __future__ import annotations

from alembic import op


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS slug TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS uq_campaigns_slug ON campaigns(slug) WHERE slug IS NOT NULL;
        """
    )


def downgrade() -> None:
    pass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.schemas.campaigns import CampaignCreate


def create_campaign(db: Session, payload: CampaignCreate) -> Campaign:
    campaign = Campaign(
        name=payload.name,
        region=payload.region,
        objective="lead_gen",
        target=payload.target,
        offer=payload.offer,
        niche=payload.niche,
        status=payload.status,
    )

    # Optional slug support (requires migration 0002_add_campaign_slug)
    if hasattr(campaign, "slug"):
        setattr(campaign, "slug", payload.slug)

    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def list_campaigns(db: Session, region: str | None = None, status: str | None = None, limit: int = 50) -> list[Campaign]:
    stmt = select(Campaign).order_by(Campaign.created_at.desc()).limit(limit)
    if region:
        stmt = stmt.where(Campaign.region == region)
    if status:
        stmt = stmt.where(Campaign.status == status)
    return list(db.scalars(stmt).all())

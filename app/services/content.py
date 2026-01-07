from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.content_pack import ContentPack
from app.schemas.content import ContentGenerateRequest


def generate_content_packs(db: Session, payload: ContentGenerateRequest):
    if payload.campaign_id is None and not payload.campaign_slug:
        raise ValueError("campaign_slug or campaign_id required")

    campaign_id = payload.campaign_id
    campaign_slug = payload.campaign_slug

    if campaign_id is None and campaign_slug:
        campaign = db.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if not campaign:
            raise ValueError("Campaign not found")
        campaign_id = campaign.id

    if campaign_slug is None and campaign_id is not None:
        campaign = db.get(Campaign, campaign_id)
        campaign_slug = getattr(campaign, "slug", None) if campaign else None
        if campaign_slug is None:
            campaign_slug = ""

    created: list[ContentPack] = []

    for platform in payload.platforms:
        key = platform.value
        content_json = payload.content_json_by_platform.get(key) or {}
        if payload.cta and "cta" not in content_json:
            content_json["cta"] = {"target": payload.target, **payload.cta}

        pack = ContentPack(
            campaign_id=int(campaign_id),
            trend_item_id=payload.trend_item_id,
            platform=platform,
            title=None,
            content_json=content_json,
            quality_score=0,
            is_approved=False,
        )
        db.add(pack)
        created.append(pack)

    db.commit()
    for pack in created:
        db.refresh(pack)

    return {
        "campaign_slug": campaign_slug,
        "created": len(created),
        "packs": [{"content_pack_id": p.id, "platform": p.platform, "is_approved": p.is_approved} for p in created],
    }


def list_approved_content_packs(db: Session, limit: int = 50) -> list[ContentPack]:
    stmt = select(ContentPack).where(ContentPack.is_approved.is_(True)).order_by(ContentPack.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())


def approve_content_pack(db: Session, content_pack_id: int, is_approved: bool) -> ContentPack:
    pack = db.get(ContentPack, content_pack_id)
    if not pack:
        raise ValueError("Content pack not found")

    pack.is_approved = is_approved
    db.add(pack)
    db.commit()
    db.refresh(pack)
    return pack

from typing import Generator

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.campaigns import CampaignCreate, CampaignCreateResponse, CampaignListResponse
from app.services.campaigns import create_campaign, list_campaigns

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=CampaignCreateResponse, status_code=201)
def create(payload: CampaignCreate, db: Session = Depends(get_db)):
    campaign = create_campaign(db, payload)
    return CampaignCreateResponse(
        campaign_id=campaign.id,
        name=campaign.name,
        slug=getattr(campaign, "slug", None) or payload.slug,
        region=campaign.region,
        target=campaign.target,
        status=campaign.status,
    )


@router.get("", response_model=CampaignListResponse)
def list_all(
    region: str | None = None,
    status: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    campaigns = list_campaigns(db, region=region, status=status, limit=limit)
    items = [
        CampaignCreateResponse(
            campaign_id=c.id,
            name=c.name,
            slug=getattr(c, "slug", None) or "",
            region=c.region,
            target=c.target,
            status=c.status,
        )
        for c in campaigns
    ]
    return CampaignListResponse(items=items)

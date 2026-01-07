from typing import Generator

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.trends import (
    TrendIngestRequest,
    TrendIngestResponse,
    TrendIngestTopTrend,
    TrendTopItem,
    TrendTopResponse,
)
from app.services.trends import ingest_trends, list_top_trends

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ingest", response_model=TrendIngestResponse)
def ingest(payload: TrendIngestRequest, db: Session = Depends(get_db)):
    touched = ingest_trends(db, payload)

    top = list_top_trends(db, region=payload.region, limit=20)
    top_trends = [
        TrendIngestTopTrend(
            trend_item_id=t.id,
            topic=t.topic,
            score=float(t.score),
            region=t.region,
            category=t.category,
            url=t.url,
        )
        for t in top
    ]

    # Return MVP envelope + keep legacy ingested_count for existing callers.
    return TrendIngestResponse(ingested=len(touched), ingested_count=len(touched), top_trends=top_trends)


@router.get("/top", response_model=TrendTopResponse)
def top(region: str, limit: int = 10, db: Session = Depends(get_db)):
    items = list_top_trends(db, region=region, limit=limit)
    out_items = [
        TrendTopItem(
            trend_item_id=t.id,
            topic=t.topic,
            score=float(t.score),
            category=t.category,
            last_seen_at=t.last_seen_at,
            url=t.url,
        )
        for t in items
    ]
    return TrendTopResponse(region=region, items=out_items)

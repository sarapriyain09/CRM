from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.posts import (
    PostMetricsResponse,
    PostMetricsUpdate,
    PostRecentItem,
    PostRecentResponse,
    PostScheduleRequest,
    PostScheduleResponse,
    PostStatusUpdate,
    PostStatusUpdateResponse,
)
from app.services.posts import (
    schedule_post,
    update_post_status,
    update_post_metrics,
    list_recent_posts,
)

router = APIRouter()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/schedule", response_model=PostScheduleResponse)
def schedule(payload: PostScheduleRequest, db: Session = Depends(get_db)):
    post = schedule_post(db, payload)
    return {"post_id": post.id, "status": post.status, "scheduled_at": post.scheduled_at}


@router.post("/update-status", response_model=PostStatusUpdateResponse)
def update_status(payload: PostStatusUpdate, db: Session = Depends(get_db)):
    try:
        post = update_post_status(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"post_id": post.id, "status": post.status}


@router.post("/metrics", response_model=PostMetricsResponse)
def metrics(payload: PostMetricsUpdate, db: Session = Depends(get_db)):
    try:
        post = update_post_metrics(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"post_id": post.id, "updated": True}


@router.get("/recent", response_model=PostRecentResponse)
def recent(status: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    posts = list_recent_posts(db, status=status, limit=limit)
    items = [PostRecentItem(post_id=p.id, platform=p.platform, status=p.status, post_url=p.post_url) for p in posts]
    return PostRecentResponse(items=items)

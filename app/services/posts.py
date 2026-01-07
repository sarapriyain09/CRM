from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.social_post import SocialPost
from app.models.enums import PostStatus
from app.schemas.posts import PostMetricsUpdate, PostScheduleRequest, PostStatusUpdate


def schedule_post(db: Session, payload: PostScheduleRequest) -> SocialPost:
    post = SocialPost(
        campaign_id=payload.campaign_id,
        content_pack_id=payload.content_pack_id,
        platform=payload.platform,
        status=PostStatus.scheduled,
        scheduled_at=payload.scheduled_at,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post_status(db: Session, payload: PostStatusUpdate) -> SocialPost:
    post = db.get(SocialPost, payload.post_id)
    if not post:
        raise ValueError("Post not found")

    post.status = payload.status
    if payload.scheduled_at is not None:
        post.scheduled_at = payload.scheduled_at
    if payload.published_at is not None:
        post.published_at = payload.published_at
    if payload.external_post_id is not None:
        post.external_post_id = payload.external_post_id
    if payload.post_url is not None:
        post.post_url = payload.post_url

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post_metrics(db: Session, payload: PostMetricsUpdate) -> SocialPost:
    post = db.get(SocialPost, payload.post_id)
    if not post:
        raise ValueError("Post not found")

    existing = post.metrics or {}
    incoming = payload.metrics or {}
    # MVP: shallow merge; platform-specific metrics can be nested later.
    post.metrics = {**existing, **incoming}
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def list_recent_posts(db: Session, status: str | None = None, limit: int = 50) -> list[SocialPost]:
    stmt = select(SocialPost).order_by(SocialPost.created_at.desc()).limit(limit)
    if status:
        try:
            stmt = stmt.where(SocialPost.status == PostStatus(status))
        except ValueError:
            stmt = stmt.where(SocialPost.status == status)
    return list(db.scalars(stmt).all())

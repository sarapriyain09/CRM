from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.trend_item import TrendItem
from app.models.trend_snapshot import TrendSnapshot
from app.models.trend_source import TrendSource
from app.schemas.trends import TrendIngestRequest


def _compute_trend_score(metrics: dict[str, Any], features: dict[str, Any]) -> float:
    """Compute a simple 0..1-ish score.

    MVP heuristic:
    - `metrics.interest` (0..100) is primary signal
    - `features.recency_hours` boosts newer items
    """
    interest = metrics.get("interest")
    if interest is None:
        interest_f = 0.0
    else:
        try:
            interest_f = float(interest)
        except (TypeError, ValueError):
            interest_f = 0.0

    interest_norm = max(0.0, min(1.0, interest_f / 100.0))

    recency_hours = features.get("recency_hours")
    if recency_hours is None:
        recency_f = None
    else:
        try:
            recency_f = float(recency_hours)
        except (TypeError, ValueError):
            recency_f = None

    if recency_f is None:
        recency_factor = 0.5
    else:
        # Newer -> closer to 1.0; older -> decays toward 0.0
        recency_factor = 1.0 / (1.0 + (recency_f / 24.0))

    score = (0.75 * interest_norm) + (0.25 * recency_factor)
    return float(round(max(0.0, min(1.0, score)), 3))


def ingest_trends(db: Session, payload: TrendIngestRequest) -> list[TrendItem]:
    sources = {s.name: s for s in db.scalars(select(TrendSource)).all()}
    touched_items: list[TrendItem] = []

    now = datetime.now(timezone.utc)

    for item in payload.items:
        source = sources.get(item.source)
        if not source:
            source = TrendSource(name=item.source, details={})
            db.add(source)
            db.flush()
            sources[source.name] = source

        score = _compute_trend_score(item.metrics, item.features)

        # "Upsert" approximation: match by (source, region, topic, category, language, url)
        existing = db.scalar(
            select(TrendItem).where(
                and_(
                    TrendItem.source_id == source.id,
                    TrendItem.region == payload.region,
                    TrendItem.topic == item.topic,
                    TrendItem.category.is_(None) if item.category is None else TrendItem.category == item.category,
                    TrendItem.language.is_(None) if item.language is None else TrendItem.language == item.language,
                    TrendItem.url.is_(None) if item.url is None else TrendItem.url == item.url,
                )
            )
        )

        if existing:
            existing.last_seen_at = now
            existing.features = item.features or {}
            existing.score = score
            db.add(existing)
            trend = existing
        else:
            trend = TrendItem(
                source_id=source.id,
                region=payload.region,
                language=item.language,
                topic=item.topic,
                url=item.url,
                category=item.category,
                score=score,
                features=item.features,
                first_seen_at=now,
                last_seen_at=now,
            )
            db.add(trend)

        db.flush()  # ensure trend.id exists
        db.add(TrendSnapshot(trend_item_id=trend.id, snapshot_at=now, metrics=item.metrics or {}))
        touched_items.append(trend)

    db.commit()
    for trend in touched_items:
        db.refresh(trend)

    return touched_items


def list_top_trends(db: Session, region: str, limit: int = 20) -> list[TrendItem]:
    stmt = (
        select(TrendItem)
        .where(TrendItem.region == region)
        .order_by(TrendItem.score.desc(), TrendItem.last_seen_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())

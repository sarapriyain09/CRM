from fastapi import APIRouter, Depends

from app.api.routes import campaigns, content, handoff, leads, posts, scoring, trends
from app.api.deps import require_auth

api_router = APIRouter(dependencies=[Depends(require_auth)])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])
api_router.include_router(handoff.router, prefix="/handoff", tags=["handoff"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])

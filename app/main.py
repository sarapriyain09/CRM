from fastapi import FastAPI

from app.api.api import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Splendid CRM API", version="0.1.0")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()

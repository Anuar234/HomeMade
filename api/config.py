"""
API Configuration
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


class CachedStaticFiles(StaticFiles):
    """Custom StaticFiles with cache headers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        # Cache static files for 1 year
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


def configure_app(app: FastAPI):
    """Configure FastAPI app with middleware and static files"""

    # Mount static files
    app.mount("/static", CachedStaticFiles(directory="static"), name="static")

    # CORS for Telegram Mini App
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

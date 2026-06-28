"""
Routers package — exposes all route modules
"""

from app.routers.auth import router as auth_router
from app.routers.heroes import router as heroes_router
from app.routers.missions import router as missions_router

__all__ = [
    "auth_router",
    "heroes_router",
    "missions_router",
]
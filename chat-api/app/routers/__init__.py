from .auth import router as auth_router
from .user import router as user_router
from .room import router as room_router

__all__ = (
    'auth_router',
    'user_router',
    'room_router')
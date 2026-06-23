from .incidents import router as incidents_router
from .rgph import router as rgph_router
from .ai import predict_router, router as ai_router
from .health import router as health_router
from .map import router as map_router

__all__ = [
    'incidents_router',
    'rgph_router',
    'ai_router',
    'predict_router',
    'health_router',
    'map_router'
]

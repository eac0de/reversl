from fastapi import APIRouter

from app.dependencies.csrf_protect import CSRFProtectDep

from .api import router as api_router
from .ssr import router as ssr_router
from .ws import router as ws_router

router = APIRouter()

router.include_router(
    router=ssr_router,
    dependencies=[
        CSRFProtectDep,
    ],
)

router.include_router(
    prefix="/api",
    router=api_router,
    dependencies=[
        CSRFProtectDep,
    ],
)
router.include_router(
    prefix="/ws",
    router=ws_router,
)

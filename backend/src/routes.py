from fastapi import APIRouter

from .packages.auth import auth_router
from .packages.companies import company_router
from .packages.ai.endpoints import router as ai_router

router = APIRouter()

router.include_router(ai_router)
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(company_router, prefix="/company", tags=["Company"])
# router.include_router(
#     users_router,
#     prefix="/users",
#     tags=["Users"],
# )

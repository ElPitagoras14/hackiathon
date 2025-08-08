from fastapi import APIRouter

from packages.auth import auth_router
# from packages.users import users_router


router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# router.include_router(
#     users_router,
#     prefix="/users",
#     tags=["Users"],
# )

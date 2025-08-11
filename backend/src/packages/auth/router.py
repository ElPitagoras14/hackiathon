import time
from fastapi import APIRouter, Request, Response
from loguru import logger

from ...utils.responses import (
    ConflictResponse,
    InternalServerErrorResponse,
    SuccessResponse,
)

from .service import login_controller, register_controller
from .responses import TokenOut
from .schemas import LoginInfo, CreateInfo
from .config import auth_settings

auth_router = APIRouter()

ACCESS_TOKEN_EXP_MIN = auth_settings.ACCESS_TOKEN_EXP_MIN
REFRESH_TOKEN_EXP_DAY = auth_settings.REFRESH_TOKEN_EXP_DAY


@auth_router.post(
    "/login",
    responses={
        200: {"model": TokenOut},
        409: {"model": ConflictResponse},
        500: {"model": InternalServerErrorResponse},
    },
)
async def login(request: Request, response: Response, login_info: LoginInfo):
    start_time = time.time()
    request_id = request.state.request_id
    try:
        logger.info(f"Logging in {login_info.email}")
        data, error = login_controller(
            login_info.email, login_info.password
        )
        process_time = time.time() - start_time

        if error:
            logger.warning(f"Error logging in: {error}")
            response.status_code = 409
            return ConflictResponse(
                request_id=request_id,
                process_time=process_time,
                message=error,
                func="login",
            )

        logger.info(f"Logged in in {process_time:.2f} seconds")
        return TokenOut(
            request_id=request_id,
            process_time=process_time,
            func="login",
            message="User logged in",
            payload=data,
        )
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        response.status_code = 500
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="login"
        )


@auth_router.post(
    "/register",
    responses={
        200: {"model": SuccessResponse},
        409: {"model": ConflictResponse},
        500: {"model": InternalServerErrorResponse},
    },
)
async def register(
    request: Request,
    response: Response,
    register_info: CreateInfo,
):
    start_time = time.time()
    request_id = request.state.request_id
    try:
        logger.info(f"Registering {register_info.email}")
        data, error = register_controller(
            register_info.email,
            register_info.password,
        )
        process_time = time.time() - start_time

        if error:
            logger.warning(f"Error registering: {error}")
            response.status_code = 409
            return ConflictResponse(
                request_id=request_id,
                process_time=process_time,
                message=error,
                func="register",
            )

        logger.info(f"Registered in {process_time:.2f} seconds")
        return SuccessResponse(
            request_id=request_id,
            process_time=process_time,
            func="register",
            message="User registered",
        )
    except Exception as e:
        logger.error(f"Error registering: {e}")
        return InternalServerErrorResponse(
            request_id=request_id, message=str(e), func="register"
        )

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.gzip import GZipMiddleware

from app.config import settings
from app.core.exceptions import ResponseException
from app.database import get_session
from app.services.users_service import UsersService
from app.web.admin_panel.router import router as admin_panel_router
from app.web.api.router import router as api_router
from app.web.middlewares.csrf import CSRFMiddleware
from app.web.middlewares.process_time import ProcessTimeMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await settings.FILES_PATH.mkdir(parents=True, exist_ok=True)
    async with get_session() as db_session:
        await UsersService.create_init_user(
            db_session=db_session,
            email=settings.REVERSL_FIRST_USER_EMAIL,
            password=settings.REVERSL_FIRST_USER_PASSWORD,
        )
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url="/api/docs",
)


@app.exception_handler(ResponseException)
async def raise_response_handler(
    request: Request,  # pylint: disable=unused-argument
    exc: ResponseException,
):
    return exc.response


@app.exception_handler(Exception)
async def internal_server_error_handler(
    request: Request,
    exc: Exception,
):
    tb = traceback.extract_tb(exc.__traceback__)
    last_call = tb[-1] if tb else None
    if last_call:
        error_location = (
            f"File {last_call.filename}, line {last_call.lineno}, in {last_call.name}"
        )
    else:
        error_location = "No traceback available"
    message = f"{request.method} {request.url}\n{error_location}\n{str(exc)}\nError type: {type(exc).__name__}"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": message if settings.MODE != "PROD" else "Internal server error"
        },
    )


# __________________________ Middlewares __________________________ #

if settings.MODE != "PROD":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.add_middleware(
    ProcessTimeMiddleware,
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)
app.add_middleware(
    CSRFMiddleware,
)

# __________________________ Routers __________________________ #

app.include_router(
    prefix="/api",
    router=api_router,
)
app.include_router(
    prefix="/admin",
    router=admin_panel_router,
)

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.gzip import GZipMiddleware

from app.api.middlewares.process_time import ProcessTimeMiddleware
from app.api.routers import documents, images, includes, variables
from app.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    root_path="/api",
)


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    tb = traceback.extract_tb(exc.__traceback__)
    last_call = tb[-1] if tb else None
    if last_call:
        error_location = (
            f"File {last_call.filename}, line {last_call.lineno}, in {last_call.name}"
        )
    else:
        error_location = "No traceback available"
    message = f"{request.method} {request.url}\n{error_location}\n{str(exc)}\nError type: {type(exc).__name__}"
    await TelegramSender.send(message)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc) if settings.MODE != "PROD" else "Internal server error"
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

# __________________________ Routers __________________________ #

app.include_router(
    router=documents.router,
    prefix="/documents",
)
app.include_router(
    router=includes.router,
    prefix="/includes",
)
app.include_router(
    router=variables.router,
    prefix="/variables",
)
app.include_router(
    router=images.router,
    prefix="/images",
)
# app.include_router(
#     router=auth.router,
#     prefix="/auth",
# )

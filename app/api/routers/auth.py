from fastapi import APIRouter

from app.schemas.auth import AccessTokenScheme

router = APIRouter(
    tags=["auth"],
)


@router.post(
    path="/login",
    response_model=AccessTokenScheme,
)
async def login():
    return


@router.post(
    path="/logout",
)
async def logout():
    return

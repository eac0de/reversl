from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_csrf_protect import CsrfProtect  # type: ignore

from app.config import settings
from app.database import DBSessionDep
from app.models.permission import PermissionCode
from app.models.user import User
from app.schemas.auth import LoginSchema
from app.services.users_service import UsersService
from app.web.dependencies.auth import Auth
from app.web.dependencies.users import UserDep

router = APIRouter(
    tags=["Admin panel"],
)

templates = Jinja2Templates(
    directory=settings.PROJECT_DIR.joinpath("web", "admin_panel", "static", "templates")
)


@router.get(
    path="/auth/",
    name="admin_panel_auth",
)
async def get_auth_page(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    context = {
        "request": request,
        "csrf_token": csrf_token,
    }
    response = templates.TemplateResponse(
        name="auth.j2",
        context=context,
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post(
    path="/auth/login/",
    name="admin_panel_login",
)
async def login(
    request: Request,
    db_session: DBSessionDep,
    schema: LoginSchema = Form(),
    csrf_protect: CsrfProtect = Depends(),
):
    await csrf_protect.validate_csrf(request)
    users_service = UsersService(db_session=db_session)
    user = await users_service.auth_user(
        email=schema.email,
        password=schema.password,
    )
    if not user:
        return RedirectResponse(
            url=request.url_for("admin_panel_auth").include_query_params(error=True),
            status_code=303,
        )
    response = RedirectResponse(
        url=request.url_for("admin_panel_home"),
        status_code=303,
    )
    Auth.set_session_cookie(response, user.uid)
    return response


@router.get(
    path="/",
    name="admin_panel_home",
)
async def get_home_page(
    request: Request,
    user: User = UserDep(),
):
    context = {
        "request": request,
        "user": UsersService.to_user_r_schema(user).model_dump(mode="json"),
    }
    return templates.TemplateResponse(
        name="base.j2",
        context=context,
    )


@router.get(
    path="/users/",
    name="admin_panel_users",
)
async def get_users_page(
    request: Request,
    user: User = UserDep(PermissionCode.R_USER),
):

    context = {
        "request": request,
        "user": UsersService.to_user_r_schema(user).model_dump(mode="json"),
    }
    return templates.TemplateResponse(
        name="users.j2",
        context=context,
    )

import bcrypt
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import ScalarResult, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.admin_panel.filters.users import UsersFilter
from app.models.permission import Permission, PermissionCode
from app.models.user import User
from app.schemas.users import (
    PermissionCodesSchema,
    UserCSchema,
    UserRSchemaWithPermissions,
    UserUSchema,
)

AUTO_PERMISSIONS_MAP: dict[PermissionCode, set[PermissionCode]] = {
    PermissionCode.R_PERMISSION: {
        PermissionCode.R_USER,
    },
    PermissionCode.U_PERMISSION: {c for c in PermissionCode.__members__.values()},
    PermissionCode.C_USER: set(),
    PermissionCode.R_USER: set(),
    PermissionCode.U_USER: {
        PermissionCode.R_USER,
    },
    PermissionCode.D_USER: {
        PermissionCode.R_USER,
    },
    PermissionCode.C_MESSAGE: {
        PermissionCode.R_CHAT,
    },
    PermissionCode.R_MESSAGE: {
        PermissionCode.R_CHAT,
    },
    PermissionCode.U_MESSAGE: {
        PermissionCode.R_CHAT,
        PermissionCode.R_MESSAGE,
    },
    PermissionCode.D_MESSAGE: {
        PermissionCode.R_CHAT,
        PermissionCode.R_MESSAGE,
    },
    PermissionCode.R_CHAT: set(),
    PermissionCode.U_CHAT: {
        PermissionCode.R_CHAT,
    },
    PermissionCode.D_CHAT: {
        PermissionCode.R_CHAT,
    },
}


class UsersService:
    def __init__(
        self,
        db_session: AsyncSession,
    ) -> None:
        self.db_session = db_session

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password=password.encode("utf-8"),
            salt=bcrypt.gensalt(),
        ).decode("utf-8")

    async def create_user(
        self,
        schema: UserCSchema,
    ) -> UserRSchemaWithPermissions:
        if await self.db_session.scalar(
            select(exists().where(User.email == schema.email))
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        user = User(
            email=schema.email,
            password=self.hash_password(schema.password),
        )
        self.db_session.add(user)
        await self.db_session.commit()
        return UserRSchemaWithPermissions.model_validate(user, from_attributes=True)

    @classmethod
    async def create_init_user(
        cls,
        db_session: AsyncSession,
        email: EmailStr,
        password: str,
    ) -> None:
        user = await db_session.scalar(
            select(User)
            .where(User.email == email)
            .options(
                joinedload(User.permissions),
            )
        )
        if not user:
            user = User(
                email=email,
                password=cls.hash_password(password),
            )
            db_session.add(user)
        user.permissions.clear()
        for c in PermissionCode.__members__.values():
            user.permissions.append(
                Permission(
                    code=c,
                )
            )

    @staticmethod
    async def auth_user(
        db_session: AsyncSession,
        email: EmailStr,
        password: str,
    ) -> User | None:
        user = await db_session.scalar(select(User).where(User.email == email))
        if not user:
            return None
        if not bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=user.password.encode("utf-8"),
        ):
            return None
        return user

    @staticmethod
    def to_user_r_schema(user: User) -> UserRSchemaWithPermissions:
        return UserRSchemaWithPermissions(
            uid=user.uid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic_name=user.patronymic_name,
            phone_number=user.phone_number,
            permission_codes={p.code for p in user.permissions},
        )

    async def get_users_list(
        self,
        users_filter: UsersFilter,
    ) -> ScalarResult[User]:
        return await self.db_session.scalars(users_filter(select(User)))

    async def get_user_or_none(
        self,
        user_uid: int,
        *,
        join_permissions: bool = False,
    ) -> User | None:
        stmt = select(User).where(User.uid == user_uid)
        if join_permissions:
            stmt = stmt.options(joinedload(User.permissions))
        user = await self.db_session.scalar(stmt)
        return user

    async def update_user(
        self,
        user: User,
        schema: UserUSchema,
    ) -> User:
        data = schema.model_dump(exclude_unset=True)
        email = data.setdefault("email", user.email)
        if email != user.email and await self.db_session.scalar(
            select(exists().where(User.email == data["email"]))
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        await self.db_session.execute(
            update(User).where(User.uid == user.uid).values(**data)
        )
        await self.db_session.flush()
        await self.db_session.refresh(user, attribute_names=["permissions"])
        return user

    async def update_user_permissions(
        self,
        current_user_uid: int,
        user: User,
        schema: PermissionCodesSchema,
    ) -> ScalarResult[Permission]:
        if user.uid == current_user_uid:
            schema.permission_codes.add(PermissionCode.U_PERMISSION)
        validated_permission_codes = set(schema.permission_codes)
        for code in schema.permission_codes:
            validated_permission_codes.update(AUTO_PERMISSIONS_MAP.get(code, set()))
        user.permissions = [
            Permission(
                code=code,
            )
            for code in validated_permission_codes
        ]
        await self.db_session.flush()
        return await self.db_session.scalars(
            select(Permission).where(Permission.user_uid == user.uid)
        )

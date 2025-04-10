from uuid import UUID, uuid4

import bcrypt
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.permission import Permission, PermissionCode
from app.models.user import User
from app.schemas.users import UserCSchema, UserLSchema, UserRSchema


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
    ) -> UserRSchema:
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
        return UserRSchema.model_validate(user, from_attributes=True)

    async def create_init_user(
        self,
        email: EmailStr,
        password: str,
    ):
        user = await self.db_session.scalar(
            select(User)
            .where(User.email == email)
            .options(
                joinedload(User.permissions),
            )
        )
        if not user:
            user = User(
                uid=uuid4(),
                email=email,
                password=self.hash_password(password),
            )
            self.db_session.add(user)
        user.permissions.clear()
        for c in PermissionCode.__members__.values():
            user.permissions.append(
                Permission(
                    code=c,
                )
            )
        await self.db_session.commit()

    async def auth_user(
        self,
        email: EmailStr,
        password: str,
    ) -> User | None:
        user = await self.db_session.scalar(select(User).where(User.email == email))
        if not user:
            return None
        if not bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=user.password.encode("utf-8"),
        ):
            return None
        return user

    @staticmethod
    def to_user_r_schema(user: User) -> UserRSchema:
        return UserRSchema(
            uid=user.uid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic_name=user.patronymic_name,
            phone_number=user.phone_number,
            permissions=[p.code.value for p in user.permissions],
        )

    async def get_users_list(self) -> list[UserLSchema]:
        return [
            UserLSchema.model_validate(user, from_attributes=True)
            async for user in await self.db_session.stream_scalars(select(User))
        ]

    async def get_user(self, user_uid: UUID) -> UserRSchema | None:
        user = await self.get_user_or_none(
            user_uid,
            join_permissions=True,
        )
        if not user:
            return None
        return self.to_user_r_schema(user)

    async def get_user_or_none(
        self,
        user_uid: UUID,
        *,
        join_permissions: bool = False,
    ) -> User | None:
        stmt = select(User).where(User.uid == user_uid)
        if join_permissions:
            stmt = stmt.options(joinedload(User.permissions))
        return await self.db_session.scalar(stmt)

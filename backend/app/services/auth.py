"""
Authentication service layer.

Handles:
- User authentication
- Password verification
- JWT token generation
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.jwt import (
    create_access_token,
    create_refresh_token,
)

from backend.app.core.security import verify_password

from backend.app.repositories.user import UserRepository
from backend.app.schemas.user import UserResponse


class AuthService:
    """
    Authentication business logic.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.repository = UserRepository(session)


    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> UserResponse | None:
        """
        Validate user credentials.
        """

        user = await self.repository.get_by_username(
            username
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        return UserResponse.model_validate(user)


    def create_tokens(
        self,
        user_id: int,
    ) -> dict[str, str]:
        """
        Generate JWT access and refresh tokens.
        """

        return {
            "access_token": create_access_token(
                str(user_id)
            ),
            "refresh_token": create_refresh_token(
                str(user_id)
            ),
            "token_type": "bearer",
        }
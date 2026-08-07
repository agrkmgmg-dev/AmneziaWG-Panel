"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db
from backend.app.schemas.user import UserLogin
from backend.app.services.auth import AuthService


router = APIRouter()


@router.post("/login")
async def login(
    data: UserLogin,
    session: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT tokens.
    """

    service = AuthService(session)

    user = await service.authenticate(
        username=data.username,
        password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    tokens = service.create_tokens(
        user_id=user.id,
    )

    return {
        "user": user,
        **tokens,
    }
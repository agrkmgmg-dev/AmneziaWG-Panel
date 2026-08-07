"""
Authentication API router.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from backend.app.api.dependencies import (
    get_auth_service,
)

from backend.app.core.dependencies import (
    get_current_user,
)

from backend.app.models.user import User

from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)

from backend.app.schemas.user import (
    UserResponse,
)

from backend.app.services.auth import (
    AuthService,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    """

    user = await service.authenticate(
        data.username,
        data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return TokenResponse(
        **service.create_tokens(
            user.id
        )
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_current_user_profile(
    user: User = Depends(
        get_current_user
    ),
) -> UserResponse:
    """
    Get current authenticated user.
    """

    return UserResponse.model_validate(
        user
    )
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

from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
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
        )

    return service.create_tokens(
        user.id
    )
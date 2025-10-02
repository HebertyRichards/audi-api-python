from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from schemas.auth_schemas import UserCurrent
from typing import Optional

from services.auth_service import get_user_by_token
from helpers.exceptions import AppException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token_from_header: Optional[str] = Depends(oauth2_scheme),
) -> UserCurrent:

    access_token = token_from_header

    if not access_token:
        access_token = request.cookies.get("sb-access-token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_data = await get_user_by_token(access_token)
        return UserCurrent(**user_data)
    except AppException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

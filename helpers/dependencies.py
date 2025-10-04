from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from schemas.auth_schemas import UserCurrent
from typing import Optional

from services.auth_service import get_user_by_token
from helpers.exceptions import AppException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_token(
    request: Request,
    token_from_header: Optional[str] = Depends(oauth2_scheme),
) -> str:

    access_token = token_from_header
    if not access_token:
        access_token = request.cookies.get("sb-access-token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return access_token


async def get_current_user(
    access_token: str = Depends(get_current_token),
) -> UserCurrent:
    try:
        user_data = await get_user_by_token(access_token)
        return UserCurrent(**user_data)
    except AppException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_for_delete(
    current_user: UserCurrent = Depends(get_current_user),
) -> UserCurrent:

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado para operação de exclusão de conta.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

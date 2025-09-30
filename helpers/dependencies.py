from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas.auth_schemas import UserCurrent

from services.auth_service import get_user_by_token
from helpers.exceptions import AppException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserCurrent:

    try:
        user_data = await get_user_by_token(token)
        return UserCurrent(**user_data)
    except AppException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

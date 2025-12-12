from fastapi import Depends, HTTPException, status, Request, Response, WebSocket, Query
import os
from fastapi.security import OAuth2PasswordBearer
from schemas.auth_schemas import UserCurrent
from typing import Optional
from services.auth_service import get_user_by_token, refresh_user_token
from helpers.exceptions import AppException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user_ws(
    websocket: WebSocket, token_query: Optional[str] = Query(None, alias="token")
) -> UserCurrent:
    access_token = token_query

    if not access_token:
        access_token = websocket.cookies.get("sb-access-token")

    if not access_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="Token não fornecido")

    try:
        user_data = await get_user_by_token(access_token)
        return UserCurrent(**user_data)

    except AppException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="Token inválido")


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


IS_PRODUCTION = os.environ.get("NODE_ENV") == "production"
ONE_HOUR = 3600


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: Optional[str],
    access_expiry: int,
    refresh_expiry: int,
):
    response.set_cookie(
        key="sb-access-token",
        value=access_token,
        max_age=access_expiry,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="none" if IS_PRODUCTION else "lax",
    )
    if refresh_token:
        response.set_cookie(
            key="sb-refresh-token",
            value=refresh_token,
            max_age=refresh_expiry,
            httponly=True,
            secure=IS_PRODUCTION,
            samesite="none" if IS_PRODUCTION else "lax",
        )
    else:
        response.delete_cookie("sb-refresh-token")


def clear_auth_cookies(response: Response):
    response.delete_cookie("sb-access-token")
    response.delete_cookie("sb-refresh-token")


async def get_session(request: Request, response: Response):
    access_token = request.cookies.get("sb-access-token")
    refresh_token = request.cookies.get("sb-refresh-token")

    if access_token:
        try:
            return await get_user_by_token(access_token)
        except AppException:
            pass

    if refresh_token:
        try:
            refreshed_data = await refresh_user_token(refresh_token)
            new_access_token = refreshed_data["new_access_token"]
            refreshed_user = await get_user_by_token(new_access_token)

            set_auth_cookies(response, new_access_token, None, ONE_HOUR, 0)
            return refreshed_user
        except AppException:
            clear_auth_cookies(response)
            return None
    return None


async def get_required_user(request: Request, response: Response) -> dict:
    user = await get_session(request, response)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado ou sessão inválida.",
        )
    return user


async def get_required_admin_user(request: Request, response: Response) -> dict:
    user = await get_required_user(request, response)

    user_role = user.get("role")
    if user_role not in ("Fundador", "Desenvolvedor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer privilégios de administrador.",
        )

    return user

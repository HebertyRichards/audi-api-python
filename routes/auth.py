import os
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from typing import Optional

from services.auth import (
    register_user,
    login_user,
    get_user_by_token,
    refresh_user_token,
    send_recovery_email,
    update_password_with_token,
    update_authenticated_user_password,
    delete_user_account,
)

from schemas.auth import (
    UserCreate,
    UserLogin,
    UserSession,
    PasswordRecovery,
    PasswordChange,
    PasswordUpdate,
    AccountDelete,
)

auth_routes = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

IS_PRODUCTION = os.environ.get("NODE_ENV") == 'production'
ONE_HOUR = 3600

def set_auth_cookies(response: Response, access_token: str, refresh_token: Optional[str], access_expiry: int, refresh_expiry: int):
    response.set_cookie(
        key="sb-access-token", value=access_token, max_age=access_expiry,
        httponly=True, secure=IS_PRODUCTION, samesite='none' if IS_PRODUCTION else 'lax'
    )
    if refresh_token:
        response.set_cookie(
            key="sb-refresh-token", value=refresh_token, max_age=refresh_expiry,
            httponly=True, secure=IS_PRODUCTION, samesite='none' if IS_PRODUCTION else 'lax'
        )

def clear_auth_cookies(response: Response):
    response.delete_cookie("sb-access-token")
    response.delete_cookie("sb-refresh-token")

async def get_current_user(request: Request, response: Response) -> Optional[dict]:
    access_token = request.cookies.get("sb-access-token")
    if access_token:
        try:
            return await get_user_by_token(access_token)
        except:
            pass

    refresh_token = request.cookies.get("sb-refresh-token")
    if refresh_token:
        try:
            refreshed = await refresh_user_token(refresh_token)
            new_access_token = refreshed["new_access_token"]
            user = await get_user_by_token(new_access_token)
            response.set_cookie(
                key="sb-access-token", value=new_access_token, max_age=ONE_HOUR,
                httponly=True, secure=IS_PRODUCTION, samesite='none' if IS_PRODUCTION else 'lax'
            )
            return user
        except:
            clear_auth_cookies(response)
    return None

async def get_required_user(user: Optional[dict] = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado ou sessão inválida."
        )
    return user


@auth_routes.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    return await register_user(user_data)

@auth_routes.post("/login", status_code=status.HTTP_200_OK)
async def login(response: Response, user_data: UserLogin):
    tokens = await login_user(user_data.email, user_data.password, user_data.keep_logged)
    set_auth_cookies(
        response, tokens["access_token"], tokens.get("refresh_token"),
        tokens["access_token_expiry"], tokens["refresh_token_expiry"]
    )
    return {"message": "Login realizado com sucesso!"}

@auth_routes.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logout realizado com sucesso!"}

@auth_routes.get("/session", response_model=Optional[UserSession])
async def get_session(user: Optional[dict] = Depends(get_current_user)):
    return user

@auth_routes.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(body: PasswordRecovery):
    return await send_recovery_email(body.email)

@auth_routes.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(body: PasswordChange):
    return await update_password_with_token(body.access_token, body.new_password)


@auth_routes.patch("/update-password", status_code=status.HTTP_200_OK)
async def update_password(
    request: Request,
    body: PasswordUpdate,
    user: dict = Depends(get_required_user)
):
    access_token = request.cookies.get("sb-access-token")
    return await update_authenticated_user_password(access_token, body.new_password)

@auth_routes.delete("/delete-account", status_code=status.HTTP_200_OK)
async def delete_account(
    response: Response,
    body: AccountDelete,
    user: dict = Depends(get_required_user)
):
    result = await delete_user_account(user_id=str(user['id']), email=user['email'], password=body.password)
    clear_auth_cookies(response)
    return result
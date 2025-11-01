import os
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from typing import Optional
from fastapi.responses import JSONResponse
from helpers.exceptions import AppException
from services.auth_service import (
    register_user,
    login_user,
    send_recovery_email,
    update_password_with_token,
    update_authenticated_user_password,
    delete_user_account,
)
from schemas.auth_schemas import (
    UserCreate,
    UserLogin,
    UserSession,
    PasswordRecovery,
    PasswordChange,
    PasswordUpdate,
    AccountDelete,
    UserCurrent,
    MessageResponse,
)
from helpers.dependencies import (
    get_current_user,
    get_current_user_for_delete,
    set_auth_cookies,
    clear_auth_cookies,
    get_session,
)

auth_tag_metadata = {
    "name": "Autenticação",
    "description": "Endpoints para registro, login, logout, recuperação de senha e gerenciamento de conta.",
}
auth_routes = APIRouter(prefix="/auth", tags=[auth_tag_metadata["name"]])


@auth_routes.post(
    "/register", summary="Registra um novo usuário", status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate):
    return await register_user(user_data)


@auth_routes.post(
    "/login", summary="Autentica um usuário", status_code=status.HTTP_200_OK
)
async def login(response: Response, user_data: UserLogin):
    tokens = await login_user(
        user_data.email, user_data.password, user_data.keep_logged
    )
    set_auth_cookies(
        response,
        tokens["access_token"],
        tokens.get("refresh_token"),
        tokens["access_token_expiry"],
        tokens["refresh_token_expiry"],
    )
    return {"message": "Login realizado com sucesso!"}


@auth_routes.post(
    "/logout", summary="Desconecta o usuário", status_code=status.HTTP_200_OK
)
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logout realizado com sucesso!"}


@auth_routes.get(
    "/session",
    summary="Obtém a sessão do usuário",
    response_model=Optional[UserSession],
)
async def get_session_route(request: Request, response: Response):
    return await get_session(request, response)


@auth_routes.post(
    "/forgot-password",
    summary="Envia e-mail de recuperação de senha",
    status_code=status.HTTP_200_OK,
)
async def forgot_password(body: PasswordRecovery):
    return await send_recovery_email(body.email)


@auth_routes.put(
    "/change-password",
    summary="Altera a senha do usuário com token de recuperação",
    status_code=status.HTTP_200_OK,
)
async def change_password(body: PasswordChange):
    return await update_password_with_token(body.access_token, body.new_password)


@auth_routes.patch(
    "/update-password",
    summary="Atualiza a senha do usuário autenticado",
    status_code=status.HTTP_200_OK,
)
async def update_password(
    response: Response,
    body: PasswordUpdate,
    current_user: UserCurrent = Depends(get_current_user),
):
    new_session_data = await update_authenticated_user_password(
        user=current_user, new_password=body.new_password
    )

    response.set_cookie(
        key="sb-access-token",
        value=new_session_data["access_token"],
        httponly=True,
        samesite="lax",
        secure=True,
    )
    response.set_cookie(
        key="sb-refresh-token",
        value=new_session_data["refresh_token"],
        httponly=True,
        samesite="lax",
        secure=True,
    )

    return {"message": "Senha atualizada com sucesso e sessão renovada!"}


@auth_routes.delete(
    "/delete-account",
    response_model=MessageResponse,
    summary="Deleta a conta do usuário autenticado",
    status_code=status.HTTP_200_OK,
)
async def delete_account_route(
    body: AccountDelete,
    current_user: UserCurrent = Depends(get_current_user_for_delete),
):
    result = await delete_user_account(
        user_id=str(current_user.id),
        email=current_user.email,
        password=body.password,
    )

    final_response = JSONResponse(content=result)

    final_response.delete_cookie("sb-access-token")
    final_response.delete_cookie("sb-refresh-token")

    return final_response

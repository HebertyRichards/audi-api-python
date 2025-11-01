from fastapi import APIRouter, Request, Response, HTTPException, status
from services.auth_service import login_user
from routes.auth_routes import set_auth_cookies
from schemas.auth_schemas import UserLogin

admin_tag_metadata = {
    "name": "Administração",
    "description": "Endpoints para funcionalidades administrativas.",
}

admin_routes = APIRouter(prefix="/admin", tags=[admin_tag_metadata["name"]])


@admin_routes.post(
    "/login",
    summary="Login de Administrador",
    status_code=status.HTTP_200_OK,
)
async def admin_login(response: Response, user_data: UserLogin):
    tokens = await login_user(
        user_data.email, user_data.password, user_data.keep_logged
    )

    if tokens.get("role") not in ("Fundador", "Desenvolvedor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer privilégios de administrador.",
        )

    set_auth_cookies(
        response,
        tokens["access_token"],
        tokens.get("refresh_token"),
        tokens["access_token_expiry"],
        tokens["refresh_token_expiry"],
    )
    return {"message": "Login de administrador realizado com sucesso!"}

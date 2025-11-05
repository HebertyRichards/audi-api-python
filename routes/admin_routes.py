from fastapi import APIRouter, Request, Response, HTTPException, status
from services.auth_service import login_user
from routes.auth_routes import set_auth_cookies
from schemas.auth_schemas import UserLogin
from schemas.category_schemas import CategoryCreate
from services import category_service

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


@admin_routes.post(
    "/create-category",
    response_model=CategoryCreate,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova categoria",
)
async def create_category(category_data: CategoryCreate):
    return await category_service.create_category(
        name=category_data.name,
        slug=category_data.slug,
        role=category_data.role,
        description=category_data.description,
    )


@admin_routes.get(
    "/category-permission",
    status_code=status.HTTP_200_OK,
    summary="Obtém permissões de uma categoria pelo slug",
)
async def get_category_permission():
    return await category_service.get_all_categories()


@admin_routes.delete(
    "/delete-category",
    status_code=status.HTTP_200_OK,
    summary="Deleta uma categoria pelo slug",
)
async def delete_category_route(slug: str):
    await category_service.delete_category(slug)
    return {"message": f"Categoria com slug '{slug}' deletada com sucesso."}

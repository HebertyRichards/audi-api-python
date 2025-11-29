from fastapi import APIRouter, Response, HTTPException, status
from urllib.parse import unquote
from services.auth_service import login_user
from routes.auth_routes import set_auth_cookies
from schemas.auth_schemas import UserLogin
from schemas.category_schemas import CategoryCreate, Category, UpdateCategory
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
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova categoria",
)
async def create_category(category_data: CategoryCreate):
    return await category_service.create_category(
        name=category_data.name,
        slug=category_data.slug,
        topicroles=category_data.topicRoles,
        commentroles=category_data.commentRoles,
        description=category_data.description,
    )


@admin_routes.put(
    "/update-category",
    response_model=Category,
    status_code=status.HTTP_200_OK,
    summary="Atualiza uma categoria existente",
)
async def update_category_route(category_data: UpdateCategory):
    decoded_old_slug = unquote(category_data.old_slug)
    decoded_new_slug = unquote(category_data.new_slug)
    decoded_name = unquote(category_data.name)
    decoded_description = (
        unquote(category_data.description) if category_data.description else None
    )
    return await category_service.update_category(
        old_slug=decoded_old_slug,
        new_slug=decoded_new_slug,
        name=decoded_name,
        topicroles=category_data.topicRoles,
        commentroles=category_data.commentRoles,
        description=decoded_description,
    )


@admin_routes.get(
    "/category-details/{slug}",
    status_code=status.HTTP_200_OK,
    summary="Obtém detalhes de uma categoria pelo slug",
)
async def get_category_details(slug: str):
    return await category_service.get_category_details(slug)


@admin_routes.delete(
    "/delete-category/{slug}",
    status_code=status.HTTP_200_OK,
    summary="Deleta uma categoria pelo slug",
)
async def delete_category_route(slug: str):
    await category_service.delete_category(slug)
    return {"message": f"Categoria deletada com sucesso."}

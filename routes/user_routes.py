from fastapi import APIRouter, Depends, status, Query, Response
from schemas.user_schemas import AllUserResponse
from services import user_service
from helpers.dependencies import get_current_user, UserCurrent

user_tag_metadata = {
    "name": "Usuários",
    "description": "Endpoints para gerenciar usuários.",
}

user_routes = APIRouter(prefix="/user", tags=[user_tag_metadata["name"]])


@user_routes.post(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Atualiza o status online do usuário logado",
)
async def ping(current_user: UserCurrent = Depends(get_current_user)):
    await user_service.upsert_online_user(user_id=str(current_user.id))

    return Response(status_code=status.HTTP_200_OK)


@user_routes.get(
    "/user/all",
    response_model=AllUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtém uma lista paginada de todos os perfis de usuário",
)
async def get_all_users(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)
):
    return await user_service.get_all_profiles(page=page, limit=limit)

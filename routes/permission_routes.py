from fastapi import APIRouter, status, Depends
from services.permission_service import (
    check_comment_creation_permission,
    check_topic_creation_permission,
)

from schemas.permission_schemas import TopicPermissionCheckRequest, PermissionResponse
from helpers.dependencies import get_current_user, UserCurrent

permission_tag_metadata = {
    "name": "Permissões",
    "description": "Endpoints para verificar permissões de criação de tópicos e comentários.",
}

permission_routes = APIRouter(
    prefix="/permission", tags=[permission_tag_metadata["name"]]
)


@permission_routes.post(
    "/topics/check-permission",
    response_model=PermissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Verifica se o usuário logado tem permissão para criar um tópico",
)
async def verify_topic_creation_permission(
    request_data: TopicPermissionCheckRequest,
    current_user: UserCurrent = Depends(get_current_user),
):
    has_permission = await check_topic_creation_permission(
        author_id=str(current_user.id),
        category_slug=request_data.category_slug,
    )
    return {"allowed": has_permission}


@permission_routes.get(
    "/comments/{topic_id}/check-permission",
    response_model=PermissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Verifica se o usuário logado tem permissão para comentar em um tópico",
)
async def verify_comment_creation_permission(
    topic_id: int, current_user: UserCurrent = Depends(get_current_user)
):
    has_permission = await check_comment_creation_permission(
        author_id=str(current_user.id), topic_id=topic_id
    )
    return {"allowed": has_permission}

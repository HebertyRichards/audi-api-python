from fastapi import APIRouter, Depends, status
from services import follow_service
from schemas.follow_schemas import (
    followerProfile,
    FollowStatsResponse,
    FollowingStatsResponse,
    GenericMessageResponse,
)
from helpers.dependencies import get_current_user, UserCurrent

follow_tag_metadata = {
    "name": "Seguir/Deixar de Seguir",
    "description": "Endpoints para seguir e deixar de seguir usuários, além de obter estatísticas de seguidores.",
}

follow_routes = APIRouter(prefix="/follow", tags=[follow_tag_metadata["name"]])


@follow_routes.post(
    "/{username}/follow",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Segue um usuário pelo nome de usuário",
)
async def follow_user(
    username: str, current_user: UserCurrent = Depends(get_current_user)
):
    await follow_service.follow_user(current_user.id, username)
    return {"message": f"Você está seguindo {username} agora."}


@follow_routes.delete(
    "/{username}/follow",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Deixa de seguir um usuário pelo nome de usuário",
)
async def unfollow_user(
    username: str, current_user: UserCurrent = Depends(get_current_user)
):
    await follow_service.unfollow_user(current_user.id, username)
    return {"message": f"Você deixou de seguir {username}."}


@follow_routes.get(
    "/{username}/stats",
    response_model=FollowStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtém estatísticas de seguidores de um usuário",
)
async def get_follow_stats(username: str):
    return await follow_service.get_follow_stats(username)


@follow_routes.get(
    "/{username}/followers",
    response_model=list[followerProfile],
    status_code=status.HTTP_200_OK,
    summary="Obtém a lista de seguidores de um usuário",
)
async def get_followers(username: str):
    return await follow_service.get_followers(username)


@follow_routes.get(
    "/{username}/following",
    response_model=list[followerProfile],
    status_code=status.HTTP_200_OK,
    summary="Obtém a lista de usuários que um usuário está seguindo",
)
async def get_following(username: str):
    return await follow_service.get_following(username)


@follow_routes.get(
    "/{username}/is-following",
    response_model=FollowingStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Verifica se o usuário logado está seguindo outro usuário pelo nome de usuário",
)
async def is_following_user(
    username: str, current_user: UserCurrent = Depends(get_current_user)
):
    return await follow_service.check_following_status(str(current_user.id), username)


@follow_routes.delete(
    "/followers/{username}",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove um seguidor pelo nome de usuário",
)
async def remove_follower(
    username: str, current_user: UserCurrent = Depends(get_current_user)
):
    await follow_service.remove_follower(current_user.id, username)
    return {"message": f"Você removeu {username} dos seus seguidores."}

from fastapi import APIRouter, Depends, status, UploadFile, File
from schemas.profile_schemas import (
    ProfilePublic,
    ProfileDataUpdate,
    ProfileUpdate,
    AvatarUpdateResponse,
    MessageResponse,
)
from services import profile_service
from helpers.dependencies import get_current_user, get_current_token, UserCurrent

profile_tag_metadata = {
    "name": "Perfis de Usuário",
    "description": "Endpoints para gerenciar perfis de usuário.",
}

profile_routes = APIRouter(prefix="/profile", tags=[profile_tag_metadata["name"]])


@profile_routes.get(
    "/{username}",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
    summary="Obtém o perfil de um usuário pelo nome de usuário",
)
async def get_profile_by_username(
    username: str,
):

    return await profile_service.get_user_profile_by_username(username)


@profile_routes.get(
    "/user/{username}",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
    summary="Obtém o perfil de um usuário pelo nome de usuário",
)
async def get_user_profile(username: str):
    return await profile_service.get_user_profile_by_username(username)


@profile_routes.put(
    "/update",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza o perfil do usuário logado",
)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: UserCurrent = Depends(get_current_user),
):
    return await profile_service.update_profile(
        user_id=str(current_user.id),
        profile_data=profile_data.model_dump(exclude_unset=True),
    )


@profile_routes.patch(
    "/update-data",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza o perfil do usuário logado (nome de usuário e e-mail)",
)
async def update_profile_data(
    profile_update: ProfileDataUpdate,
    current_user: UserCurrent = Depends(get_current_user),
    access_token: str = Depends(get_current_token),
):
    return await profile_service.update_user_profile_and_auth(
        access_token=access_token,
        new_username=profile_update.username,
        new_email=profile_update.new_email,
    )


@profile_routes.patch(
    "/user/avatar",
    response_model=AvatarUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Faz upload do avatar do usuário logado",
)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: UserCurrent = Depends(get_current_user),
    token: str = Depends(get_current_token),
):
    return await profile_service.update_avatar(
        user_id=str(current_user.id),
        token=token,
        avatar_file=avatar,
    )


@profile_routes.delete(
    "/user/avatar",
    response_model=AvatarUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove o avatar do usuário logado",
)
async def delete_avatar(current_user: UserCurrent = Depends(get_current_user)):
    return await profile_service.delete_avatar(user_id=str(current_user.id))

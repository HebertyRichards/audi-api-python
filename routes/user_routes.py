from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from schemas.user_schemas import AllUserResponse
from services import user_service
from helpers.dependencies import get_current_user_ws, UserCurrent

user_tag_metadata = {
    "name": "Usuários",
    "description": "Endpoints para gerenciar usuários.",
}

user_routes = APIRouter(prefix="/user", tags=[user_tag_metadata["name"]])


@user_routes.websocket("/ws/ping")
async def websocket_ping(
    websocket: WebSocket,
    current_user: UserCurrent = Depends(get_current_user_ws),
):
    await websocket.accept()
    user_id = str(current_user.id)

    await user_service.upsert_online_user(user_id)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "ping":
                await user_service.upsert_online_user(user_id)

    except WebSocketDisconnect:
        await user_service.remove_online_user(user_id)
        print(f"Usuário {user_id} desconectou.")


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

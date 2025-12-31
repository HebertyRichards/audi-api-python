from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect, Depends
from typing import List, Optional
from services import forum_service
from schemas.forum_schemas import (
    ForumStats,
    RecentPost,
    LastRegistredUser,
    DashboardData,
    OnlineUser,
)
from helpers.dependencies import (
    UserCurrent,
    get_optional_current_user_ws,
)
from helpers.socket_manager import manager

forum_tag_metadata = {
    "name": "Fórum",
    "description": "Endpoints para informações e estatísticas gerais do fórum.",
}

forum_routes = APIRouter(prefix="/forum", tags=[forum_tag_metadata["name"]])


@forum_routes.websocket("/ws/online")
async def websocket_online_users(
    websocket: WebSocket,
    current_user: Optional[UserCurrent] = Depends(get_optional_current_user_ws),
):
    await manager.connect(websocket)
    user_id = str(current_user.id) if current_user else None

    try:
        if user_id:
            await forum_service.upsert_online_user(user_id)

        await manager.broadcast_user_list()
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                if user_id:
                    await forum_service.upsert_online_user(user_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

        if user_id:
            await forum_service.remove_online_user(user_id)

            await manager.broadcast_user_list()


@forum_routes.get(
    "/stats",
    response_model=ForumStats,
    status_code=status.HTTP_200_OK,
    summary="Obtém estatísticas do fórum",
)
async def get_stats():
    return await forum_service.get_forum_stats()


@forum_routes.get(
    "/posts/recent",
    response_model=List[RecentPost],
    status_code=status.HTTP_200_OK,
    summary="Obtém os posts mais recentes",
)
async def get_posts_recent():
    return await forum_service.get_recent_posts()


@forum_routes.get(
    "/last-registration",
    response_model=LastRegistredUser,
    status_code=status.HTTP_200_OK,
    summary="Mostra o último usuário registrado",
)
async def get_last_registration_user():
    return await forum_service.get_last_registration_user()


@forum_routes.get(
    "/online",
    response_model=list[OnlineUser],
    status_code=status.HTTP_200_OK,
    summary="Obtém a lista de usuários online",
)
async def get_online_users():
    return await forum_service.get_online_users()


@forum_routes.get(
    "/data",
    response_model=DashboardData,
    status_code=status.HTTP_200_OK,
    summary="Obtém os dados consolidados da página inicial do fórum",
)
async def get_dashboard_route():
    return await forum_service.get_forum_data()

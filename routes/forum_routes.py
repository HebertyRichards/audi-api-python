from fastapi import APIRouter, status
from typing import List
from services.forum_service import get_forum_stats, get_recent_posts
from schemas.forum_schemas import ForumStats, RecentPost

forum_tag_metadata = {
    "name": "Fórum",
    "description": "Endpoints para informações e estatísticas gerais do fórum.",
}

forum_routes = APIRouter(prefix="/forum", tags=[forum_tag_metadata["name"]])


@forum_routes.get(
    "/stats",
    response_model=ForumStats,
    status_code=status.HTTP_200_OK,
    summary="Obtém estatísticas do fórum",
)
async def get_stats():
    return await get_forum_stats()


@forum_routes.get(
    "/posts/recent",
    response_model=List[RecentPost],
    status_code=status.HTTP_200_OK,
    summary="Obtém os posts mais recentes",
)

async def get_posts_recent():
    return await get_recent_posts()

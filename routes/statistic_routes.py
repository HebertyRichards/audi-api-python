from fastapi import APIRouter
from services import statistic_service
from schemas.statistic_schemas import (
    UseStatsResponse,
    TopicByAuthor,
)
from typing import List

statistic_tag_metadata = {
    "name": "Estatísticas",
    "description": "Endpoints para obter estatísticas do fórum e dos usuários.",
}

statistic_router = APIRouter(prefix="/statistic", tags=[statistic_tag_metadata["name"]])


@statistic_router.get("/profile/{username}/stats", response_model=UseStatsResponse)
async def get_user_statistics(username: str):
    stats = await statistic_service.get_user_stats(username)
    return stats


@statistic_router.get("/profile/{username}/topics", response_model=List[TopicByAuthor])
async def get_topics_by_author_controller(username: str):
    topics = await statistic_service.get_topics_by_author(username)
    return topics

from fastapi import APIRouter, status
from typing import List
from services.category_service import get_all_categories, get_topics_by_category
from schemas.category_schemas import Category, paginatedTopics

category_tag_metadata = {
    "name": "Categorias",
    "description": "Endpoints para gerenciar categorias e tópicos relacionados.",
}

category_routes = APIRouter(prefix="/categories", tags=[category_tag_metadata["name"]])


@category_routes.get(
    "/",
    response_model=List[Category],
    status_code=status.HTTP_200_OK,
    summary="Obtém todas as categorias",
)
async def fetch_all_categories():
    return await get_all_categories()


@category_routes.get(
    "/topics/category/{category}",
    response_model=paginatedTopics,
    status_code=status.HTTP_200_OK,
    summary="Obtém tópicos por categoria com paginação",
)
async def fetch_topics_by_category(category: str, page: int = 1, page_size: int = 10):
    return await get_topics_by_category(category, page, page_size)

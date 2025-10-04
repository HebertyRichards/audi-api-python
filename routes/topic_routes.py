from fastapi import APIRouter, Depends, status, Query, Response, Form, File, UploadFile
from schemas.topic_schemas import (
    TopicResponse,
    TopicPaginatedResponse,
    TopicUpdate,
    CommentResponse,
    CommentUpdate,
)
from services import topic_service, upload_service
from helpers.dependencies import get_current_user, UserCurrent
from typing import List

topic_tag_metadata = {
    "name": "Tópicos e Comentários",
    "description": "Endpoints para gerenciar tópicos e comentários no fórum.",
}

topic_routes = APIRouter(prefix="/posts", tags=[topic_tag_metadata["name"]])


@topic_routes.post(
    "/topics",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo tópico",
)
async def create_topic_route(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    images: List[UploadFile] = File([]),
    current_user: UserCurrent = Depends(get_current_user),
):
    image_urls = []
    if images:
        for image_file in images:
            if image_file.filename:
                url = await upload_service.upload_file(image_file)
                image_urls.append(url)
    new_topic = await topic_service.create_topic(
        title=title,
        content=content,
        author_id=str(current_user.id),
        category=category,
        images=image_urls if image_urls else None,
    )

    topic_details = await topic_service.get_topic_by_field("id", new_topic["id"], 1, 0)
    return topic_details["data"]


@topic_routes.get(
    "/topics/{id}",
    response_model=TopicPaginatedResponse,
    summary="Busca um tópico pelo ID",
)
async def get_topic_route(
    topic_id: int, page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)
):
    return await topic_service.get_topic_by_field("id", topic_id, page, limit)


@topic_routes.get(
    "/topics/slug/{slug}",
    response_model=TopicPaginatedResponse,
    summary="Busca um tópico pelo slug",
)
async def get_topic_by_slug_route(
    slug: str, page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)
):
    return await topic_service.get_topic_by_field("slug", slug, page, limit)


@topic_routes.patch(
    "/topics/{id}", response_model=TopicResponse, summary="Atualiza um tópico"
)
async def update_topic_route(
    id: int,
    topic_data: TopicUpdate,
    current_user: UserCurrent = Depends(get_current_user),
):
    updated_topic = await topic_service.update_topic(
        topic_id=id,
        user_id=str(current_user.id),
        updates=topic_data.model_dump(exclude_unset=True),
    )
    topic_details = await topic_service.get_topic_by_field(
        "id", updated_topic["id"], 1, 0
    )
    return topic_details["data"]


@topic_routes.delete(
    "/topics/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta um tópico"
)
async def delete_topic_route(
    id: int, current_user: UserCurrent = Depends(get_current_user)
):
    await topic_service.delete_topic(topic_id=id, user_id=str(current_user.id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@topic_routes.post(
    "/topics/{topic_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo comentário para um tópico",
)
async def create_comment_route(
    topic_id: int,
    content: str = Form(...),
    images: List[UploadFile] = File([]),
    current_user: UserCurrent = Depends(get_current_user),
):
    image_urls = []
    if images:
        for image_file in images:
            if image_file.filename:
                url = await upload_service.upload_file(image_file)
                image_urls.append(url)

    return await topic_service.create_comment(
        content=content,
        author_id=str(current_user.id),
        topic_id=topic_id,
        images=image_urls if image_urls else None,
    )


@topic_routes.patch(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Atualiza um comentário",
)
async def update_comment_route(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: UserCurrent = Depends(get_current_user),
):
    return await topic_service.update_comment(
        comment_id=comment_id,
        user_id=str(current_user.id),
        content=comment_data.content,
    )


@topic_routes.delete(
    "/comments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deleta um comentário",
)
async def delete_comment_route(
    id: int, current_user: UserCurrent = Depends(get_current_user)
):
    await topic_service.delete_comment(comment_id=id, user_id=str(current_user.id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

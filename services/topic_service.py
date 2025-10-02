import time
import re
import unicodedata
from datetime import datetime, timezone
from typing import List

from config.supabase_client import supabase_admin as supabase
from helpers.exceptions import AppException
from postgrest.exceptions import APIError

from services.category_service import category_exists
from services.upload_service import delete_file


def generate_slug(title: str) -> str:
    normalized_title = (
        unicodedata.normalize("NFD", title).encode("ascii", "ignore").decode("utf-8")
    )
    slug_base = re.sub(r"[^\w\s-]", "", normalized_title).strip().lower()
    slug_base = re.sub(r"[-\s]+", "-", slug_base)
    return f"{slug_base}-{int(time.time() * 1000)}"


async def get_topic_by_field(field: str, value, page: int, limit: int):
    try:
        topic_res = (
            supabase.from_("topicos")
            .select(
                "*, profiles(username, avatar_url, role), imagens(id, url), comment_count:comentarios(count)"
            )
            .eq(field, value)
            .single()
            .execute()
        )

        if not topic_res.data:
            raise AppException("NOT_FOUND", "Tópico não encontrado.")

        topic_data = topic_res.data

        total_comments = topic_data.get("comment_count", [{}])[0].get("count", 0)
        del topic_data["comment_count"]

        comments_from = (page - 1) * limit
        comments_to = comments_from + limit - 1

        comments_res = (
            supabase.from_("comentarios")
            .select("*, profiles(username, avatar_url, role)")
            .eq("topic_id", topic_data["id"])
            .order("created_in", desc=False)
            .range(comments_from, comments_to)
            .execute()
        )

        final_topic_data = {**topic_data, "comentarios": comments_res.data or []}
        return {"data": final_topic_data, "totalComments": total_comments}
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao buscar o tópico: {e.message}")


async def create_topic(
    title: str, content: str, author_id: str, category: str, images: List[str] = None
):
    if not await category_exists(category):
        raise AppException(
            "VALIDATION_ERROR", f"A categoria '{category}' não é válida."
        )

    try:
        rpc_res = supabase.rpc(
            "can_create_topic", {"p_user_id": author_id, "p_category_slug": category}
        ).execute()

        if not rpc_res.data:
            raise AppException(
                "FORBIDDEN_ERROR",
                "Você não tem permissão para criar tópicos nesta categoria.",
            )

        slug = generate_slug(title)
        topic_res = (
            supabase.from_("topicos")
            .insert(
                {
                    "title": title,
                    "content": content,
                    "author_id": author_id,
                    "category": category,
                    "slug": slug,
                }
            )
            .execute()
        )
        topic_data = topic_res.data[0] if topic_res.data else None

        if not topic_data:
            raise AppException(
                "DATABASE_ERROR", "Falha ao criar o tópico, nenhum dado retornado."
            )

        if images and topic_data:
            images_to_insert = [
                {"url": url, "topic_id": topic_data["id"], "author_id": author_id}
                for url in images
            ]
            supabase.from_("imagens").insert(images_to_insert).execute()

        return topic_data
    except (APIError, IndexError) as e:
        raise AppException("DATABASE_ERROR", f"Erro ao criar tópico: {e.message}")


async def update_topic(topic_id: int, user_id: str, updates: dict):
    try:
        response = (
            supabase.from_("topicos")
            .update({**updates, "updated_in": datetime.now(timezone.utc).isoformat()})
            .match({"id": topic_id, "author_id": user_id})
            .execute()
        )

        if not response.data:
            raise AppException(
                "UPDATE_ERROR",
                "Não foi possível atualizar o tópico. Verifique se você é o autor ou se o tópico existe.",
            )

        return response.data[0]

    except APIError as e:
        raise AppException(
            "UPDATE_ERROR", f"Não foi possível atualizar o tópico: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao atualizar o tópico: {str(e)}",
        )


async def delete_topic(topic_id: int, user_id: str):
    try:
        images_res = (
            supabase.from_("imagens").select("url").eq("topic_id", topic_id).execute()
        )
        if images_res.data:
            for image in images_res.data:
                await delete_file(image["url"])

        supabase.from_("topicos").delete().match(
            {"id": topic_id, "author_id": user_id}
        ).execute()
    except APIError as e:
        raise AppException(
            "DATABASE_ERROR", f"Ocorreu um erro ao deletar o tópico: {e.message}"
        )


async def create_comment(
    content: str, author_id: str, topic_id: int, images: List[str] = None
):
    try:
        rpc_res = supabase.rpc(
            "can_create_comment", {"p_user_id": author_id, "p_topic_id": topic_id}
        ).execute()
        if not rpc_res.data:
            raise AppException(
                "FORBIDDEN_ERROR", "Você не tem permissão para comentar neste tópico."
            )

        comment_res = (
            supabase.from_("comentarios")
            .insert({"content": content, "author_id": author_id, "topic_id": topic_id})
            .execute()
        )

        comment_data = comment_res.data[0] if comment_res.data else None

        if images and comment_data:
            images_to_insert = [
                {"url": url, "comment_id": comment_data["id"], "author_id": author_id}
                for url in images
            ]
            supabase.from_("imagens").insert(images_to_insert).execute()

        full_comment_res = (
            supabase.from_("comentarios")
            .select("*, profiles(username, avatar_url, role), imagens(id, url)")
            .eq("id", comment_data["id"])
            .single()
            .execute()
        )

        return full_comment_res.data
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao criar comentário: {e.message}")


async def update_comment(comment_id: int, user_id: str, content: str):
    try:
        update_response = (
            supabase.from_("comentarios")
            .update(
                {
                    "content": content,
                    "updated_in": datetime.now(timezone.utc).isoformat(),
                }
            )
            .match({"id": comment_id, "author_id": user_id})
            .execute()
        )

        if not update_response.data:
            raise AppException(
                "UPDATE_ERROR",
                "Não foi possível atualizar o comentário. Verifique se você é o autor ou se o comentário existe.",
            )
        response = (
            supabase.from_("comentarios")
            .select("*, profiles(username, avatar_url, role), imagens(id, url)")
            .eq("id", comment_id)
            .single()
            .execute()
        )

        return response.data

    except APIError as e:
        raise AppException(
            "UPDATE_ERROR", f"Não foi possível atualizar o comentário: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao atualizar o comentário: {str(e)}",
        )


async def delete_comment(comment_id: int, user_id: str):
    try:
        images_res = (
            supabase.from_("imagens")
            .select("url")
            .eq("comment_id", comment_id)
            .execute()
        )
        if images_res.data:
            for image in images_res.data:
                await delete_file(image["url"])

        supabase.from_("comentarios").delete().match(
            {"id": comment_id, "author_id": user_id}
        ).execute()
    except APIError as e:
        raise AppException(
            "DATABASE_ERROR", f"Ocorreu um erro ao deletar o comentário: {e.message}"
        )

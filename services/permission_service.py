from config.supabase_client import supabase
from helpers.exceptions import AppException
from postgrest.exceptions import APIError


async def check_topic_creation_permission(author_id: str, category_slug: str) -> bool:
    try:
        response = supabase.rpc(
            "can_create_topic",
            params={"user_id": author_id, "category_slug": category_slug},
        ).execute()

        return response
    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível verificar a permissão de criação de tópico: {e.message}",
        )
    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message=f"Ocorreu um erro inesperado no servidor: {e.message}",
        )


async def check_comment_creation_permission(author_id: str, topic_id: int) -> bool:
    try:
        response = supabase.rpc(
            "can_create_comment",
            params={"user_id": author_id, "topic_id": topic_id},
        ).execute()

        return response
    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível verificar a permissão de criação de comentário: {e.message}",
        )
    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message=f"Ocorreu um erro inesperado no servidor: {e.message}",
        )

from config.supabase_client import supabase, supabase_admin
from helpers.exceptions import AppException
from postgrest.exceptions import APIError


async def get_forum_stats():
    try:
        members_res = (
            supabase.from_("profiles").select("*", count="exact", head=True).execute()
        )

        topics_res = (
            supabase.from_("topicos").select("*", count="exact", head=True).execute()
        )
        comments_res = (
            supabase.from_("comentarios")
            .select("*", count="exact", head=True)
            .execute()
        )
        newest_member_res = (
            supabase.from_("profiles")
            .select("username, role")
            .order("joined_at", desc=True)
            .limit(1)
            .single()
            .execute()
        )

        return {
            "activeMembers": members_res.count or 0,
            "totalTopics": topics_res.count or 0,
            "totalPosts": (topics_res.count or 0) + (comments_res.count or 0),
            "newestMember": newest_member_res.data,
        }
    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message="Não foi possível buscar as estatísticas do fórum.",
        )
    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message="Ocorreu um erro inesperado no servidor.",
        )


async def get_recent_posts(limit: int = 10):
    try:
        response = supabase_admin.rpc(
            "get_recent_posts", params={"post_limit": limit}
        ).execute()

        return response.data
    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message="Não foi possível buscar os posts.",
        )
    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message="Ocorreu um erro inesperado no servidor.",
        )

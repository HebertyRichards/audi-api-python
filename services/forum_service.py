import asyncio
from config.supabase_client import supabase, supabase_admin
from helpers.exceptions import AppException
from postgrest.exceptions import APIError
from datetime import datetime, timezone, timedelta


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


async def get_last_registration_user():
    try:
        response = (
            supabase.from_("profiles")
            .select("username, role, avatar_url, location, joined_at")
            .order("joined_at", desc=True)
            .limit(1)
            .execute()
        )
        if not response.data:
            raise AppException("NOT_FOUND", "Nenhum usuário encontrado.")
        return response.data[0]
    except APIError as e:
        raise AppException(
            "DATABASE_ERROR", f"Erro ao buscar o último usuário: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao buscar o último usuário: {str(e)}",
        )


async def get_online_users():
    try:
        time_threshold = datetime.now(timezone.utc) - timedelta(minutes=2)
        response = (
            supabase.from_("online_users")
            .select("last_seen_at, profiles(username, role, avatar_url)")
            .gt("last_seen_at", time_threshold.isoformat())
            .execute()
        )
        return response.data or []
    except APIError as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro ao buscar usuários online: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao buscar usuários online: {str(e)}",
        )


async def get_forum_data():
    try:
        results = await asyncio.gather(
            get_forum_stats(),
            get_recent_posts(),
            get_last_registration_user(),
            get_online_users(),
        )

        forum_stats_data = results[0]
        recent_posts_data = results[1]
        last_user_data = results[2]
        online_users_data = results[3]

        return {
            "stats": forum_stats_data,
            "recent_posts": recent_posts_data,
            "last_user": last_user_data,
            "online_users": online_users_data,
        }

    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message=f"Erro ao buscar os dados do painel: {str(e)}",
        )

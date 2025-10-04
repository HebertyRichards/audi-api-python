from datetime import datetime, timezone
from config.supabase_client import supabase
from helpers.exceptions import AppException
from postgrest.exceptions import APIError
from services.follow_service import get_user_id_by_username
from services.forum_service import get_forum_stats


async def get_user_stats(username):
    try:
        user_id = await get_user_id_by_username(username)

        profile_res = (
            supabase.from_("profiles")
            .select("joined_at, mensagens_count, followers_count, last_login")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if not profile_res.data:
            raise AppException("NOT_FOUND", "Perfil não encontrado.")
        profile = profile_res.data
        last_topic_res = (
            supabase.from_("topicos")
            .select("created_in")
            .eq("author_id", user_id)
            .order("created_in", desc=True)
            .limit(1)
            .execute()
        )
        last_comment_res = (
            supabase.from_("comentarios")
            .select("created_in")
            .eq("author_id", user_id)
            .order("created_in", desc=True)
            .limit(1)
            .execute()
        )
        count_res = (
            supabase.from_("topicos")
            .select("*", count="exact", head=True)
            .eq("author_id", user_id)
            .execute()
        )
        topics_count = count_res.count or 0

        forum_stats = await get_forum_stats()
        total_topics = forum_stats.get("totalTopics", 0)
        total_posts = forum_stats.get("totalPosts", 0)

        member_since = datetime.fromisoformat(profile["joined_at"])
        days_as_member = (datetime.now(timezone.utc) - member_since).days
        days_as_member = max(1, days_as_member)

        topics_per_day = round(topics_count / days_as_member, 2)
        topics_percentage = (
            round((topics_count / total_topics) * 100, 2) if total_topics > 0 else 0
        )

        messages_count = profile.get("mensagens_count", 0)
        messages_per_day = round(messages_count / days_as_member, 2)
        messages_percentage = (
            round((messages_count / total_posts) * 100, 2) if total_posts > 0 else 0
        )

        last_topic_date = (
            datetime.fromisoformat(last_topic_res.data[0]["created_in"])
            if last_topic_res.data
            else None
        )
        last_comment_date = (
            datetime.fromisoformat(last_comment_res.data[0]["created_in"])
            if last_comment_res.data
            else None
        )

        last_post_date = None
        if last_topic_date and last_comment_date:
            last_post_date = max(last_topic_date, last_comment_date)
        else:
            last_post_date = last_topic_date or last_comment_date

        return {
            "topicsCount": topics_count,
            "topicsPerDay": topics_per_day,
            "topicsPercentage": topics_percentage,
            "lastTopicDate": last_topic_date,
            "messagesCount": messages_count,
            "messagesPerDay": messages_per_day,
            "messagesPercentage": messages_percentage,
            "lastPostDate": last_post_date,
            "followersCount": profile.get("followers_count", 0),
            "memberSince": profile["joined_at"],
            "lastLogin": profile.get("last_login"),
        }
    except APIError as e:
        raise AppException(
            "DATABASE_ERROR", f"Erro ao buscar estatísticas do usuário: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao buscar estatísticas do usuário: {str(e)}",
        )


async def get_topics_by_author(username: str):
    try:
        author_id = await get_user_id_by_username(username)
        response = (
            supabase.from_("topicos")
            .select(
                "title, slug, category, created_in, profiles( username, role, avatar_url), comentarios ( count )"
            )
            .eq("author_id", author_id)
            .order("created_in", desc=True)
            .execute()
        )
        return response.data or []
    except APIError as e:
        raise AppException(
            "DATABASE_ERROR",
            f"Não foi possível buscar os tópicos do usuário: {e.message}",
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao buscar os tópicos do usuário: {str(e)}",
        )

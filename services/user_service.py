from config.supabase_client import supabase
from helpers.exceptions import AppException
from postgrest.exceptions import APIError
from datetime import datetime, timezone, timedelta


async def get_last_registration_user():
    try:
        response = (
            supabase.from_("profiles")
            .select("username, role")
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


async def upsert_online_user(user_id: str) -> None:
    try:
        payload = {
            "user_id": user_id,
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
        }
        supabase.from_("online_users").upsert(payload).execute()

        return

    except APIError as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Não foi possível atualizar o status online: {e.message}",
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao atualizar o status online: {str(e)}",
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


async def get_all_profiles(page: int, limit: int):
    try:
        from_range = (page - 1) * limit
        to_range = from_range + limit - 1

        count_response = (
            supabase.from_("profiles").select("*", count="exact", head=True).execute()
        )
        total_count = count_response.count or 0

        response = (
            supabase.from_("profiles")
            .select(
                "username, role, joined_at, last_login, avatar_url, mensagens_count"
            )
            .range(from_range, to_range)
            .execute()
        )
        data = response.data or []

        if not data and page > 1:
            raise AppException("NOT_FOUND", "Nenhum perfil encontrado nesta página.")

        return {"data": data, "total_count": total_count}

    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao buscar perfis: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao buscar perfis: {str(e)}"
        )

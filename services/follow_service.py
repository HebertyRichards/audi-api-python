from config.supabase_client import supabase
from helpers.exceptions import AppException
from postgrest.exceptions import APIError
from schemas.follow_schemas import FollowingStatsResponse


async def get_user_id_by_username(username: str):
    try:
        response = (
            supabase.from_("profiles")
            .select("id")
            .eq("username", username)
            .single()
            .execute()
        )
        if not response.data:
            raise AppException("NOT_FOUND", "Usuário não encontrado.")
        return response.data["id"]
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao buscar o usuário: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao buscar o usuário: {str(e)}"
        )


async def follow_user(follower_id: str, following_username: str):
    following_id = await get_user_id_by_username(following_username)
    if follower_id == following_id:
        raise AppException("BAD_REQUEST", "Você não pode seguir a si mesmo.")

    try:
        supabase.rpc(
            "handle_follow",
            {
                "follower_uuid": follower_id,
                "following_uuid": following_id,
            },
        ).execute()
        return {"message": "Usuário seguido com sucesso!"}
    except APIError as e:
        if e.code == "23505":
            raise AppException("CONFLICT", "Você já está seguindo este usuário.")
        raise AppException("DATABASE_ERROR", f"Erro ao seguir o usuário: {e.message}")


async def unfollow_user(follower_id: str, following_username: str):
    following_id = await get_user_id_by_username(following_username)
    if follower_id == following_id:
        raise AppException("BAD_REQUEST", "Você não pode deixar de seguir a si mesmo.")

    try:
        supabase.rpc(
            "handle_unfollow",
            {
                "follower_uuid": follower_id,
                "following_uuid": following_id,
            },
        ).execute()
        return {"message": "Você deixou de seguir o usuário."}
    except APIError as e:
        if e.code == "23505":
            raise AppException("CONFLICT", "Você já não está seguindo este usuário.")
        raise AppException(
            "DATABASE_ERROR", f"Não foi possível deixar de seguir: {e.message}"
        )


async def get_follow_stats(username: str):
    user_id = await get_user_id_by_username(username)
    try:
        response = (
            supabase.from_("profiles")
            .select("followers_count, following_count")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if not response.data:
            raise AppException("NOT_FOUND", "Usuário não encontrado.")
        return response.data
    except APIError as e:
        raise AppException(
            "DATABASE_ERROR", f"Erro ao buscar estatísticas: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao buscar estatísticas: {str(e)}"
        )


async def get_followers(username: str):
    user_id = await get_user_id_by_username(username)
    try:
        response = (
            supabase.from_("followers")
            .select(
                "follower:profiles!followers_follower_id_fkey(username, role, avatar_url)"
            )
            .eq("following_id", user_id)
            .execute()
        )
        return [item.get("follower") for item in response.data if item.get("follower")]
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao buscar seguidores: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao buscar seguidores: {str(e)}",
        )


async def get_following(username: str):
    user_id = await get_user_id_by_username(username)
    try:
        response = (
            supabase.from_("followers")
            .select(
                "following:profiles!followers_following_id_fkey(username, role, avatar_url)"
            )
            .eq("follower_id", user_id)
            .execute()
        )
        return [
            item.get("following") for item in response.data if item.get("following")
        ]
    except APIError as e:
        raise AppException(
            "DATABASE_ERROR", f"Erro ao buscar usuários que você segue: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao buscar usuários que você segue: {str(e)}",
        )


async def check_following_status(
    follower_id: str, following_username: str
) -> FollowingStatsResponse:
    following_id = await get_user_id_by_username(following_username)
    try:
        response = (
            supabase.from_("followers")
            .select("follower_id")
            .eq("follower_id", follower_id)
            .eq("following_id", following_id)
            .maybe_single()
            .execute()
        )

        is_user_following = bool(response and response.data)
        return FollowingStatsResponse(is_following=is_user_following)

    except APIError as e:
        raise AppException(
            "DATABASE_ERROR", f"Erro ao verificar status de seguimento: {e.message}"
        )
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao verificar status de seguimento: {str(e)}",
        )


async def remove_follower(remover_id: str, follower_username: str):
    follower_id = await get_user_id_by_username(follower_username)
    if remover_id == follower_id:
        raise AppException("BAD_REQUEST", "Ação inválida.")

    try:
        response = (
            supabase.from_("followers")
            .delete()
            .match(
                {
                    "follower_id": follower_id,
                    "following_id": remover_id,
                }
            )
            .execute()
        )

        if response.count == 0:
            raise AppException("NOT_FOUND", "Este usuário não é seu seguidor.")
        return {"message": "Seguidor removido com sucesso."}
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao remover seguidor: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR",
            f"Erro inesperado ao remover seguidor: {str(e)}",
        )

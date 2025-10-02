import time

from config.supabase_client import (
    create_authenticated_client,
    supabase,
    supabase_admin,
)
from fastapi import UploadFile
from helpers.exceptions import AppException
from postgrest.exceptions import APIError
from datetime import date


async def get_profile_by_id(id: str):
    try:
        response = (
            supabase.from_("profiles")
            .select(
                "username, avatar_url, role, joined_at, gender, birthdate, website, last_login, facebook, instagram, discord, steam, location, followers_count, following_count, mensagens_count"
            )
            .eq("id", id)
            .single()
            .execute()
        )
        if not response.data:
            raise AppException("NOT_FOUND", "Perfil não encontrado.")
        return response.data
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao buscar o perfil: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao buscar o perfil: {str(e)}"
        )


async def get_user_profile_by_username(username: str):
    try:
        response = (
            supabase.from_("profiles")
            .select(
                "username, gender, birthdate, location, website, joined_at, last_login, role, facebook, instagram, discord, steam, avatar_url, followers_count, following_count"
            )
            .eq("username", username)
            .single()
            .execute()
        )
        if not response.data:
            raise AppException("NOT_FOUND", "Perfil não encontrado.")
        return response.data
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao buscar o perfil: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao buscar o perfil: {str(e)}"
        )


async def update_profile(user_id: str, profile_data: dict):
    allowed_fields = [
        "website",
        "gender",
        "birthdate",
        "location",
        "facebook",
        "instagram",
        "discord",
        "steam",
    ]
    fields_to_update = {
        key: value for key, value in profile_data.items() if key in allowed_fields
    }

    if not fields_to_update:
        raise AppException(
            "BAD_REQUEST", "Nenhum campo válido para atualização foi fornecido."
        )

    if "birthdate" in fields_to_update and isinstance(
        fields_to_update["birthdate"], date
    ):
        fields_to_update["birthdate"] = fields_to_update["birthdate"].isoformat()

    if "birthdate" in fields_to_update and fields_to_update["birthdate"] == "":
        fields_to_update["birthdate"] = None
    try:
        response = (
            supabase.from_("profiles")
            .update(fields_to_update)
            .eq("id", user_id)
            .execute()
        )
        if not response.data:
            raise AppException(
                "NOT_FOUND",
                "O perfil que você tentou atualizar não foi encontrado ou você не tem permissão.",
            )
        return {"message": "Perfil atualizado com sucesso!"}
    except APIError as e:
        raise AppException("DATABASE_ERROR", f"Erro ao atualizar perfil: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao atualizar perfil: {str(e)}"
        )


async def update_user_profile_and_auth(
    access_token: str, new_username: str, new_email: str
):
    try:
        user_response = supabase.auth.get_user(access_token)
        user = user_response.user
        if not user:
            raise AppException("UNAUTHORIZED", "Token inválido ou expirado.")

        profile_res = (
            supabase.from_("profiles")
            .update({"username": new_username})
            .eq("id", user.id)
            .execute()
        )

        if new_email and new_email.lower() != user.email.lower():
            supabase_admin.auth.admin.update_user_by_id(user.id, {"email": new_email})
            return {
                "message": "Perfil atualizado! Um e-mail de confirmação foi enviado para o novo endereço."
            }

        return {"message": "Perfil atualizado com sucesso!"}
    except APIError as e:
        if e.code == "23505":
            raise AppException("CONFLICT", "Nome de usuário ou e-mail já está em uso.")
        raise AppException("DATABASE_ERROR", f"Erro ao atualizar perfil: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao atualizar perfil: {str(e)}"
        )


async def update_avatar(user_id: str, token: str, avatar_file: UploadFile):
    try:
        profile_res = (
            supabase.from_("profiles")
            .select("avatar_url")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if profile_res.data and profile_res.data.get("avatar_url"):
            old_url = profile_res.data["avatar_url"]
            search_string = "/avatars/"
            start_index = old_url.find(search_string)
            if start_index != -1:
                old_file_path = old_url[start_index + 1 :].split("?")[0]
                supabase_admin.storage.from_("avatars").remove([old_file_path])

        file_content = await avatar_file.read()
        file_path = f"avatars/{user_id}-{int(time.time())}"

        supabase_autenticado = create_authenticated_client(token)
        supabase_autenticado.storage.from_("avatars").upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": avatar_file.content_type, "upsert": "true"},
        )

        public_url = supabase.storage.from_("avatars").get_public_url(file_path)
        final_url = f"{public_url}?t={int(time.time())}"

        update_res = (
            supabase.from_("profiles")
            .update({"avatar_url": final_url})
            .eq("id", user_id)
            .select("avatar_url")
            .single()
            .execute()
        )

        return {
            "message": "Avatar atualizado com sucesso!",
            "avatar_url": update_res.data.get("avatar_url"),
        }
    except APIError as e:
        raise AppException("STORAGE_ERROR", f"Falha ao atualizar o avatar: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao atualizar avatar: {str(e)}"
        )


async def delete_avatar(user_id: str):
    try:
        profile_res = (
            supabase.from_("profiles")
            .select("avatar_url")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if profile_res.data and profile_res.data.get("avatar_url"):
            old_url = profile_res.data["avatar_url"]
            search_string = "/avatars/"
            start_index = old_url.find(search_string)
            if start_index != -1:
                old_file_path = old_url[start_index + 1 :].split("?")[0]
                supabase_admin.storage.from_("avatars").remove([old_file_path])

        update_res = (
            supabase.from_("profiles")
            .update({"avatar_url": None})
            .eq("id", user_id)
            .select("avatar_url")
            .single()
            .execute()
        )

        return {"message": "Avatar removido com sucesso!", "avatar_url": None}
    except APIError as e:
        raise AppException("STORAGE_ERROR", f"Falha ao remover o avatar: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao remover avatar: {str(e)}"
        )

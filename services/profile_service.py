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


async def get_user_profile_by_username(username: str):
    try:
        response = (
            supabase.from_("profiles")
            .select(
                "username, gender, birthdate, location, website, joined_at, last_login, role, facebook, instagram, discord, steam, avatar_url, followers_count, following_count, mensagens_count"
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
            try:
                supabase_admin.auth.admin.update_user_by_id(
                    user.id, {"email": new_email}
                )
                return {
                    "message": "Perfil atualizado! Um e-mail de confirmação foi enviado para o novo endereço."
                }
            except Exception as auth_error:
                if "already been registered" in str(auth_error).lower():
                    raise AppException(
                        "CONFLICT", "Este novo e-mail já está em uso por outra conta."
                    )
                raise AppException(
                    "INTERNAL_SERVER_ERROR",
                    "Ocorreu uma falha ao tentar atualizar o e-mail.",
                )

        return {"message": "Perfil atualizado com sucesso!"}
    except APIError as e:
        if e.code == "23505":
            raise AppException("CONFLICT", "Nome de usuário ou e-mail já está em uso.")
        raise AppException("DATABASE_ERROR", f"Erro ao atualizar perfil: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao atualizar perfil: {str(e)}"
        )


async def update_avatar(user_id: str, avatar_file: UploadFile, token: str):
    try:
        if not avatar_file:
            raise AppException("BAD_REQUEST", "Nenhum arquivo de avatar foi enviado.")

        supabase_autenticated = await create_authenticated_client(token)

        profile_res = (
            supabase_admin.from_("profiles")
            .select("avatar_url")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if profile_res.data and profile_res.data.get("avatar_url"):
            old_url = profile_res.data["avatar_url"]
            old_file_name = old_url.split("/")[-1].split("?")[0]
            if old_file_name:
                supabase_autenticated.storage.from_("avatars").remove(
                    [f"avatars/{old_file_name}"]
                )

        MIME_TYPE_MAP = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
        content_type = avatar_file.content_type
        file_extension = MIME_TYPE_MAP.get(content_type, "jpg")

        file_name = f"{user_id}.{file_extension}"
        file_path = f"avatars/{file_name}"

        file_content = await avatar_file.read()

        supabase_autenticated.storage.from_("avatars").upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": avatar_file.content_type, "upsert": "true"},
        )

        url_data = supabase_autenticated.storage.from_("avatars").get_public_url(
            file_path
        )
        public_url = url_data
        timestamp = int(time.time())
        if "?" in public_url:
            avatar_url = f"{public_url}&t={timestamp}"
        else:
            avatar_url = f"{public_url}?t={timestamp}"

        update_response = (
            supabase_autenticated.from_("profiles")
            .update({"avatar_url": avatar_url})
            .eq("id", user_id)
            .execute()
        )

        if not update_response.data:
            raise AppException(
                "INTERNAL_SERVER_ERROR",
                "Falha ao salvar a URL do avatar no perfil (nenhum registro atualizado).",
            )

        return {
            "message": "Avatar atualizado com sucesso!",
            "avatar_url": avatar_url,
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
            supabase_admin.from_("profiles")
            .select("avatar_url")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if not (profile_res.data and profile_res.data.get("avatar_url")):
            return {"message": "Nenhum avatar para remover."}

        old_url = profile_res.data["avatar_url"]
        old_file_name = old_url.split("/")[-1].split("?")[0]

        if old_file_name:
            supabase_admin.storage.from_("avatars").remove([old_file_name])

        update_res = (
            supabase_admin.from_("profiles")
            .update({"avatar_url": None})
            .eq("id", user_id)
            .execute()
        )

        if not update_res.data:
            raise AppException(
                "INTERNAL_SERVER_ERROR", "Falha ao remover a URL do avatar do perfil."
            )

        return {"message": "Avatar removido com sucesso!"}

    except APIError as e:
        raise AppException("STORAGE_ERROR", f"Falha ao remover o avatar: {e.message}")
    except Exception as e:
        raise AppException(
            "INTERNAL_SERVER_ERROR", f"Erro inesperado ao remover avatar: {str(e)}"
        )

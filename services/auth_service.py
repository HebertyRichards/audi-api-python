import os
from datetime import datetime, timezone
from config.supabase_client import supabase, supabase_admin, create_authenticated_client
from helpers.exceptions import AppException
from schemas.auth_schemas import UserCreate

ONE_HOUR = 60 * 60
THIRTY_DAYS = 60 * 60 * 24 * 30


async def register_user(user_data: UserCreate):
    existing_user_req = (
        supabase.from_("profiles")
        .select("id")
        .eq("username", user_data.username)
        .execute()
    )

    if existing_user_req.data:
        raise AppException(
            type="CONFLICT", message="Este nome de usuário já está em uso."
        )

    user_id = None
    try:
        session = supabase.auth.sign_up(
            {
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "email_redirect_to": user_data.email_redirect_to
                    or f"{os.environ.get('FRONTEND_URL')}/confirmation"
                },
            }
        )

        if not session.user:
            raise AppException(
                type="INTERNAL_SERVER_ERROR",
                message="O registro falhou ao tentar criar o usuário.",
            )
        user_id = session.user.id
    except Exception as e:
        error_message = str(e).lower()
        if "user already registered" in error_message:
            raise AppException(type="CONFLICT", message="Este e-mail já está em uso.")
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message="Não foi possível registrar o usuário.",
        )

    try:
        profile_data = {"id": user_id, "username": user_data.username}
        supabase.from_("profiles").insert(profile_data).execute()
    except Exception:
        if user_id:
            supabase_admin.auth.admin.delete_user(user_id)
        raise AppException(
            type="INTERNAL_SERVER_ERROR", message="Falha ao criar o perfil do usuário."
        )

    return {"message": "Usuário registrado com sucesso!"}


async def login_user(email: str, password: str, keep_logged: bool):
    try:
        session = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if not session.session:
            raise AppException(
                type="INTERNAL_SERVER_ERROR",
                message="Não foi possível criar uma sessão.",
            )

        supabase.from_("profiles").update(
            {"last_login": datetime.now(timezone.utc).isoformat()}
        ).eq("id", session.user.id).execute()

        return {
            "access_token": session.session.access_token,
            "refresh_token": session.session.refresh_token if keep_logged else None,
            "access_token_expiry": ONE_HOUR,
            "refresh_token_expiry": THIRTY_DAYS if keep_logged else ONE_HOUR,
        }
    except Exception as e:
        error_message = str(e).lower()
        if "invalid login credentials" in error_message:
            raise AppException(type="UNAUTHORIZED", message="Email ou senha inválidos.")
        raise AppException(
            type="INTERNAL_SERVER_ERROR", message="Ocorreu um erro durante o login."
        )


async def get_user_by_token(token: str):
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise Exception("Usuário não encontrado")
        profile_response = (
            supabase.from_("profiles")
            .select("username")
            .eq("id", user.id)
            .single()
            .execute()
        )
        if not profile_response.data:
            raise AppException(
                type="NOT_FOUND",
                message="Não foi possível carregar os dados do perfil associado.",
            )

        return {**user.dict(), "username": profile_response.data["username"]}
    except Exception:
        raise AppException(
            type="UNAUTHORIZED", message="Token de acesso inválido ou expirado."
        )


async def refresh_user_token(refresh_token: str):
    try:
        session = supabase.auth.refresh_session(refresh_token)
        if not session.session:
            raise Exception("Sessão inválida")

        return {
            "new_access_token": session.session.access_token,
            "access_token_expiry": ONE_HOUR,
        }
    except Exception:
        raise AppException(
            type="UNAUTHORIZED",
            message="Sua sessão expirou. Por favor, faça o login novamente.",
        )


async def send_recovery_email(email: str):
    try:
        redirect_url = f"{os.environ.get('FRONTEND_URL')}/reset-password"
        supabase.auth.reset_password_email(email, redirect_to=redirect_url)
    except Exception as e:
        error_message = str(e)
        if "429" in error_message:
            raise AppException(
                type="TOO_MANY_REQUESTS",
                message="Você realizou muitas tentativas. Por favor, aguarde antes de tentar novamente.",
            )
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message="Não foi possível processar sua solicitação.",
        )

    return {
        "message": "Se uma conta com este e-mail existir, um link para redefinição de senha foi enviado."
    }


async def update_password_with_token(access_token: str, new_password: str):
    try:
        user_response = supabase.auth.get_user(access_token)
        if not user_response.user:
            raise Exception("Token inválido")
        user_id = user_response.user.id

        supabase_admin.auth.admin.update_user_by_id(user_id, {"password": new_password})

        return {"message": "Senha atualizada com sucesso!"}
    except Exception as e:
        error_message = str(e).lower()
        if "password should be at least 6 characters" in error_message:
            raise AppException(
                type="BAD_REQUEST", message="A senha deve ter no mínimo 6 caracteres."
            )
        raise AppException(
            type="INTERNAL_SERVER_ERROR", message="Não foi possível atualizar a senha."
        )


async def update_authenticated_user_password(access_token: str, new_password: str):
    try:
        supabase_auth_client = create_authenticated_client(access_token)
        await supabase_auth_client.auth.update_user({"password": new_password})
        return {"message": "Senha atualizada com sucesso!"}
    except Exception as e:
        error_message = str(e).lower()
        if "password should be at least 6 characters" in error_message:
            raise AppException(
                type="BAD_REQUEST",
                message="A nova senha deve ter no mínimo 6 caracteres.",
            )
        raise AppException(
            type="INTERNAL_SERVER_ERROR", message="Não foi possível atualizar a senha."
        )


async def delete_user_account(user_id: str, email: str, password: str):
    try:
        supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
        raise AppException(
            type="UNAUTHORIZED",
            message="Senha incorreta. A exclusão da conta foi cancelada.",
        )

    try:
        supabase_admin.auth.admin.delete_user(user_id)
    except Exception:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message="Não foi possível deletar a conta do usuário.",
        )

    return {"message": "Conta de usuário deletada com sucesso."}

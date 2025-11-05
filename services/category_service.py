from config.supabase_client import supabase
from helpers.exceptions import AppException
from postgrest.exceptions import APIError


async def category_exists(slug: str) -> bool:
    try:
        response = (
            supabase.from_("categorias")
            .select("slug")
            .eq("slug", slug)
            .single()
            .execute()
        )
        return response.data is not None
    except APIError as e:
        return False
    except Exception as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível verificar a existência da categoria. {e.message}",
        )


async def get_all_categories():
    try:
        response = (
            supabase.from_("categorias")
            .select("slug, name, description")
            .order("name", desc=False)
            .execute()
        )
        return response.data or []
    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível buscar as categorias: {e.message}",
        )
    except Exception as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Erro inesperado ao buscar categorias. {e.message}",
        )


async def get_topics_by_category(category_slug: str, page: int, limit: int = 10):
    try:
        from_range = (page - 1) * limit
        to_range = from_range + limit - 1

        count_response = (
            supabase.from_("topicos")
            .select("*", count="exact", head=True)
            .eq("category", category_slug)
            .execute()
        )
        total_count = count_response.count or 0

        response = (
            supabase.from_("topicos")
            .select(
                """
                title, 
                slug, 
                created_in,
                profiles ( username, avatar_url, role ),
                comentarios ( count )
            """
            )
            .eq("category", category_slug)
            .order("created_in", desc=True)
            .range(from_range, to_range)
            .execute()
        )
        data = response.data or []

        if not data and page > 1:
            raise AppException("NOT_FOUND", "Não há mais tópicos para mostrar.")

        return {"data": data, "totalCount": total_count}

    except APIError as e:
        raise AppException(
            "DATABASE_ERROR",
            f"Não foi possível buscar os tópicos da categoria: {e.message}",
        )
    except Exception as e:
        raise AppException(
            "DATABASE_ERROR",
            f"Erro inesperado ao buscar tópicos da categoria. {e.message}",
        )


async def create_category(slug: str, name: str, role: str, description: str) -> dict:
    try:
        payload = {
            "p_slug": slug,
            "p_name": name,
            "p_role": role,
            "p_description": description,
        }
        response = supabase.rpc("create_full_category", payload).execute()

        if not response.data:
            raise AppException(
                type="DATABASE_ERROR",
                message="Falha ao criar a categoria, a operação não retornou dados.",
            )

        return response.data[0]

    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível criar a categoria: {e.message}",
        ) from e
    except Exception as e:
        if isinstance(e, AppException):
            raise
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message=f"Erro inesperado ao criar categoria: {str(e)}",
        )


async def get_category_permission(category_slug: str):
    try:
        response = (
            supabase.from_("categorias")
            .select(
                "slug, role, category_topic_permissions(user_role), category_comment_permissions(user_role)"
            )
            .eq("slug", category_slug)
            .single()
            .execute()
        )
        if not response.data:
            raise AppException(
                type="NOT_FOUND",
                message="Categoria não encontrada ao buscar permissões.",
            )

        return response.data

    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível buscar a categoria: {e.message}",
        )
    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message=f"Erro inesperado ao buscar categoria: {str(e)}",
        )


async def delete_category(slug: str):
    try:
        response = supabase.from_("categorias").delete().eq("slug", slug).execute()

        if not response.data:
            raise AppException(
                type="NOT_FOUND", message="Categoria não encontrada ou já deletada."
            )

        return {"message": f"Categoria '{slug}' e todo o seu conteúdo foram deletados."}

    except APIError as e:
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível deletar a categoria: {e.message}",
        )
    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message=f"Erro inesperado: {str(e)}",
        )

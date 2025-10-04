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
            .select("slug, name")
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

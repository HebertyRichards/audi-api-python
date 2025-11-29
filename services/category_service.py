from config.supabase_client import supabase
from helpers.exceptions import AppException
from postgrest.exceptions import APIError
from typing import List


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


async def create_category(
    slug: str,
    name: str,
    topicroles: List[str],
    commentroles: List[str],
    description: str,
) -> dict:
    try:
        payload = {
            "p_slug": slug,
            "p_name": name,
            "p_topicroles": topicroles,
            "p_commentroles": commentroles,
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


async def update_category(
    old_slug: str,
    new_slug: str,
    name: str,
    topicroles: List[str],
    commentroles: List[str],
    description: str,
) -> dict:
    print(f"update_category called with:")
    print(f"  old_slug: {old_slug}")
    print(f"  new_slug: {new_slug}")
    print(f"  name: {name}")
    print(f"  topicroles: {topicroles}")
    print(f"  commentroles: {commentroles}")
    print(f"  description: {description}")
    try:
        payload = {
            "p_old_slug": old_slug,
            "p_new_slug": new_slug,
            "p_name": name,
            "p_topicroles": topicroles,
            "p_commentroles": commentroles,
            "p_description": description,
        }
        print(f"Payload for RPC 'update_full_category': {payload}")
        response = supabase.rpc("update_full_category", payload).execute()
        print(f"Response from RPC: {response}")

        if not response.data:
            print("Update failed, no data returned.")
            raise AppException(
                type="DATABASE_ERROR",
                message="Falha ao atualizar a categoria, a operação não retornou dados.",
            )

        result = response.data[0]
        print(f"Result from update: {result}")
        return result

    except APIError as e:
        print(f"APIError during category update: {e}")
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível atualizar a categoria: {e.message}",
        ) from e
    except Exception as e:
        print(f"Unexpected exception during category update: {e}")
        if isinstance(e, AppException):
            raise
        raise AppException(
            type="INTERNAL_SERVER_ERROR",
            message=f"Erro inesperado ao atualizar categoria: {str(e)}",
        )


async def get_category_details(slug: str) -> dict:
    print(f"get_category_details called with slug: {slug}")
    try:
        response = (
            supabase.table("categorias")
            .select(
                "slug, name, description, category_topic_permissions(user_role), category_comment_permissions(user_role)"
            )
            .eq("slug", slug)
            .single()
            .execute()
        )
        print(f"Response from Supabase: {response}")
        data = response.data
        print(f"Data from response: {data}")

        if not data:
            print(f"Category with slug '{slug}' not found.")
            raise AppException(type="NOT_FOUND", message="Categoria não encontrada.")

        topic_roles = [
            p["user_role"] for p in data.get("category_topic_permissions", [])
        ]
        comment_roles = [
            p["user_role"] for p in data.get("category_comment_permissions", [])
        ]
        print(f"Extracted topic_roles: {topic_roles}")
        print(f"Extracted comment_roles: {comment_roles}")

        result = {
            "slug": data["slug"],
            "name": data["name"],
            "description": data["description"],
            "topicRoles": topic_roles,
            "commentRoles": comment_roles,
        }
        print(f"Returning result: {result}")
        return result

    except APIError as e:
        print(f"APIError in get_category_details: {e}")
        raise AppException(
            type="DATABASE_ERROR",
            message=f"Não foi possível buscar a categoria: {e.message}",
        )
    except Exception as e:
        print(f"Unexpected exception in get_category_details: {e}")
        if isinstance(e, AppException):
            raise
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

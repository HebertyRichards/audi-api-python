import time
from fastapi import UploadFile
from config.supabase_client import supabase_admin
from helpers.exceptions import AppException
from postgrest.exceptions import APIError


async def upload_file(file: UploadFile) -> str:
    if not file or not file.filename:
        raise AppException(
            type="VALIDATION_ERROR", message="Nenhum arquivo fornecido para upload."
        )

    try:
        file_content = await file.read()

        file_path = (
            f"public/{int(time.time() * 1000)}-{file.filename.replace(' ', '_')}"
        )

        supabase_admin.storage.from_("images").upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type or "application/octet-stream",
                "upsert": "false",
            },
        )

        public_url = supabase_admin.storage.from_("images").get_public_url(file_path)

        if not public_url:
            raise AppException(
                "STORAGE_ERROR", "Não foi possível obter a URL pública do arquivo."
            )

        return public_url

    except APIError as e:
        raise AppException(
            type="STORAGE_ERROR", message="Falha ao fazer upload do arquivo."
        )
    except Exception as e:
        raise AppException(
            type="INTERNAL_SERVER_ERROR", message="Ocorreu um erro interno no servidor."
        )


async def delete_file(public_url: str) -> None:
    try:
        bucket_name = "images"
        search_string = f"/{bucket_name}/"

        start_index = public_url.find(search_string)
        if start_index == -1:

            return

        file_path = public_url[start_index + len(search_string) :]

        supabase_admin.storage.from_(bucket_name).remove([file_path])

    except Exception as e:
        return

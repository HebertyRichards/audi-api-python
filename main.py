from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import auth_routes, auth_tag_metadata
from routes.forum_routes import forum_routes, forum_tag_metadata
from helpers.exceptions import AppException, app_exception_handler
import os
from dotenv import load_dotenv

load_dotenv()

cliente_app = os.getenv("FRONTEND_URL", "").split(",")

app = FastAPI(
    title="Auditore Fórum API",
    description="Documentação da API para o projeto de fórum.",
    version="1.0.0",
    openapi_tags=[auth_tag_metadata, forum_tag_metadata],
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(auth_routes)
app.include_router(forum_routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cliente_app,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import auth_routes, auth_tag_metadata
from routes.forum_routes import forum_routes, forum_tag_metadata
from routes.category_routes import category_routes, category_tag_metadata
from routes.permission_routes import permission_routes, permission_tag_metadata
from routes.topic_routes import topic_routes, topic_tag_metadata
from routes.profile_routes import profile_routes, profile_tag_metadata
from routes.user_routes import user_routes, user_tag_metadata
from routes.follow_routes import follow_routes, follow_tag_metadata
from routes.statistic_routes import statistic_router, statistic_tag_metadata
from routes.admin_routes import admin_routes, admin_tag_metadata
from helpers.exceptions import AppException, app_exception_handler
import os
from dotenv import load_dotenv

load_dotenv()

cliente_app = os.getenv("FRONTEND_URL", "").split(",")

app = FastAPI(
    title="Auditore Fórum API",
    description="Documentação da API para o projeto de fórum.",
    version="1.0.0",
    openapi_tags=[
        auth_tag_metadata,
        user_tag_metadata,
        profile_tag_metadata,
        follow_tag_metadata,
        statistic_tag_metadata,
        category_tag_metadata,
        topic_tag_metadata,
        permission_tag_metadata,
        forum_tag_metadata,
        admin_tag_metadata,
    ],
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(auth_routes)
app.include_router(forum_routes)
app.include_router(category_routes)
app.include_router(permission_routes)
app.include_router(topic_routes)
app.include_router(profile_routes)
app.include_router(user_routes)
app.include_router(follow_routes)
app.include_router(statistic_router)
app.include_router(admin_routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cliente_app,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

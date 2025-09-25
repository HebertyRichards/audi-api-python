from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import auth_routes
from helpers.exceptions import AppException, app_exception_handler
import os
from dotenv import load_dotenv

load_dotenv()

cliente_app = os.getenv("FRONTEND_URL", "").split(",")

app = FastAPI(
    title="Minha API de Autenticação",
    description="Uma API para gerenciar usuários com FastAPI e Supabase.",
    version="1.0.0"
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(auth_routes)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=cliente_app,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
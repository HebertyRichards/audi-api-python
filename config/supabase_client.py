import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
supabase_service_key = os.environ.get("SUPABASE_SERVICE_KEY")


supabase: Client = create_client(supabase_url, supabase_anon_key)
supabase_admin: Client = create_client(supabase_url, supabase_service_key)


async def create_authenticated_client(token: str) -> Client:
    return create_client(
        supabase_url,
        supabase_anon_key,
        options={"global": {"headers": {"Authorization": f"Bearer {token}"}}},
    )

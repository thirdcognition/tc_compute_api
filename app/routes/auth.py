from fastapi import APIRouter, HTTPException
from supabase.client import AsyncClient
from supabase_auth.types import Session
from app.core.session_storage import get_storage, get_supabase_client
from pydantic import BaseModel

router = APIRouter()


class LoginRequestData(BaseModel):
    email: str
    password: str


@router.get("/auth/callback")
async def api_authenticate_supabase():
    return {"message": "ok"}


@router.post("/auth/login")
async def api_login(login_request: LoginRequestData) -> Session:
    print(f"login: {login_request.email=}, {login_request.password=}")
    if login_request.email is None or login_request.password is None:
        raise HTTPException(401, "Email and Password are required for authentication")

    supabase: AsyncClient = await get_supabase_client()
    await supabase.auth.sign_in_with_password(
        {"email": login_request.email, "password": login_request.password}
    )
    session: Session = await supabase.auth.get_session()
    get_storage(access_token=session.access_token, supabase_client=supabase)
    print(f"session: {session=}")
    return session

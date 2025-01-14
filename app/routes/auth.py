from fastapi import APIRouter, HTTPException
from supabase import AuthApiError
from supabase.client import AsyncClient
from supabase_auth.types import Session
from app.core.session_storage import get_storage, get_supabase_client
from pydantic import BaseModel, EmailStr, ValidationError

from app.core.supabase import excempt_from_auth_check
from source.models.config.logging import logger
from source.helpers.routes import handle_exception

router = APIRouter()


class LoginRequestData(BaseModel):
    email: EmailStr
    password: str


@router.get("/auth/callback")
async def api_authenticate_supabase():
    return {"message": "ok"}


excempt_from_auth_check("/auth/login", ["POST"])


@router.post("/auth/login")
async def api_login(login_request: LoginRequestData) -> Session:
    try:
        logger.debug(f"login: {login_request.email=}, {login_request.password=}")

        # Validate input
        if not login_request.email or not login_request.password:
            raise HTTPException(
                status_code=400,
                detail="Email and Password are required for authentication",
            )

        supabase: AsyncClient = await get_supabase_client()

        # Use parameterized methods to prevent SQL injection
        await supabase.auth.sign_in_with_password(
            {"email": login_request.email, "password": login_request.password}
        )

        session: Session = await supabase.auth.get_session()
        get_storage(access_token=session.access_token, supabase_client=supabase)
        logger.debug(f"session: {session=}")
        return session
    except AuthApiError as ae:
        raise handle_exception(ae, "Invalid login", 401)
    except ValidationError as ve:
        raise handle_exception(ve, "Organization not found", 422)
    except Exception as e:
        raise handle_exception(e, "Error", 500)

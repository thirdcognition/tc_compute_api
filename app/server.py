from typing import Annotated
from app.core.session_storage import SessionStorage, get_storage, get_supabase_client
from app.core.supabase import SupaClientDep, get_supabase_client_by_request
from app.models.organization import AddOrganizationUserRequestData, Organization, OrganizationRequestData, add_organization_user, create_organization
from app.models.supabase.organization import OrganizationsModel, OrganizationUsersModel
from fastapi import Depends, FastAPI, HTTPException, Header, Request
from fastapi.responses import RedirectResponse
from langserve import add_routes
from supabase.client import AsyncClient
from gotrue.types import Session, UserResponse
from app.core.init_app import init_app
from app.core.config import settings
from app.chains.virtualbuddy_base import chain as virtual_buddy_chain
from pydantic import UUID4, BaseModel

app = init_app()

from langchain.globals import set_debug

set_debug(True)

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/auth/callback")
async def api_authenticate_supabase():
    return {"message": "ok"}

class LoginRequestData(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
async def api_login(login_request: LoginRequestData) -> Session:
    print(f"login: {login_request.email =}, {login_request.password =}")
    if login_request.email is None or login_request.password is None:
        raise HTTPException(401, "Email and Password are required for authentication")

    supabase:AsyncClient = await get_supabase_client()
    await supabase.auth.sign_in_with_password({"email": login_request.email, "password": login_request.password})
    session:Session = await supabase.auth.get_session()
    store:SessionStorage = get_storage(access_token = session.access_token, supabase_client = supabase)
    print(f"session: {session =}")
    return session


@app.post("/organization/create")
async def api_create_organization(organization: OrganizationRequestData, supabase: SupaClientDep) -> OrganizationsModel:
    org:Organization = await create_organization(supabase, organization)
    return org.model

@app.post("/organization/{organization_id}/add_user")
async def api_add_organization_user(organization_id: UUID4, user_data: AddOrganizationUserRequestData, supabase: SupaClientDep) -> OrganizationUsersModel:
    try:
        return await add_organization_user(supabase, organization_id, user_data)
    except Exception as e:
        raise HTTPException(500, str(e))

add_routes(
    app,
    virtual_buddy_chain(),
    path="/chat",
    # enable_feedback_endpoint=True,
    # enable_public_trace_link_endpoint=True,
    # playground_type="chat",
)

# Edit this to add the chain you want to add
# add_routes(app, NotImplemented)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)

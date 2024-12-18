from langchain.globals import set_debug
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes.auth import router as auth_router
from app.routes.organization import router as organization_router
from app.routes.organization_user import router as organization_user_router
from app.routes.journey import router as journey_router
from app.routes.profile import router as profile_router
from app.routes.system import router as system_router
from app.routes.public_panel import router as public_panel_router
from app.routes.panel import router as panel_router
from app.core.init_app import init_app
from lib.load_env import SETTINGS

app = init_app()

set_debug(True)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/morning_show/{path_name:path}")
async def serve_morning_show(path_name: str):
    return FileResponse("static/morning_show/index.html")


# Include routers
app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(organization_user_router)
app.include_router(journey_router)
app.include_router(profile_router)
app.include_router(system_router)
app.include_router(public_panel_router)
app.include_router(panel_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=SETTINGS.server_host, port=SETTINGS.server_port)

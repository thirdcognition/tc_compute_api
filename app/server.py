import os
from langchain.globals import set_debug
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.supabase import (
    excempt_from_auth_check,
    excempt_from_auth_check_with_prefix,
)
from app.routes.auth import router as auth_router
from app.routes.organization import router as organization_router
from app.routes.organization_user import router as organization_user_router

# from app.routes.journey import router as journey_router
from app.routes.profile import router as profile_router
from app.routes.system import router as system_router
from app.routes.panel import router as panel_router
from app.core.init_app import init_app
from app.routes.communication import router as communication_router
from source.load_env import SETTINGS
from source.models.config.logging import logger

app = init_app()

set_debug(True)

excempt_from_auth_check_with_prefix("/static", ["GET"])
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
excempt_from_auth_check_with_prefix("/assets", ["GET"])
app.mount("/assets", StaticFiles(directory="assets", html=True), name="assets")

excempt_from_auth_check("/", ["GET"])


@app.get("/")
async def redirect_root_to_player():
    return RedirectResponse("/player")


excempt_from_auth_check("/health", ["GET"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


script_dir = os.path.dirname(os.path.abspath(__file__))


def serve_static_file(base_dir: str, path_name: str):
    path_parts = os.path.normpath(path_name).split(os.sep)

    if len(path_parts) >= 2:
        second_to_last_directory, last_directory = path_parts[-2], path_parts[-1]
    elif len(path_parts) == 1:
        second_to_last_directory, last_directory = "", path_parts[-1]
    else:
        second_to_last_directory, last_directory = "", ""

    file_path_with_dir = os.path.abspath(
        os.path.join(
            script_dir,
            base_dir,
            "static",
            second_to_last_directory,
            last_directory,
        )
    )
    file_path_wo_dir = os.path.abspath(
        os.path.join(script_dir, base_dir, last_directory)
    )

    if os.path.isfile(file_path_with_dir):
        return FileResponse(file_path_with_dir)
    elif os.path.isfile(file_path_wo_dir):
        return FileResponse(file_path_wo_dir)
    else:
        logger.info(f"File not found: {file_path_with_dir=}, {file_path_wo_dir=}")
        index_file_path = os.path.join(script_dir, base_dir, "index.html")
        return FileResponse(index_file_path)


excempt_from_auth_check_with_prefix("/admin", ["GET"])


@app.get("/admin/{path_name:path}")
async def serve_admin(path_name: str):
    return serve_static_file("../static/admin/build", path_name)


# @app.get("/player/{path_name:path}")
# async def serve_player(path_name: str):
#     return FileResponse("static/player/build/index.html")

# app.mount("/player/", StaticFiles(directory="static/player/build/", html=True), name="player")

excempt_from_auth_check_with_prefix("/player", ["GET"])


@app.get("/player/{path_name:path}")
async def serve_player_root(path_name: str):
    return serve_static_file("../static/player/build", path_name)


excempt_from_auth_check("/favicon.ico", ["GET"])


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(script_dir, "../assets", "favicon.ico"))


app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(organization_user_router)
# app.include_router(journey_router)
app.include_router(communication_router)
app.include_router(profile_router)
app.include_router(system_router)
app.include_router(panel_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=SETTINGS.server_host,
        port=SETTINGS.server_port,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "source.models.config.logging.ColoredFormatter",
                    "format": "%(processName)s - %(levelname)-8s: %(asctime)s| %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S.%f",
                },
            },
            "handlers": {
                "default": {
                    "level": SETTINGS.log_level,
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                },
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["default"],
                    "level": SETTINGS.log_level,
                },
            },
        },
    )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.supabase import supabase_middleware
from source.load_env import SETTINGS


def init_app() -> FastAPI:
    # init FastAPI with lifespan
    app = FastAPI(
        title=SETTINGS.project_name,
        # openapi_url=f"{settings.API_V1_STR}/openapi.json",
        # generate_unique_id_function=lambda router: f"{router.tags[0]}-{router.name}",
    )

    # set CORS
    # Set all CORS enabled origins
    # if settings.BACKEND_CORS_ORIGINS:
    #     app.add_middleware(
    #         CORSMiddleware,
    #         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    #         allow_credentials=True,
    #         allow_methods=["*"],
    #         allow_headers=["*"],
    #     )
    # else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Include the routers
    # app.include_router(api_router, prefix=settings.API_V1_STR)

    # app.middleware("http")(supabase_middleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=supabase_middleware)
    # app.add_middleware(supabase_middleware)

    return app

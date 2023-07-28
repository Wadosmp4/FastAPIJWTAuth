import logging

from logging.config import dictConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError

from app.config import config, LogConfig
from app.routers import user_router, auth_router, settings_router
from app.middlewares import LogRequestsMiddleware, RateLimitMiddleware, ExceptionHandlingMiddleware, RequestIDMiddleware
from app.exception_handlers import validation_exception_handler

dictConfig(LogConfig().dict())
logger = logging.getLogger("app")

middlewares = [
    (RequestIDMiddleware, {}),
    (RateLimitMiddleware, {"limit": config.RATE_LIMIT, "interval": config.RATE_LIMIT_INTERVAL}),
    (LogRequestsMiddleware, {}),
    (ExceptionHandlingMiddleware, {})
]

exception_handlers = {RequestValidationError: validation_exception_handler}

app = FastAPI(middleware=middlewares,
              exception_handlers=exception_handlers)

origins = [
    config.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")


@app.get('/healthchecker')
async def root():
    return {'message': 'Hello World'}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Documentation",
        version="1.0.0",
        description="Docs for Authentication App",
        routes=app.routes
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

import beetsplug.websearch.controller as ctrl

from typing import Any, Optional, Union
from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    ctrl.lib = app.state.lib
    yield


def create_app():
    app = FastAPI(
        title="Song search and playlist generator API",
        description="Song search and playlist generator API",
        version="1.0.0",
        lifespan=lifespan,
    )

    from beetsplug.websearch.gen.apis.websearch_api import router as WebsearchApiRouter

    app.include_router(WebsearchApiRouter)

    return app


def configure_app(app, lib):
    app.state.lib = lib

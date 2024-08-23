import os
import beetsplug.websearch.controller as ctrl

from beets import config
from typing import Any, Optional, Union
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi import FastAPI

from beetsplug.websearch.state.jsonfile import JSONFileRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    state_dir = config['websearch']['state_dir'].get()
    playlists_file = os.path.join(state_dir, "playlists.json")
    ctrl.lib = app.state.lib
    ctrl.playlists = JSONFileRepository(playlists_file)
    yield


def create_app():
    app = FastAPI(
        title="Song search and playlist management API",
        description="Song search and playlist management API",
        version="1.0.0",
        lifespan=lifespan,
    )

    from beetsplug.websearch.gen.apis.websearch_api import router as WebsearchApiRouter

    app.include_router(WebsearchApiRouter)

    return app


def configure_app(app, lib):
    app.state.lib = lib

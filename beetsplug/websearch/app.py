import os
import beetsplug.websearch.controller as ctrl

from beets import config
from typing import Any, Optional, Union
from fastapi import FastAPI, Path, Request
from contextlib import asynccontextmanager

from beetsplug.websearch.state.jsonfile import JSONFileRepository
from beetsplug.websearch.sendfile import sendfile
from beetsplug.websearch.m3uprovider import router as M3UProviderRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    state_dir = config['websearch']['state_dir'].get()
    playlists_file = os.path.join(state_dir, "playlists.json")
    playlists_repo = JSONFileRepository(playlists_file)
    ctrl.lib = app.state.lib
    ctrl.playlists = playlists_repo
    yield


def create_app():
    app = FastAPI(
        title="Playlist composer API",
        description="Playlist composer and M3U provider API",
        version="1.0.0",
        lifespan=lifespan,
    )

    from beetsplug.websearch.gen.apis.composer_api import router as WebsearchApiRouter

    app.include_router(WebsearchApiRouter)
    app.include_router(M3UProviderRouter)

    return app


def configure_app(app, lib):
    app.state.lib = lib

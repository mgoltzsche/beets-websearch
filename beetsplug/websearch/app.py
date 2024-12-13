import logging
import os
import beetsplug.websearch.controller as ctrl

from beets import config
from typing import Any, Optional, Union
from fastapi import FastAPI, Path, Request
from contextlib import asynccontextmanager

from beetsplug.websearch.state.jsonfile import JSONFileRepository
from beetsplug.websearch.sendfile import sendfile
from beetsplug.websearch.middleware import get_request, RequestContextMiddleware
from beetsplug.websearch.mediaroutes import router as MediaRouter
from beetsplug.websearch.provider.composed import ComposedPlaylistProvider, NamedPlaylistProvider
from beetsplug.websearch.provider.custom import CustomPlaylistProvider
from beetsplug.websearch.provider.m3u import M3UPlaylistProvider


logger = logging.getLogger('uvicorn.error')


def url_for(*v, **kwargs):
    return str(get_request().url_for(*v, **kwargs))


@asynccontextmanager
async def lifespan(app: FastAPI):
    lib = app.state.lib
    providers = []

    if config['websearch']['provider']['db']['enabled'].get():
        playlists_file = config['websearch']['provider']['db']['file'].get()
        playlists_repo = JSONFileRepository(playlists_file)
        providers.append(NamedPlaylistProvider('db', CustomPlaylistProvider(lib, playlists_repo)))

    if config['websearch']['provider']['m3u']['enabled'].get():
        m3u_dir = config['websearch']['provider']['m3u']['dir'].get()
        if not m3u_dir:
            try:
                m3u_dir = config['smartplaylist']['playlist_dir'].get()
            except:
                logger.warn('Neither config option websearch.m3u.dir nor smartplaylist.playlist_dir was specified - disabling m3u playlist provider')
        if m3u_dir:
            providers.append(NamedPlaylistProvider('m3u', M3UPlaylistProvider(lib, m3u_dir, logger)))

    app.state.provider = ComposedPlaylistProvider(providers, logger)
    ctrl.provider = app.state.provider
    ctrl.lib = lib
    ctrl.url_for = url_for

    yield


def create_app():
    app = FastAPI(
        title="Playlist composer API",
        description="Playlist composer and media server API",
        version="1.0.0",
        lifespan=lifespan,
    )

    from beetsplug.websearch.gen.apis.composer_api import router as WebsearchApiRouter

    app.include_router(WebsearchApiRouter)
    app.include_router(MediaRouter)
    app.add_middleware(RequestContextMiddleware)

    return app


def configure_app(app, lib):
    app.state.lib = lib

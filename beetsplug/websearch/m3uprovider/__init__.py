# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Security,
    status,
)
from fastapi.responses import StreamingResponse
from beetsplug.websearch.sendfile import sendfile


router = APIRouter()


@router.get(
    "/tracks/{id}/audio",
    responses={
        200: {},
    },
    tags=["provider"],
    summary="Get audio data for the given track ID",
    response_model_by_alias=True,
)
async def get_audio_data(
    request: Request,
    id: str = Path(..., description="Beets item ID"),
) -> StreamingResponse:
    """Get/stream audio data for the given track ID."""
    item = request.app.state.lib.get_item(id)
    if not item:
        raise KeyError(f"item {id} not found")
    filepath = item.path.decode('utf-8')
    return sendfile(filepath, request.headers.get('range'))


@router.get(
    "/playlists.m3u",
    responses={
        200: {"model": str, "description": "Index playlist in EXTM3U format"},
    },
    tags=["provider"],
    summary="Get index EXTM3U playlist that lists all playlists",
    response_model_by_alias=True,
)
async def get_m3_u_index(
) -> str:
    """Get the index playlist that contains URLs pointing to the actual playlists."""
    raise HTTPException(status_code=500, detail="Not implemented")


@router.get(
    "/playlists/{playlistId}/tracks.m3u",
    responses={
        200: {"model": str, "description": "Playlist tracks in EXTM3U format"},
    },
    tags=["provider"],
    summary="Get playlist tracks in EXTM3U format",
    response_model_by_alias=True,
)
async def get_m3_u_playlist(
    playlistId: str = Path(..., description="Playlist ID"),
) -> str:
    """Get the tracks contained within a playlist in the EXTM3U format."""
    raise HTTPException(status_code=500, detail="Not implemented")

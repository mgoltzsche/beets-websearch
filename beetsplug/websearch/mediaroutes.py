# coding: utf-8

import importlib
import logging
import pkgutil
import re
from typing import Dict, Generator, List  # noqa: F401
from typing_extensions import Annotated
from urllib.parse import quote_plus

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
from beetsplug.websearch.provider import Playlist, PlaylistTrack

# TODO: remove test endpoint imports
#from beetsplug.websearch.gen.models.track_type_switch import TrackTypeSwitch
#from beetsplug.websearch.gen.models.track import Track
#from beetsplug.websearch.gen.models.a_track_alternative import ATrackAlternative


router = APIRouter()

_format_regex = re.compile(r'\$[a-z0-9_]+')
_logger = logging.getLogger('uvicorn.error')


@router.get(
    "/tracks/{id}/audio",
    responses={
        200: {},
    },
    tags=["media"],
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
        200: {
            "content": {"audio/mpegurl": {}},
            "description": "Index playlist in EXTM3U format",
        },
    },
    tags=["media"],
    summary="Get index EXTM3U playlist that lists all playlists",
    response_model_by_alias=True,
)
async def get_m3u_index(
    request: Request,
    uri_format: Annotated[str | None, Query(
        alias="uri-format",
        description="Playlist item URI template. Dollar-prefixed item/song field names can be used as placeholders, e.g. `beets:library:track;$id` or `subidy:song:3$id`. `$url` is a built-in placeholder and the default value.",
    )] = None,
) -> Response:
    """Get the index playlist that contains URLs pointing to the actual playlists."""
    playlists = await request.app.state.provider.playlists()
    q = uri_format and f"?uri-format={quote_plus(uri_format)}" or ''
    lines = [_m3u_line4playlist(playlist, q, request) for playlist in playlists]
    return Response(f"#EXTM3U\n{''.join(lines)}", media_type='audio/mpegurl')


@router.get(
    "/playlists/{playlistId}/tracks.m3u",
    responses={
        200: {
            "content": {"audio/mpegurl": {}},
            "description": "EXTM3U playlist",
        },
    },
    tags=["media"],
    summary="Get playlist in EXTM3U format",
    response_model_by_alias=True,
)
async def get_m3u_playlist(
    request: Request,
    playlistId: str = Path(..., description="Playlist ID"),
    uri_format: Annotated[str | None, Query(
        alias="uri-format",
        description="Playlist item URI template. Dollar-prefixed item/song field names can be used as placeholders, e.g. `beets:library:track;$id` or `subidy:song:3$id`. `$url` is a built-in placeholder and the default value.",
    )] = None,
) -> StreamingResponse:
    """Get the tracks contained within a playlist in the EXTM3U format."""
    playlist = await request.app.state.provider.playlist(playlistId)
    if not playlist:
        return Exception(f"playlist {playlistId} not found")
    return StreamingResponse(playlist2m3u(playlist, uri_format, request),
        media_type = 'audio/mpegurl')


async def playlist2m3u(playlist: Playlist, uri_format: str, request: Request) -> Generator[bytes, None, None]:
    tracks = await playlist.tracks()
    yield "#EXTM3U\n".encode('utf-8')
    skipped = False
    for item in tracks:
        try:
            yield _m3u_line4track(item, uri_format, request).encode('utf-8')
        except KeyError as e:
            if not skipped:
                skipped = True
                msg = f"Skipping playlist item(s) because URI format refers to missing key {e}"
                _logger.warning(msg)
                yield f"# {msg}\n"


def _m3u_line4playlist(playlist: Playlist, query: str, request: Request):
    uri = request.url_for('get_m3u_playlist', playlistId=playlist.id)
    return f'#EXTINF:0,{playlist.title}\n{uri}{query}\n'


def _m3u_line4track(track: PlaylistTrack, uri_format: str | None, request: Request):
    url = request.url_for('get_audio_data', id=track.id)
    track.url = str(url)
    uri = _format_regex.sub(_format(track.__dict__), uri_format or '$url')
    title = track.artist and f"{track.artist} - {track.title}" or track.title
    return f'#EXTINF:0,{title}\n{uri}\n'


def _format(attrs):
    return lambda m: attrs[m.group(0)[1:]]


# TODO: remove test endpoint
#@router.get(
#    "/test",
#    responses={
#        200: {"model": TrackTypeSwitch, "description": "example model"},
#    },
#    tags=["media"],
#    summary="test endpoint",
#    response_model_by_alias=True,
#    response_model_exclude_unset=True,
#)
#async def test() -> TrackTypeSwitch:
#    """Return example model"""
#    #return TrackTypeSwitch(root=Track(id="1", title="title", artist="artist", album="album", audio_url="url", object_type="Track"))
#    #return TrackTypeSwitch.parse_obj({'objectType': 'alt', 'some_field': 'some value'})
#    return ATrackAlternative(some_field="some value")

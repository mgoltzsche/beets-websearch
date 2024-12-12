import asyncio
import json
from typing import Callable, Dict, List
from beets.library import Library, Item
from beetsplug.websearch.gen.models.attribute_definition_list import AttributeDefinitionList
from beetsplug.websearch.gen.models.attribute_definition import AttributeDefinition
from beetsplug.websearch.gen.models.attribute_type_definition import AttributeTypeDefinition
from beetsplug.websearch.gen.models.attribute_info import AttributeInfo
from beetsplug.websearch.gen.models.playlist import Playlist as PlaylistDTO
from beetsplug.websearch.gen.models.playlist_list import PlaylistList as PlaylistListDTO
from beetsplug.websearch.gen.models.track_list import TrackList
from beetsplug.websearch.gen.models.track import Track
from beetsplug.websearch.gen.models.operation import Operation
from beetsplug.websearch.gen.apis.composer_api_base import BaseComposerApi
from beetsplug.websearch.query import to_beets_query
from beetsplug.websearch.provider import PlaylistProvider, Playlist
from beetsplug.websearch.provider.custom import CustomPlaylist


provider: PlaylistProvider
lib: Library
url_for: Callable


class ComposerApi(BaseComposerApi):

    async def attributes(
        self,
    ) -> AttributeDefinitionList:
        """Lists attributes that can be used as search criteria."""
        # TODO: implement
        return AttributeDefinitionList(
            attributes=[
                AttributeDefinition(
                    name="title",
                    title="Title",
                    type="string",
                ),
                AttributeDefinition(
                    name="artist",
                    title="Artist",
                    type="string",
                ),
                AttributeDefinition(
                    name="genre",
                    title="Genre",
                    type="string",
                ),
                AttributeDefinition(
                    name="bpm",
                    title="BPM",
                    type="int",
                ),
            ],
            types=[
                AttributeTypeDefinition(
                    name="string",
                    operators=["eq", "contains", "regex"],
                ),
                AttributeTypeDefinition(
                    name="int",
                    operators=["eq", "gt", "lt"],
                ),
                AttributeTypeDefinition(
                    name="date",
                    operators=["eq", "gt", "lt"],
                ),
            ],
        )


    async def get_attribute_info(
        self,
        attribute: str,
        query: str,
    ) -> AttributeInfo:
        """Provides the range of available values for a given attribute definition and search query. """
        q = _query_from_str(query or "{}")
        # TODO: implement
        return AttributeInfo(
            name="genre",
            values=["Dub", "Dubstep", "House"],
        )


    async def delete_playlist(
        self,
        playlistId: str,
    ) -> None:
        """Delete a playlist."""
        await provider.delete_playlist(playlistId)


    async def list_playlists(
        self,
    ) -> PlaylistListDTO:
        """List all playlists."""
        items = await provider.playlists()
        items.sort(key=lambda i: (i.title, i.id))
        return PlaylistListDTO(
            items=[_playlist_to_dto(p) for p in items],
        )


    async def list_tracks(
        self,
        query: str,
    ) -> TrackList:
        """List and search tracks."""
        q = to_beets_query(_query_from_str(query or "{}"))
        loop = asyncio.get_event_loop()
        items = await loop.run_in_executor(None, _query, q)
        return TrackList(
            items=[_item_to_dto(item) for item in items],
        )


    async def get_playlist_tracks(
        self,
        playlistId: str,
    ) -> TrackList:
        """Get the tracks contained within a playlist."""
        playlist = await provider.playlist(playlistId)
        if not playlist:
            raise Exception(f"playlist {playlistId} not found")
        return TrackList(
            items=[_item_to_dto(item) for item in await playlist.tracks()],
        )


    async def create_playlist(
        self,
        playlist: PlaylistDTO,
    ) -> PlaylistDTO:
        """Create a playlist."""
        p = _playlist_from_dto(playlist)
        await provider.create_playlist(p)
        return _playlist_to_dto(p)


    async def update_playlist(
        self,
        playlistId: str,
        playlist: PlaylistDTO,
    ) -> PlaylistDTO:
        """Update a playlist."""
        if playlist.id != playlistId:
            raise Exception("playlist ID from path variable differs from playlist ID within body")
        p = _playlist_from_dto(playlist)
        await provider.update_playlist(p)
        return _playlist_to_dto(p)


def _query(q: str) -> List[Item]:
    return lib.items(query=q)


# DTO transformations:


def _query_to_str(query: Dict[str, Operation]) -> str:
    return json.dumps(query)

def _query_from_str(querystr: str) -> Dict[str, Operation]:
    return json.loads(querystr)

def _queries_from_strs(querystrs: List[str]) -> List[Dict[str, Operation]]:
    if querystrs == None:
        return []
    return [json.loads(q) for q in querystrs]

def _item_to_dto(item: Item) -> Track:
    dto = Track(
        id=str(item.id),
        title=item.title,
        artist=item.artist,
        length=item.get('length') or 0,
        audio_url=url_for('get_audio_data', id=item.id),
    )
    if item.get('album'):
        dto.album = item.get('album')
    if item.get('genre'):
        dto.genre = item.get('genre')
    if item.get('bpm'):
        dto.bpm = str(item.get('bpm'))
    return dto

def _playlist_from_dto(dto: PlaylistDTO) -> CustomPlaylist:
    return CustomPlaylist(
        id=dto.id,
        title=dto.title,
        created=dto.created,
        query=dto.query and [{k: {o: v for (o,v) in op.model_dump().items()} for (k,op) in q.items()} for q in dto.query] or None,
        provider=None,
    )

def _playlist_to_dto(p: Playlist) -> PlaylistDTO:
    return PlaylistDTO(
        id=p.id,
        created=p.created,
        title=p.title,
        query=p.query and [{k: Operation.parse_obj(op) for (k,op) in q.items()} for q in p.query] or None,
        m3u_url=url_for('get_m3u_playlist', playlistId=p.id),
    )

import asyncio
import json
from typing import Dict, List
from datetime import datetime, timezone
from beets.library import Library, Item
from beetsplug.websearch.gen.models.attribute_definition_list import AttributeDefinitionList
from beetsplug.websearch.gen.models.attribute_definition import AttributeDefinition
from beetsplug.websearch.gen.models.attribute_type_definition import AttributeTypeDefinition
from beetsplug.websearch.gen.models.attribute_info import AttributeInfo
from beetsplug.websearch.gen.models.playlist import Playlist
from beetsplug.websearch.gen.models.playlist_list import PlaylistList
from beetsplug.websearch.gen.models.track_list import TrackList
from beetsplug.websearch.gen.models.track import Track
from beetsplug.websearch.gen.models.operation import Operation
from beetsplug.websearch.gen.apis.composer_api_base import BaseComposerApi
from beetsplug.websearch.query import to_beets_query
from beetsplug.websearch.state import Repository


lib: Library
playlists: Repository

class ComposerApi(BaseComposerApi):

    async def attributes(
        self,
    ) -> AttributeDefinitionList:
        """Lists attributes that can be used as search criteria. (The frontend could generate a search form based on this data.) """
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
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, playlists.delete, playlistId)


    async def list_playlists(
        self,
    ) -> PlaylistList:
        """List all playlists."""
        loop = asyncio.get_event_loop()
        items = await loop.run_in_executor(None, playlists.list)
        items.sort(key=lambda i: (i['title']))
        return PlaylistList(
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
        items = []
        loop = asyncio.get_event_loop()
        playlist = await loop.run_in_executor(None, playlists.get, playlistId)
        if playlist:
            q = [to_beets_query(q) for q in playlist['query']]
            items = await _query_union(q)
        return TrackList(
            items=[_item_to_dto(item) for item in items],
        )


    async def get_playlist(
        self,
        playlistId: str,
    ) -> Playlist:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, playlists.get, playlistId)


    async def save_playlist(
        self,
        playlistId: str,
        playlist: Playlist,
    ) -> Playlist:
        """Create or update a playlist."""
        playlist.id = playlistId
        existing = await self.get_playlist(playlistId)
        playlist.created = existing and existing['created'] or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        playlist_dict = _playlist_from_dto(playlist)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, playlists.save, playlist_dict)
        return _playlist_to_dto(playlist_dict)


def _query_to_str(query: Dict[str, Operation]) -> str:
    return json.dumps(query)

def _query_from_str(querystr: str) -> Dict[str, Operation]:
    return json.loads(querystr)

def _queries_from_strs(querystrs: List[str]) -> List[Dict[str, Operation]]:
    if querystrs == None:
        return []
    return [json.loads(q) for q in querystrs]

async def _query_union(queries: List[str]) -> List[Item]:
    loop = asyncio.get_event_loop()
    resultsets = [loop.run_in_executor(None, _query, q) for q in queries]
    itemset = {item.id: item for resultset in resultsets for item in await resultset}
    items = [item for item in itemset.values()]
    items.sort(key=lambda i: (i.artist, i.title, i.id))
    return items

def _query(q: str) -> List[Item]:
    return lib.items(query=q)


# DTO transformations:


def _item_to_dto(item: Item) -> Track:
    return Track(
        id=str(item.id),
        title=item.title,
        artist=item.artist,
        album=item.album,
        genre=item.genre,
        bpm=str(item.bpm),
        # TODO: generate URL
        audio_url="TODO",
    )

def _playlist_from_dto(dto: Playlist) -> Dict:
    return {
        'id': dto.id,
        'title': dto.title,
        'created': dto.created,
        'query': [{k: {o: v for (o,v) in op.model_dump().items()} for (k,op) in q.items()} for q in dto.query],
    }

def _playlist_to_dto(p: Dict) -> Playlist:
    return Playlist(
        id=p['id'],
        created=p['created'],
        title=p['title'],
        query=[{k: Operation.parse_obj(op) for (k,op) in q.items()} for q in p['query']],
        # TODO: generate URL
        m3u_url="TODO",
    )

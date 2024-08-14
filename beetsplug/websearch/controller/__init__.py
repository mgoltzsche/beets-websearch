import asyncio
from typing import Dict, List
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
from beetsplug.websearch.gen.apis.websearch_api_base import BaseWebsearchApi


lib: Library

class WebsearchApi(BaseWebsearchApi):

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
        query: List[str],
    ) -> AttributeInfo:
        """Provides the range of values for a given attribute definition and search query. """
        queries = _queries_from_strs(query)
        # TODO: implement
        return AttributeInfo(
            name="genre",
            values=["Dub", "Dubstep", "House"],
        )


    async def create_playlist(
        self,
        playlist: Playlist,
    ) -> Playlist:
        """Create a new playlist based on the given set of song queries."""
        # TODO: implement
        return Playlist()


    async def delete_playlist(
        self,
        playlist: str,
    ) -> None:
        """Delete a playlist."""
        # TODO: implement
        ...


    async def list_playlists(
        self,
    ) -> PlaylistList:
        """List all playlists."""
        # TODO: implement
        return PlaylistList()


    async def list_tracks(
        self,
        query: List[str],
    ) -> TrackList:
        """List and search tracks."""
        queries = _queries_from_strs(query)
        # TODO: implement query
        q = None
        loop = asyncio.get_event_loop()
        items = await loop.run_in_executor(None, _query, q)
        return TrackList(
            items=items,
        )


    async def update_playlist(
        self,
        playlist: Playlist,
    ) -> Playlist:
        """Update an existing playlist."""
        # TODO: implement
        return playlist


def _query_to_str(query: Dict[str, Operation]) -> str:
    return json.dumps(query)

def _query_from_str(querystr: str) -> Dict[str, Operation]:
    return json.loads(querystr)

def _queries_from_strs(querystrs: List[str]) -> List[Dict[str, Operation]]:
    if querystrs == None:
        return []
    return [json.loads(q) for q in querystrs]

def _query(q: str) -> List[Item]:
    return [_item_to_track(item) for item in lib.items(query=q)]


# DTO transformations:


def _item_to_track(item: Item) -> Track:
    return Track(
        id=str(item.id),
        title=item.title,
        artist=item.artist,
        genre=item.genre,
        bpm=str(item.bpm),
    )

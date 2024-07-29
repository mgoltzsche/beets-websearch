from typing import Dict, List

from beetsplug.websearch.gen.models.attribute_definition_list import AttributeDefinitionList
from beetsplug.websearch.gen.models.attribute_definition import AttributeDefinition
from beetsplug.websearch.gen.models.attribute_type_definition import AttributeTypeDefinition
from beetsplug.websearch.gen.models.attribute_info import AttributeInfo
from beetsplug.websearch.gen.models.playlist import Playlist
from beetsplug.websearch.gen.models.playlist_list import PlaylistList
from beetsplug.websearch.gen.models.track_list import TrackList
from beetsplug.websearch.gen.models.track import Track
from beetsplug.websearch.gen.apis.websearch_api_base import BaseWebsearchApi


class WebsearchApi(BaseWebsearchApi):


    async def attributes(
        self,
    ) -> AttributeDefinitionList:
        """Lists attributes that can be used as search criteria. (The frontend could generate a search form based on this data.) """
        # TODO: implement
        return AttributeDefinitionList(
            attributes=[
                AttributeDefinition(
                    name="genre",
                    type="string",
                ),
                AttributeDefinition(
                    name="bpm",
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
        # TODO: implement
        return TrackList(
            items=[
                Track(
                    id="123",
                    title="Serpiente Dorada",
                    # TODO: make this work (generated code expects a string currently):
                    #additional_properties={
                    #    "genre": "Dub",
                    #    "bpm": "90",
                    #},
                ),
            ],
        )


    async def update_playlist(
        self,
        playlist: Playlist,
    ) -> Playlist:
        """Update an existing playlist."""
        # TODO: implement
        return playlist

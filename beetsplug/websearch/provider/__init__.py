from abc import ABC, abstractmethod
from typing import Dict, List
from beets.library import Item


class PlaylistTrack:
    id: str
    artist: str = None # may not be set for m3u playlist items
    title: str
    length: float # seconds
    uri: str = None # not set for beets items

    def get(self, k: str):
        return self.__dict__.get(k)


class Playlist(ABC):
    id: str
    title: str
    created: str
    query: List[Dict[str, Dict[str, str]]] = None

    def __init__(self, id: str, title: str, created: str):
        self.id = id
        self.title = title
        self.created = created

    @abstractmethod
    async def tracks(self) -> List[PlaylistTrack]:
        ...


class PlaylistProvider(ABC):

    @abstractmethod
    async def playlists(self) -> List[Playlist]:
        ...

    @abstractmethod
    async def playlist(self, id: str) -> Playlist:
        ...

    @abstractmethod
    async def create_playlist(self, p: Playlist):
        ...

    @abstractmethod
    async def update_playlist(self, p: Playlist):
        ...

    @abstractmethod
    async def delete_playlist(self, id: str):
        ...

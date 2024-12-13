import asyncio
import re
import unicodedata
from typing import Dict, List
from beets.library import Library, Item
from beetsplug.websearch.provider import PlaylistProvider, Playlist, PlaylistTrack
from beetsplug.websearch.query import to_beets_query
from beetsplug.websearch.state import Repository


_id_regex = re.compile('[^a-z0-9-]+')


class CustomPlaylistProvider(PlaylistProvider):

    def __init__(self, lib: Library, repo: Repository):
        self._lib = lib
        self._repo = repo

    async def playlists(self) -> List[Playlist]:
        loop = asyncio.get_event_loop()
        playlist_dicts = await loop.run_in_executor(None, self._repo.list)
        return [self._to_playlist(p) for p in playlist_dicts]

    async def playlist(self, id: str) -> Playlist:
        loop = asyncio.get_event_loop()
        playlist_dict = await loop.run_in_executor(None, self._repo.get, id)
        if not playlist_dict:
            return None
        return self._to_playlist(playlist_dict)

    async def create_playlist(self, p: Playlist):
        if not p.title:
            raise Exception('playlist does not specify title')
        if not p.id:
            p.id = p.title
        p.id = _id_regex.sub('-', _strip_accents(p.id).lower())
        p.query = p.query or []
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._repo.create, self._to_dict(p))

    async def update_playlist(self, p: Playlist):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._repo.update, self._to_dict(p))

    async def delete_playlist(self, id: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._repo.delete, id)

    def _to_playlist(self, p: Dict) -> Playlist:
        return CustomPlaylist(
            id=p['id'],
            title=p['title'],
            created=p['created'],
            query=p['query'],
            provider=self,
        )

    def _to_dict(self, p: Playlist) -> Dict:
        return {
            'id': p.id,
            'title': p.title,
            'created': p.created,
            'query': p.query,
        }

    async def _query_union(self, queries: List[str]) -> List[Item]:
        loop = asyncio.get_event_loop()
        results = [loop.run_in_executor(None, self._query, q) for q in queries]
        itemset = {item.id: item for result in results for item in await result}
        items = [item for item in itemset.values()]
        items.sort(key=lambda i: (i.artist, i.title, i.id))
        return items

    def _query(self, q: str) -> List[Item]:
        return self._lib.items(query=q)


class CustomPlaylist(Playlist):

    def __init__(self, provider: CustomPlaylistProvider, id: str, title: str, created: str, query: List[Dict[str, Dict[str, str]]]):
        super().__init__(
            id=id,
            title=title,
            created=created,
        )
        self._provider = provider
        self.query = query

    async def tracks(self) -> List[PlaylistTrack]:
        q = [to_beets_query(q) for q in self.query or []]
        return await self._provider._query_union(q)


def _strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

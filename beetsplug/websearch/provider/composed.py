import asyncio
import copy
import re
from logging import Logger
from typing import Dict, List, Tuple
from beets.library import Library, Item
from beetsplug.websearch.provider import PlaylistProvider, Playlist, PlaylistTrack
from beetsplug.websearch.query import to_beets_query
from beetsplug.websearch.state import Repository


_id_regex = re.compile('^([^:]+):(.+)$')


class NamedPlaylistProvider:
    def __init__(self, name: str, provider: PlaylistProvider):
        self.name = name
        self.provider = provider


class ComposedPlaylistProvider(PlaylistProvider):

    def __init__(self, providers: List[NamedPlaylistProvider], logger: Logger):
        self._providers = providers
        self._logger = logger

    async def playlists(self) -> List[Playlist]:
        return [_prefix_id(playlist, p.name) for p in self._providers for playlist in await p.provider.playlists()]

    async def playlist(self, id: str) -> Playlist:
        provider, id = _parse_id(id)
        return await self._provider(provider).playlist(id)

    async def create_playlist(self, p: Playlist):
        for pr in self._providers:
            try:
                pn = copy.copy(p)
                await pr.provider.create_playlist(pn)
                prefixed = _prefix_id(p, pr.name)
                p.id = prefixed.id
                return
            except NotImplementedError:
                pass
            except BaseException as e:
                raise Exception(f"cannot create playlist using {pr.name} provider: {e}") from e
        raise Exception('cannot create playlist since no provider registered that supports playlist creation')

    async def update_playlist(self, p: Playlist):
        provider, p.id = _parse_id(p.id)
        await self._provider(provider).update_playlist(p)

    async def delete_playlist(self, id: str):
        provider, id = _parse_id(id)
        await self._provider(provider).delete_playlist(id)

    def _provider(self, name: str) -> PlaylistProvider:
        for p in self._providers:
            if p.name == name:
                return p.provider
        raise Exception(f"Unsupported playlist provider '{name}' specified")


def _prefix_id(playlist: Playlist, provider_name: str) -> Playlist:
    p = copy.copy(playlist)
    p.id = f"{provider_name}:{playlist.id}"
    return p


def _parse_id(id: str) -> Tuple[str, str]:
    m = _id_regex.match(id)
    if not m:
        raise Exception("malformed playlist ID provided, expected a qualified ID in the format PROVIDER:ID")
    return (m.group(1), m.group(2))

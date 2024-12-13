import asyncio
import glob
import os
import pathlib
import re
from datetime import datetime, timezone
from logging import Logger
from typing import Dict, Generator, List
from urllib.parse import unquote
from beets.library import Library
from beetsplug.websearch.provider import PlaylistProvider, Playlist, PlaylistTrack


extinf_regex = re.compile(r'^#EXTINF:([0-9]+)( [^,]+)?,[\s]*(.*)')
_id_regex = re.compile('[^a-z0-9-]+')


class M3UPlaylist(Playlist):
    path: str

    def __init__(self, id: str, title: str, created: str, path: str):
        super().__init__(
            id=id,
            title=title,
            created=created,
        )
        self.path = path

    async def tracks(self) -> List[PlaylistTrack]:
        loop = asyncio.get_event_loop()
        tracks = await loop.run_in_executor(None, parse_m3u_playlist, self.path)
        return [track for track in tracks if track.id]


class M3UPlaylistProvider(PlaylistProvider):

    _playlists: Dict[str, M3UPlaylist]

    def __init__(self, lib: Library, dir: str, logger: Logger):
        self._lib = lib
        self._dir = dir
        self._playlists = {}
        self._logger = logger

    async def _refresh(self):
        loop = asyncio.get_event_loop()
        playlists = await loop.run_in_executor(None, self._load_playlists)
        self._playlists = {p.id: p for p in playlists}
        self._logger.debug(f"Loaded {len(self._playlists)} m3u playlists")

    def _load_playlists(self) -> List[Playlist]:
        if not self._dir:
            return []
        paths = glob.glob(os.path.join(self._dir, "**.m3u"))
        paths.sort()
        playlists = []
        for path in paths:
            try:
                playlists.append(self._playlist_from_path(path))
            except BaseException as e:
                self._logger.exception(f"Failed to load m3u playlist {path}: {e}")
        return playlists

    def _playlist_from_path(self, filepath):
        id = self._path2id(filepath)
        title = pathlib.Path(os.path.basename(filepath)).stem
        playlist = self._playlists.get(id)
        mtime = pathlib.Path(filepath).stat().st_mtime
        mtimestr = datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if playlist and playlist.created == mtimestr:
            return playlist # cached metadata
        self._logger.debug(f"Loading m3u playlist {filepath}")
        return M3UPlaylist(
            id=id,
            title=title,
            created=mtimestr,
            path=filepath,
        )

    def _path2id(self, filepath):
        relpath = os.path.relpath(filepath, self._dir)
        basename = pathlib.Path(relpath).stem
        return _id_regex.sub('-', basename)

    async def playlists(self) -> List[M3UPlaylist]:
        await self._refresh()
        playlists = self._playlists
        ids = [k for k, v in playlists.items() if v]
        ids.sort()
        return [playlists[id] for id in ids]

    async def playlist(self, id: str) -> M3UPlaylist:
        await self._refresh()
        playlist = self._playlists.get(id)
        if not playlist:
            raise KeyError(f"m3u playlist '{id}' not found")
        return playlist

    async def create_playlist(self, p: Playlist):
        raise NotImplementedError('M3UPlaylistProvider does not support creating a playlist')

    async def update_playlist(self, p: Playlist):
        raise NotImplementedError('M3UPlaylistProvider does not support updating a playlist')

    async def delete_playlist(self, id: str):
        raise NotImplementedError('M3UPlaylistProvider does not support deleting a playlist')


def parse_m3u_playlist(filepath) -> Generator[PlaylistTrack, None, None]:
    '''
    Parses an M3U playlist and yields its contained tracks, one at a time.
    It expects attribute values to be URL-encoded.
    '''
    with open(filepath, 'r', encoding='utf-8') as file:
        linenum = 0
        track = PlaylistTrack()
        while line := file.readline():
            line = line.rstrip()
            linenum += 1
            if linenum == 1:
                assert line == '#EXTM3U', f"File {filepath} is not an EXTM3U playlist!"
                continue
            if len(line.strip()) == 0:
                continue
            m = extinf_regex.match(line)
            if m:
                track = PlaylistTrack()
                attrs = m.group(2)
                if attrs:
                    # requires attributes to be encoded using urllib.parse.quote(attr, safe='/:')
                    track.__dict__ = {k: unquote(v.strip('"')) for k,v in [kv.split('=') for kv in attrs.strip().split(' ')]}
                track.length = int(m.group(1))
                track.title = m.group(3)
                title_parts = track.title.split(' - ')
                if len(title_parts) > 1:
                    track.artist = title_parts[0]
                    track.title = ' - '.join(title_parts[1:])
                continue
            if line.startswith('#'):
                continue
            track.uri = line
            yield track
            track = PlaylistTrack()

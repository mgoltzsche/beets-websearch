from fastapi.responses import StreamingResponse
import logging
import mimetypes
from pathlib import Path
import posixpath
from typing import IO, Generator

"""
Stream a file with FastAPI and range request support.
Based on https://gist.github.com/tombulled/712fd8e19ed0618c5f9f7d5f5f543782
"""

logger = logging.getLogger(__name__)

DEFAULT_MIME_TYPE = 'application/octet-stream'
EXTENSION_TO_MIME_TYPE_FALLBACK = {
    '.aac'  : 'audio/aac',
    '.flac' : 'audio/flac',
    '.mp3'  : 'audio/mpeg',
    '.mp4'  : 'audio/mp4',
    '.m4a'  : 'audio/mp4',
    '.ogg'  : 'audio/ogg',
    '.opus' : 'audio/opus',
}

def path_to_content_type(path: str):
    result = mimetypes.guess_type(path)[0]
    if result:
        return result

    base, ext = posixpath.splitext(path)
    result = EXTENSION_TO_MIME_TYPE_FALLBACK.get(ext)

    if result:
        return result

    logger.warning(f"No mime type mapped for {ext} extension: {path}")

    return DEFAULT_MIME_TYPE

def sendfile(filepath: str, content_range: str) -> StreamingResponse:
    path = Path(filepath)

    # TODO: close file after response was sent
    file = path.open('rb')

    file_size = path.stat().st_size

    content_length = file_size
    status_code = 200
    headers = {}

    if content_range is not None:
        content_range = content_range.strip().lower()

        content_ranges = content_range.split('=')[-1]

        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))

        range_start = max(0, int(range_start)) if range_start else 0
        range_end   = min(file_size - 1, int(range_end)) if range_end else file_size - 1

        content_length = (range_end - range_start) + 1

        file = _ranged(file, start = range_start, end = range_end + 1)

        status_code = 206

        headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

    response = StreamingResponse(file,
        media_type = path_to_content_type(filepath),
        status_code = status_code,
    )

    response.headers.update({
        'Accept-Ranges': 'bytes',
        'Content-Length': str(content_length),
        **headers,
    })

    return response

def _ranged(file: IO[bytes],
            start: int = 0,
            end: int = None,
            block_size: int = 8192,
        ) -> Generator[bytes, None, None]:
    consumed = 0

    try:
        file.seek(start)
    
        while True:
            data_length = min(block_size, end - start - consumed) if end else block_size
    
            if data_length <= 0:
                break
    
            data = file.read(data_length)
    
            if not data:
                break
    
            consumed += data_length
    
            yield data
    finally:
        if hasattr(file, 'close'):
            file.close()

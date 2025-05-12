import mimetypes
import os
from collections.abc import AsyncGenerator
from typing import Literal
from urllib.parse import quote

import aiofiles
import aiofiles.os
from anyio import Path


class FileStreamer:
    """
    Class for streaming a file in chunks from a given file path.
    """

    def __init__(  # noqa: PLR0913
        self,
        filepath: str | Path,
        read_mode: Literal["r", "rb"] = "rb",
        chunk_size: int = 1024,
        with_cleanup: bool = False,
        filename: str | None = None,
        mime_type: str | None = None,
        encoding: str | None = None,
    ):
        if not isinstance(filepath, Path):
            filepath = Path(filepath)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        if not os.path.isfile(filepath):
            raise ValueError(f"Path is not a file: {filepath}")
        if filename is None:
            filename = filepath.name
        self.filename = filename
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.with_cleanup = with_cleanup
        if not mime_type or not encoding:
            _mime_type, _encoding = mimetypes.guess_type(self.filepath.name)
            mime_type = (
                mime_type if mime_type else _mime_type or "application/octet-stream"
            )
            encoding = encoding if encoding else _encoding or "utf-8"
        self._media_type = mime_type
        self._encoding = encoding
        self._content_disposition = (
            f"attachment; filename*={self._encoding}''{quote(self.filename)}"
        )
        self.read_mode = read_mode

    async def get_stream(self) -> AsyncGenerator[str, None]:
        """
        Asynchronously reads the file in chunks and yields each chunk as a string.

        Yields:
            str: A chunk of the file content as a string.

        This function opens the file specified by `self.filepath` in read mode and
        reads it using the specified `self.chunk_size`. It continuously reads and
        yields chunks of the file until the end of the file is reached.
        """

        try:
            async with aiofiles.open(
                file=self.filepath,
                encoding=self._encoding if self.read_mode == "r" else None,
                mode=self.read_mode,
            ) as f:
                while True:
                    chunk = await f.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
        finally:
            if self.with_cleanup:
                await aiofiles.os.remove(self.filepath)

    @property
    def content_disposition(self) -> str:
        """
        Returns:
            str: The content disposition of the file.
        """

        return self._content_disposition

    @property
    def encoding(self) -> str:
        """
        Returns:
            str: The encoding of the file.
        """

        return self._encoding

    @property
    def media_type(self) -> str:
        """
        Returns:
            str: The media type of the file.
        """

        return self._media_type

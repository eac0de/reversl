"""
Middleware to track and add process time to the response headers.

This middleware captures the time when the request is started and when the response is sent.
The difference of these two times is added to the response headers as 'X-Process-Time'.

The time is formatted as a float with 4 digits after the decimal point.

    Example:
        X-Process-Time: 0.0123 seconds

"""

import time

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ProcessTimeMiddleware:

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        start_time = time.time()

        async def send_with_process_time(message: Message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                headers = MutableHeaders(raw=message["headers"])
                headers["X-Process-Time"] = f"{process_time:.4f} seconds"

            await send(message)

        await self.app(scope, receive, send_with_process_time)

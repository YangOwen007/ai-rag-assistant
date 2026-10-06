"""Bound request bodies before JSON decoding or multipart parsing."""
from starlette.responses import JSONResponse


class BodyLimitMiddleware:
    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        # Buffer a bounded body, then replay it; this also covers chunked requests.
        chunks = []
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > self.max_bytes:
                await JSONResponse({"detail": "Request body is too large."}, status_code=413)(scope, receive, send)
                return
            chunks.append(message)
            if not message.get("more_body", False):
                break
        async def replay():
            if chunks:
                return chunks.pop(0)
            return await receive()
        await self.app(scope, replay, send)

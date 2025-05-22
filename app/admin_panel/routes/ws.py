import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.constants import AP_REDIS_CHANNEL
from app.core.rediss import get_redis
from app.dependencies.users import UserDepWS

router = APIRouter(
    tags=["ap_api"],
)


@router.websocket(
    path="/",
    name="ap_ws",
    dependencies=[UserDepWS()],
)
async def admin_panel_websocket(
    websocket: WebSocket,
) -> None:
    await websocket.accept()
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(AP_REDIS_CHANNEL)

    async def listen_redis() -> None:
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            await websocket.send_json(data=json.loads(msg["data"]))

    task = asyncio.create_task(listen_redis())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        task.cancel()
        await pubsub.unsubscribe(AP_REDIS_CHANNEL)
        await pubsub.close()

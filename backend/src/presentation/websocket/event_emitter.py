from fastapi import WebSocket


class EventEmitter:
    def __init__(self, websocket: WebSocket) -> None:
        self._websocket = websocket

    async def emit(self, event: str, data: dict) -> None:
        await self._websocket.send_json({"event": event, "data": data})

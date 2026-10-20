import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List

class EventBroadcaster:
    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "event": event_type,
            "data": data
        }
        dead_queues = []
        for q in self._subscribers:
            try:
                q.put_nowait(payload)
            except Exception:
                dead_queues.append(q)
        for dq in dead_queues:
            self.unsubscribe(dq)

pipeline_broadcaster = EventBroadcaster()
alert_broadcaster = EventBroadcaster()

import asyncio
from typing import Dict, Optional

from ...application.ports.browser_automation_port import BrowserAutomationPort
from ...domain.entities.browser_session import BrowserSession


class SessionManager:

    def __init__(self, browser_automation: BrowserAutomationPort) -> None:
        self._browser_automation = browser_automation
        self._sessions: Dict[str, BrowserSession] = {}
        # Varias conexiones WebSocket pueden crear/destruir sesiones a la vez;
        # el lock evita carreras sobre el diccionario.
        self._lock = asyncio.Lock()

    async def create_session(self) -> BrowserSession:
        session = await self._browser_automation.create_session()
        async with self._lock:
            self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        return self._sessions.get(session_id)

    async def destroy_session(self, session_id: str) -> None:
        async with self._lock:
            session = self._sessions.pop(session_id, None)
        if session:
            await self._browser_automation.destroy_session(session)

    async def destroy_all(self) -> None:
        async with self._lock:
            session_ids = list(self._sessions.keys())
        for session_id in session_ids:
            await self.destroy_session(session_id)

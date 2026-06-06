from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import uuid


@dataclass
class BrowserSession:
    # Los objetos del navegador se tipan como Any para que el dominio no
    # dependa de Playwright.
    session_id: str = field(default_factory=lambda: f"session_{uuid.uuid4().hex[:6]}")
    browser: Optional[Any] = None
    browser_context: Optional[Any] = None
    page: Optional[Any] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def touch(self) -> None:
        self.last_activity = datetime.now()

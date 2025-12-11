from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict


class EventType(str, Enum):
    BAR = "BAR"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


@dataclass(frozen=True)
class Event:
    type: EventType
    dt: datetime
    payload: Dict[str, Any]

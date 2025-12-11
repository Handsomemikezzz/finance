from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from finance.core.coreTypes import Bar, Signal


class StrategyBase(ABC):
    @abstractmethod
    def on_bar(self, bar: Bar) -> Optional[Signal]:
        """消费一根 bar（收盘后），返回 Signal（目标仓位）或 None。"""

        raise NotImplementedError

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Sequence

from finance.core.coreTypes import Bar


@dataclass(frozen=True)
class DataHandler:
    """MVP：单标的/多标的接口预留。"""

    _bars_by_symbol: Dict[str, List[Bar]]

    def symbols(self) -> Sequence[str]:
        return list(self._bars_by_symbol.keys())

    def get_bars(self, symbol: str) -> List[Bar]:
        return self._bars_by_symbol[symbol]

    def iter_bars(self, symbol: str) -> Iterator[Bar]:
        for b in self._bars_by_symbol[symbol]:
            yield b

    def bar_count(self, symbol: str) -> int:
        return len(self._bars_by_symbol[symbol])

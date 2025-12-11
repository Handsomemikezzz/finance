from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List, Optional


class RollingSma:
    """按顺序更新的 SMA（用于逐 bar 回测）。"""

    def __init__(self, window: int) -> None:
        if window <= 0:
            raise ValueError("window must be > 0")
        self.window = window
        self._buf: Deque[float] = deque(maxlen=window)
        self._sum: float = 0.0

    def update(self, price: float) -> Optional[float]:
        if len(self._buf) == self.window:
            oldest = self._buf[0]
            self._sum -= oldest
        self._buf.append(price)
        self._sum += price

        if len(self._buf) < self.window:
            return None
        return self._sum / self.window


def compute_sma_series(values: Iterable[float], window: int) -> List[Optional[float]]:
    """批量计算 SMA，返回与输入等长、前 window-1 为 None 的序列。"""

    r = RollingSma(window=window)
    out: List[Optional[float]] = []
    for v in values:
        out.append(r.update(float(v)))
    return out

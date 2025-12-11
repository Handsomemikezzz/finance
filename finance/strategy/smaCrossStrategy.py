from __future__ import annotations

from typing import Optional

from finance.core.coreTypes import Bar, Signal
from finance.indicators.smaIndicator import RollingSma
from finance.strategy.strategyBase import StrategyBase


class SmaCrossStrategy(StrategyBase):
    """双均线交叉策略（MVP：目标仓位 0/1）。

    - fast_sma > slow_sma => target_position = 1
    - 否则 => target_position = 0
    - warm-up 期间（slow SMA 未就绪）不输出信号
    - 只有当目标仓位发生变化时才输出信号
    """

    def __init__(self, symbol: str, fast_window: int, slow_window: int) -> None:
        if fast_window <= 0 or slow_window <= 0:
            raise ValueError("fast_window/slow_window must be > 0")
        if fast_window >= slow_window:
            raise ValueError("fast_window must be < slow_window")

        self.symbol = symbol
        self.fast_window = fast_window
        self.slow_window = slow_window

        self._fast = RollingSma(window=fast_window)
        self._slow = RollingSma(window=slow_window)
        self._current_target: float = 0.0

    def on_bar(self, bar: Bar) -> Optional[Signal]:
        if bar.symbol != self.symbol:
            raise ValueError(f"Strategy symbol {self.symbol} got bar {bar.symbol}")

        fast = self._fast.update(bar.close)
        slow = self._slow.update(bar.close)

        if slow is None or fast is None:
            # warm-up
            return None

        target = 1.0 if fast > slow else 0.0
        if target == self._current_target:
            return None

        self._current_target = target
        return Signal(
            dt=bar.dt,
            symbol=bar.symbol,
            target_position=target,
            reason=f"sma_cross fast={self.fast_window} slow={self.slow_window}",
        )

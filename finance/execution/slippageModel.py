from __future__ import annotations

from dataclasses import dataclass

from finance.core.coreTypes import Side


@dataclass(frozen=True)
class SlippageModel:
    """滑点模型：按 bps（万分之一）调整成交价。"""

    bps: float = 0.0

    def apply(self, market_price: float, side: Side) -> tuple[float, float]:
        mp = float(market_price)
        if mp <= 0:
            raise ValueError("market_price must be > 0")

        factor = float(self.bps) / 1e4
        if side == Side.BUY:
            exec_price = mp * (1.0 + factor)
        elif side == Side.SELL:
            exec_price = mp * (1.0 - factor)
        else:
            raise ValueError(f"Unsupported side: {side}")

        return exec_price, abs(exec_price - mp)

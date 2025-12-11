from __future__ import annotations

from dataclasses import dataclass

from finance.core.coreTypes import Fill, RiskRejectedError, Side


@dataclass(frozen=True)
class RiskManager:
    """MVP 风控：仅做最小现金校验。"""

    def validate_fill(self, *, cash_before: float, fill: Fill) -> None:
        if fill.side == Side.BUY:
            required = fill.price * fill.quantity + fill.fee + fill.slippage
            if cash_before + 1e-12 < required:
                raise RiskRejectedError(f"现金不足：cash={cash_before}, required={required}")
        # SELL 不做校验（持仓校验在 Position.apply_fill 做）

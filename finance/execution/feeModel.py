from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeeModel:
    """手续费模型：按成交额比例 + 最低费用（可选）。"""

    rate: float = 0.0  # 例如 0.0003
    min_fee: float = 0.0

    def calc(self, notional: float) -> float:
        fee = float(notional) * float(self.rate)
        if fee < float(self.min_fee):
            fee = float(self.min_fee)
        return fee

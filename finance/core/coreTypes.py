from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"


@dataclass(frozen=True)
class Bar:
    dt: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Signal:
    """策略输出：目标仓位（MVP：0/1）。"""

    dt: datetime
    symbol: str
    target_position: float
    reason: str = ""


@dataclass(frozen=True)
class Order:
    id: str
    dt: datetime
    symbol: str
    side: Side
    quantity: int
    order_type: OrderType = OrderType.MARKET
    reason: str = ""


@dataclass(frozen=True)
class Fill:
    order_id: str
    dt: datetime
    symbol: str
    side: Side
    quantity: int
    price: float
    fee: float
    slippage: float

    @property
    def notional(self) -> float:
        return float(self.quantity) * float(self.price)

    @property
    def total_cost(self) -> float:
        """买入：成本（含费用/滑点）为正；卖出：成本为正但现金流方向由 Portfolio 决定。"""

        return float(self.fee) + float(self.slippage)


@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0

    def market_value(self, price: float) -> float:
        return float(self.quantity) * float(price)

    def apply_fill(self, fill: Fill) -> None:
        """基于 Fill 更新持仓数量与均价（MVP：只支持多头）。"""

        if fill.symbol != self.symbol:
            raise ValueError(f"Fill symbol {fill.symbol} != position symbol {self.symbol}")

        if fill.side == Side.BUY:
            new_qty = self.quantity + fill.quantity
            if new_qty < 0:
                raise ValueError(f"BUY fill would make quantity negative: {self.quantity} + {fill.quantity} = {new_qty}")
            if new_qty == 0:
                self.quantity = 0
                self.avg_price = 0.0
                return

            # 加权平均成本（不把 fee/slippage 计入均价；成本在现金侧体现）
            total_cost = self.avg_price * self.quantity + fill.price * fill.quantity
            self.quantity = new_qty
            self.avg_price = total_cost / new_qty
            return

        if fill.side == Side.SELL:
            new_qty = self.quantity - fill.quantity
            if new_qty < 0:
                raise ValueError("Sell quantity exceeds position")
            self.quantity = new_qty
            if self.quantity == 0:
                self.avg_price = 0.0
            return

        raise ValueError(f"Unsupported side: {fill.side}")


@dataclass(frozen=True)
class EquityPoint:
    dt: datetime
    cash: float
    position_qty: int
    close: float
    position_value: float
    total_equity: float


@dataclass(frozen=True)
class TradeRecord:
    dt: datetime
    symbol: str
    side: Side
    quantity: int
    price: float
    fee: float
    slippage: float
    order_id: str
    reason: str = ""


@dataclass(frozen=True)
class DroppedSignalRecord:
    dt: datetime
    symbol: str
    target_position: float
    reason: str


@dataclass(frozen=True)
class RunSummary:
    symbol: str
    bars: int
    trades: int
    dropped_signals_last_bar: int
    initial_cash: float
    final_equity: float


class FinanceError(Exception):
    """框架内部错误基类。"""


class DataValidationError(FinanceError):
    pass


class RiskRejectedError(FinanceError):
    pass

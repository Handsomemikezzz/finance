from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from finance.core.coreTypes import Bar, EquityPoint, Fill, Order, Position, Side, TradeRecord
from finance.portfolio.riskManager import RiskManager


@dataclass
class Portfolio:
    symbol: str
    initial_cash: float
    risk_manager: RiskManager

    cash: float
    position: Position
    equity_curve: List[EquityPoint]
    trades: List[TradeRecord]

    def __init__(self, symbol: str, initial_cash: float, risk_manager: Optional[RiskManager] = None) -> None:
        self.symbol = symbol
        self.initial_cash = float(initial_cash)
        self.risk_manager = risk_manager or RiskManager()

        self.cash = float(initial_cash)
        self.position = Position(symbol=symbol)
        self.equity_curve = []
        self.trades = []

    @property
    def position_qty(self) -> int:
        return int(self.position.quantity)

    def apply_fill(self, order: Order, fill: Fill) -> None:
        if order.id != fill.order_id:
            raise ValueError("Order/Fill id mismatch")
        if order.symbol != self.symbol or fill.symbol != self.symbol:
            raise ValueError("Symbol mismatch")

        self.risk_manager.validate_fill(cash_before=self.cash, fill=fill)

        notional = float(fill.price) * int(fill.quantity)
        cost = float(fill.fee) + float(fill.slippage)

        if fill.side == Side.BUY:
            self.cash -= notional + cost
        elif fill.side == Side.SELL:
            self.cash += notional - cost
        else:
            raise ValueError(f"Unsupported side: {fill.side}")

        self.position.apply_fill(fill)

        self.trades.append(
            TradeRecord(
                dt=fill.dt,
                symbol=fill.symbol,
                side=fill.side,
                quantity=fill.quantity,
                price=fill.price,
                fee=fill.fee,
                slippage=fill.slippage,
                order_id=order.id,
                reason=order.reason,
            )
        )

    def mark_to_market(self, bar: Bar) -> EquityPoint:
        if bar.symbol != self.symbol:
            raise ValueError("Symbol mismatch")

        position_value = self.position.market_value(bar.close)
        total_equity = float(self.cash) + float(position_value)

        # 运行时校验：资金守恒（允许小误差，比如浮点精度）
        expected_equity = float(self.cash) + float(position_value)
        if abs(total_equity - expected_equity) > 1e-6:
            raise ValueError(
                f"资金不守恒: cash={self.cash}, position_value={position_value}, "
                f"total={total_equity}, expected={expected_equity}, diff={abs(total_equity - expected_equity)}"
            )

        pt = EquityPoint(
            dt=bar.dt,
            cash=float(self.cash),
            position_qty=int(self.position.quantity),
            close=float(bar.close),
            position_value=float(position_value),
            total_equity=float(total_equity),
        )
        self.equity_curve.append(pt)
        return pt

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from finance.core.coreTypes import Bar, Fill, Order, Side, Signal
from finance.execution.feeModel import FeeModel
from finance.execution.slippageModel import SlippageModel


@dataclass
class PendingSignal:
    signal: Signal


class Broker:
    """MVP Broker：

    - 消费 Signal（t 收盘后）并缓存为 pending
    - 在下一根 bar 的 open 时撮合成交
    - 成本（fee/slippage）在这里计算，并写入 Fill
    """

    def __init__(self, fee_model: Optional[FeeModel] = None, slippage_model: Optional[SlippageModel] = None) -> None:
        self._fee_model = fee_model or FeeModel()
        self._slippage_model = slippage_model or SlippageModel()
        self._pending: Optional[PendingSignal] = None

    def queue_signal(self, signal: Signal) -> None:
        self._pending = PendingSignal(signal=signal)

    def has_pending(self) -> bool:
        return self._pending is not None

    def pop_pending(self) -> Optional[Signal]:
        if self._pending is None:
            return None
        s = self._pending.signal
        self._pending = None
        return s

    def execute_open(self, bar: Bar, *, cash: float, position_qty: int) -> tuple[Optional[Order], Optional[Fill]]:
        """在当前 bar.open 处理 pending signal，返回 (Order, Fill)。

        说明：
        - 这里只做“生成订单 + 撮合成交”
        - Portfolio 侧负责据 Fill 更新现金/持仓
        """

        if self._pending is None:
            return None, None

        signal = self._pending.signal
        # 消费掉 pending（无论是否产生成交）
        self._pending = None

        if signal.symbol != bar.symbol:
            raise ValueError(f"Pending signal symbol {signal.symbol} != bar symbol {bar.symbol}")

        target = float(signal.target_position)
        if target <= 0.0:
            # 目标空仓：卖出全部
            if position_qty <= 0:
                return None, None
            side = Side.SELL
            qty = int(position_qty)
            market_price = float(bar.open)
            exec_price, per_share_slip = self._slippage_model.apply(market_price, side=side)
            slippage = per_share_slip * qty
            fee = self._fee_model.calc(exec_price * qty)
            order = Order(
                id=str(uuid.uuid4()),
                dt=bar.dt,
                symbol=bar.symbol,
                side=side,
                quantity=qty,
                reason=signal.reason,
            )
            fill = Fill(
                order_id=order.id,
                dt=bar.dt,
                symbol=bar.symbol,
                side=side,
                quantity=qty,
                price=exec_price,
                fee=fee,
                slippage=slippage,
            )
            return order, fill

        # 目标满仓：尽可能全仓
        # 注意：全仓买入需要考虑手续费和滑点，存在循环依赖（需要知道买多少才能算成本，但算成本又需要知道买多少）
        # 这里用迭代法逼近：先估算数量，再根据实际成本调整
        if target >= 1.0:
            market_price = float(bar.open)
            total_equity_open = float(cash) + float(position_qty) * market_price

            side = Side.BUY
            exec_price, per_share_slip = self._slippage_model.apply(market_price, side=side)

            # 迭代逼近：用总资产估算能买多少（考虑滑点，但先忽略手续费）
            # 第一次估算：假设手续费为 0
            qty_estimate = int(total_equity_open // exec_price)
            if qty_estimate <= position_qty:
                # 不需要买入，检查是否需要卖出
                if qty_estimate < position_qty:
                    # 持仓过多，需要卖出
                    sell_qty = position_qty - qty_estimate
                    sell_exec_price, sell_per_share_slip = self._slippage_model.apply(market_price, side=Side.SELL)
                    sell_slippage = sell_per_share_slip * sell_qty
                    sell_fee = self._fee_model.calc(sell_exec_price * sell_qty)
                    order = Order(
                        id=str(uuid.uuid4()),
                        dt=bar.dt,
                        symbol=bar.symbol,
                        side=Side.SELL,
                        quantity=sell_qty,
                        reason=signal.reason,
                    )
                    fill = Fill(
                        order_id=order.id,
                        dt=bar.dt,
                        symbol=bar.symbol,
                        side=Side.SELL,
                        quantity=sell_qty,
                        price=sell_exec_price,
                        fee=sell_fee,
                        slippage=sell_slippage,
                    )
                    return order, fill
                return None, None

            # 需要买入：迭代调整数量（考虑手续费和滑点）
            # 用总资产（现金+持仓市值）来算能买多少，但实际买入时只用现金
            for _ in range(5):  # 最多迭代 5 次，通常 2-3 次就收敛
                buy_qty = qty_estimate - position_qty
                if buy_qty <= 0:
                    return None, None

                notional = exec_price * buy_qty
                fee = self._fee_model.calc(notional)
                total_cost = notional + fee
                slippage = per_share_slip * buy_qty

                # 检查：买入成本不能超过可用现金
                if total_cost <= cash:
                    # 能买得起，生成订单
                    order = Order(
                        id=str(uuid.uuid4()),
                        dt=bar.dt,
                        symbol=bar.symbol,
                        side=side,
                        quantity=buy_qty,
                        reason=signal.reason,
                    )
                    fill = Fill(
                        order_id=order.id,
                        dt=bar.dt,
                        symbol=bar.symbol,
                        side=side,
                        quantity=buy_qty,
                        price=exec_price,
                        fee=fee,
                        slippage=slippage,
                    )
                    return order, fill

                # 买不起，减少数量（用现金上限反推，保守估计）
                # 简化：假设手续费率是固定的，用 cash / (exec_price * (1 + fee_rate)) 估算
                if self._fee_model.rate > 0:
                    qty_estimate = int(cash // (exec_price * (1.0 + self._fee_model.rate)))
                else:
                    # 如果手续费率是 0，只用 exec_price 算
                    qty_estimate = int(cash // exec_price)
                # 再减去一点，给 min_fee 留空间
                if self._fee_model.min_fee > 0:
                    qty_estimate = max(0, qty_estimate - 1)
                if qty_estimate <= position_qty:
                    # 现金不够，无法买入
                    return None, None

            # 迭代未收敛，用最保守估计（只用现金，不考虑持仓市值）
            # 这种情况理论上不应该发生，但作为兜底
            buy_qty = max(0, int((cash - self._fee_model.min_fee) // exec_price) - 1)
            if buy_qty <= 0:
                return None, None
            notional = exec_price * buy_qty
            fee = self._fee_model.calc(notional)
            if notional + fee > cash:
                return None, None

            slippage = per_share_slip * buy_qty
            order = Order(
                id=str(uuid.uuid4()),
                dt=bar.dt,
                symbol=bar.symbol,
                side=side,
                quantity=buy_qty,
                reason=signal.reason,
            )
            fill = Fill(
                order_id=order.id,
                dt=bar.dt,
                symbol=bar.symbol,
                side=side,
                quantity=buy_qty,
                price=exec_price,
                fee=fee,
                slippage=slippage,
            )
            return order, fill

            # desired_qty < position_qty: 卖出差额
            side = Side.SELL
            sell_qty = position_qty - desired_qty
            exec_price, per_share_slip = self._slippage_model.apply(market_price, side=side)
            slippage = per_share_slip * sell_qty
            fee = self._fee_model.calc(exec_price * sell_qty)
            order = Order(
                id=str(uuid.uuid4()),
                dt=bar.dt,
                symbol=bar.symbol,
                side=side,
                quantity=sell_qty,
                reason=signal.reason,
            )
            fill = Fill(
                order_id=order.id,
                dt=bar.dt,
                symbol=bar.symbol,
                side=side,
                quantity=sell_qty,
                price=exec_price,
                fee=fee,
                slippage=slippage,
            )
            return order, fill

        raise ValueError("MVP 仅支持 target_position 为 0 或 1")

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from finance.core.coreTypes import DroppedSignalRecord, EquityPoint, RunSummary, TradeRecord
from finance.data.dataHandler import DataHandler
from finance.execution.broker import Broker
from finance.portfolio.portfolio import Portfolio
from finance.strategy.strategyBase import StrategyBase


@dataclass(frozen=True)
class ResultBundle:
    symbol: str
    equity_curve: List[EquityPoint]
    trades: List[TradeRecord]
    dropped_signals: List[DroppedSignalRecord]
    run_summary: RunSummary
    metrics: Optional[dict] = None


class BacktestEngine:
    """MVP 回测引擎（单标的）：

    顺序（对每个 bar）：
    1) 若存在 pending signal，则在当日 open 撮合成交并更新组合
    2) 当日 close 盯市，记录 equity
    3) 基于当日 close 生成 signal，放入 pending（用于下一日 open）

    边界：最后一根 bar 产生的 signal 会被丢弃并记录。
    """

    def __init__(
        self,
        *,
        symbol: str,
        data: DataHandler,
        strategy: StrategyBase,
        broker: Broker,
        portfolio: Portfolio,
    ) -> None:
        self.symbol = symbol
        self.data = data
        self.strategy = strategy
        self.broker = broker
        self.portfolio = portfolio

    def run(self) -> ResultBundle:
        bars = self.data.get_bars(self.symbol)
        dropped: List[DroppedSignalRecord] = []
        dropped_last_bar = 0

        for i, bar in enumerate(bars):
            # 1) open 撮合（使用上一交易日生成的 pending signal）
            order, fill = self.broker.execute_open(
                bar,
                cash=self.portfolio.cash,
                position_qty=self.portfolio.position_qty,
            )
            if order is not None and fill is not None:
                self.portfolio.apply_fill(order, fill)

            # 2) close 盯市（无论是否有交易，都记录 equity 点）
            self.portfolio.mark_to_market(bar)

            # 3) close 后生成 signal
            signal = self.strategy.on_bar(bar)
            if signal is None:
                continue

            if i == len(bars) - 1:
                dropped_last_bar += 1
                dropped.append(
                    DroppedSignalRecord(
                        dt=signal.dt,
                        symbol=signal.symbol,
                        target_position=signal.target_position,
                        reason="last_bar_no_next_open",
                    )
                )
                continue

            self.broker.queue_signal(signal)

        final_equity = self.portfolio.equity_curve[-1].total_equity if self.portfolio.equity_curve else self.portfolio.initial_cash
        summary = RunSummary(
            symbol=self.symbol,
            bars=len(bars),
            trades=len(self.portfolio.trades),
            dropped_signals_last_bar=dropped_last_bar,
            initial_cash=self.portfolio.initial_cash,
            final_equity=float(final_equity),
        )

        return ResultBundle(
            symbol=self.symbol,
            equity_curve=list(self.portfolio.equity_curve),
            trades=list(self.portfolio.trades),
            dropped_signals=dropped,
            run_summary=summary,
            metrics=None,
        )

import unittest
from datetime import datetime, timedelta

from finance.backtest.backtestEngine import BacktestEngine
from finance.data.dataHandler import DataHandler
from finance.core.coreTypes import Bar
from finance.execution.broker import Broker
from finance.portfolio.portfolio import Portfolio
from finance.strategy.smaCrossStrategy import SmaCrossStrategy


class TestBacktestEngineMvp(unittest.TestCase):
    def test_equity_length_equals_bars(self):
        symbol = "TEST"
        base = datetime(2025, 1, 1)
        bars = []
        for i, c in enumerate([1, 1, 1, 2, 3, 2, 1]):
            dt = base + timedelta(days=i)
            bars.append(Bar(dt=dt, symbol=symbol, open=c, high=c, low=c, close=c, volume=100))

        data = DataHandler(_bars_by_symbol={symbol: bars})
        strategy = SmaCrossStrategy(symbol=symbol, fast_window=2, slow_window=3)
        broker = Broker()
        portfolio = Portfolio(symbol=symbol, initial_cash=1000.0)

        engine = BacktestEngine(symbol=symbol, data=data, strategy=strategy, broker=broker, portfolio=portfolio)
        result = engine.run()

        self.assertEqual(len(result.equity_curve), len(bars))

import unittest
from datetime import datetime

from finance.core.coreTypes import Bar, Fill, Order, Side
from finance.portfolio.portfolio import Portfolio


class TestPortfolioAccounting(unittest.TestCase):
    def test_cash_position_conservation(self):
        p = Portfolio(symbol="TEST", initial_cash=1000.0)

        order = Order(id="o1", dt=datetime(2025, 1, 2), symbol="TEST", side=Side.BUY, quantity=10, reason="")
        fill = Fill(order_id="o1", dt=datetime(2025, 1, 2), symbol="TEST", side=Side.BUY, quantity=10, price=10.0, fee=0.0, slippage=0.0)
        p.apply_fill(order, fill)

        bar = Bar(dt=datetime(2025, 1, 2), symbol="TEST", open=10.0, high=10.0, low=10.0, close=10.0, volume=0.0)
        eq = p.mark_to_market(bar)

        self.assertAlmostEqual(eq.cash + eq.position_value, eq.total_equity)
        self.assertAlmostEqual(eq.total_equity, 1000.0)

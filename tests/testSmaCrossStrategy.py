import unittest
from datetime import datetime, timedelta

from finance.core.coreTypes import Bar
from finance.strategy.smaCrossStrategy import SmaCrossStrategy


class TestSmaCrossStrategy(unittest.TestCase):
    def test_emits_signal_on_target_change(self):
        s = SmaCrossStrategy(symbol="TEST", fast_window=2, slow_window=3)

        base = datetime(2025, 1, 1)
        closes = [1, 1, 1, 3, 3, 1]
        signals = []
        for i, c in enumerate(closes):
            dt = base + timedelta(days=i)
            bar = Bar(dt=dt, symbol="TEST", open=c, high=c, low=c, close=c, volume=100)
            sig = s.on_bar(bar)
            if sig is not None:
                signals.append(sig)

        # 价格在第 4 根开始上升，fast>slow 后应出一次 target=1
        self.assertTrue(any(sig.target_position == 1.0 for sig in signals))
        # 最后回落后应出一次 target=0
        self.assertTrue(any(sig.target_position == 0.0 for sig in signals))

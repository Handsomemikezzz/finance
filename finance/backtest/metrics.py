from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from finance.core.coreTypes import EquityPoint


@dataclass(frozen=True)
class MetricsConfig:
    trading_days_per_year: int = 252
    risk_free_rate: float = 0.0


class Metrics:
    @staticmethod
    def compute(equity_curve: List[EquityPoint], config: Optional[MetricsConfig] = None) -> Dict[str, float | int]:
        cfg = config or MetricsConfig()
        if not equity_curve:
            return {
                "bars": 0,
                "cumulative_return": 0.0,
                "annualized_return": 0.0,
                "max_drawdown": 0.0,
                "sharpe": 0.0,
            }

        df = pd.DataFrame(
            {
                "dt": [p.dt for p in equity_curve],
                "equity": [p.total_equity for p in equity_curve],
            }
        )
        df = df.sort_values("dt").reset_index(drop=True)

        equity = df["equity"].astype(float)
        rets = equity.pct_change().fillna(0.0)

        cumulative_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0) if equity.iloc[0] != 0 else 0.0

        n = len(equity)
        years = n / float(cfg.trading_days_per_year)
        if years <= 0 or equity.iloc[0] <= 0:
            annualized_return = 0.0
        else:
            annualized_return = float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0)

        # max drawdown
        running_max = equity.cummax()
        dd = equity / running_max - 1.0
        max_drawdown = float(dd.min())

        # sharpe（MVP：rf=0，按日收益年化）
        rf_daily = float(cfg.risk_free_rate) / float(cfg.trading_days_per_year)
        excess = rets - rf_daily
        vol = float(excess.std(ddof=0))
        if vol == 0.0:
            sharpe = 0.0
        else:
            sharpe = float(np.sqrt(cfg.trading_days_per_year) * (excess.mean() / vol))

        return {
            "bars": int(n),
            "cumulative_return": cumulative_return,
            "annualized_return": annualized_return,
            "max_drawdown": max_drawdown,
            "sharpe": sharpe,
        }

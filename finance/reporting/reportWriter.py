from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Any, Dict, Optional

import pandas as pd

from finance.backtest.backtestEngine import ResultBundle


class ReportWriter:
    def __init__(self, output_root: str = "outputs") -> None:
        self.output_root = output_root

    def write(self, result: ResultBundle, *, run_id: str, run_config: Optional[Dict[str, Any]] = None) -> str:
        out_dir = os.path.join(self.output_root, run_id)
        os.makedirs(out_dir, exist_ok=True)

        equity_df = pd.DataFrame([
            {
                "dt": p.dt,
                "cash": p.cash,
                "position_qty": p.position_qty,
                "close": p.close,
                "position_value": p.position_value,
                "total_equity": p.total_equity,
            }
            for p in result.equity_curve
        ])
        equity_df.to_csv(os.path.join(out_dir, "equity_curve.csv"), index=False)

        trades_df = pd.DataFrame([
            {
                "dt": t.dt,
                "symbol": t.symbol,
                "side": t.side,
                "quantity": t.quantity,
                "price": t.price,
                "fee": t.fee,
                "slippage": t.slippage,
                "order_id": t.order_id,
                "reason": t.reason,
            }
            for t in result.trades
        ])
        trades_df.to_csv(os.path.join(out_dir, "trades.csv"), index=False)

        metrics = result.metrics or {}
        payload = {
            "symbol": result.symbol,
            "run_summary": asdict(result.run_summary),
            "metrics": metrics,
        }
        with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        if result.dropped_signals:
            dropped_df = pd.DataFrame([
                {
                    "dt": d.dt,
                    "symbol": d.symbol,
                    "target_position": d.target_position,
                    "reason": d.reason,
                }
                for d in result.dropped_signals
            ])
            dropped_df.to_csv(os.path.join(out_dir, "dropped_signals.csv"), index=False)

        if run_config is not None:
            with open(os.path.join(out_dir, "run_config.json"), "w", encoding="utf-8") as f:
                json.dump(run_config, f, ensure_ascii=False, indent=2)

        return out_dir

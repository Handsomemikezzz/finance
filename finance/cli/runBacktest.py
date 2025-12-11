from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime

from finance.backtest.backtestEngine import BacktestEngine
from finance.backtest.metrics import Metrics, MetricsConfig
from finance.config.defaultConfig import DEFAULT_CONFIG
from finance.data.csvDataSource import CsvDataSource
from finance.data.dataHandler import DataHandler
from finance.execution.broker import Broker
from finance.execution.feeModel import FeeModel
from finance.execution.slippageModel import SlippageModel
from finance.portfolio.portfolio import Portfolio
from finance.reporting.reportWriter import ReportWriter
from finance.strategy.smaCrossStrategy import SmaCrossStrategy


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="日线回测 MVP：CSV + SMA Cross")

    p.add_argument("--symbol", required=True, help="标的代码（用于输出与记录）")
    p.add_argument("--csv-path", default=None, help="CSV 文件路径（优先级高于 data_dir）")
    p.add_argument("--data-dir", default=DEFAULT_CONFIG["data_dir"], help="数据目录（默认 data/raw）")

    p.add_argument("--output-root", default=DEFAULT_CONFIG["output_root"], help="输出根目录（默认 outputs）")
    p.add_argument("--run-id", default=None, help="本次运行ID（默认使用时间戳）")

    p.add_argument("--initial-cash", type=float, default=DEFAULT_CONFIG["initial_cash"], help="初始资金")
    p.add_argument("--fast", type=int, default=DEFAULT_CONFIG["fast_window"], help="SMA fast window")
    p.add_argument("--slow", type=int, default=DEFAULT_CONFIG["slow_window"], help="SMA slow window")

    p.add_argument("--fee-rate", type=float, default=DEFAULT_CONFIG["fee_rate"], help="手续费率（成交额比例）")
    p.add_argument("--fee-min", type=float, default=DEFAULT_CONFIG["fee_min"], help="最低手续费")
    p.add_argument("--slippage-bps", type=float, default=DEFAULT_CONFIG["slippage_bps"], help="滑点（bps）")

    p.add_argument("--trading-days", type=int, default=DEFAULT_CONFIG["trading_days_per_year"], help="年交易日数")
    p.add_argument("--risk-free", type=float, default=DEFAULT_CONFIG["risk_free_rate"], help="无风险利率（年化）")

    p.add_argument("--log-level", default="INFO", help="日志级别：DEBUG/INFO/WARNING/ERROR")

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger("runBacktest")

    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = args.csv_path
    if not csv_path:
        csv_path = os.path.join(args.data_dir, f"{args.symbol}.csv")

    log.info("symbol=%s csv=%s", args.symbol, csv_path)

    # 1) data
    ds = CsvDataSource()
    load = ds.load(symbol=args.symbol, csv_path=csv_path)
    data = DataHandler(_bars_by_symbol={args.symbol: load.bars})
    log.info("loaded bars=%d range=%s..%s", len(load.bars), load.bars[0].dt.date(), load.bars[-1].dt.date())

    # 2) components
    strategy = SmaCrossStrategy(symbol=args.symbol, fast_window=args.fast, slow_window=args.slow)
    broker = Broker(
        fee_model=FeeModel(rate=args.fee_rate, min_fee=args.fee_min),
        slippage_model=SlippageModel(bps=args.slippage_bps),
    )
    portfolio = Portfolio(symbol=args.symbol, initial_cash=args.initial_cash)

    # 3) engine
    engine = BacktestEngine(symbol=args.symbol, data=data, strategy=strategy, broker=broker, portfolio=portfolio)
    result = engine.run()

    # 4) metrics
    metrics = Metrics.compute(
        result.equity_curve,
        config=MetricsConfig(trading_days_per_year=args.trading_days, risk_free_rate=args.risk_free),
    )
    result = type(result)(
        symbol=result.symbol,
        equity_curve=result.equity_curve,
        trades=result.trades,
        dropped_signals=result.dropped_signals,
        run_summary=result.run_summary,
        metrics=metrics,
    )

    # 5) report
    writer = ReportWriter(output_root=args.output_root)
    out_dir = writer.write(
        result,
        run_id=run_id,
        run_config={
            "symbol": args.symbol,
            "csv_path": csv_path,
            "initial_cash": args.initial_cash,
            "fast": args.fast,
            "slow": args.slow,
            "fee_rate": args.fee_rate,
            "fee_min": args.fee_min,
            "slippage_bps": args.slippage_bps,
            "trading_days": args.trading_days,
            "risk_free": args.risk_free,
        },
    )

    log.info(
        "done out=%s trades=%d final_equity=%.2f cumret=%.4f maxdd=%.4f sharpe=%.4f dropped_last_bar=%d",
        out_dir,
        result.run_summary.trades,
        result.run_summary.final_equity,
        metrics.get("cumulative_return", 0.0),
        metrics.get("max_drawdown", 0.0),
        metrics.get("sharpe", 0.0),
        result.run_summary.dropped_signals_last_bar,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

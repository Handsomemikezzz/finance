from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from finance.core.coreTypes import Bar, DataValidationError


DEFAULT_COLUMN_MAP: Dict[str, str] = {
    "date": "date",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
}


@dataclass(frozen=True)
class CsvLoadResult:
    symbol: str
    bars: List[Bar]
    df: pd.DataFrame


class CsvDataSource:
    """读取单标的 CSV 并输出 Bar 序列（按日期升序）。"""

    def __init__(
        self,
        column_map: Optional[Dict[str, str]] = None,
        date_format: str = "%Y-%m-%d",
        allow_volume_missing_as_zero: bool = True,
        enforce_unique_date: bool = True,
    ) -> None:
        self._column_map = column_map or dict(DEFAULT_COLUMN_MAP)
        self._date_format = date_format
        self._allow_volume_missing_as_zero = allow_volume_missing_as_zero
        self._enforce_unique_date = enforce_unique_date

    def load(self, symbol: str, csv_path: str) -> CsvLoadResult:
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            raise DataValidationError(f"读取CSV失败: {csv_path}: {e}") from e

        df = self._normalize_columns(df)
        df = self._validate_and_clean(df)

        bars: List[Bar] = []
        for row in df.itertuples(index=False):
            bars.append(
                Bar(
                    dt=row.dt.to_pydatetime(),
                    symbol=symbol,
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.close),
                    volume=float(row.volume),
                )
            )

        return CsvLoadResult(symbol=symbol, bars=bars, df=df)

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {src: dst for src, dst in self._column_map.items() if src in df.columns}
        df = df.rename(columns=rename_map)
        return df

    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        required = ["date", "open", "high", "low", "close", "volume"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise DataValidationError(f"CSV缺少必需列: {missing}")

        # date
        try:
            dt = pd.to_datetime(df["date"], format=self._date_format)
        except Exception as e:
            raise DataValidationError(f"date解析失败（期望格式 {self._date_format}）: {e}") from e

        df = df.copy()
        df["dt"] = dt

        # 基础缺失值
        price_cols = ["open", "high", "low", "close"]
        if df[price_cols].isna().any().any():
            raise DataValidationError("open/high/low/close 存在缺失值")

        if df["volume"].isna().any():
            if self._allow_volume_missing_as_zero:
                df["volume"] = df["volume"].fillna(0)
            else:
                raise DataValidationError("volume 存在缺失值")

        # 排序
        df = df.sort_values("dt", ascending=True, kind="mergesort").reset_index(drop=True)

        # 去重
        if self._enforce_unique_date:
            dup = df["dt"].duplicated(keep=False)
            if bool(dup.any()):
                dts = df.loc[dup, "dt"].dt.strftime(self._date_format).tolist()
                raise DataValidationError(f"存在重复日期（MVP默认不允许）: {dts[:10]}{'...' if len(dts) > 10 else ''}")

        # 合法性：价格必须为正
        for c in price_cols:
            if (df[c] <= 0).any():
                bad = df.loc[df[c] <= 0, ["dt", c]].head(5)
                raise DataValidationError(f"价格列 {c} 存在非正值，示例: {bad.to_dict(orient='records')}")

        if (df["volume"] < 0).any():
            bad = df.loc[df["volume"] < 0, ["dt", "volume"]].head(5)
            raise DataValidationError(f"volume 存在负值，示例: {bad.to_dict(orient='records')}")

        # 可选的高低价一致性（先做轻量校验）
        if (df["high"] < df[["open", "close", "low"]].max(axis=1)).any():
            raise DataValidationError("high 小于 open/close/low 中的最大值（数据不一致）")
        if (df["low"] > df[["open", "close", "high"]].min(axis=1)).any():
            raise DataValidationError("low 大于 open/close/high 中的最小值（数据不一致）")

        # 仅保留需要的列
        df = df[["dt", "open", "high", "low", "close", "volume"]]
        return df

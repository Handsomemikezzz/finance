# 代码 Review 报告

## 总体评价

整体架构清晰，模块职责分离合理，符合 MVP 目标。但发现几个**需要修复的问题**和**可以改进的点**。

---

## 🔴 必须修复的问题

### 1. **Broker 全仓买入计算存在循环依赖（严重）**

**位置**：`finance/execution/broker.py` 第 95-96 行

**问题**：
```python
total_equity_open = float(cash) + float(position_qty) * market_price
desired_qty = int(total_equity_open // market_price)  # ❌ 问题在这里
```

**解释**：
- 你想用“总资产 ÷ 单价”来算能买多少股，但**实际买入时还要付手续费和滑点**
- 这导致：你算出的 `desired_qty` 需要的总成本 > 总资产，实际买不到这么多
- 例如：总资产 100 万，单价 12，手续费率 0.0003，滑点 5 bps
  - 按你的算法：`desired_qty = 1000000 // 12 = 83333`
  - 但实际买 83333 股需要：`83333 * 12 * (1 + 0.0003 + 0.0005) ≈ 1000500`（超过 100 万）

**修复建议**：
```python
# 方案1：迭代逼近（简单但不够精确）
market_price = float(bar.open)
exec_price, _ = self._slippage_model.apply(market_price, Side.BUY)
total_equity = float(cash) + float(position_qty) * market_price

# 先估算（不考虑手续费）
qty_estimate = int(total_equity // exec_price)
if qty_estimate <= position_qty:
    return None, None

# 迭代：用估算数量算手续费，再反推能买多少
for _ in range(3):  # 通常 2-3 次就收敛
    notional = exec_price * qty_estimate
    fee = self._fee_model.calc(notional)
    total_cost = notional + fee
    if total_cost <= total_equity:
        break
    qty_estimate = int((total_equity - fee) // exec_price)
    if qty_estimate <= position_qty:
        return None, None

buy_qty = qty_estimate - position_qty
```

**或者方案2（更精确）**：用二分法或解析解（如果手续费是线性的）。

---

### 2. **Portfolio 卖出时的成本处理可能有歧义**

**位置**：`finance/portfolio/portfolio.py` 第 49 行

**问题**：
```python
elif fill.side == Side.SELL:
    self.cash += notional - cost  # cost = fee + slippage
```

**解释**：
- 卖出时，`slippage` 在 `SlippageModel` 里是“对卖方不利的滑点”（成交价更低）
- 但 `Fill.slippage` 字段存储的是**绝对值**（`abs(exec_price - market_price) * qty`）
- 所以这里 `notional - cost` 是对的（收入减去所有成本）

**但需要确认**：`SlippageModel.apply()` 返回的 `slippage` 是否已经是“总滑点成本”（`per_share_slip * qty`）？

查看 `broker.py` 第 109 行：`slippage = per_share_slip * buy_qty`，所以 `Fill.slippage` 已经是总成本，这里处理是对的。

**建议**：加注释说明，避免后续维护时误解。

---

### 3. **Metrics 年化收益计算可能有精度问题**

**位置**：`finance/backtest/metrics.py` 第 49 行

**问题**：
```python
annualized_return = float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0)
```

**解释**：
- 这个公式在数学上是对的：`(终值/初值)^(1/年数) - 1`
- 但如果 `years` 很小（比如只有 7 天），`1/years ≈ 0.0278`，可能导致精度问题
- 另外，如果 `equity.iloc[0] == 0` 已经在前面检查了，这里应该安全

**建议**：对于极短期回测（< 30 天），可以考虑直接返回累计收益，不年化。

---

## ⚠️ 需要改进的点

### 4. **Broker 全仓逻辑：应该用“可用资金”而非“总资产”**

**位置**：`finance/execution/broker.py` 第 95 行

**问题**：
```python
total_equity_open = float(cash) + float(position_qty) * market_price
```

**解释**：
- 当前逻辑：如果要全仓，会先卖出部分持仓（如果持仓 > 目标），再用全部资产买入
- 但更常见的“全仓”语义是：**用现金 + 卖出多余持仓后的资金，全部买入**
- 你的实现会先算“总资产能买多少”，如果持仓多了就卖，少了就买，这是对的

**但有个边界情况**：如果 `desired_qty < position_qty`，你会在第 131-155 行卖出。但这里没有考虑“卖出后得到的现金 + 原有现金，能否买到 `desired_qty`”？实际上，如果目标是全仓，卖出后应该用全部资金再买入，而不是只买到 `desired_qty`。

**建议**：明确“全仓”的语义：
- 选项 A：目标仓位 = 1.0 时，用全部可用资金买入（包括卖出多余持仓后的现金）
- 选项 B：目标仓位 = 1.0 时，持仓市值 / 总资产 = 1.0（允许有现金余额，因为无法整除）

当前实现更像选项 B，但计算 `desired_qty` 时用的是“总资产能买多少”，这会导致最终持仓市值 < 总资产（因为手续费/滑点）。

---

### 5. **Position.apply_fill 的边界保护不够**

**位置**：`finance/core/coreTypes.py` 第 89-93 行

**问题**：
```python
if new_qty <= 0:
    # 理论上不会出现（BUY 不可能让 qty 变小），但这里做个保护
    self.quantity = new_qty
    self.avg_price = 0.0 if new_qty == 0 else self.avg_price
    return
```

**解释**：
- 如果 `new_qty < 0`，说明数据有问题（BUY 不可能让持仓变负），应该抛异常而不是静默处理
- 当前实现会允许 `quantity` 变成负数，这会导致后续计算错误

**建议**：
```python
if new_qty < 0:
    raise ValueError(f"BUY fill would make quantity negative: {self.quantity} + {fill.quantity} = {new_qty}")
if new_qty == 0:
    self.quantity = 0
    self.avg_price = 0.0
    return
```

---

### 6. **缺少“资金守恒”的运行时校验**

**位置**：`finance/portfolio/portfolio.py` `mark_to_market()` 方法

**问题**：
- 当前只在测试里验证了资金守恒，但生产代码里没有运行时检查
- 如果出现 bug（比如手续费计算错误），可能静默产生错误结果

**建议**：
```python
def mark_to_market(self, bar: Bar) -> EquityPoint:
    # ... 现有代码 ...
    
    # 运行时校验（允许小误差，比如浮点精度）
    expected_equity = float(self.cash) + float(position_value)
    if abs(total_equity - expected_equity) > 1e-6:
        raise ValueError(f"资金不守恒: cash={self.cash}, position_value={position_value}, total={total_equity}, expected={expected_equity}")
    
    return pt
```

---

### 7. **Metrics 的 Sharpe 计算：ddof 参数**

**位置**：`finance/backtest/metrics.py` 第 59 行

**问题**：
```python
vol = float(excess.std(ddof=0))  # 总体标准差
```

**解释**：
- `ddof=0` 是总体标准差（除以 n），`ddof=1` 是样本标准差（除以 n-1）
- 对于回测，通常用样本标准差更合理（因为收益序列是样本）
- 但这不是 bug，只是统计口径的选择

**建议**：如果想更符合业界习惯，可以改成 `ddof=1`，或者在配置里可选。

---

## ✅ 做得好的地方

1. **时间序清晰**：t 收盘算指标 → t+1 开盘成交 → t 收盘盯市，逻辑正确
2. **成本归属明确**：手续费/滑点都在 Broker 计算，Portfolio 只消费 Fill，职责分离好
3. **边界处理**：最后一根 bar 的信号丢弃、warm-up 期间不出信号，都处理了
4. **数据结构**：用 dataclass 和 frozen，不可变性好，减少 bug
5. **测试覆盖**：至少覆盖了核心逻辑（CSV解析、SMA、策略、资金守恒）

---

## 📝 建议补充的文档/注释

1. **Broker.execute_open()**：在方法开头加注释，说明“全仓”的语义（是选项 A 还是 B）
2. **Portfolio.apply_fill()**：说明卖出时 `notional - cost` 的含义（收入 - 所有成本）
3. **SlippageModel**：说明 `slippage` 返回的是“对交易方不利的绝对成本”

---

## 🎯 优先级建议

1. **P0（必须修复）**：问题 1（Broker 全仓买入的循环依赖）
2. **P1（强烈建议）**：问题 5（Position 边界保护）、问题 6（资金守恒运行时校验）
3. **P2（可选改进）**：问题 4（全仓语义明确）、问题 7（Sharpe 的 ddof）

---

## 总结

整体代码质量不错，架构清晰。**最严重的问题是 Broker 的全仓买入计算**，在手续费/滑点不为 0 时会算错。其他问题主要是边界保护和文档完善。

建议先修复问题 1，然后补充运行时校验，再逐步完善其他点。

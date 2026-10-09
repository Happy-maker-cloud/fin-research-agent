from pathlib import Path

from fin_agent.backtest.momentum import demo_backtest


def main() -> None:
    result = demo_backtest()
    curves = result["curves"]

    lines = [
        "# Day11 动量因子回测报告",
        "",
        "## 回测设置",
        "",
        "- 数据：固定随机种子的模拟行情，6 个模拟资产。",
        f"- 区间：{curves[0]['date']} 至 {curves[-1]['date']}。",
        "- 因子：20 日价格动量。",
        "- 分组：低、中、高动量三组，组内等权，每日调仓。",
        "- 时序：t-2 收盘信号，t-1 收盘调仓，赚取 t-1 至 t 收益。",
        "- 成本：买入和卖出成交金额各按 0.1% 计费。",
        "- 基准：同一资产池初始等权买入并持有，包含初始买入费用。",
        "- 不计结束清仓费用；Sharpe 使用 252 日年化，无风险利率为 0。",
        "",
        "## 结果",
        "",
        "| 组合 | 累计收益 | 最大回撤 | Sharpe |",
        "| --- | --- | --- | --- |",
    ]

    for name, metrics in result["summary"].items():
        sharpe = metrics["sharpe"]
        sharpe_text = "N/A" if sharpe is None else f"{sharpe:.2f}"

        lines.append(
            f"| {name} "
            f"| {metrics['total_return']:.2%} "
            f"| {metrics['max_drawdown']:.2%} "
            f"| {sharpe_text} |"
        )

    excess = (
        result["summary"]["high"]["total_return"] - result["summary"]["benchmark"]["total_return"]
    )

    lines.extend(
        [
            "",
            "## 观察",
            "",
            f"- 高动量组合与基准的累计收益差：{excess:.2%}。",
            "- 此处为累计收益之差，不是年化超额收益或 Alpha。",
            "",
            "## 局限",
            "",
            "- 模拟数据只能验证程序流程，不能证明因子有效。",
            "- 工作日索引不是真实交易日历。",
            "- 未模拟停牌、涨跌停、滑点及无法成交。",
            "- 真实回测需使用一致复权口径及当时可获得的数据和股票池。",
            "",
            "## 下一步",
            "",
            "- 替换为经过清洗的真实多股票行情。",
            "- 比较 5、20、60 日动量，并保留独立验证区间。",
            "- 比较不同交易成本下的结果。",
        ]
    )

    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "reports" / "day11_momentum_report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")

    print(f"报告已生成：{output}")


if __name__ == "__main__":
    main()

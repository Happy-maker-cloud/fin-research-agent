"use client";

import { useEffect, useState } from "react";
import {
    CartesianGrid,
    Legend,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

type CurvePoint = {
  date: string;
  low: number;
  middle: number;
  high: number;
  benchmark: number;
  high_drawdown: number;
  benchmark_drawdown: number;
};

type Metrics = {
  total_return: number;
  max_drawdown: number;
  sharpe: number | null;
};

type BacktestResult = {
  data_source: string;
  lookback: number;
  fee_rate: number;
  summary: Record<string, Metrics>;
  curves: CurvePoint[];
};

function percent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

export default function BacktestPanel() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        const baseUrl =
          process.env.NEXT_PUBLIC_API_BASE_URL ??
          "http://127.0.0.1:8000";

        const response = await fetch(
          `${baseUrl}/api/v1/backtest/demo`,
          { signal: controller.signal },
        );

        if (!response.ok) {
          throw new Error(`回测请求失败：HTTP ${response.status}`);
        }

        const data: BacktestResult = await response.json();
        setResult(data);
      } catch (err) {
        if (controller.signal.aborted) return;

        setError(
          err instanceof Error ? err.message : "回测加载失败",
        );
      }
    }

    void load();

    return () => controller.abort();
  }, []);

  if (error) {
    return <p role="alert" className="text-red-600">{error}</p>;
  }

  if (!result) {
    return <p>正在加载回测结果……</p>;
  }

  const drawdowns = result.curves.map((point) => ({
    date: point.date,
    high: point.high_drawdown * 100,
    benchmark: point.benchmark_drawdown * 100,
  }));

  return (
    <section className="w-full min-w-0 space-y-6 rounded-xl border p-4">
      <div>
        <h2 className="text-xl font-semibold">动量因子回测</h2>
        <p className="text-sm text-gray-500">
          模拟数据 · {result.lookback} 日动量 ·
          成交费用 {percent(result.fee_rate)}
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr>
              <th className="p-2">组合</th>
              <th className="p-2">累计收益</th>
              <th className="p-2">最大回撤</th>
              <th className="p-2">Sharpe</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(result.summary).map(([name, metrics]) => (
              <tr key={name} className="border-t">
                <td className="p-2">{name}</td>
                <td className="p-2">{percent(metrics.total_return)}</td>
                <td className="p-2">{percent(metrics.max_drawdown)}</td>
                <td className="p-2">
                  {metrics.sharpe?.toFixed(2) ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h3 className="mb-2 font-medium">分组净值与基准</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={result.curves}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" minTickGap={40} />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Legend />
            <Line dataKey="low" name="低动量" stroke="#94a3b8" dot={false} />
            <Line dataKey="middle" name="中动量" stroke="#f59e0b" dot={false} />
            <Line dataKey="high" name="高动量" stroke="#2563eb" dot={false} />
            <Line
              dataKey="benchmark"
              name="基准"
              stroke="#16a34a"
              dot={false}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3 className="mb-2 font-medium">回撤幅度（%）</h3>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={drawdowns}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" minTickGap={40} />
            <YAxis unit="%" />
            <Tooltip />
            <Legend />
            <Line dataKey="high" name="高动量回撤" stroke="#dc2626" dot={false} />
            <Line
              dataKey="benchmark"
              name="基准回撤"
              stroke="#16a34a"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
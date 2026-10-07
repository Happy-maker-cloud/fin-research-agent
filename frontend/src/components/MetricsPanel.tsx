"use client";

import { useEffect, useState } from "react";

interface Metrics {
  total_return: number;
  annualized_volatility: number;
  sharpe: number | null;
  max_drawdown: number;
  ic: number | null;
  rank_ic: number | null;
}

interface MetricCardProps {
  label: string;
  value: number | null;
  percentage?: boolean;
}

function MetricCard({
  label,
  value,
  percentage = false,
}: MetricCardProps) {
  const text =
    value === null
      ? "无法计算"
      : percentage
        ? `${(value * 100).toFixed(2)}%`
        : value.toFixed(3);

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{text}</p>
    </div>
  );
}

export default function MetricsPanel() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadMetrics() {
      try {
        const baseUrl =
          process.env.NEXT_PUBLIC_API_BASE_URL ??
          "http://127.0.0.1:8000";

        const response = await fetch(
          `${baseUrl}/api/v1/metrics/demo`,
          { signal: controller.signal },
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = (await response.json()) as Metrics;
        setMetrics(data);
      } catch (requestError: unknown) {
        if (controller.signal.aborted) return;

        setError(
          requestError instanceof Error
            ? requestError.message
            : "请求失败",
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadMetrics();

    return () => controller.abort();
  }, []);

  if (loading) return <p>正在加载指标……</p>;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!metrics) return <p>没有指标数据</p>;

  return (
    <section>
      <h2 className="mb-4 text-xl font-bold">合成数据指标演示</h2>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MetricCard
          label="累计收益率"
          value={metrics.total_return}
          percentage
        />
        <MetricCard
          label="年化波动率"
          value={metrics.annualized_volatility}
          percentage
        />
        <MetricCard label="Sharpe" value={metrics.sharpe} />
        <MetricCard
          label="最大回撤"
          value={metrics.max_drawdown}
          percentage
        />
        <MetricCard label="IC" value={metrics.ic} />
        <MetricCard label="RankIC" value={metrics.rank_ic} />
      </div>
    </section>
  );
}
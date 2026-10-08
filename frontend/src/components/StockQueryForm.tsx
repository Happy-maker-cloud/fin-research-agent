"use client";

import type { FormEvent } from "react";
import { useState } from "react";

interface DailyBar {
  symbol: string;
  as_of: string;
  data_date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  cached: boolean;
}

export default function StockQueryForm() {
  const [symbol, setSymbol] = useState("000001");
  const [asOf, setAsOf] = useState("2024-01-23");
  const [result, setResult] = useState<DailyBar | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (loading) return;

    setError("");
    setResult(null);

    const normalizedSymbol = symbol.trim();

    if (!/^\d{6}$/.test(normalizedSymbol)) {
      setError("请输入6位股票代码，例如000001");
      return;
    }

    if (!asOf) {
      setError("请选择截止日期");
      return;
    }

    setLoading(true);

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);

    try {
      const baseUrl =
        process.env.NEXT_PUBLIC_API_BASE_URL ??
        "http://127.0.0.1:8000";

      const params = new URLSearchParams({ as_of: asOf });
      const response = await fetch(
        `${baseUrl}/api/v1/market-data/${normalizedSymbol}?${params}`,
        { signal: controller.signal },
      );

      if (!response.ok) {
        const body = await response.text();
        let message = body || "查询失败";

        try {
          const payload = JSON.parse(body);
          message = payload.message ?? payload.detail ?? message;
        } catch {
          // 非JSON错误响应，使用原始内容。
        }

        throw new Error(
          `HTTP ${response.status}：${String(message)}`,
        );
      }

      const data = (await response.json()) as DailyBar;
      setResult(data);
    } catch (requestError: unknown) {
      setError(
        controller.signal.aborted
          ? "查询超过15秒，请稍后重试"
          : requestError instanceof Error
            ? requestError.message
            : "查询失败",
      );
    } finally {
      clearTimeout(timer);
      setLoading(false);
    }
  }

  return (
    <section className="mt-8 rounded-xl border border-slate-700 p-6">
      <h2 className="mb-4 text-xl font-bold">股票行情查询</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="stock-symbol">股票代码</label>
          <input
            id="stock-symbol"
            type="text"
            value={symbol}
            onChange={(event) => setSymbol(event.target.value)}
            placeholder="例如000001"
            maxLength={6}
            required
            disabled={loading}
            className="mt-1 block w-full rounded border p-2 text-black"
          />
        </div>

        <div>
          <label htmlFor="stock-date">截止日期</label>
          <input
            id="stock-date"
            type="date"
            value={asOf}
            onChange={(event) => setAsOf(event.target.value)}
            required
            disabled={loading}
            className="mt-1 block w-full rounded border p-2 text-black"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {loading ? "查询中……" : "查询行情"}
        </button>
      </form>

      {error && (
        <p role="alert" className="mt-4 text-red-500">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-6 space-y-2">
          <p>股票代码：{result.symbol}</p>
          <p>查询截止日期：{result.as_of}</p>
          <p>实际行情日期：{result.data_date}</p>
          <p>收盘价：{result.close.toFixed(2)}</p>
          <p>开盘价：{result.open.toFixed(2)}</p>
          <p>最高价：{result.high.toFixed(2)}</p>
          <p>最低价：{result.low.toFixed(2)}</p>
          <p>成交量：{result.volume}</p>
          <p>命中缓存：{result.cached ? "是" : "否"}</p>

          {result.data_date !== result.as_of && (
            <p className="text-amber-500">
              返回截止日期前最近一条可用行情；
              是否停牌或缺失需结合日历和状态数据判断。
            </p>
          )}
        </div>
      )}
    </section>
  );
}
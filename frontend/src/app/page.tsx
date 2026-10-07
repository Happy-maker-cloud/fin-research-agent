"use client";

import MetricsPanel from "@/components/MetricsPanel";
import { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  service: string;
}

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function checkBackend(): Promise<void> {
      try {
        const apiBaseUrl =
          process.env.NEXT_PUBLIC_API_BASE_URL ??
          "http://127.0.0.1:8000";

        const response = await fetch(`${apiBaseUrl}/health`);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = (await response.json()) as HealthResponse;
        setHealth(data);
      } catch (requestError: unknown) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : String(requestError);

        setError(message);
      } finally {
        setLoading(false);
      }
    }

    void checkBackend();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-20 text-white">
      <div className="mx-auto max-w-3xl">
        <p className="mb-3 text-sm font-semibold text-cyan-400">
          FINANCIAL AGENT
        </p>

        <h1 className="text-4xl font-bold tracking-tight">
          金融研究 Agent
        </h1>

        <p className="mt-4 text-slate-400">
          Next.js 前端与 FastAPI 后端连接测试
        </p>

        <section className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">后端运行状态</h2>

          {loading && (
            <p className="mt-4 text-yellow-300">正在检查后端……</p>
          )}

          {health && (
            <div className="mt-4">
              <p className="text-emerald-400">
                ● 后端连接正常
              </p>
              <p className="mt-2 text-slate-300">
                服务：{health.service}
              </p>
              <p className="text-slate-300">
                状态：{health.status}
              </p>
            </div>
          )}

          {error && (
            <div className="mt-4">
              <p className="text-red-400">● 后端连接失败</p>
              <p className="mt-2 text-slate-400">{error}</p>
            </div>
          )}
        </section>
      </div>
      <MetricsPanel />
    </main>
  );
}
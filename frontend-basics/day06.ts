interface HealthResponse {
  status: string;
}

interface DailyBarResponse {
  symbol: string;
  as_of: string;
  data_date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  source: string;
  retrieved_at: string;
  cached: boolean;
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `请求失败: ${response.status} ${response.statusText}`,
    );
  }

  return (await response.json()) as T;
}

async function main(): Promise<void> {
  console.log("开始请求FastAPI");

  const health = await fetchJson<HealthResponse>(
    "http://127.0.0.1:8000/health",
  );

  console.log("健康检查:", health);

  try {
    const dailyBar = await fetchJson<DailyBarResponse>(
      "http://127.0.0.1:8000/api/v1/market-data/000001"
      + "?as_of=2024-01-23",
    );

    console.log("股票代码:", dailyBar.symbol);
    console.log("数据日期:", dailyBar.data_date);
    console.log("收盘价:", dailyBar.close);
    console.log("是否来自缓存:", dailyBar.cached);
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error("行情接口异常:", error.message);
    } else {
      console.error("未知异常:", error);
    }
  }
}

main().catch((error: unknown) => {
  console.error("程序执行失败:", error);
});
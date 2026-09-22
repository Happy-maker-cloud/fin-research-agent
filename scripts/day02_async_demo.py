import asyncio
import logging

from fin_agent.logging_config import setup_logging
from fin_agent.services.market_data import fetch_quotes


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    symbols = ["AAPL", "MSFT", "NVDA"]
    logger.info("开始并发获取 %d 只股票", len(symbols))

    quotes = await fetch_quotes(symbols)

    for quote in quotes:
        logger.info("%s 当前价格 %.2f", quote.symbol, quote.price)


if __name__ == "__main__":
    asyncio.run(main())

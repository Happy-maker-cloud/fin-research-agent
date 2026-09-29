import re
from dataclasses import asdict
from datetime import date
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fin_agent.api.schemas import (
    BatchQuoteRequest,
    BatchQuoteResponse,
    DailyBarResponse,
    ErrorResponse,
    QuoteResponse,
)
from fin_agent.exceptions import (
    MarketDataError,
    MarketDataTimeoutError,
)
from fin_agent.services.akshare_market import fetch_daily_bar
from fin_agent.services.market_data import fetch_quote, fetch_quotes

app = FastAPI(
    title="Financial Research Agent API",
    description="金融研究 Agent 数据服务",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_request_id(request: Request) -> str:
    """获取当前请求ID。"""

    return getattr(request.state, "request_id", "unknown")


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """为每个请求生成或复用请求ID。"""

    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """处理Pydantic参数校验错误。"""

    details = [
        {
            "location": list(error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]

    error = ErrorResponse(
        code="VALIDATION_ERROR",
        message="请求参数校验失败",
        request_id=get_request_id(request),
        details=details,
    )

    return JSONResponse(
        status_code=422,
        content=error.model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_error_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """处理HTTP业务错误。"""

    error = ErrorResponse(
        code="HTTP_ERROR",
        message=str(exc.detail),
        request_id=get_request_id(request),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
    )


@app.exception_handler(MarketDataTimeoutError)
async def timeout_error_handler(
    request: Request,
    exc: MarketDataTimeoutError,
) -> JSONResponse:
    """处理行情请求超时。"""

    error = ErrorResponse(
        code="MARKET_DATA_TIMEOUT",
        message=str(exc),
        request_id=get_request_id(request),
    )

    return JSONResponse(
        status_code=504,
        content=error.model_dump(),
    )


@app.exception_handler(MarketDataError)
async def market_data_error_handler(
    request: Request,
    exc: MarketDataError,
) -> JSONResponse:
    """处理行情数据错误。"""

    error = ErrorResponse(
        code="MARKET_DATA_ERROR",
        message=str(exc),
        request_id=get_request_id(request),
    )

    return JSONResponse(
        status_code=502,
        content=error.model_dump(),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "fin-research-agent",
    }


@app.get(
    "/api/v1/quotes/{symbol}",
    response_model=QuoteResponse,
)
async def get_quote(symbol: str) -> QuoteResponse:
    """查询单只证券行情。"""

    normalized_symbol = symbol.strip().upper()

    if not re.fullmatch(r"[A-Z0-9.\-]{1,16}", normalized_symbol):
        raise HTTPException(
            status_code=422,
            detail="证券代码格式不正确",
        )

    quote = await fetch_quote(normalized_symbol)

    return QuoteResponse(
        symbol=quote.symbol,
        price=quote.price,
        timestamp=quote.timestamp,
    )


@app.post(
    "/api/v1/quotes/batch",
    response_model=BatchQuoteResponse,
)
async def get_batch_quotes(
    request: BatchQuoteRequest,
) -> BatchQuoteResponse:
    """批量查询证券行情。"""

    quotes = await fetch_quotes(request.symbols)

    responses = [
        QuoteResponse(
            symbol=quote.symbol,
            price=quote.price,
            timestamp=quote.timestamp,
        )
        for quote in quotes
    ]

    return BatchQuoteResponse(
        count=len(responses),
        quotes=responses,
    )


@app.get(
    "/api/v1/market-data/{symbol}",
    response_model=DailyBarResponse,
)
async def get_market_data(
    symbol: str,
    as_of: date,
) -> DailyBarResponse:
    normalized_symbol = symbol.strip()

    if not re.fullmatch(r"\d{6}", normalized_symbol):
        raise HTTPException(
            status_code=422,
            detail="A股代码必须是6位数字",
        )

    bar = await fetch_daily_bar(
        symbol=normalized_symbol,
        as_of=as_of,
    )

    return DailyBarResponse(**asdict(bar))

class FinAgentError(Exception):
    """金融 Agent 基础异常。"""


class ConfigurationError(FinAgentError):
    """配置不正确。"""


class MarketDataError(FinAgentError):
    """行情数据获取失败。"""


class MarketDataTimeoutError(MarketDataError):
    """行情接口请求超时。"""

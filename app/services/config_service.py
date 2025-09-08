from functools import lru_cache
from typing import Optional
from ..models import Config


class ConfigService:
    """配置读取服务（带缓存）
    - 统一从 Config 表读取配置，并提供默认值
    - 对常用读取进行 LRU 缓存，减少数据库访问
    """

    @staticmethod
    @lru_cache(maxsize=128)
    def get_decimal(key: str, default: float = 0.0) -> float:
        config: Optional[Config] = Config.query.filter_by(key=key).first()
        if not config or config.value is None:
            return default
        try:
            return float(config.value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    @lru_cache(maxsize=128)
    def get_string(key: str, default: str = "") -> str:
        config: Optional[Config] = Config.query.filter_by(key=key).first()
        if not config or config.value is None:
            return default
        return str(config.value)

    @staticmethod
    def clear_cache():
        ConfigService.get_decimal.cache_clear()
        ConfigService.get_string.cache_clear()


"""
配置管理模块
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """大语言模型配置"""
    provider: str = "openai"
    model_name: str = "Qwen3-32B"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    openai_api_base: Optional[str] = None
    openai_api_key: Optional[str] = None


class AgentConfig(BaseModel):
    """智能体配置"""
    max_iterations: int = 5
    max_execution_time: int = 300
    early_stopping_method: str = "generate"
    memory_type: str = "buffer_window"
    memory_window_size: int = 10


class SearchConfig(BaseModel):
    """搜索配置"""
    max_results_per_query: int = 20
    min_confidence_threshold: float = 0.6
    verification_rounds: int = 3
    quality_threshold: float = 0.7


class SearxngConfig(BaseModel):
    """SearXNG配置"""
    base_url: str = "http://localhost:8888"
    categories: list = Field(default_factory=lambda: ["general", "images", "news"])
    engines: list = Field(default_factory=lambda: ["bing", "google", "duckduckgo"])
    language: str = "zh-CN"
    safesearch: int = 1
    timeout: int = 10


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/relicseek.log"
    max_file_size: str = "10MB"
    backup_count: int = 5


class CacheConfig(BaseModel):
    """缓存配置"""
    enabled: bool = True
    ttl: int = 3600
    max_size: int = 1000


class EngineConfig(BaseModel):
    """引擎总配置"""
    model: ModelConfig = Field(default_factory=ModelConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    searxng: SearxngConfig = Field(default_factory=SearxngConfig)


class Settings:
    """设置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化设置管理器
        
        Args:
            config_dir: 配置文件目录路径，默认为项目根目录的config文件夹
        """
        if config_dir is None:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self._engine_config: Optional[EngineConfig] = None
        self._logging_config: Optional[LoggingConfig] = None
        self._cache_config: Optional[CacheConfig] = None
        
    def load_engine_config(self) -> EngineConfig:
        """加载引擎配置"""
        if self._engine_config is None:
            config_file = self.config_dir / "engine_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._engine_config = EngineConfig(**config_data.get("engine", {}))
            else:
                self._engine_config = EngineConfig()
        return self._engine_config
    
    def load_logging_config(self) -> LoggingConfig:
        """加载日志配置"""
        if self._logging_config is None:
            config_file = self.config_dir / "engine_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._logging_config = LoggingConfig(**config_data.get("logging", {}))
            else:
                self._logging_config = LoggingConfig()
        return self._logging_config
    
    def load_cache_config(self) -> CacheConfig:
        """加载缓存配置"""
        if self._cache_config is None:
            config_file = self.config_dir / "engine_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._cache_config = CacheConfig(**config_data.get("cache", {}))
            else:
                self._cache_config = CacheConfig()
        return self._cache_config
    
    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量"""
        return os.getenv(key, default)
    
    def get_openai_api_key(self) -> Optional[str]:
        """获取OpenAI API密钥"""
        # 优先从环境变量获取
        env_key = self.get_env_var("OPENAI_API_KEY")
        if env_key:
            return env_key
        
        # 从配置文件获取
        config_key = self.load_engine_config().model.openai_api_key
        if config_key:
            return config_key
        
        # 如果都没有，返回EMPTY
        return "EMPTY"
    
    def get_openai_api_base(self) -> Optional[str]:
        """获取OpenAI API Base URL"""
        # 优先从环境变量获取
        env_base = self.get_env_var("OPENAI_API_BASE")
        if env_base:
            return env_base
        
        # 从配置文件获取
        config_base = self.load_engine_config().model.openai_api_base
        if config_base:
            return config_base
        
        # 如果没有配置，返回None（使用默认的OpenAI API）
        return None
    
    def get_searxng_url(self) -> str:
        """获取SearXNG服务地址"""
        return self.get_env_var("SEARXNG_URL", self.load_engine_config().searxng.base_url)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """保存配置到文件"""
        config_file = self.config_dir / f"{config_name}.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    def reload_configs(self) -> None:
        """重新加载所有配置"""
        self._engine_config = None
        self._logging_config = None
        self._cache_config = None

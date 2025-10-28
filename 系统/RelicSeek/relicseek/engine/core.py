"""
RelicSeek核心引擎
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..config.settings import Settings
from .agent import RelicSeekAgent


class RelicSeekEngine:
    """RelicSeek核心引擎"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化引擎
        
        Args:
            config_dir: 配置文件目录路径
        """
        # 初始化设置
        self.settings = Settings(config_dir)
        
        # 设置日志
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.agent: Optional[RelicSeekAgent] = None
        self._initialize_engine()
        
        self.logger.info("RelicSeek引擎初始化完成")
    
    def _setup_logging(self):
        """设置日志系统"""
        logging_config = self.settings.load_logging_config()
        
        # 创建日志目录
        log_file = Path(logging_config.file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=getattr(logging, logging_config.level),
            format=logging_config.format,
            handlers=[
                logging.FileHandler(logging_config.file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _initialize_engine(self):
        """初始化引擎组件"""
        try:
            # 初始化智能体
            self.agent = RelicSeekAgent(self.settings)
            self.logger.info("智能体初始化成功")
            
        except Exception as e:
            self.logger.error(f"引擎初始化失败: {str(e)}")
            raise
    
    def search(self, query: str, user_id: Optional[str] = None, 
               session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行文物搜索
        
        Args:
            query: 用户查询
            user_id: 用户ID（可选）
            session_id: 会话ID（可选）
            
        Returns:
            搜索结果字典
        """
        if not self.agent:
            raise RuntimeError("引擎未正确初始化")
        
        # 记录搜索开始
        search_id = self._generate_search_id()
        
        # 打印引擎搜索调试信息
        self.logger.info("🚀" + "=" * 60)
        self.logger.info("🚀 RelicSeek引擎开始执行搜索")
        self.logger.info(f"🚀 🆔 搜索ID: {search_id}")
        self.logger.info(f"🚀 📝 用户查询: {query}")
        self.logger.info(f"🚀 👤 用户ID: {user_id or '未指定'}")
        self.logger.info(f"🚀 💬 会话ID: {session_id or '未指定'}")
        self.logger.info(f"🚀 ⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("🚀" + "=" * 60)
        
        try:
            # 构建搜索上下文
            context = {
                'search_id': search_id,
                'user_id': user_id,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"🚀 🔍 构建搜索上下文完成")
            
            # 执行搜索
            self.logger.info(f"🚀 🤖 调用智能体执行搜索")
            result = self.agent.search(query, context)
            
            # 添加元数据
            result['search_id'] = search_id
            result['context'] = context
            
            # 记录搜索完成
            if result.get('success', False):
                self.logger.info(f"🚀 ✅ 搜索完成 [ID: {search_id}]: 成功")
                self.logger.info(f"🚀 📊 搜索结果包含:")
                if 'analysis' in result:
                    self.logger.info(f"🚀   - 查询分析: ✅")
                if 'strategy' in result:
                    self.logger.info(f"🚀   - 搜索策略: ✅")
                if 'results' in result:
                    self.logger.info(f"🚀   - 搜索结果: ✅")
                if 'report' in result:
                    self.logger.info(f"🚀   - 最终报告: ✅")
                if 'metadata' in result:
                    iterations = result['metadata'].get('iterations', 0)
                    self.logger.info(f"🚀   - 执行迭代次数: {iterations}")
            else:
                self.logger.warning(f"🚀 ❌ 搜索完成 [ID: {search_id}]: 失败 - {result.get('error', '未知错误')}")
            
            self.logger.info("🚀" + "=" * 60)
            
            return result
            
        except Exception as e:
            self.logger.error(f"🚀 ❌ 搜索执行错误 [ID: {search_id}]: {str(e)}")
            self.logger.info("🚀" + "=" * 60)
            return {
                'success': False,
                'error': str(e),
                'search_id': search_id,
                'query': query
            }
    
    def get_search_history(self, user_id: Optional[str] = None, 
                          session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取搜索历史
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            搜索历史列表
        """
        # 这里可以实现基于数据库或文件的历史记录查询
        # 当前版本从内存中获取对话历史
        if self.agent:
            history = self.agent.get_conversation_history()
            return [{'message': msg.content, 'type': type(msg).__name__} for msg in history]
        return []
    
    def clear_session(self, session_id: Optional[str] = None):
        """
        清除会话状态
        
        Args:
            session_id: 会话ID
        """
        if self.agent:
            self.agent.clear_memory()
            self.logger.info(f"会话状态已清除 [Session: {session_id}]")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """
        获取引擎状态
        
        Returns:
            引擎状态信息
        """
        status = {
            'initialized': self.agent is not None,
            'timestamp': datetime.now().isoformat(),
            'config': {
                'model': self.settings.load_engine_config().model.dict(),
                'agent': self.settings.load_engine_config().agent.dict(),
                'search': self.settings.load_engine_config().search.dict()
            }
        }
        
        if self.agent:
            status['agent_status'] = {
                'tools_count': len(self.agent.tools),
                'memory_enabled': self.agent.memory is not None,
                'conversation_length': len(self.agent.get_conversation_history())
            }
        
        return status
    
    def reload_config(self):
        """重新加载配置"""
        try:
            self.settings.reload_configs()
            self._initialize_engine()
            self.logger.info("配置重新加载成功")
        except Exception as e:
            self.logger.error(f"配置重新加载失败: {str(e)}")
            raise
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        验证系统设置
        
        Returns:
            验证结果
        """
        validation_results = {
            'overall_status': 'success',
            'checks': {}
        }
        
        # 检查API密钥和模型配置
        api_key = self.settings.get_openai_api_key()
        api_base = self.settings.get_openai_api_base()
        
        # 对于自定义模型服务器，允许使用EMPTY占位符
        if api_base and api_key == "EMPTY":
            validation_results['checks']['openai_api_key'] = {
                'status': 'success',
                'message': f'自定义模型服务器已配置 ({api_base})'
            }
        elif api_key and api_key != "EMPTY":
            validation_results['checks']['openai_api_key'] = {
                'status': 'success',
                'message': 'OpenAI API密钥已配置'
            }
        else:
            validation_results['checks']['openai_api_key'] = {
                'status': 'error',
                'message': 'API密钥未配置 (需要设置OPENAI_API_KEY或配置自定义API Base)'
            }
        
        # 检查SearXNG连接
        searxng_url = self.settings.get_searxng_url()
        try:
            import requests
            response = requests.get(f"{searxng_url}/search", timeout=5)
            searxng_status = 'success' if response.status_code == 200 else 'warning'
            searxng_message = 'SearXNG服务连接正常' if searxng_status == 'success' else 'SearXNG服务连接异常'
        except Exception as e:
            searxng_status = 'error'
            searxng_message = f'SearXNG服务不可用: {str(e)}'
        
        validation_results['checks']['searxng_connection'] = {
            'status': searxng_status,
            'message': searxng_message
        }
        
        # 检查配置文件
        config_files = ['engine_config.json', 'prompts_config.json']
        for config_file in config_files:
            config_path = self.settings.config_dir / config_file
            file_exists = config_path.exists()
            validation_results['checks'][f'config_{config_file}'] = {
                'status': 'success' if file_exists else 'error',
                'message': f'配置文件{config_file}存在' if file_exists else f'配置文件{config_file}不存在'
            }
        
        # 检查prompt文件
        prompt_files = [
            'prompts/query_analysis.txt',
            'prompts/strategy_planning.txt',
            'prompts/reflection.txt',
            'prompts/system/agent_system.txt'
        ]
        project_root = Path(__file__).parent.parent.parent
        for prompt_file in prompt_files:
            prompt_path = project_root / prompt_file
            file_exists = prompt_path.exists()
            validation_results['checks'][f'prompt_{prompt_file.split("/")[-1]}'] = {
                'status': 'success' if file_exists else 'error',
                'message': f'Prompt文件{prompt_file}存在' if file_exists else f'Prompt文件{prompt_file}不存在'
            }
        
        # 检查智能体初始化
        validation_results['checks']['agent_initialization'] = {
            'status': 'success' if self.agent else 'error',
            'message': '智能体初始化成功' if self.agent else '智能体初始化失败'
        }
        
        # 计算总体状态
        error_count = sum(1 for check in validation_results['checks'].values() if check['status'] == 'error')
        if error_count > 0:
            validation_results['overall_status'] = 'error'
        elif any(check['status'] == 'warning' for check in validation_results['checks'].values()):
            validation_results['overall_status'] = 'warning'
        
        return validation_results
    
    def _generate_search_id(self) -> str:
        """生成搜索ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 执行清理操作
        pass

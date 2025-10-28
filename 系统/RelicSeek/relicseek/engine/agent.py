"""
RelicSeek智能体实现
"""
import json
import logging
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from ..config.settings import Settings, EngineConfig
from ..config.prompt_manager import PromptManager
from .tools import RelicSearchToolkit


class RelicSeekAgent:
    """RelicSeek文物搜索智能体"""
    
    def __init__(self, settings: Settings):
        """
        初始化智能体
        
        Args:
            settings: 系统设置
        """
        self.settings = settings
        self.engine_config = settings.load_engine_config()
        self.prompt_manager = PromptManager()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self._setup_llm()
        self._setup_memory()
        self._setup_tools()
        self._setup_agent()
    
    def _setup_llm(self):
        """设置大语言模型"""
        model_config = self.engine_config.model
        
        # 获取API密钥
        api_key = self.settings.get_openai_api_key()
        
        # 对于自定义模型服务器，允许使用EMPTY或其他占位符
        # 只有在没有配置API base URL且API密钥为空时才报错
        api_base = self.settings.get_openai_api_base()
        if not api_base and (not api_key or api_key == "EMPTY"):
            raise ValueError("请设置OPENAI_API_KEY环境变量或配置API密钥")
        
        # 如果使用自定义API base，将EMPTY替换为有效的占位符
        if api_base and (not api_key or api_key == "EMPTY"):
            api_key = "sk-custom-api-key-placeholder"
        
        # 构建LLM参数
        llm_kwargs = {
            'model': model_config.model_name,
            'temperature': model_config.temperature,
            'max_tokens': model_config.max_tokens,
            'timeout': model_config.timeout,
            'openai_api_key': api_key
        }
        
        # 如果配置了自定义API base URL，则添加
        if api_base:
            llm_kwargs['base_url'] = api_base
        
        self.llm = ChatOpenAI(**llm_kwargs)
    
    def _setup_memory(self):
        """设置记忆管理"""
        agent_config = self.engine_config.agent
        
        if agent_config.memory_type == "buffer_window":
            self.memory = ConversationBufferWindowMemory(
                k=agent_config.memory_window_size,
                return_messages=True,
                memory_key="chat_history"
            )
        else:
            self.memory = ConversationBufferWindowMemory(
                k=10,
                return_messages=True,
                memory_key="chat_history"
            )
    
    def _setup_tools(self):
        """设置工具"""
        searxng_config = self.engine_config.searxng.dict()
        # 添加搜索配置参数
        searxng_config['search_config'] = self.engine_config.search.dict()
        self.search_toolkit = RelicSearchToolkit(searxng_config)
        self.tools = self.search_toolkit.get_langchain_tools()
    
    def _setup_agent(self):
        """设置智能体"""
        # 获取系统prompt
        system_prompt = self.prompt_manager.get_system_prompt("agent_system")
        
        # 创建ReAct prompt模板
        react_prompt = PromptTemplate.from_template(
            f"""{system_prompt}

你有权访问以下工具:

{{tools}}

使用以下格式:

Question: 用户的问题
Thought: 我需要思考应该做什么
Action: 要采取的行动，应该是[{{tool_names}}]中的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个Thought/Action/Action Input/Observation可以重复N次)
Thought: 我现在知道最终答案了
Final Answer: 对原始问题的最终答案

开始!

Previous conversation history:
{{chat_history}}

Question: {{input}}
{{agent_scratchpad}}"""
        )
        
        # 创建ReAct智能体
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=react_prompt
        )
        
        # 创建智能体执行器
        agent_config = self.engine_config.agent
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            max_iterations=agent_config.max_iterations,
            max_execution_time=agent_config.max_execution_time,
            early_stopping_method=agent_config.early_stopping_method,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def search(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行文物搜索
        
        Args:
            query: 用户查询
            context: 搜索上下文
            
        Returns:
            搜索结果
        """
        try:
            # 打印智能体搜索调试信息
            self.logger.info("🤖" + "=" * 58)
            self.logger.info("🤖 RelicSeek智能体开始处理查询")
            self.logger.info(f"🤖 📝 用户查询: {query}")
            if context:
                self.logger.info(f"🤖 🔍 搜索上下文: {context}")
            self.logger.info("🤖" + "=" * 58)
            
            # 分析查询
            self.logger.info("🤖 🔍 步骤1: 分析用户查询")
            analysis_result = self._analyze_query(query)
            self.logger.info(f"🤖 ✅ 查询分析完成")
            if 'analysis_text' in analysis_result:
                self.logger.info(f"🤖 📋 分析结果: {analysis_result['analysis_text'][:200]}...")
            
            # 制定搜索策略
            self.logger.info("🤖 🎯 步骤2: 制定搜索策略")
            strategy = self._plan_search_strategy(analysis_result)
            self.logger.info(f"🤖 ✅ 搜索策略制定完成")
            if 'strategy_text' in strategy:
                self.logger.info(f"🤖 📋 策略内容: {strategy['strategy_text'][:200]}...")
            if 'keywords' in strategy:
                self.logger.info(f"🤖 🔑 关键词: {strategy['keywords']}")
            
            # 执行搜索
            self.logger.info("🤖 🔍 步骤3: 执行搜索")
            search_results = self._execute_search(query, strategy)
            self.logger.info(f"🤖 ✅ 搜索执行完成")
            if 'agent_output' in search_results:
                self.logger.info(f"🤖 📋 智能体输出: {search_results['agent_output'][:200]}...")
            
            # 验证和反思
            self.logger.info("🤖 🔍 步骤4: 验证和反思搜索结果")
            validated_results = self._validate_and_reflect(search_results, query)
            self.logger.info(f"🤖 ✅ 验证和反思完成")
            if 'quality_score' in validated_results:
                self.logger.info(f"🤖 ⭐ 质量评分: {validated_results['quality_score']}")
            if 'confidence' in validated_results:
                self.logger.info(f"🤖 🎯 置信度: {validated_results['confidence']}")
            
            # 生成最终报告
            self.logger.info("🤖 📝 步骤5: 生成最终报告")
            final_report = self._generate_final_report(validated_results, query)
            self.logger.info(f"🤖 ✅ 最终报告生成完成")
            self.logger.info(f"🤖 📋 报告长度: {len(final_report)} 字符")
            
            result = {
                'success': True,
                'query': query,
                'analysis': analysis_result,
                'strategy': strategy,
                'results': validated_results,
                'report': final_report,
                'metadata': {
                    'timestamp': self._get_current_timestamp(),
                    'iterations': getattr(self.agent_executor, 'iterations', 0)
                }
            }
            
            self.logger.info("🤖 🎉 智能体搜索处理完成")
            self.logger.info("🤖" + "=" * 58)
            
            return result
            
        except Exception as e:
            self.logger.error(f"🤖 ❌ 搜索过程中出现错误: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """分析用户查询"""
        try:
            prompt = self.prompt_manager.get_prompt("query_analysis", user_query=query)
            
            response = self.llm.invoke([
                SystemMessage(content=self.prompt_manager.get_system_prompt("search_expert")),
                HumanMessage(content=prompt)
            ])
            
            # 简单解析响应（实际应用中可能需要更复杂的解析）
            return {
                'analysis_text': response.content,
                'complexity': self._extract_complexity(response.content),
                'entities': self._extract_entities(response.content),
                'query_type': self._extract_query_type(response.content)
            }
        except Exception as e:
            self.logger.error(f"查询分析失败: {str(e)}")
            return {'error': str(e)}
    
    def _plan_search_strategy(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """制定搜索策略"""
        try:
            prompt = self.prompt_manager.get_prompt(
                "strategy_planning", 
                analysis_result=json.dumps(analysis_result, ensure_ascii=False)
            )
            
            response = self.llm.invoke([
                SystemMessage(content=self.prompt_manager.get_system_prompt("search_expert")),
                HumanMessage(content=prompt)
            ])
            
            return {
                'strategy_text': response.content,
                'keywords': self._extract_keywords(response.content),
                'search_steps': self._extract_search_steps(response.content)
            }
        except Exception as e:
            self.logger.error(f"策略制定失败: {str(e)}")
            return {'error': str(e)}
    
    def _execute_search(self, query: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """执行搜索"""
        try:
            # 使用智能体执行器进行搜索
            result = self.agent_executor.invoke({
                'input': f"请根据以下搜索策略为用户查询'{query}'寻找相关的文物信息：\n{strategy.get('strategy_text', '')}"
            })
            
            return {
                'agent_output': result.get('output', ''),
                'intermediate_steps': result.get('intermediate_steps', []),
                'final_answer': result.get('output', '')
            }
        except Exception as e:
            self.logger.error(f"搜索执行失败: {str(e)}")
            return {'error': str(e)}
    
    def _validate_and_reflect(self, search_results: Dict[str, Any], 
                             original_query: str) -> Dict[str, Any]:
        """验证和反思搜索结果"""
        try:
            prompt = self.prompt_manager.get_prompt(
                "reflection",
                current_results=json.dumps(search_results, ensure_ascii=False),
                original_query=original_query
            )
            
            response = self.llm.invoke([
                SystemMessage(content=self.prompt_manager.get_system_prompt("search_expert")),
                HumanMessage(content=prompt)
            ])
            
            # 获取质量评估
            quality_assessment = self._assess_quality(search_results)
            
            return {
                'validated_results': search_results,
                'reflection': response.content,
                'quality_score': quality_assessment.get('score', 0),
                'confidence': quality_assessment.get('confidence', 'low'),
                'recommendations': self._extract_recommendations(response.content)
            }
        except Exception as e:
            self.logger.error(f"验证和反思失败: {str(e)}")
            return search_results
    
    def _assess_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """评估结果质量"""
        try:
            prompt = self.prompt_manager.get_prompt(
                "quality_assessment",
                artifact_info=json.dumps(results, ensure_ascii=False),
                source_info="搜索结果集"
            )
            
            response = self.llm.invoke([
                SystemMessage(content=self.prompt_manager.get_system_prompt("search_expert")),
                HumanMessage(content=prompt)
            ])
            
            return {
                'score': self._extract_quality_score(response.content),
                'confidence': self._extract_confidence(response.content),
                'assessment_text': response.content
            }
        except Exception as e:
            self.logger.error(f"质量评估失败: {str(e)}")
            return {'score': 0, 'confidence': 'low'}
    
    def _generate_final_report(self, validated_results: Dict[str, Any], 
                              query: str) -> str:
        """生成最终报告"""
        try:
            prompt = self.prompt_manager.get_prompt(
                "final_summary",
                artifact_data=json.dumps(validated_results, ensure_ascii=False),
                search_context=query
            )
            
            response = self.llm.invoke([
                SystemMessage(content=self.prompt_manager.get_system_prompt("search_expert")),
                HumanMessage(content=prompt)
            ])
            
            return response.content
        except Exception as e:
            self.logger.error(f"报告生成失败: {str(e)}")
            return f"报告生成失败: {str(e)}"
    
    # 辅助方法用于从LLM响应中提取结构化信息
    def _extract_complexity(self, text: str) -> str:
        """从分析文本中提取复杂度"""
        if "复杂度：" in text:
            line = [l for l in text.split('\n') if "复杂度：" in l][0]
            return line.split("复杂度：")[1].strip()
        return "中等"
    
    def _extract_entities(self, text: str) -> List[str]:
        """从分析文本中提取实体"""
        entities = []
        if "关键实体：" in text:
            line = [l for l in text.split('\n') if "关键实体：" in l][0]
            entities_text = line.split("关键实体：")[1].strip()
            entities = [e.strip() for e in entities_text.split(',') if e.strip()]
        return entities
    
    def _extract_query_type(self, text: str) -> str:
        """从分析文本中提取查询类型"""
        if "查询类型：" in text:
            line = [l for l in text.split('\n') if "查询类型：" in l][0]
            return line.split("查询类型：")[1].strip()
        return "属性搜索"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从策略文本中提取关键词"""
        keywords = []
        if "主要关键词：" in text:
            line = [l for l in text.split('\n') if "主要关键词：" in l][0]
            keywords_text = line.split("主要关键词：")[1].strip()
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        return keywords
    
    def _extract_search_steps(self, text: str) -> List[str]:
        """从策略文本中提取搜索步骤"""
        steps = []
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith('步骤'):
                steps.append(line.strip())
        return steps
    
    def _extract_quality_score(self, text: str) -> float:
        """从质量评估文本中提取评分"""
        if "综合评分：" in text:
            line = [l for l in text.split('\n') if "综合评分：" in l][0]
            score_text = line.split("综合评分：")[1].strip()
            try:
                return float(score_text.split('/')[0])
            except:
                pass
        return 3.0
    
    def _extract_confidence(self, text: str) -> str:
        """从质量评估文本中提取置信度"""
        if "置信度：" in text:
            line = [l for l in text.split('\n') if "置信度：" in l][0]
            return line.split("置信度：")[1].strip()
        return "中"
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """从反思文本中提取建议"""
        recommendations = []
        if "改进建议：" in text:
            lines = text.split('\n')
            start_idx = -1
            for i, line in enumerate(lines):
                if "改进建议：" in line:
                    start_idx = i
                    break
            
            if start_idx >= 0:
                for line in lines[start_idx:]:
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        recommendations.append(line.strip())
        
        return recommendations
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """获取对话历史"""
        if hasattr(self.memory, 'chat_memory'):
            return self.memory.chat_memory.messages
        return []
    
    def clear_memory(self):
        """清除记忆"""
        if hasattr(self.memory, 'clear'):
            self.memory.clear()

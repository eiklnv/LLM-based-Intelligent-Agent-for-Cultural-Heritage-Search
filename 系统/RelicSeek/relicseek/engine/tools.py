"""
外部工具集成模块
"""
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
import re
from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field


class SearchResult(BaseModel):
    """搜索结果数据模型"""
    title: str = Field(description="页面标题")
    url: str = Field(description="页面URL")
    content: str = Field(description="页面内容摘要")
    score: float = Field(description="相关性评分", default=0.0)
    source: str = Field(description="信息来源", default="")


class SearxngTool:
    """SearXNG搜索工具"""
    
    def __init__(self, base_url: str = "http://localhost:8888", 
                 language: str = "zh-CN", timeout: int = 10):
        """
        初始化SearXNG搜索工具
        
        Args:
            base_url: SearXNG服务地址
            language: 搜索语言
            timeout: 请求超时时间
        """
        self.base_url = base_url.rstrip('/')
        self.language = language
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'RelicSeek/1.0 (Cultural Heritage Search System)',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': language
        })
    
    def search(self, query: str, categories: List[str] = None, 
               engines: List[str] = None, max_results: int = 20) -> List[SearchResult]:
        """
        执行搜索查询
        
        Args:
            query: 搜索查询词
            categories: 搜索分类，如['general', 'images', 'news']
            engines: 搜索引擎，如['bing', 'google', 'duckduckgo']
            max_results: 最大结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 打印搜索调试信息
            self.logger.info("=" * 60)
            self.logger.info("🔍 开始执行SearXNG搜索")
            self.logger.info(f"📝 搜索关键词: {query}")
            self.logger.info(f"🌐 搜索语言: {self.language}")
            self.logger.info(f"📂 搜索分类: {categories or ['general']}")
            self.logger.info(f"🔧 搜索引擎: {engines or ['default']}")
            self.logger.info(f"📊 最大结果数: {max_results}")
            self.logger.info(f"🌍 服务地址: {self.base_url}")
            
            # 构建搜索参数
            params = {
                'q': query,
                'format': 'json',
                'language': self.language,
                'safesearch': '1'
            }
            
            if categories:
                params['categories'] = ','.join(categories)
            if engines:
                params['engines'] = ','.join(engines)
            
            self.logger.info(f"📋 搜索参数: {params}")
            
            # 发送搜索请求
            search_url = f"{self.base_url}/search"
            self.logger.info(f"🚀 发送请求到: {search_url}")
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            self.logger.info(f"✅ 请求成功，状态码: {response.status_code}")
            
            # 解析搜索结果
            data = response.json()
            raw_results = data.get('results', [])
            
            self.logger.info(f"📥 收到原始结果数量: {len(raw_results)}")
            
            results = []
            
            for i, item in enumerate(raw_results[:max_results]):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    content=item.get('content', ''),
                    score=self._calculate_relevance_score(item, query),
                    source=self._extract_source_domain(item.get('url', ''))
                )
                results.append(result)
                
                # 打印每个搜索结果的详细信息
                self.logger.info(f"📄 结果 {i+1}:")
                self.logger.info(f"   📌 标题: {result.title[:100]}{'...' if len(result.title) > 100 else ''}")
                self.logger.info(f"   🔗 URL: {result.url}")
                self.logger.info(f"   📝 内容摘要: {result.content[:150]}{'...' if len(result.content) > 150 else ''}")
                self.logger.info(f"   ⭐ 相关性评分: {result.score:.2f}")
                self.logger.info(f"   🏢 来源: {result.source}")
            
            # 按相关性排序
            results.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"🎯 最终返回结果数量: {len(results)}")
            self.logger.info("=" * 60)
            
            return results
            
        except requests.RequestException as e:
            self.logger.error(f"❌ SearXNG搜索失败: {str(e)}")
            raise Exception(f"SearXNG搜索失败: {str(e)}")
        except json.JSONDecodeError:
            self.logger.error("❌ SearXNG返回数据格式错误")
            raise Exception("SearXNG返回数据格式错误")
        except Exception as e:
            self.logger.error(f"❌ 搜索过程中出现错误: {str(e)}")
            raise Exception(f"搜索过程中出现错误: {str(e)}")
    
    def _calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """计算搜索结果的相关性评分"""
        score = 0.0
        query_terms = set(query.lower().split())
        
        # 标题匹配度
        title = item.get('title', '').lower()
        title_matches = sum(1 for term in query_terms if term in title)
        score += title_matches * 0.4
        
        # 内容匹配度
        content = item.get('content', '').lower()
        content_matches = sum(1 for term in query_terms if term in content)
        score += content_matches * 0.3
        
        # URL匹配度
        url = item.get('url', '').lower()
        url_matches = sum(1 for term in query_terms if term in url)
        score += url_matches * 0.1
        
        # 权威性加权
        source_bonus = self._get_source_authority_bonus(item.get('url', ''))
        score += source_bonus
        
        return min(score, 5.0)  # 限制最高分为5分
    
    def _get_source_authority_bonus(self, url: str) -> float:
        """根据信息源的权威性给予加分"""
        if not url:
            return 0.0
        
        url = url.lower()
        
        # 官方博物馆和文化机构
        if any(domain in url for domain in ['museum', 'gov.cn', 'palace', 'cultural']):
            return 1.0
        
        # 学术机构和教育网站
        if any(domain in url for domain in ['edu.cn', 'academic', 'university', 'scholar']):
            return 0.8
        
        # 权威百科网站
        if any(domain in url for domain in ['baike.baidu.com', 'wikipedia', 'britannica']):
            return 0.6
        
        # 专业文化媒体
        if any(domain in url for domain in ['cul.cn', 'wenhua', 'heritage']):
            return 0.4
        
        return 0.0
    
    def _extract_source_domain(self, url: str) -> str:
        """提取信息源域名"""
        if not url:
            return "未知来源"
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # 简化域名显示
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return "未知来源"


class WebContentExtractor:
    """网页内容提取器"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RelicSeek/1.0 (Cultural Heritage Search System)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def extract_content(self, url: str, max_length: int = 5000) -> Dict[str, str]:
        """
        提取网页内容
        
        Args:
            url: 网页URL
            max_length: 最大内容长度
            
        Returns:
            包含标题、正文内容的字典
        """
        try:
            # 打印内容提取调试信息
            self.logger.info("=" * 50)
            self.logger.info("📄 开始提取网页内容")
            self.logger.info(f"🔗 目标URL: {url}")
            self.logger.info(f"📏 最大内容长度: {max_length}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            self.logger.info(f"✅ 网页请求成功，状态码: {response.status_code}")
            self.logger.info(f"📝 响应编码: {response.encoding}")
            self.logger.info(f"📊 响应内容长度: {len(response.text)} 字符")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式标签
            for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
                tag.decompose()
            
            # 提取标题
            title = ""
            if soup.title:
                title = soup.title.get_text().strip()
            
            self.logger.info(f"📌 提取到标题: {title[:100]}{'...' if len(title) > 100 else ''}")
            
            # 提取正文内容
            content = ""
            
            # 优先寻找主要内容区域
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
            
            if main_content:
                content = main_content.get_text()
                self.logger.info("🎯 使用主要内容区域提取内容")
            else:
                # 如果找不到主要内容区域，则提取body中的文本
                body = soup.find('body')
                if body:
                    content = body.get_text()
                    self.logger.info("📄 使用body区域提取内容")
                else:
                    content = soup.get_text()
                    self.logger.info("🌐 使用整个页面提取内容")
            
            # 清理内容
            original_length = len(content)
            content = self._clean_content(content)
            cleaned_length = len(content)
            
            self.logger.info(f"🧹 内容清理: {original_length} -> {cleaned_length} 字符")
            
            # 截断过长的内容
            if len(content) > max_length:
                content = content[:max_length] + "..."
                self.logger.info(f"✂️ 内容截断到 {max_length} 字符")
            
            self.logger.info(f"📋 最终内容长度: {len(content)} 字符")
            self.logger.info("=" * 50)
            
            return {
                'title': title,
                'content': content,
                'url': url
            }
            
        except Exception as e:
            self.logger.error(f"❌ 内容提取失败: {str(e)}")
            return {
                'title': f"内容提取失败: {str(e)}",
                'content': "",
                'url': url
            }
    
    def _clean_content(self, content: str) -> str:
        """清理提取的内容"""
        if not content:
            return ""
        
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 移除特殊字符
        content = re.sub(r'[^\w\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', ' ', content)
        
        # 移除过短的行
        lines = content.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(cleaned_lines).strip()


class RelicSearchToolkit:
    """文物搜索工具包"""
    
    def __init__(self, searxng_config: Dict[str, Any]):
        """
        初始化工具包
        
        Args:
            searxng_config: SearXNG配置
        """
        self.searxng = SearxngTool(
            base_url=searxng_config.get('base_url', 'http://localhost:8888'),
            language=searxng_config.get('language', 'zh-CN'),
            timeout=searxng_config.get('timeout', 10)
        )
        self.extractor = WebContentExtractor()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 默认搜索参数
        self.default_categories = searxng_config.get('categories', ['general'])
        self.default_engines = searxng_config.get('engines', ['bing', 'google'])
        
        # 搜索配置参数
        search_config = searxng_config.get('search_config', {})
        self.max_results_per_query = search_config.get('max_results_per_query', 10)
        self.token_limit = search_config.get('token_limit', 3000)  # 默认3000 tokens
        
        self.logger.info("🔧 RelicSearchToolkit 初始化完成")
        self.logger.info(f"📂 默认搜索分类: {self.default_categories}")
        self.logger.info(f"🔧 默认搜索引擎: {self.default_engines}")
    
    def search_relics(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        搜索文物相关信息
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        try:
            # 使用配置的默认值
            if max_results is None:
                max_results = self.max_results_per_query
            
            # 打印工具包搜索调试信息
            self.logger.info("🏛️ 开始执行文物搜索")
            self.logger.info(f"📝 原始查询: {query}")
            self.logger.info(f"📊 最大结果数: {max_results}")
            
            # 增强查询词，添加文物相关关键词
            enhanced_query = self._enhance_query(query)
            self.logger.info(f"🔍 增强后查询: {enhanced_query}")
            
            # 执行搜索
            results = self.searxng.search(
                query=enhanced_query,
                categories=self.default_categories,
                engines=self.default_engines,
                max_results=max_results
            )
            
            self.logger.info(f"✅ 搜索完成，获得 {len(results)} 个结果")
            
            # 转换为字典格式
            formatted_results = [
                {
                    'title': result.title,
                    'url': result.url,
                    'content': result.content,
                    'score': result.score,
                    'source': result.source
                }
                for result in results
            ]
            
            # 打印结果摘要
            self.logger.info("📋 搜索结果摘要:")
            for i, result in enumerate(formatted_results[:5]):  # 只显示前5个结果
                self.logger.info(f"  {i+1}. {result['title'][:50]}... (评分: {result['score']:.2f})")
            
            if len(formatted_results) > 5:
                self.logger.info(f"  ... 还有 {len(formatted_results) - 5} 个结果")
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"❌ 文物搜索失败: {str(e)}")
            return [{'error': f"搜索失败: {str(e)}"}]
    
    def extract_page_content(self, url: str) -> Dict[str, str]:
        """
        提取网页详细内容
        
        Args:
            url: 网页URL
            
        Returns:
            网页内容字典
        """
        self.logger.info(f"📄 开始提取网页内容: {url}")
        result = self.extractor.extract_content(url)
        self.logger.info(f"✅ 网页内容提取完成")
        return result
    
    def _enhance_query(self, query: str) -> str:
        """增强搜索查询，添加文物相关关键词"""
        relic_keywords = ["文物", "古代", "历史", "博物馆", "文化", "艺术"]
        
        # 如果查询中没有文物相关关键词，则添加
        if not any(keyword in query for keyword in relic_keywords):
            query = f"{query} 文物"
        
        return query
    
    def _format_search_results_for_llm(self, results: List[Dict[str, Any]], max_tokens: int = None) -> str:
        """
        格式化搜索结果，控制返回给LLM的内容长度
        
        Args:
            results: 搜索结果列表
            max_tokens: 最大token数（粗略估算，1token约4个中文字符）
            
        Returns:
            格式化的结果字符串
        """
        if not results:
            return "未找到相关搜索结果。"
        
        # 使用配置的token限制
        if max_tokens is None:
            max_tokens = self.token_limit
        
        # 粗略估算：1 token ≈ 4个中文字符 ≈ 3个英文字符
        max_chars = max_tokens * 3
        formatted_results = []
        current_length = 0
        
        # 添加头部信息
        header = f"找到 {len(results)} 个相关文物信息：\n\n"
        formatted_results.append(header)
        current_length += len(header)
        
        for i, result in enumerate(results[:8]):  # 最多处理前8个结果，进一步减少
            # 智能截断标题和内容，保留关键信息
            title = self._extract_key_info(result.get('title', '无标题'), 80)
            content = self._extract_key_info(result.get('content', '无内容'), 150)
            url = result.get('url', '')
            score = result.get('score', 0)
            
            # 构建单个结果的字符串，简化格式
            result_str = f"{i+1}. {title}\n"
            result_str += f"   {content}\n"
            if score > 0.5:  # 只显示高相关性的来源
                result_str += f"   来源：{self._shorten_url(url)}\n"
            result_str += "\n"
            
            # 检查是否会超出长度限制
            if current_length + len(result_str) > max_chars:
                # 如果添加当前结果会超出限制，则停止添加
                remaining_count = len(results) - i
                if remaining_count > 0:
                    formatted_results.append(f"... 还有 {remaining_count} 个结果因长度限制未显示")
                break
            
            formatted_results.append(result_str)
            current_length += len(result_str)
        
        result_text = ''.join(formatted_results)
        
        # 记录截断信息
        self.logger.info(f"🔤 搜索结果格式化完成：原始 {len(results)} 个结果，返回内容长度 {len(result_text)} 字符")
        
        return result_text
    
    def _extract_key_info(self, text: str, max_length: int) -> str:
        """
        智能提取关键信息，优先保留文物相关内容
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            优化后的文本
        """
        if not text or len(text) <= max_length:
            return text
        
        # 文物相关关键词
        important_keywords = [
            '文物', '古迹', '遗址', '博物馆', '历史', '文化', '收藏', '展品',
            '朝代', '年代', '考古', '古代', '文献', '艺术', '传统', '保护',
            '世界遗产', '国宝', '珍品', '古董', '典藏', '陶瓷', '青铜', '玉器'
        ]
        
        # 按句号分句
        sentences = text.split('。')
        result_sentences = []
        current_length = 0
        
        # 优先选择包含关键词的句子
        for sentence in sentences:
            if current_length >= max_length:
                break
            
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 检查句子是否包含重要关键词
            has_keyword = any(keyword in sentence for keyword in important_keywords)
            
            if has_keyword or len(result_sentences) == 0:  # 保证至少有一句
                if current_length + len(sentence) <= max_length:
                    result_sentences.append(sentence)
                    current_length += len(sentence)
                else:
                    # 截断当前句子
                    remaining = max_length - current_length
                    if remaining > 10:  # 保证有意义的截断
                        result_sentences.append(sentence[:remaining] + "...")
                    break
        
        return '。'.join(result_sentences) if result_sentences else text[:max_length] + "..."
    
    def _shorten_url(self, url: str) -> str:
        """
        缩短URL显示
        
        Args:
            url: 原始URL
            
        Returns:
            缩短的URL
        """
        if not url:
            return ""
        
        # 提取域名
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain:
                return domain
        except:
            pass
        
        # 如果解析失败，简单截断
        if len(url) > 50:
            return url[:47] + "..."
        return url
    
    def _format_content_for_llm(self, content_result: Dict[str, Any], max_tokens: int = 2000) -> str:
        """
        格式化网页内容，控制返回给LLM的内容长度
        
        Args:
            content_result: 网页内容结果
            max_tokens: 最大token数
            
        Returns:
            格式化的内容字符串
        """
        if not content_result or 'error' in content_result:
            return f"网页内容提取失败：{content_result.get('error', '未知错误')}"
        
        max_chars = max_tokens * 3
        title = content_result.get('title', '无标题')[:100]
        content = content_result.get('content', '无内容')
        url = content_result.get('url', '')
        
        # 构建结果字符串
        result_str = f"标题：{title}\n"
        result_str += f"来源：{url}\n"
        result_str += f"内容：\n"
        
        # 计算内容可用的字符数
        available_chars = max_chars - len(result_str)
        
        if len(content) > available_chars:
            content = content[:available_chars] + "...[内容因长度限制被截断]"
        
        result_str += content
        
        # 记录截断信息
        self.logger.info(f"🔤 网页内容格式化完成：返回内容长度 {len(result_str)} 字符")
        
        return result_str
    
    def get_langchain_tools(self) -> List[Tool]:
        """获取LangChain工具列表"""
        tools = [
            Tool(
                name="search_relics",
                description="搜索文物相关信息。输入：搜索查询字符串。输出：相关文物信息的搜索结果列表。",
                func=lambda query: self._format_search_results_for_llm(self.search_relics(query))
            ),
            Tool(
                name="extract_content",
                description="提取网页的详细内容。输入：网页URL。输出：网页的标题和主要内容。",
                func=lambda url: self._format_content_for_llm(self.extract_page_content(url))
            )
        ]
        
        return tools

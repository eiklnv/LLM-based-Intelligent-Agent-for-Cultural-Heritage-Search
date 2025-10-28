"""
Streamlit Web界面
"""
import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

from ..engine.core import RelicSeekEngine


class StreamlitInterface:
    """Streamlit Web界面"""
    
    def __init__(self):
        """初始化Streamlit界面"""
        self.setup_page_config()
        self.initialize_session_state()
        
    def setup_page_config(self):
        """设置页面配置"""
        st.set_page_config(
            page_title="RelicSeek - 文物搜索智能体",
            page_icon="🏺",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 添加自定义CSS
        st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #8B4513;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .search-container {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .result-container {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #8B4513;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .sidebar-header {
            color: #8B4513;
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 1rem;
        }
        .status-success {
            color: #28a745;
            font-weight: bold;
        }
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }
        .search-stats {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            margin: 1rem 0;
        }
        .artifact-info {
            background: #fff8e1;
            padding: 1rem;
            border-radius: 5px;
            border-left: 3px solid #ffc107;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """初始化会话状态"""
        if 'engine' not in st.session_state:
            st.session_state.engine = None
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
        if 'engine_initialized' not in st.session_state:
            st.session_state.engine_initialized = False
    
    def run(self):
        """运行Streamlit应用"""
        # 页面标题
        st.markdown('<h1 class="main-header">🏺 RelicSeek 文物搜索智能体</h1>', unsafe_allow_html=True)
        
        # 侧边栏
        self.render_sidebar()
        
        # 主界面
        if st.session_state.engine_initialized:
            self.render_main_interface()
        else:
            self.render_initialization_interface()
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.markdown('<div class="sidebar-header">🔧 系统控制</div>', unsafe_allow_html=True)
            
            # 引擎初始化
            if st.button("🚀 初始化引擎", use_container_width=True):
                self.initialize_engine()
            
            # 系统状态
            if st.session_state.engine:
                status = st.session_state.engine.get_engine_status()
                st.markdown("**📊 系统状态**")
                if status['initialized']:
                    st.markdown('<span class="status-success">✅ 引擎运行正常</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-error">❌ 引擎未初始化</span>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 配置信息
            st.markdown('<div class="sidebar-header">⚙️ 配置信息</div>', unsafe_allow_html=True)
            
            if st.button("🔍 验证系统设置", use_container_width=True):
                self.validate_system_setup()
            
            if st.button("🔄 重新加载配置", use_container_width=True):
                self.reload_config()
            
            st.markdown("---")
            
            # 会话管理
            st.markdown('<div class="sidebar-header">💬 会话管理</div>', unsafe_allow_html=True)
            
            if st.button("🗑️ 清除会话", use_container_width=True):
                self.clear_session()
            
            # 显示会话信息
            st.markdown(f"**会话ID:** `{st.session_state.session_id[:8]}...`")
            st.markdown(f"**搜索次数:** {len(st.session_state.search_history)}")
            
            st.markdown("---")
            
            # 搜索历史
            if st.session_state.search_history:
                st.markdown('<div class="sidebar-header">📚 搜索历史</div>', unsafe_allow_html=True)
                for i, search in enumerate(reversed(st.session_state.search_history[-5:])):
                    with st.expander(f"🔍 {search['query'][:20]}..."):
                        st.markdown(f"**时间:** {search['timestamp']}")
                        st.markdown(f"**状态:** {'✅ 成功' if search['success'] else '❌ 失败'}")
                        if search['success']:
                            st.markdown(f"**搜索ID:** `{search['search_id']}`")
    
    def render_initialization_interface(self):
        """渲染初始化界面"""
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.markdown("### 🚀 欢迎使用RelicSeek文物搜索智能体")
        st.markdown("""
        RelicSeek是一个基于大语言模型的智能文物搜索系统，能够帮助您：
        
        - 🔍 **智能搜索**: 理解自然语言查询，智能搜索文物信息
        - 🧠 **多轮验证**: 通过多轮验证确保信息准确性
        - 🔗 **多源整合**: 整合多个信息源，提供完整的文物档案
        - 📊 **质量评估**: 对搜索结果进行可信度评估
        - 📖 **专业报告**: 生成结构化的文物信息报告
        
        请点击侧边栏的"🚀 初始化引擎"按钮开始使用。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 系统要求说明
        with st.expander("📋 系统要求和配置说明"):
            st.markdown("""
            **环境要求:**
            - Python 3.8+
            - OpenAI API密钥 (需要设置 `OPENAI_API_KEY` 环境变量)
            - SearXNG搜索服务 (可选，默认使用 http://localhost:8888)
            
            **配置文件:**
            - `config/engine_config.json`: 引擎配置
            - `config/prompts_config.json`: Prompt配置
            - `prompts/`: Prompt模板文件
            
            **使用说明:**
            1. 确保已安装所有依赖: `pip install -r requirements.txt`
            2. 设置环境变量: `export OPENAI_API_KEY=your_api_key`
            3. (可选) 启动SearXNG服务
            4. 运行程序: `streamlit run app.py`
            """)
    
    def render_main_interface(self):
        """渲染主界面"""
        # 搜索区域
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.markdown("### 🔍 文物搜索")
        
        # 搜索输入
        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input(
                "请输入您要搜索的文物信息:",
                placeholder="例如: 青铜鼎、唐三彩、清明上河图...",
                key="search_query"
            )
        
        with col2:
            search_button = st.button("🔍 搜索", use_container_width=True, type="primary")
        
        # 高级选项
        with st.expander("🔧 高级搜索选项"):
            col1, col2 = st.columns(2)
            with col1:
                max_iterations = st.slider("最大搜索轮次", 1, 10, 5)
                include_images = st.checkbox("包含图片搜索", value=True)
            with col2:
                quality_threshold = st.slider("质量阈值", 0.0, 1.0, 0.7, 0.1)
                verification_rounds = st.slider("验证轮数", 1, 5, 3)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 执行搜索
        if search_button and query.strip():
            self.execute_search(query, {
                'max_iterations': max_iterations,
                'include_images': include_images,
                'quality_threshold': quality_threshold,
                'verification_rounds': verification_rounds
            })
        
        # 显示搜索结果
        if st.session_state.search_history:
            self.render_search_results()
    
    def execute_search(self, query: str, options: Dict[str, Any]):
        """执行搜索"""
        if not st.session_state.engine:
            st.error("❌ 引擎未初始化，请先初始化引擎")
            return
        
        # 显示搜索进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 开始搜索
            status_text.text("🔍 正在分析查询...")
            progress_bar.progress(20)
            
            # 执行搜索
            with st.spinner("🤖 智能体正在搜索中..."):
                result = st.session_state.engine.search(
                    query=query,
                    session_id=st.session_state.session_id
                )
            
            progress_bar.progress(80)
            status_text.text("📊 正在处理结果...")
            
            # 保存搜索记录
            search_record = {
                'query': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'success': result.get('success', False),
                'search_id': result.get('search_id', ''),
                'result': result
            }
            st.session_state.search_history.append(search_record)
            
            progress_bar.progress(100)
            status_text.text("✅ 搜索完成!")
            
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # 显示结果
            if result.get('success', False):
                st.success(f"✅ 搜索成功! 搜索ID: {result.get('search_id', 'N/A')}")
            else:
                st.error(f"❌ 搜索失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ 搜索过程中出现错误: {str(e)}")
            st.error("详细错误信息:")
            st.code(traceback.format_exc())
    
    def render_search_results(self):
        """渲染搜索结果"""
        if not st.session_state.search_history:
            return
        
        # 获取最新搜索结果
        latest_search = st.session_state.search_history[-1]
        result = latest_search['result']
        
        if not result.get('success', False):
            return
        
        st.markdown("---")
        st.markdown("### 📋 搜索结果")
        
        # 结果概览
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("搜索状态", "✅ 成功" if result.get('success') else "❌ 失败")
        with col2:
            st.metric("搜索ID", result.get('search_id', 'N/A'))
        with col3:
            quality_score = result.get('results', {}).get('quality_score', 0)
            st.metric("质量评分", f"{quality_score:.1f}/5.0")
        with col4:
            confidence = result.get('results', {}).get('confidence', 'unknown')
            st.metric("置信度", confidence)
        
        # 详细结果
        tabs = st.tabs(["📖 最终报告", "🔍 搜索过程", "📊 详细数据", "🔬 质量分析"])
        
        with tabs[0]:
            # 最终报告
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            if 'report' in result:
                st.markdown("**📄 文物信息报告:**")
                st.markdown(result['report'])
            else:
                st.info("暂无生成的报告")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tabs[1]:
            # 搜索过程
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # 查询分析
            if 'analysis' in result:
                with st.expander("🧠 查询分析", expanded=True):
                    analysis = result['analysis']
                    if isinstance(analysis, dict):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**复杂度:** {analysis.get('complexity', 'N/A')}")
                            st.markdown(f"**查询类型:** {analysis.get('query_type', 'N/A')}")
                        with col2:
                            entities = analysis.get('entities', [])
                            if entities:
                                st.markdown("**关键实体:**")
                                for entity in entities:
                                    st.markdown(f"- {entity}")
            
            # 搜索策略
            if 'strategy' in result:
                with st.expander("📋 搜索策略"):
                    strategy = result['strategy']
                    if isinstance(strategy, dict):
                        keywords = strategy.get('keywords', [])
                        if keywords:
                            st.markdown("**关键词:**")
                            st.markdown(", ".join(keywords))
                        
                        steps = strategy.get('search_steps', [])
                        if steps:
                            st.markdown("**搜索步骤:**")
                            for step in steps:
                                st.markdown(f"- {step}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tabs[2]:
            # 详细数据
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # 以JSON格式显示原始数据
            with st.expander("🗃️ 原始搜索数据"):
                st.json(result)
            
            # 智能体执行步骤
            results_data = result.get('results', {})
            if 'intermediate_steps' in results_data:
                with st.expander("🤖 智能体执行步骤"):
                    steps = results_data['intermediate_steps']
                    for i, step in enumerate(steps):
                        st.markdown(f"**步骤 {i+1}:**")
                        st.code(str(step))
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tabs[3]:
            # 质量分析
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            results_data = result.get('results', {})
            
            # 质量评分
            quality_score = results_data.get('quality_score', 0)
            confidence = results_data.get('confidence', 'unknown')
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🎯 质量指标:**")
                st.progress(quality_score / 5.0)
                st.markdown(f"评分: {quality_score:.1f}/5.0")
            
            with col2:
                st.markdown("**🔒 置信度:**")
                confidence_color = {
                    'high': '🟢',
                    'medium': '🟡', 
                    'low': '🔴'
                }.get(confidence.lower(), '⚪')
                st.markdown(f"{confidence_color} {confidence}")
            
            # 改进建议
            recommendations = results_data.get('recommendations', [])
            if recommendations:
                st.markdown("**💡 改进建议:**")
                for rec in recommendations:
                    st.markdown(f"- {rec}")
            
            # 反思内容
            if 'reflection' in results_data:
                with st.expander("🤔 系统反思"):
                    st.markdown(results_data['reflection'])
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def initialize_engine(self):
        """初始化引擎"""
        try:
            with st.spinner("🚀 正在初始化RelicSeek引擎..."):
                st.session_state.engine = RelicSeekEngine()
                st.session_state.engine_initialized = True
            
            st.success("✅ 引擎初始化成功!")
            st.experimental_rerun()
            
        except Exception as e:
            st.error(f"❌ 引擎初始化失败: {str(e)}")
            st.error("请检查配置文件和环境变量设置")
            with st.expander("查看详细错误信息"):
                st.code(traceback.format_exc())
    
    def validate_system_setup(self):
        """验证系统设置"""
        if not st.session_state.engine:
            st.error("❌ 请先初始化引擎")
            return
        
        try:
            with st.spinner("🔍 正在验证系统设置..."):
                validation_result = st.session_state.engine.validate_setup()
            
            st.markdown("### 🔍 系统验证结果")
            
            overall_status = validation_result['overall_status']
            if overall_status == 'success':
                st.success("✅ 系统配置验证通过!")
            elif overall_status == 'warning':
                st.warning("⚠️ 系统配置存在警告")
            else:
                st.error("❌ 系统配置存在错误")
            
            # 显示详细检查结果
            for check_name, check_result in validation_result['checks'].items():
                status = check_result['status']
                message = check_result['message']
                
                if status == 'success':
                    st.success(f"✅ {message}")
                elif status == 'warning':
                    st.warning(f"⚠️ {message}")
                else:
                    st.error(f"❌ {message}")
                    
        except Exception as e:
            st.error(f"❌ 验证过程中出现错误: {str(e)}")
    
    def reload_config(self):
        """重新加载配置"""
        if not st.session_state.engine:
            st.error("❌ 请先初始化引擎")
            return
        
        try:
            with st.spinner("🔄 正在重新加载配置..."):
                st.session_state.engine.reload_config()
            
            st.success("✅ 配置重新加载成功!")
            
        except Exception as e:
            st.error(f"❌ 配置重新加载失败: {str(e)}")
    
    def clear_session(self):
        """清除会话"""
        if st.session_state.engine:
            st.session_state.engine.clear_session(st.session_state.session_id)
        
        # 清除搜索历史
        st.session_state.search_history = []
        
        # 生成新的会话ID
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
        
        st.success("✅ 会话已清除!")
        st.experimental_rerun()


def main():
    """主函数"""
    interface = StreamlitInterface()
    interface.run()


if __name__ == "__main__":
    main()

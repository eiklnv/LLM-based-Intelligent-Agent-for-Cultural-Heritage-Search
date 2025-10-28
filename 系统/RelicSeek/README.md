# RelicSeek - 基于大模型的文物搜索智能体系统

🏺 RelicSeek是一个基于LangChain的模块化文物搜索智能体系统，采用ReAct（推理-行动-观察）架构，能够智能地搜索、验证和整合文物相关信息，为用户提供准确、完整、可信的文物知识服务。

## ✨ 主要特性

- 🧠 **智能搜索规划**: 自动分析用户查询意图，制定个性化搜索策略
- 🔍 **多源信息整合**: 集成SearXNG搜索引擎，整合多个信息源
- 🔄 **多轮验证机制**: 通过多轮验证确保信息准确性和完整性
- 🏆 **质量评估系统**: 对搜索结果进行可信度评估和质量打分
- 📋 **结构化报告**: 自动生成专业的文物信息报告
- 🎨 **多种交互方式**: 支持Streamlit Web界面和命令行两种使用方式
- ⚙️ **模块化设计**: 配置文件驱动，便于定制和扩展

## 🏗️ 系统架构

### 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                           │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │  Streamlit Web  │    │      CLI Interface          │ │
│  │    Interface    │    │                             │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  智能体核心层                           │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   ReAct Agent   │    │   Memory Management         │ │
│  │                 │    │                             │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  工具调用层                             │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │  SearXNG Tool   │    │  Content Extractor          │ │
│  │                 │    │                             │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                 配置管理层                              │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │ Engine Config   │    │   Prompt Manager            │ │
│  │                 │    │                             │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

- **RelicSeekEngine**: 系统核心引擎，负责整体协调和控制
- **RelicSeekAgent**: 基于LangChain的ReAct智能体，执行推理和决策
- **SearxngTool**: SearXNG搜索引擎集成工具
- **PromptManager**: 智能化的提示词管理系统
- **Settings**: 统一的配置管理系统

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- OpenAI API密钥
- SearXNG搜索服务（可选）

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd RelicSeek

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY=your_openai_api_key

# 可选：配置SearXNG服务地址
export SEARXNG_URL=http://localhost:8888
```

### 4. 运行系统

#### Web界面方式
```bash
# 启动Streamlit Web应用
streamlit run app.py
```

#### 命令行方式
```bash
# 交互式搜索
python relicseek_cli.py search

# 单次搜索
python relicseek_cli.py search -q "青铜鼎"

# 验证系统设置
python relicseek_cli.py validate

# 查看系统状态
python relicseek_cli.py status
```

## 📖 使用指南

### Web界面使用

1. **初始化引擎**: 点击侧边栏的"🚀 初始化引擎"按钮
2. **输入查询**: 在搜索框中输入您要查询的文物信息
3. **查看结果**: 系统将展示详细的搜索结果和分析报告
4. **历史记录**: 在侧边栏查看搜索历史

### 命令行使用

```bash
# 查看所有可用命令
python relicseek_cli.py --help

# 初始化引擎
python relicseek_cli.py init

# 交互式搜索模式
python relicseek_cli.py search

# 单次搜索并导出结果
python relicseek_cli.py search -q "唐三彩" -o results.json

# 验证系统配置
python relicseek_cli.py validate

# 查看配置信息
python relicseek_cli.py config
```

## ⚙️ 配置说明

### 引擎配置 (`config/engine_config.json`)

```json
{
  "engine": {
    "model": {
      "provider": "openai",
      "model_name": "gpt-4-turbo-preview",
      "temperature": 0.7,
      "max_tokens": 2048
    },
    "agent": {
      "max_iterations": 5,
      "max_execution_time": 300,
      "memory_window_size": 10
    },
    "search": {
      "max_results_per_query": 20,
      "verification_rounds": 3,
      "quality_threshold": 0.7
    },
    "searxng": {
      "base_url": "http://localhost:8888",
      "categories": ["general", "images", "news"],
      "engines": ["bing", "google", "duckduckgo"]
    }
  }
}
```

### Prompt配置 (`config/prompts_config.json`)

系统使用模块化的Prompt管理方式，每个功能模块都有独立的Prompt文件：

- `prompts/query_analysis.txt`: 查询分析提示词
- `prompts/strategy_planning.txt`: 搜索策略规划提示词
- `prompts/reflection.txt`: 结果反思提示词
- `prompts/quality_assessment.txt`: 质量评估提示词
- `prompts/final_summary.txt`: 最终报告生成提示词

## 🔧 高级功能

### 自定义Prompt

您可以通过修改`prompts/`目录下的文件来自定义系统行为：

1. 修改对应的`.txt`文件
2. 更新`config/prompts_config.json`中的配置
3. 重启系统或重新加载配置

### 扩展搜索工具

系统采用插件化设计，支持扩展新的搜索工具：

```python
from relicseek.engine.tools import RelicSearchToolkit
from langchain.tools import Tool

# 创建自定义工具
custom_tool = Tool(
    name="custom_search",
    description="自定义搜索工具",
    func=your_custom_function
)

# 添加到工具包
toolkit = RelicSearchToolkit(config)
toolkit.tools.append(custom_tool)
```

### 质量评估定制

系统支持自定义质量评估标准，您可以在`prompts/quality_assessment.txt`中修改评估维度和标准。

## 📊 搜索结果格式

系统返回结构化的搜索结果，包含以下信息：

```json
{
  "success": true,
  "query": "用户查询",
  "search_id": "搜索ID",
  "analysis": {
    "complexity": "查询复杂度",
    "query_type": "查询类型",
    "entities": ["关键实体"]
  },
  "strategy": {
    "keywords": ["搜索关键词"],
    "search_steps": ["搜索步骤"]
  },
  "results": {
    "quality_score": 4.2,
    "confidence": "high",
    "recommendations": ["改进建议"]
  },
  "report": "最终的文物信息报告"
}
```

## 🛠️ 开发指南

### 项目结构

```
RelicSeek/
├── relicseek/                  # 主要代码包
│   ├── engine/                 # 引擎核心
│   │   ├── core.py            # 核心引擎
│   │   ├── agent.py           # 智能体实现
│   │   └── tools.py           # 工具集成
│   ├── interface/             # 用户界面
│   │   ├── streamlit_app.py   # Web界面
│   │   └── cli_app.py         # 命令行界面
│   └── config/                # 配置管理
│       ├── settings.py        # 配置类
│       └── prompt_manager.py  # Prompt管理
├── config/                    # 配置文件
│   ├── engine_config.json     # 引擎配置
│   └── prompts_config.json    # Prompt配置
├── prompts/                   # Prompt模板
│   ├── system/               # 系统Prompt
│   ├── query_analysis.txt    # 查询分析
│   ├── strategy_planning.txt # 策略规划
│   └── ...                   # 其他Prompt
├── docs/                     # 项目文档
├── app.py                    # Streamlit应用入口
├── relicseek_cli.py         # CLI应用入口
└── requirements.txt          # 依赖列表
```

### 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📋 TODO

- [ ] 添加更多搜索引擎支持
- [ ] 实现搜索结果缓存机制
- [ ] 添加用户反馈学习功能
- [ ] 支持多语言查询
- [ ] 实现搜索结果导出功能
- [ ] 添加API接口

## 🤝 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请：

1. 查看项目文档和FAQ
2. 提交Issue描述问题
3. 参与Discussion讨论

## 📄 许可证

本项目采用MIT许可证 - 详情请查看 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [LangChain](https://github.com/hwchase17/langchain) - 智能体框架
- [SearXNG](https://github.com/searxng/searxng) - 搜索引擎聚合
- [Streamlit](https://streamlit.io/) - Web应用框架
- [Rich](https://github.com/willmcgugan/rich) - 命令行美化

---

**RelicSeek** - 让文物搜索更智能，让文化传承更便捷！ 🏺✨

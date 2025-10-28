# RelicSeek 安装指南

本文档将指导您完成RelicSeek文物搜索智能体系统的安装和配置。

## 系统要求

### 基础环境
- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **内存**: 至少 4GB RAM
- **存储空间**: 至少 2GB 可用空间

### 外部服务
- **OpenAI API**: 需要有效的API密钥
- **SearXNG**: 可选，用于增强搜索功能

## 安装步骤

### 1. 获取源代码

```bash
# 从Git仓库克隆
git clone <repository-url>
cd RelicSeek

# 或者下载压缩包并解压
# unzip RelicSeek-main.zip
# cd RelicSeek-main
```

### 2. 创建虚拟环境

推荐使用虚拟环境来隔离项目依赖：

```bash
# 使用venv创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

#### 方法一：设置环境变量

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:SEARXNG_URL="http://localhost:8888"  # 可选
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
set SEARXNG_URL=http://localhost:8888
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export SEARXNG_URL="http://localhost:8888"  # 可选
```

#### 方法二：使用.env文件

在项目根目录创建`.env`文件：

```bash
# .env文件内容
OPENAI_API_KEY=your_openai_api_key_here
SEARXNG_URL=http://localhost:8888
```

### 5. 验证安装

运行以下命令验证安装是否成功：

```bash
# 验证系统配置
python relicseek_cli.py validate

# 查看帮助信息
python relicseek_cli.py --help
```

## 配置SearXNG（可选）

SearXNG是一个开源的搜索引擎聚合器，可以显著提升搜索质量。

### Docker方式安装（推荐）

```bash
# 拉取SearXNG镜像
docker pull searxng/searxng

# 运行SearXNG容器
docker run -d \
  --name searxng \
  -p 8888:8080 \
  -v "${PWD}/searxng:/etc/searxng" \
  -e "BASE_URL=http://localhost:8888/" \
  searxng/searxng
```

### 手动安装

```bash
# 克隆SearXNG
git clone https://github.com/searxng/searxng.git
cd searxng

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp searx/settings.yml.dist searx/settings.yml

# 运行SearXNG
python searx/webapp.py
```

### 配置验证

访问 `http://localhost:8888` 确认SearXNG运行正常。

## 配置文件说明

### 引擎配置文件

编辑 `config/engine_config.json` 来自定义系统行为：

```json
{
  "engine": {
    "model": {
      "provider": "openai",
      "model_name": "gpt-4-turbo-preview",
      "temperature": 0.7,
      "max_tokens": 2048,
      "timeout": 30
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
      "engines": ["bing", "google", "duckduckgo"],
      "language": "zh-CN"
    }
  }
}
```

### Prompt配置文件

`config/prompts_config.json` 定义了系统使用的提示词模板：

```json
{
  "prompts": {
    "query_analysis": {
      "file": "prompts/query_analysis.txt",
      "description": "分析用户查询意图和提取关键信息"
    },
    "strategy_planning": {
      "file": "prompts/strategy_planning.txt",
      "description": "制定搜索策略和执行计划"
    }
  }
}
```

## 启动系统

### Web界面方式

```bash
# 启动Streamlit应用
streamlit run app.py

# 或者指定端口
streamlit run app.py --server.port 8501
```

访问 `http://localhost:8501` 使用Web界面。

### 命令行方式

```bash
# 初始化引擎
python relicseek_cli.py init

# 交互式搜索
python relicseek_cli.py search

# 单次搜索
python relicseek_cli.py search -q "青铜器"
```

## 常见问题解决

### 1. ImportError: No module named 'langchain'

**解决方案**: 确保已安装所有依赖
```bash
pip install -r requirements.txt
```

### 2. OpenAI API错误

**可能原因**:
- API密钥未设置或错误
- API配额不足
- 网络连接问题

**解决方案**:
```bash
# 验证API密钥
echo $OPENAI_API_KEY

# 测试API连接
python -c "
import openai
openai.api_key = 'your_api_key'
print(openai.Model.list())
"
```

### 3. SearXNG连接失败

**解决方案**:
- 确认SearXNG服务运行在正确端口
- 检查防火墙设置
- 验证URL配置

```bash
# 测试SearXNG连接
curl http://localhost:8888/search?q=test&format=json
```

### 4. 配置文件未找到

**解决方案**:
- 确认文件路径正确
- 检查文件权限
- 使用绝对路径指定配置目录

```bash
# 使用自定义配置目录
python relicseek_cli.py -c /path/to/config search
```

### 5. 内存不足错误

**解决方案**:
- 减少 `max_tokens` 配置
- 降低 `memory_window_size`
- 使用更轻量的模型

## 性能优化

### 1. 模型选择

根据需求选择合适的模型：

```json
{
  "model": {
    "model_name": "gpt-3.5-turbo",  // 更快，成本更低
    // "model_name": "gpt-4-turbo-preview",  // 更准确，成本更高
    "temperature": 0.3,  // 降低随机性
    "max_tokens": 1500   // 减少token使用
  }
}
```

### 2. 搜索优化

```json
{
  "search": {
    "max_results_per_query": 10,  // 减少搜索结果数量
    "verification_rounds": 2,     // 减少验证轮数
    "quality_threshold": 0.8      // 提高质量阈值
  }
}
```

### 3. 缓存配置

```json
{
  "cache": {
    "enabled": true,
    "ttl": 7200,      // 2小时缓存
    "max_size": 500   // 最大缓存条目
  }
}
```

## 更新指南

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
```

### 迁移配置

检查配置文件格式是否有变化，必要时更新配置文件。

### 备份数据

```bash
# 备份配置文件
cp -r config config_backup_$(date +%Y%m%d)

# 备份日志文件
cp -r logs logs_backup_$(date +%Y%m%d)
```

## 下一步

安装完成后，建议：

1. 阅读 [用户指南](USER_GUIDE.md)
2. 查看 [API文档](API.md)
3. 尝试 [示例教程](EXAMPLES.md)

如果遇到问题，请查看 [故障排除指南](TROUBLESHOOTING.md) 或提交Issue。

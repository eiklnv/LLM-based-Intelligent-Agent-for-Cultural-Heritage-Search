#!/usr/bin/env python3
"""
RelicSeek CLI启动脚本
"""

import os
import sys
from pathlib import Path

def main():
    """启动RelicSeek CLI应用"""
    
    # 设置项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查环境变量，如果没有设置则设置为EMPTY
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "EMPTY"
        print("ℹ️  提示: OPENAI_API_KEY 环境变量未设置，已设置为 EMPTY")
        print("系统将使用配置文件中的API密钥设置")
        print("如需自定义，请设置:")
        print("Windows: set OPENAI_API_KEY=your_api_key")
        print("Linux/Mac: export OPENAI_API_KEY=your_api_key")
        print()
    
    # 启动CLI应用
    print("🏺 RelicSeek 文物搜索智能体 - 命令行界面")
    print("📖 使用说明:")
    print("  python run_cli.py search           # 交互式搜索")
    print("  python run_cli.py search -q '查询' # 单次搜索")
    print("  python run_cli.py validate         # 验证系统")
    print("  python run_cli.py status           # 查看状态")
    print("  python run_cli.py --help           # 查看帮助")
    print("-" * 50)
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    
    # 导入并运行CLI
    from relicseek.interface.cli_app import cli
    cli()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
RelicSeek Web启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动RelicSeek Web应用"""
    
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
    
    # 启动Streamlit应用
    print("🚀 启动RelicSeek Web应用...")
    print("📱 Web界面地址: http://localhost:8501")
    print("💡 提示: 使用 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")

if __name__ == "__main__":
    main()

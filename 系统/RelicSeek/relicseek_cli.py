#!/usr/bin/env python3
"""
RelicSeek CLI应用程序入口
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('PYTHONPATH', str(project_root))

from relicseek.interface.cli_app import cli

if __name__ == "__main__":
    cli()

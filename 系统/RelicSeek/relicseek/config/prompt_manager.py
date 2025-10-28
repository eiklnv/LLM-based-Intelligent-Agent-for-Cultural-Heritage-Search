"""
Prompt管理模块
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from string import Template


class PromptTemplate:
    """Prompt模板类"""
    
    def __init__(self, name: str, file_path: str, description: str, 
                 input_variables: List[str], output_format: str):
        self.name = name
        self.file_path = file_path
        self.description = description
        self.input_variables = input_variables
        self.output_format = output_format
        self._template_content: Optional[str] = None
    
    def load_template(self, prompts_dir: Path) -> str:
        """加载模板内容"""
        if self._template_content is None:
            template_file = prompts_dir / self.file_path
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    self._template_content = f.read()
            else:
                raise FileNotFoundError(f"Prompt模板文件不存在: {template_file}")
        return self._template_content
    
    def format(self, prompts_dir: Path, **kwargs) -> str:
        """格式化模板"""
        template_content = self.load_template(prompts_dir)
        template = Template(template_content)
        
        # 检查是否提供了所有必需的变量
        missing_vars = set(self.input_variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"缺少必需的模板变量: {missing_vars}")
        
        return template.safe_substitute(**kwargs)


class PromptManager:
    """Prompt管理器"""
    
    def __init__(self, config_dir: Optional[str] = None, prompts_dir: Optional[str] = None):
        """
        初始化Prompt管理器
        
        Args:
            config_dir: 配置文件目录
            prompts_dir: Prompt文件目录
        """
        if config_dir is None:
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        
        if prompts_dir is None:
            project_root = Path(__file__).parent.parent.parent
            prompts_dir = project_root / "prompts"
        
        self.config_dir = Path(config_dir)
        self.prompts_dir = Path(prompts_dir)
        self._prompts: Dict[str, PromptTemplate] = {}
        self._system_prompts: Dict[str, PromptTemplate] = {}
        self._loaded = False
    
    def load_prompts_config(self) -> None:
        """加载prompt配置"""
        if self._loaded:
            return
            
        config_file = self.config_dir / "prompts_config.json"
        if not config_file.exists():
            raise FileNotFoundError(f"Prompt配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 加载普通prompts
        for name, config in config_data.get("prompts", {}).items():
            self._prompts[name] = PromptTemplate(
                name=name,
                file_path=config["file"],
                description=config["description"],
                input_variables=config["input_variables"],
                output_format=config["output_format"]
            )
        
        # 加载系统prompts
        for name, config in config_data.get("system_prompts", {}).items():
            self._system_prompts[name] = PromptTemplate(
                name=name,
                file_path=config["file"],
                description=config["description"],
                input_variables=[],  # 系统prompt通常不需要变量
                output_format="natural"
            )
        
        self._loaded = True
    
    def get_prompt(self, name: str, **kwargs) -> str:
        """获取格式化的prompt"""
        if not self._loaded:
            self.load_prompts_config()
        
        if name not in self._prompts:
            raise ValueError(f"未找到名为 '{name}' 的prompt模板")
        
        template = self._prompts[name]
        return template.format(self.prompts_dir, **kwargs)
    
    def get_system_prompt(self, name: str) -> str:
        """获取系统prompt"""
        if not self._loaded:
            self.load_prompts_config()
        
        if name not in self._system_prompts:
            raise ValueError(f"未找到名为 '{name}' 的系统prompt模板")
        
        template = self._system_prompts[name]
        return template.format(self.prompts_dir)
    
    def list_prompts(self) -> List[str]:
        """列出所有可用的prompt"""
        if not self._loaded:
            self.load_prompts_config()
        return list(self._prompts.keys())
    
    def list_system_prompts(self) -> List[str]:
        """列出所有可用的系统prompt"""
        if not self._loaded:
            self.load_prompts_config()
        return list(self._system_prompts.keys())
    
    def get_prompt_info(self, name: str) -> Dict[str, Any]:
        """获取prompt信息"""
        if not self._loaded:
            self.load_prompts_config()
        
        if name in self._prompts:
            template = self._prompts[name]
        elif name in self._system_prompts:
            template = self._system_prompts[name]
        else:
            raise ValueError(f"未找到名为 '{name}' 的prompt模板")
        
        return {
            "name": template.name,
            "description": template.description,
            "input_variables": template.input_variables,
            "output_format": template.output_format,
            "file_path": template.file_path
        }
    
    def reload_prompts(self) -> None:
        """重新加载prompt配置"""
        self._prompts.clear()
        self._system_prompts.clear()
        self._loaded = False
        # 清除已缓存的模板内容
        for template in list(self._prompts.values()) + list(self._system_prompts.values()):
            template._template_content = None

"""
命令行界面
"""
import click
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
import traceback

from ..engine.core import RelicSeekEngine


class CLIInterface:
    """命令行界面"""
    
    def __init__(self):
        """初始化CLI界面"""
        self.console = Console()
        self.engine: Optional[RelicSeekEngine] = None
        self.session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def initialize_engine(self, config_dir: Optional[str] = None) -> bool:
        """
        初始化引擎
        
        Args:
            config_dir: 配置文件目录
            
        Returns:
            是否初始化成功
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("正在初始化RelicSeek引擎...", total=None)
                self.engine = RelicSeekEngine(config_dir)
                progress.update(task, description="引擎初始化完成!")
            
            self.console.print("✅ [green]引擎初始化成功![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]引擎初始化失败: {str(e)}[/red]")
            self.console.print(f"[dim]详细错误: {traceback.format_exc()}[/dim]")
            return False
    
    def search_interactive(self):
        """交互式搜索模式"""
        self.console.print(Panel.fit(
            "[bold blue]🏺 RelicSeek 文物搜索智能体[/bold blue]\n"
            "[dim]交互式搜索模式 - 输入 'exit' 或 'quit' 退出[/dim]",
            border_style="blue"
        ))
        
        if not self.engine:
            self.console.print("❌ [red]引擎未初始化，请先运行初始化命令[/red]")
            return
        
        search_count = 0
        
        while True:
            try:
                # 获取用户输入
                query = Prompt.ask("\n[bold cyan]🔍 请输入您要搜索的文物信息[/bold cyan]")
                
                if query.lower() in ['exit', 'quit', '退出']:
                    self.console.print("👋 [yellow]再见![/yellow]")
                    break
                
                if not query.strip():
                    continue
                
                search_count += 1
                
                # 执行搜索
                result = self.search_single(query, show_progress=True)
                
                if result:
                    # 显示结果
                    self.display_search_result(result, search_count)
                    
                    # 询问是否继续
                    if not Confirm.ask("\n[dim]是否继续搜索?[/dim]", default=True):
                        break
                
            except KeyboardInterrupt:
                self.console.print("\n👋 [yellow]搜索被中断，再见![/yellow]")
                break
            except Exception as e:
                self.console.print(f"❌ [red]搜索过程中出现错误: {str(e)}[/red]")
    
    def search_single(self, query: str, show_progress: bool = False) -> Optional[Dict[str, Any]]:
        """
        执行单次搜索
        
        Args:
            query: 搜索查询
            show_progress: 是否显示进度
            
        Returns:
            搜索结果
        """
        if not self.engine:
            self.console.print("❌ [red]引擎未初始化[/red]")
            return None
        
        try:
            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("🤖 智能体正在搜索中...", total=None)
                    result = self.engine.search(query, session_id=self.session_id)
                    progress.update(task, description="搜索完成!")
            else:
                result = self.engine.search(query, session_id=self.session_id)
            
            return result
            
        except Exception as e:
            self.console.print(f"❌ [red]搜索失败: {str(e)}[/red]")
            return None
    
    def display_search_result(self, result: Dict[str, Any], search_number: int = 1):
        """
        显示搜索结果
        
        Args:
            result: 搜索结果
            search_number: 搜索序号
        """
        self.console.print("\n" + "="*80)
        
        # 结果概览
        if result.get('success', False):
            self.console.print(f"✅ [green]搜索 #{search_number} 成功![/green]")
            
            # 基本信息表格
            table = Table(title="搜索结果概览", border_style="green")
            table.add_column("项目", style="cyan", no_wrap=True)
            table.add_column("值", style="white")
            
            table.add_row("搜索ID", result.get('search_id', 'N/A'))
            table.add_row("查询", result.get('query', 'N/A'))
            
            # 质量信息
            results_data = result.get('results', {})
            quality_score = results_data.get('quality_score', 0)
            confidence = results_data.get('confidence', 'unknown')
            
            table.add_row("质量评分", f"{quality_score:.1f}/5.0")
            table.add_row("置信度", confidence)
            
            self.console.print(table)
            
            # 显示最终报告
            if 'report' in result and result['report']:
                self.console.print("\n📄 [bold]文物信息报告:[/bold]")
                self.console.print(Panel(
                    Markdown(result['report']),
                    border_style="green",
                    title="📋 详细报告"
                ))
            
            # 显示搜索过程
            if Confirm.ask("\n[dim]是否查看详细搜索过程?[/dim]", default=False):
                self.display_search_process(result)
            
        else:
            self.console.print(f"❌ [red]搜索 #{search_number} 失败![/red]")
            error_msg = result.get('error', '未知错误')
            self.console.print(f"[red]错误信息: {error_msg}[/red]")
    
    def display_search_process(self, result: Dict[str, Any]):
        """显示详细搜索过程"""
        
        # 查询分析
        if 'analysis' in result:
            self.console.print("\n🧠 [bold]查询分析:[/bold]")
            analysis = result['analysis']
            if isinstance(analysis, dict):
                analysis_table = Table(border_style="blue")
                analysis_table.add_column("分析项", style="cyan")
                analysis_table.add_column("结果", style="white")
                
                analysis_table.add_row("复杂度", str(analysis.get('complexity', 'N/A')))
                analysis_table.add_row("查询类型", str(analysis.get('query_type', 'N/A')))
                
                entities = analysis.get('entities', [])
                if entities:
                    analysis_table.add_row("关键实体", ", ".join(entities))
                
                self.console.print(analysis_table)
        
        # 搜索策略
        if 'strategy' in result:
            self.console.print("\n📋 [bold]搜索策略:[/bold]")
            strategy = result['strategy']
            if isinstance(strategy, dict):
                keywords = strategy.get('keywords', [])
                if keywords:
                    self.console.print(f"🔑 关键词: {', '.join(keywords)}")
                
                steps = strategy.get('search_steps', [])
                if steps:
                    self.console.print("📝 搜索步骤:")
                    for i, step in enumerate(steps, 1):
                        self.console.print(f"  {i}. {step}")
        
        # 质量分析
        results_data = result.get('results', {})
        if 'reflection' in results_data:
            self.console.print("\n🤔 [bold]系统反思:[/bold]")
            self.console.print(Panel(
                results_data['reflection'],
                border_style="yellow",
                title="反思内容"
            ))
        
        # 改进建议
        recommendations = results_data.get('recommendations', [])
        if recommendations:
            self.console.print("\n💡 [bold]改进建议:[/bold]")
            for rec in recommendations:
                self.console.print(f"  • {rec}")
    
    def validate_system(self):
        """验证系统设置"""
        if not self.engine:
            self.console.print("❌ [red]引擎未初始化[/red]")
            return
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("正在验证系统设置...", total=None)
                validation_result = self.engine.validate_setup()
            
            self.console.print("\n🔍 [bold]系统验证结果:[/bold]")
            
            overall_status = validation_result['overall_status']
            if overall_status == 'success':
                self.console.print("✅ [green]系统配置验证通过![/green]")
            elif overall_status == 'warning':
                self.console.print("⚠️ [yellow]系统配置存在警告[/yellow]")
            else:
                self.console.print("❌ [red]系统配置存在错误[/red]")
            
            # 详细检查结果表格
            table = Table(title="详细检查结果", border_style="blue")
            table.add_column("检查项", style="cyan", no_wrap=True)
            table.add_column("状态", style="white", no_wrap=True)
            table.add_column("说明", style="white")
            
            for check_name, check_result in validation_result['checks'].items():
                status = check_result['status']
                message = check_result['message']
                
                status_icon = {
                    'success': '✅',
                    'warning': '⚠️',
                    'error': '❌'
                }.get(status, '❓')
                
                status_color = {
                    'success': 'green',
                    'warning': 'yellow',
                    'error': 'red'
                }.get(status, 'white')
                
                table.add_row(
                    check_name,
                    f"[{status_color}]{status_icon} {status}[/{status_color}]",
                    message
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ [red]验证过程中出现错误: {str(e)}[/red]")
    
    def show_engine_status(self):
        """显示引擎状态"""
        if not self.engine:
            self.console.print("❌ [red]引擎未初始化[/red]")
            return
        
        try:
            status = self.engine.get_engine_status()
            
            self.console.print("\n📊 [bold]引擎状态信息:[/bold]")
            
            # 基本状态
            status_table = Table(title="基本状态", border_style="green")
            status_table.add_column("项目", style="cyan")
            status_table.add_column("状态", style="white")
            
            status_table.add_row("引擎状态", "✅ 运行中" if status['initialized'] else "❌ 未初始化")
            status_table.add_row("更新时间", status['timestamp'])
            status_table.add_row("会话ID", self.session_id)
            
            if 'agent_status' in status:
                agent_status = status['agent_status']
                status_table.add_row("工具数量", str(agent_status.get('tools_count', 0)))
                status_table.add_row("记忆功能", "✅ 已启用" if agent_status.get('memory_enabled') else "❌ 未启用")
                status_table.add_row("对话长度", str(agent_status.get('conversation_length', 0)))
            
            self.console.print(status_table)
            
            # 配置信息
            if Confirm.ask("\n[dim]是否查看详细配置信息?[/dim]", default=False):
                config_info = status.get('config', {})
                self.console.print("\n⚙️ [bold]配置信息:[/bold]")
                self.console.print(Panel(
                    json.dumps(config_info, indent=2, ensure_ascii=False),
                    title="配置详情",
                    border_style="blue"
                ))
            
        except Exception as e:
            self.console.print(f"❌ [red]获取状态信息失败: {str(e)}[/red]")
    
    def export_results(self, output_file: str, search_results: list):
        """
        导出搜索结果
        
        Args:
            output_file: 输出文件路径
            search_results: 搜索结果列表
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_path.suffix.lower() == '.json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(search_results, f, ensure_ascii=False, indent=2)
            else:
                # 导出为文本格式
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("RelicSeek 搜索结果导出\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, result in enumerate(search_results, 1):
                        f.write(f"搜索 #{i}\n")
                        f.write(f"查询: {result.get('query', 'N/A')}\n")
                        f.write(f"搜索ID: {result.get('search_id', 'N/A')}\n")
                        f.write(f"状态: {'成功' if result.get('success') else '失败'}\n")
                        
                        if result.get('report'):
                            f.write("\n报告:\n")
                            f.write(result['report'])
                        
                        f.write("\n" + "-" * 50 + "\n\n")
            
            self.console.print(f"✅ [green]结果已导出到: {output_path}[/green]")
            
        except Exception as e:
            self.console.print(f"❌ [red]导出失败: {str(e)}[/red]")


# Click命令行接口
@click.group()
@click.option('--config-dir', '-c', help='配置文件目录路径')
@click.pass_context
def cli(ctx, config_dir):
    """RelicSeek 文物搜索智能体命令行工具"""
    ctx.ensure_object(dict)
    ctx.obj['config_dir'] = config_dir
    ctx.obj['interface'] = CLIInterface()


@cli.command()
@click.pass_context
def init(ctx):
    """初始化引擎"""
    interface = ctx.obj['interface']
    config_dir = ctx.obj['config_dir']
    
    interface.initialize_engine(config_dir)


@cli.command()
@click.option('--query', '-q', help='搜索查询（非交互模式）')
@click.option('--output', '-o', help='输出文件路径')
@click.pass_context
def search(ctx, query, output):
    """执行文物搜索"""
    interface = ctx.obj['interface']
    config_dir = ctx.obj['config_dir']
    
    # 初始化引擎
    if not interface.initialize_engine(config_dir):
        return
    
    if query:
        # 非交互模式
        result = interface.search_single(query, show_progress=True)
        if result:
            interface.display_search_result(result)
            
            if output:
                interface.export_results(output, [result])
    else:
        # 交互模式
        interface.search_interactive()


@cli.command()
@click.pass_context
def validate(ctx):
    """验证系统设置"""
    interface = ctx.obj['interface']
    config_dir = ctx.obj['config_dir']
    
    if interface.initialize_engine(config_dir):
        interface.validate_system()


@cli.command()
@click.pass_context
def status(ctx):
    """显示引擎状态"""
    interface = ctx.obj['interface']
    config_dir = ctx.obj['config_dir']
    
    if interface.initialize_engine(config_dir):
        interface.show_engine_status()


@cli.command()
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json']), help='输出格式')
@click.pass_context
def config(ctx, output_format):
    """显示配置信息"""
    interface = ctx.obj['interface']
    config_dir = ctx.obj['config_dir']
    
    if interface.initialize_engine(config_dir):
        status = interface.engine.get_engine_status()
        config_info = status.get('config', {})
        
        if output_format == 'json':
            interface.console.print(json.dumps(config_info, indent=2, ensure_ascii=False))
        else:
            interface.console.print("⚙️ [bold]当前配置:[/bold]")
            interface.console.print(Panel(
                json.dumps(config_info, indent=2, ensure_ascii=False),
                title="配置信息",
                border_style="blue"
            ))


if __name__ == '__main__':
    cli()

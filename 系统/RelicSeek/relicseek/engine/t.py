#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的 SearXNG 搜索程序
"""

from langchain_community.utilities import SearxSearchWrapper
import pprint


def search_with_searxng(searx_url, query, engines=None, count=10):
    """
    使用SearXNG进行搜索
    
    参数:
        searx_url: SearXNG服务器地址
        query: 搜索字符串
        engines: 搜索引擎列表 (可选)
        count: 返回结果数量
    """
    print(f"搜索服务器: {searx_url}")
    print(f"搜索内容: {query}")
    print(f"结果数量: {count}")
    if engines:
        print(f"指定引擎: {', '.join(engines)}")
    print("-" * 50)
    
    # 创建搜索器
    search_params = {
        "searx_host": searx_url,
        "k": count,
        "categories": ["general"]
    }
    
    # 如果指定了搜索引擎
    if engines:
        search_params["engines"] = engines
    
    searcher = SearxSearchWrapper(**search_params)
    
    try:
        # 执行搜索
        results = searcher.results(query)
        print(results)

        # 打印结果
        print("搜索结果:")
        print("=" * 50)
        
        # 如果返回的是字符串，按段落分割
        if isinstance(results, str):
            paragraphs = results.split('\n\n')
            for i, paragraph in enumerate(paragraphs, 1):
                if paragraph.strip():
                    print(f"\n结果 {i}:")
                    print(paragraph.strip())
                    print("-" * 30)
        else:
            print("返回结果格式:", type(results))
            print(results)
            
    except Exception as e:
        print(f"搜索失败: {e}")


def main():
    # 配置参数
    SEARX_URL = "http://search.deepidp.net:8080"  # 你的SearXNG地址
    QUERY = "马踏飞燕 甘肃省张掖市 东汉 青铜器"  # 搜索内容
    ENGINES = ["baidu", "google"]  # 指定搜索引擎，不指定则使用 None
    COUNT = 5  # 返回结果数量
    
    # 执行搜索
    search_with_searxng(
        searx_url=SEARX_URL,
        query=QUERY, 
        engines=ENGINES,  # 设为 None 使用所有引擎
        count=COUNT
    )


if __name__ == "__main__":
    main()
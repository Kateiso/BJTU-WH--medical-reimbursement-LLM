#!/usr/bin/env python3
"""
测试知识库搜索功能
"""
import json
import sys
from pathlib import Path

# 导入知识库搜索函数
sys.path.append(str(Path(__file__).parent))
from qwen_stream_app import search_knowledge, extract_keywords, detect_special_keywords, get_category_chinese_name, load_knowledge_base

def test_search(query):
    """测试搜索功能"""
    print(f"\n{'='*60}")
    print(f"测试查询: '{query}'")
    print(f"{'='*60}")
    
    # 提取关键词
    keywords = extract_keywords(query)
    print(f"提取的关键词: {keywords}")
    
    # 检测特殊关键词
    special_keywords = detect_special_keywords(query)
    if special_keywords:
        print(f"检测到特殊关键词: {special_keywords}")
    
    # 搜索知识库
    results = search_knowledge(query, limit=5)
    
    # 打印搜索结果
    print(f"\n找到 {len(results)} 条匹配结果")
    
    if results:
        print("\n搜索结果详情:")
        for i, result in enumerate(results):
            category_name = get_category_chinese_name(result.get("category", ""))
            print(f"\n结果 {i+1}: [{category_name}] {result.get('title')}")
            print(f"  ID: {result.get('id')}")
            print(f"  分数: {result.get('score')}")
            
            # 打印内容摘要
            content = result.get('content', '')
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"  内容: {content}")
            
            # 打印特殊字段
            if "name" in result:
                print(f"  姓名: {result.get('name')}")
            if "office_location" in result:
                print(f"  办公地点: {result.get('office_location')}")
            if "role" in result:
                print(f"  职责: {result.get('role')}")
            if "question" in result:
                print(f"  问题: {result.get('question')}")
                if "answer" in result:
                    print(f"  回答: {result.get('answer')}")
    else:
        print("未找到匹配结果")

if __name__ == "__main__":
    # 加载知识库
    KNOWLEDGE_BASE_PATH = str(Path(__file__).parent / "data" / "knowledge_base.json")
    print(f"知识库路径: {KNOWLEDGE_BASE_PATH}")
    
    # 测试常春艳老师相关查询
    test_search("常春艳老师是谁？她在哪里办公？")
    
    # 测试报销政策查询
    test_search("学生住院报销比例是多少？")
    
    # 测试报销材料查询
    test_search("报销需要准备哪些材料？")
    
    # 测试寒暑假报销查询
    test_search("寒暑假期间的医疗费用如何报销？")

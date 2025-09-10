#!/usr/bin/env python3
"""
测试新知识库的加载和搜索功能
"""
import json
import os
from pathlib import Path
from typing import Dict, List

# 导入必要的函数
from qwen_stream_app import load_knowledge_base, search_knowledge

# 设置API密钥（虽然本测试不会实际调用API）
os.environ["DASHSCOPE_API_KEY"] = "sk-2ea7b3f8fb7742828ff836eed6050f19"

def test_knowledge_base():
    """测试知识库加载和搜索"""
    print("\n" + "="*50)
    print("测试新知识库")
    print("="*50)
    
    # 加载知识库
    KNOWLEDGE_BASE_PATH = str(Path(__file__).parent / "data" / "knowledge_base.json")
    print(f"知识库路径: {KNOWLEDGE_BASE_PATH}")
    knowledge_base = load_knowledge_base(KNOWLEDGE_BASE_PATH)
    
    # 测试搜索功能
    test_queries = [
        "报销找哪个老师？",
        "门诊报销比例是多少？",
        "住院报销需要什么材料？",
        "报销的截止日期是什么时候？",
        "感冒药能报销吗？",
        "常春艳老师在哪里办公？"
    ]
    
    print("\n" + "="*50)
    print("开始测试搜索功能")
    print("="*50)
    
    for query in test_queries:
        print(f"\n\n测试查询: '{query}'")
        print("-"*30)
        
        results = search_knowledge(query, limit=3)
        
        print(f"找到 {len(results)} 条匹配结果:")
        for i, result in enumerate(results):
            print(f"\n结果 {i+1}:")
            print(f"  分类: {result.get('category')}")
            print(f"  标题: {result.get('title')}")
            print(f"  分数: {result.get('score')}")
            
            # 打印内容摘要
            content = result.get('content', '')
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"  内容: {content}")
            
            # 打印特殊字段
            if "question" in result:
                print(f"  问题: {result.get('question')}")
            if "answer" in result:
                answer = result.get('answer', '')
                if len(answer) > 100:
                    answer = answer[:100] + "..."
                print(f"  回答: {answer}")
            if "name" in result:
                print(f"  姓名: {result.get('name')}")
            if "dept" in result:
                print(f"  部门: {result.get('dept')}")
            if "office" in result:
                print(f"  办公地点: {result.get('office')}")
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)

if __name__ == "__main__":
    test_knowledge_base()

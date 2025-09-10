#!/usr/bin/env python3
"""
测试RAG修复效果
"""
import json
import sys
import asyncio
from pathlib import Path

# 导入必要的函数
sys.path.append(str(Path(__file__).parent))
from qwen_stream_app import search_knowledge, extract_keywords, detect_special_keywords, get_category_chinese_name, load_knowledge_base
from src.core.rag.qwen_stream_integration import QwenStreamLLM

# 测试用例 - 针对之前出现问题的查询
TEST_QUERIES = [
    "门诊和住院报销的截止时间是什么时候?",
    "报销后多久能到账?",
    "如需进一步咨询，可联系医保办常春艳老师吗?",
    "常春艳老师是谁？她在哪里办公？",
    "学生住院报销比例是多少？"
]

async def test_query(query, qwen_llm):
    """测试单个查询"""
    print(f"\n{'='*80}")
    print(f"测试查询: '{query}'")
    print(f"{'='*80}")
    
    # 搜索知识库
    results = search_knowledge(query, limit=3)
    
    # 打印搜索结果
    print(f"\n找到 {len(results)} 条匹配结果:")
    for i, result in enumerate(results):
        title = result.get("title") or result.get("question", "无标题")
        print(f"结果 {i+1}: {title} (分数: {result.get('score')})")
    
    # 构建上下文
    context = ""
    for i, item in enumerate(results):
        # 获取分类名称的中文表示
        category_name = get_category_chinese_name(item.get("category", ""))
        
        # 构建结构化的知识条目
        context += f"【知识条目 {i+1}】\n"
        context += f"分类: {category_name}\n"
        
        # 对于FAQ类型，优先使用question作为标题
        if item.get("category") == "common_questions" and "question" in item:
            context += f"标题: {item.get('question', '')}\n"
        else:
            title = item.get('title', '')
            if title:
                context += f"标题: {title}\n"
        
        # 添加特定字段
        if item.get("category") == "common_questions":
            if "question" in item and not context.find(f"标题: {item.get('question', '')}") >= 0:
                context += f"问题: {item.get('question', '')}\n"
            if "answer" in item:
                context += f"回答: {item.get('answer', '')}\n"
        elif item.get("category") == "contacts":
            if "name" in item:
                context += f"姓名: {item.get('name', '')}\n"
            if "dept" in item:
                context += f"部门: {item.get('dept', '')}\n"
            if "role" in item:
                context += f"职责: {item.get('role', '')}\n"
            if "office_location" in item:
                context += f"办公地点: {item.get('office_location', '')}\n"
        elif item.get("category") == "hospitals":
            if "name" in item:
                context += f"医院名称: {item.get('name', '')}\n"
            if "contract_status" in item:
                context += f"合同状态: {item.get('contract_status', '')}\n"
        elif item.get("category") == "materials_requirements":
            if "checklist" in item:
                context += "所需材料清单:\n"
                for material in item.get("checklist", []):
                    context += f"- {material}\n"
        
        # 添加通用内容
        context += f"内容: {item.get('content', '')}\n"
        
        # 添加重要的额外字段
        if "ratio" in item:
            context += f"报销比例: {item.get('ratio', '')}\n"
        if "notes" in item:
            context += f"注意事项: {item.get('notes', '')}\n"
        if "tags" in item:
            context += f"标签: {', '.join(item.get('tags', []))}\n"
        
        # 添加分隔符
        context += "\n---\n\n"
    
    print(f"\n构建的上下文长度: {len(context)} 字符")
    
    # 生成回答
    print("\n生成回答中...")
    answer = qwen_llm.rag_generate(query, context)
    
    print("\n生成的回答:")
    print("-" * 40)
    print(answer)
    print("-" * 40)
    
    # 检查回答是否包含占位符文本
    placeholders = ["[请参考", "[根据", "[联系方式", "[添加"]
    has_placeholder = any(ph in answer for ph in placeholders)
    if has_placeholder:
        print("\n⚠️ 警告: 回答中包含占位符文本!")
        for ph in placeholders:
            if ph in answer:
                print(f"  - 发现占位符: '{ph}'")
    else:
        print("\n✅ 回答中没有占位符文本")
    
    # 检查回答是否基于知识库内容
    keywords = []
    for result in results:
        if result.get("title"):
            keywords.append(result.get("title").lower())
        if result.get("question"):
            keywords.append(result.get("question").lower())
        if result.get("answer"):
            # 从答案中提取关键短语
            answer_text = result.get("answer").lower()
            if len(answer_text) > 10:
                keywords.append(answer_text[:10])
    
    # 检查回答中是否包含知识库中的关键词
    found_keywords = []
    for kw in keywords:
        if kw and len(kw) > 5 and kw in answer.lower():
            found_keywords.append(kw)
    
    if found_keywords:
        print(f"\n✅ 回答中包含 {len(found_keywords)} 个知识库关键词:")
        for kw in found_keywords[:3]:  # 只显示前3个
            print(f"  - '{kw}'")
    else:
        print("\n⚠️ 警告: 回答中未找到知识库关键词!")
    
    return {
        "query": query,
        "results_count": len(results),
        "context_length": len(context),
        "answer_length": len(answer),
        "has_placeholder": has_placeholder,
        "keywords_found": len(found_keywords)
    }

async def main():
    """主函数"""
    print("开始测试RAG修复效果...")
    
    # 加载知识库
    KNOWLEDGE_BASE_PATH = str(Path(__file__).parent / "data" / "knowledge_base.json")
    print(f"知识库路径: {KNOWLEDGE_BASE_PATH}")
    
    # 创建通义千问实例
    qwen_llm = QwenStreamLLM()
    
    # 测试所有查询
    results = []
    for query in TEST_QUERIES:
        result = await test_query(query, qwen_llm)
        results.append(result)
    
    # 打印汇总结果
    print("\n" + "="*80)
    print("测试结果汇总:")
    print("="*80)
    
    success_count = sum(1 for r in results if not r["has_placeholder"] and r["keywords_found"] > 0)
    print(f"总测试用例: {len(TEST_QUERIES)}")
    print(f"成功用例: {success_count}")
    print(f"失败用例: {len(TEST_QUERIES) - success_count}")
    
    if success_count == len(TEST_QUERIES):
        print("\n✅ 所有测试用例通过!")
    else:
        print("\n⚠️ 有测试用例失败，请检查详细日志")

if __name__ == "__main__":
    asyncio.run(main())

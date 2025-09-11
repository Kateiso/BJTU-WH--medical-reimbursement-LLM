#!/usr/bin/env python3
"""
知识库条目添加示例
演示如何通过代码添加新的知识库条目
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.knowledge.json_manager import JSONKnowledgeManager
from src.core.knowledge.base import KnowledgeItem

async def add_example_items():
    """添加示例知识条目"""
    # 初始化管理器
    manager = JSONKnowledgeManager()
    await manager.load()
    
    print("🚀 开始添加示例知识条目...")
    
    # 示例1: 添加新政策
    policy_item = KnowledgeItem(
        category="policy",
        title="学生体检报销政策",
        content="学生年度体检费用可报销80%，需提供体检报告和发票。体检项目包括：血常规、尿常规、心电图、胸片等基础项目。",
        tags=["体检", "报销", "学生", "年度体检"],
        metadata={"priority": "medium", "effective_date": "2024-01-01"}
    )
    
    success = await manager.add_item(policy_item)
    if success:
        print(f"✅ 成功添加政策条目: {policy_item.title}")
    else:
        print("❌ 添加政策条目失败")
    
    # 示例2: 添加新医院信息
    hospital_item = KnowledgeItem(
        category="hospitals",
        title="威海市妇幼保健院信息",
        content="威海市妇幼保健院位于威海市环翠区文化中路，电话：0631-3806666。专科特色：妇科、产科、儿科。预约方式：微信公众号'威海妇幼'或现场挂号。",
        tags=["医院", "妇幼保健", "威海", "专科"],
        metadata={
            "address": "威海市环翠区文化中路",
            "phone": "0631-3806666",
            "specialties": ["妇科", "产科", "儿科"],
            "appointment": "微信公众号'威海妇幼'"
        }
    )
    
    success = await manager.add_item(hospital_item)
    if success:
        print(f"✅ 成功添加医院条目: {hospital_item.title}")
    else:
        print("❌ 添加医院条目失败")
    
    # 示例3: 添加常见问题
    faq_item = KnowledgeItem(
        category="common_questions",
        title="体检费用报销流程",
        question="体检费用如何报销？",
        answer="体检费用报销流程：1. 完成体检后保留所有发票和报告；2. 填写报销申请表；3. 携带材料到思源东楼812B找常春艳老师；4. 审核通过后3-6个月到账。",
        tags=["体检", "报销流程", "常见问题"],
        metadata={"type": "faq", "priority": "high"}
    )
    
    success = await manager.add_item(faq_item)
    if success:
        print(f"✅ 成功添加FAQ条目: {faq_item.title}")
    else:
        print("❌ 添加FAQ条目失败")
    
    # 示例4: 添加联系人信息
    contact_item = KnowledgeItem(
        category="contacts",
        title="体检中心联系人",
        content="体检中心负责人：王医生，办公地点：校医院2楼体检科，联系电话：0631-5688888，办公时间：周一至周五 8:00-17:00。",
        name="王医生",
        dept="体检中心",
        position="负责人",
        office="校医院2楼体检科",
        contact="0631-5688888",
        tags=["联系人", "体检中心", "王医生"],
        metadata={"type": "contact", "priority": "medium"}
    )
    
    success = await manager.add_item(contact_item)
    if success:
        print(f"✅ 成功添加联系人条目: {contact_item.title}")
    else:
        print("❌ 添加联系人条目失败")
    
    # 显示统计信息
    stats = await manager.get_stats()
    print(f"\n📊 当前知识库统计:")
    print(f"   总条目数: {stats['total_items']}")
    print(f"   分类数: {len(stats['categories'])}")
    
    print("\n🎉 示例条目添加完成！")

async def search_example():
    """搜索示例"""
    manager = JSONKnowledgeManager()
    await manager.load()
    
    print("\n🔍 搜索示例:")
    
    # 搜索体检相关条目
    results = await manager.search("体检", limit=5)
    print(f"搜索'体检'找到 {len(results)} 个条目:")
    for i, item in enumerate(results, 1):
        print(f"  {i}. [{item.category}] {item.title}")
    
    # 按分类搜索
    policy_items = await manager.get_by_category("policy")
    print(f"\n政策类条目共 {len(policy_items)} 个:")
    for i, item in enumerate(policy_items[:3], 1):
        print(f"  {i}. {item.title}")

if __name__ == "__main__":
    print("=" * 60)
    print("📚 知识库条目添加示例")
    print("=" * 60)
    
    # 运行示例
    asyncio.run(add_example_items())
    asyncio.run(search_example())
    
    print("\n" + "=" * 60)
    print("✨ 示例运行完成！")
    print("💡 提示: 可以使用以下命令查看结果:")
    print("   python scripts/manage_knowledge.py list")
    print("   python scripts/manage_knowledge.py search 体检")
    print("=" * 60)

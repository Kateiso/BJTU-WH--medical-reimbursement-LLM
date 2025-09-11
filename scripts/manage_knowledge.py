#!/usr/bin/env python3
"""
知识库管理脚本
提供命令行界面来管理知识库条目
"""
import asyncio
import sys
import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.knowledge.json_manager import JSONKnowledgeManager
from src.core.knowledge.base import KnowledgeItem

class KnowledgeManagerCLI:
    """知识库管理命令行工具"""
    
    def __init__(self):
        self.manager = JSONKnowledgeManager()
    
    async def init(self):
        """初始化管理器"""
        await self.manager.load()
        print("✅ 知识库管理器初始化完成")
    
    async def add_item(self, category: str, title: str, content: str, tags: List[str] = None, metadata: Dict[str, Any] = None):
        """添加知识条目"""
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}
        
        item = KnowledgeItem(
            category=category,
            title=title,
            content=content,
            tags=tags,
            metadata=metadata
        )
        
        success = await self.manager.add_item(item)
        if success:
            print(f"✅ 成功添加条目: {item.id}")
            print(f"   标题: {item.title}")
            print(f"   分类: {item.category}")
            print(f"   标签: {', '.join(item.tags)}")
        else:
            print("❌ 添加条目失败")
    
    async def list_items(self, category: str = None, limit: int = 10):
        """列出知识条目"""
        if category:
            items = await self.manager.get_by_category(category)
        else:
            # 获取所有条目
            all_items = []
            categories = await self.manager.get_categories()
            for cat in categories:
                cat_items = await self.manager.get_by_category(cat)
                all_items.extend(cat_items)
            items = all_items
        
        if not items:
            print("📭 没有找到条目")
            return
        
        print(f"📋 找到 {len(items)} 个条目:")
        print("-" * 80)
        
        for i, item in enumerate(items[:limit], 1):
            print(f"{i:2d}. [{item.category}] {item.title}")
            print(f"    ID: {item.id}")
            print(f"    标签: {', '.join(item.tags) if item.tags else '无'}")
            print(f"    创建: {item.created_at}")
            print()
    
    async def search_items(self, query: str, category: str = None, limit: int = 10):
        """搜索知识条目"""
        results = await self.manager.search(query, category=category, limit=limit)
        
        if not results:
            print(f"🔍 没有找到包含 '{query}' 的条目")
            return
        
        print(f"🔍 找到 {len(results)} 个相关条目:")
        print("-" * 80)
        
        for i, item in enumerate(results, 1):
            score = item.metadata.get("search_score", 0)
            print(f"{i:2d}. [{item.category}] {item.title} (相关度: {score})")
            print(f"    ID: {item.id}")
            print(f"    内容: {item.content[:100]}{'...' if len(item.content) > 100 else ''}")
            print()
    
    async def get_item(self, item_id: str):
        """获取单个条目详情"""
        item = await self.manager.get_by_id(item_id)
        if not item:
            print(f"❌ 未找到 ID 为 '{item_id}' 的条目")
            return
        
        print(f"📄 条目详情:")
        print("-" * 80)
        print(f"ID: {item.id}")
        print(f"分类: {item.category}")
        print(f"标题: {item.title}")
        print(f"内容: {item.content}")
        print(f"标签: {', '.join(item.tags) if item.tags else '无'}")
        print(f"元数据: {json.dumps(item.metadata, ensure_ascii=False, indent=2)}")
        print(f"创建时间: {item.created_at}")
        print(f"更新时间: {item.updated_at}")
    
    async def update_item(self, item_id: str, **kwargs):
        """更新条目"""
        item = await self.manager.get_by_id(item_id)
        if not item:
            print(f"❌ 未找到 ID 为 '{item_id}' 的条目")
            return
        
        # 更新字段
        if 'title' in kwargs:
            item.title = kwargs['title']
        if 'content' in kwargs:
            item.content = kwargs['content']
        if 'category' in kwargs:
            item.category = kwargs['category']
        if 'tags' in kwargs:
            item.tags = kwargs['tags']
        if 'metadata' in kwargs:
            item.metadata.update(kwargs['metadata'])
        
        success = await self.manager.update_item(item)
        if success:
            print(f"✅ 成功更新条目: {item_id}")
        else:
            print("❌ 更新条目失败")
    
    async def delete_item(self, item_id: str):
        """删除条目"""
        item = await self.manager.get_by_id(item_id)
        if not item:
            print(f"❌ 未找到 ID 为 '{item_id}' 的条目")
            return
        
        print(f"⚠️  即将删除条目:")
        print(f"   标题: {item.title}")
        print(f"   分类: {item.category}")
        
        confirm = input("确认删除? (y/N): ").strip().lower()
        if confirm == 'y':
            success = await self.manager.delete_item(item_id)
            if success:
                print(f"✅ 成功删除条目: {item_id}")
            else:
                print("❌ 删除条目失败")
        else:
            print("❌ 取消删除")
    
    async def get_stats(self):
        """获取统计信息"""
        stats = await self.manager.get_stats()
        
        print("📊 知识库统计信息:")
        print("-" * 80)
        print(f"总条目数: {stats['total_items']}")
        print(f"文件路径: {stats['file_path']}")
        print(f"加载状态: {'已加载' if stats['loaded'] else '未加载'}")
        print()
        
        if stats['categories']:
            print("分类统计:")
            for category, count in stats['categories'].items():
                print(f"  {category}: {count} 条")
    
    async def get_categories(self):
        """获取所有分类"""
        categories = await self.manager.get_categories()
        
        print("📂 知识库分类:")
        print("-" * 80)
        for i, category in enumerate(categories, 1):
            count = len(await self.manager.get_by_category(category))
            print(f"{i:2d}. {category} ({count} 条)")
    
    async def backup(self, backup_path: str = None):
        """备份知识库"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/knowledge_base_backup_{timestamp}.json"
        
        # 读取当前数据
        with open(self.manager.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 写入备份文件
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 知识库已备份到: {backup_path}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="知识库管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加条目
    add_parser = subparsers.add_parser('add', help='添加知识条目')
    add_parser.add_argument('--category', required=True, help='分类')
    add_parser.add_argument('--title', required=True, help='标题')
    add_parser.add_argument('--content', required=True, help='内容')
    add_parser.add_argument('--tags', nargs='*', default=[], help='标签')
    add_parser.add_argument('--metadata', type=json.loads, default={}, help='元数据 (JSON格式)')
    
    # 列出条目
    list_parser = subparsers.add_parser('list', help='列出知识条目')
    list_parser.add_argument('--category', help='按分类过滤')
    list_parser.add_argument('--limit', type=int, default=10, help='显示数量限制')
    
    # 搜索条目
    search_parser = subparsers.add_parser('search', help='搜索知识条目')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--category', help='按分类过滤')
    search_parser.add_argument('--limit', type=int, default=10, help='结果数量限制')
    
    # 获取条目
    get_parser = subparsers.add_parser('get', help='获取条目详情')
    get_parser.add_argument('item_id', help='条目ID')
    
    # 更新条目
    update_parser = subparsers.add_parser('update', help='更新条目')
    update_parser.add_argument('item_id', help='条目ID')
    update_parser.add_argument('--title', help='新标题')
    update_parser.add_argument('--content', help='新内容')
    update_parser.add_argument('--category', help='新分类')
    update_parser.add_argument('--tags', nargs='*', help='新标签')
    update_parser.add_argument('--metadata', type=json.loads, help='新元数据 (JSON格式)')
    
    # 删除条目
    delete_parser = subparsers.add_parser('delete', help='删除条目')
    delete_parser.add_argument('item_id', help='条目ID')
    
    # 统计信息
    subparsers.add_parser('stats', help='获取统计信息')
    
    # 分类列表
    subparsers.add_parser('categories', help='获取分类列表')
    
    # 备份
    backup_parser = subparsers.add_parser('backup', help='备份知识库')
    backup_parser.add_argument('--path', help='备份文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化管理器
    cli = KnowledgeManagerCLI()
    await cli.init()
    
    # 执行命令
    try:
        if args.command == 'add':
            await cli.add_item(
                category=args.category,
                title=args.title,
                content=args.content,
                tags=args.tags,
                metadata=args.metadata
            )
        elif args.command == 'list':
            await cli.list_items(category=args.category, limit=args.limit)
        elif args.command == 'search':
            await cli.search_items(args.query, category=args.category, limit=args.limit)
        elif args.command == 'get':
            await cli.get_item(args.item_id)
        elif args.command == 'update':
            update_kwargs = {}
            if args.title is not None:
                update_kwargs['title'] = args.title
            if args.content is not None:
                update_kwargs['content'] = args.content
            if args.category is not None:
                update_kwargs['category'] = args.category
            if args.tags is not None:
                update_kwargs['tags'] = args.tags
            if args.metadata is not None:
                update_kwargs['metadata'] = args.metadata
            
            await cli.update_item(args.item_id, **update_kwargs)
        elif args.command == 'delete':
            await cli.delete_item(args.item_id)
        elif args.command == 'stats':
            await cli.get_stats()
        elif args.command == 'categories':
            await cli.get_categories()
        elif args.command == 'backup':
            await cli.backup(args.path)
    
    except Exception as e:
        print(f"❌ 执行命令失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

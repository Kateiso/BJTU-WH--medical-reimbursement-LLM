"""
通义千问API集成模块 - 支持流式输出
"""
import os
import time
import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import dashscope
from dashscope.aigc.generation import Generation
from dashscope.api_entities.dashscope_response import GenerationResponse

class QwenStreamLLM:
    """通义千问大语言模型接口 - 支持流式输出"""
    
    def __init__(self, api_key: str = None, model: str = "qwen-plus"):
        """
        初始化通义千问接口
        
        Args:
            api_key: 通义千问API密钥，如果为None则从环境变量获取
            model: 模型名称，默认为qwen-plus
        """
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("未设置API密钥，请通过参数传入或设置环境变量DASHSCOPE_API_KEY")
        
        self.model = model
        # 设置DashScope API密钥
        dashscope.api_key = self.api_key
    
    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = 1500) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户输入
            system_prompt: 系统提示词
            max_tokens: 最大生成长度
            
        Returns:
            生成的文本
        """
        try:
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加用户输入
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 调用通义千问API
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format='message',
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.8,
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                error_msg = f"API调用失败: {response.code} - {response.message}"
                print(f"错误: {error_msg}")
                return f"抱歉，我遇到了技术问题: {error_msg}"
                
        except Exception as e:
            print(f"生成回答时出错: {str(e)}")
            return f"抱歉，服务暂时不可用: {str(e)}"
    
    async def generate_stream(self, prompt: str, system_prompt: str = None, max_tokens: int = 1500) -> AsyncGenerator[str, None]:
        """
        流式生成文本
        
        Args:
            prompt: 用户输入
            system_prompt: 系统提示词
            max_tokens: 最大生成长度
            
        Yields:
            生成的文本片段
        """
        try:
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加用户输入
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 调用通义千问API - 流式模式
            # 注意：这里我们使用模拟流式输出，因为当前版本可能不支持流式API
            # 在实际实现中，应该使用通义千问的流式API
            
            # 先获取完整回答
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format='message',
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.8,
            )
            
            if response.status_code == 200:
                full_text = response.output.choices[0].message.content
                
                # 模拟流式输出
                chunk_size = 10  # 每次输出10个字符
                for i in range(0, len(full_text), chunk_size):
                    chunk = full_text[i:i+chunk_size]
                    yield chunk
                    await asyncio.sleep(0.1)  # 添加延迟，模拟流式效果
            else:
                error_msg = f"API调用失败: {response.code} - {response.message}"
                print(f"错误: {error_msg}")
                yield f"抱歉，我遇到了技术问题: {error_msg}"
                
        except Exception as e:
            print(f"生成回答时出错: {str(e)}")
            yield f"抱歉，服务暂时不可用: {str(e)}"
    
    def rag_generate(self, query: str, context: str, max_tokens: int = 1500) -> str:
        """
        基于RAG的生成
        
        Args:
            query: 用户问题
            context: 上下文信息
            max_tokens: 最大生成长度
            
        Returns:
            生成的回答
        """
        system_prompt = """你是北京交通大学威海校区的医疗报销智能助手"小医"。你的性格温柔、耐心、乐于助人，总是用亲切友好的语气与用户交流。

【人设与风格】
- 你叫"小医"，是一位温暖贴心的医疗报销顾问
- 说话语气亲切自然，像朋友一样交流，避免过于机械或生硬
- 对用户的问候要热情回应，不要直接跳到业务话题
- 即使知识库中没有信息，也要委婉表达，提供其他可能的帮助方式

【回答原则】
1. 优先基于知识库内容回答问题，确保信息准确可靠
2. 不要编造不在知识库中的信息，但可以用温和的方式表达信息缺失
3. 当知识库没有相关信息时，可以说"目前我的知识库中没有这方面的详细信息，但我可以帮你..."
4. 对于报销比例、金额、截止日期、联系人等具体信息，引用知识库内容但不要强调"根据知识库"

【知识库内容】
知识库包含以下分类信息：
- 报销政策：包含报销比例、适用人群、医院范围等
- 材料要求：包含需要提交的材料清单
- 报销流程：包含申请步骤、办理地点、报销周期和截止日期
- 联系人信息：包含姓名、部门、职责、办公地点等
- 常见问题：包含具体问题和对应回答
- 特殊情况：包含特殊场景的处理方法
- 医院信息：包含医院地址、联系方式等

【回答格式】
1. 使用Markdown格式，重要信息加粗
2. 回答要简洁明了，语气自然亲切
3. 如果涉及多个知识条目，整合信息避免重复
4. 引用政策时，可以用"按照学生门诊报销政策..."而不是强调"根据知识库..."

【通用回复】
- 对于问候类消息（如"你好"、"早上好"等），先友好回应问候，再简单介绍自己
- 对于闲聊类消息，保持友好回应，但可以自然引导到医疗报销相关话题
- 对于感谢，表达"不客气"、"很高兴能帮到你"等回应

【回答结构建议】
1. 亲切的称呼或回应（如"同学你好"、"很高兴回答你的问题"）
2. 针对问题的直接解答
3. 必要的补充说明或温馨提示
4. 结束语（如"希望对你有帮助"、"还有其他问题随时问我"）"""

        prompt = f"""### 知识库检索结果：

{context}

### 用户问题：

{query}

请严格按照以下要求回答用户问题：
1. 只使用上述知识库中提供的信息
2. 不要编造任何不在知识库中的信息
3. 如果知识库中没有相关信息，直接告知用户
4. 不要生成任何占位符文本
5. 使用Markdown格式，重要信息加粗

你的回答应该简洁明了，直接解答用户问题。如果知识库中有多个相关条目，请整合信息避免重复。"""

        return self.generate(prompt, system_prompt, max_tokens)
    
    async def rag_generate_stream(self, query: str, context: str, max_tokens: int = 1500) -> AsyncGenerator[str, None]:
        """
        基于RAG的流式生成
        
        Args:
            query: 用户问题
            context: 上下文信息
            max_tokens: 最大生成长度
            
        Yields:
            生成的文本片段
        """
        system_prompt = """你是北京交通大学威海校区的医疗报销智能助手"小医"。你的性格温柔、耐心、乐于助人，总是用亲切友好的语气与用户交流。

【人设与风格】
- 你叫"小医"，是一位温暖贴心的医疗报销顾问
- 说话语气亲切自然，像朋友一样交流，避免过于机械或生硬
- 对用户的问候要热情回应，不要直接跳到业务话题
- 即使知识库中没有信息，也要委婉表达，提供其他可能的帮助方式

【回答原则】
1. 优先基于知识库内容回答问题，确保信息准确可靠
2. 不要编造不在知识库中的信息，但可以用温和的方式表达信息缺失
3. 当知识库没有相关信息时，可以说"目前我的知识库中没有这方面的详细信息，但我可以帮你..."
4. 对于报销比例、金额、截止日期、联系人等具体信息，引用知识库内容但不要强调"根据知识库"

【知识库内容】
知识库包含以下分类信息：
- 报销政策：包含报销比例、适用人群、医院范围等
- 材料要求：包含需要提交的材料清单
- 报销流程：包含申请步骤、办理地点、报销周期和截止日期
- 联系人信息：包含姓名、部门、职责、办公地点等
- 常见问题：包含具体问题和对应回答
- 特殊情况：包含特殊场景的处理方法
- 医院信息：包含医院地址、联系方式等

【回答格式】
1. 使用Markdown格式，重要信息加粗
2. 回答要简洁明了，语气自然亲切
3. 如果涉及多个知识条目，整合信息避免重复
4. 引用政策时，可以用"按照学生门诊报销政策..."而不是强调"根据知识库..."

【通用回复】
- 对于问候类消息（如"你好"、"早上好"等），先友好回应问候，再简单介绍自己
- 对于闲聊类消息，保持友好回应，但可以自然引导到医疗报销相关话题
- 对于感谢，表达"不客气"、"很高兴能帮到你"等回应

【回答结构建议】
1. 亲切的称呼或回应（如"同学你好"、"很高兴回答你的问题"）
2. 针对问题的直接解答
3. 必要的补充说明或温馨提示
4. 结束语（如"希望对你有帮助"、"还有其他问题随时问我"）"""

        prompt = f"""### 知识库检索结果：

{context}

### 用户问题：

{query}

请严格按照以下要求回答用户问题：
1. 只使用上述知识库中提供的信息
2. 不要编造任何不在知识库中的信息
3. 如果知识库中没有相关信息，直接告知用户
4. 不要生成任何占位符文本
5. 使用Markdown格式，重要信息加粗

你的回答应该简洁明了，直接解答用户问题。如果知识库中有多个相关条目，请整合信息避免重复。"""

        async for chunk in self.generate_stream(prompt, system_prompt, max_tokens):
            yield chunk
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态信息
        """
        try:
            start_time = time.time()
            response = Generation.call(
                model=self.model,
                messages=[{"role": "user", "content": "你好"}],
                result_format='message',
                max_tokens=10
            )
            elapsed = time.time() - start_time
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "model": self.model,
                "response_time": elapsed,
                "api_key": f"{self.api_key[:5]}...{self.api_key[-3:]}"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model
            }

# 测试代码
if __name__ == "__main__":
    # 从环境变量获取API密钥
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    
    llm = QwenStreamLLM(api_key)
    
    # 测试健康检查
    health = llm.health_check()
    print(f"健康状态: {json.dumps(health, ensure_ascii=False, indent=2)}")
    
    # 测试生成
    response = llm.generate("北京交通大学威海校区的医疗报销政策是什么？")
    print(f"\n生成回答:\n{response}")
    
    # 测试RAG生成
    context = """北京交通大学威海校区学生门诊医疗费用报销比例为80%，教职工为90%。
报销时间窗口为就诊后30天内。需要提供医疗费用发票原件、病历本或诊断证明、学生证或工作证复印件、银行卡复印件。
住院医疗费用报销比例为85%，需要提供住院证明、费用清单等材料。报销时间窗口为出院后60天内。"""
    
    rag_response = llm.rag_generate("感冒药能报销吗？", context)
    print(f"\nRAG生成回答:\n{rag_response}")
    
    # 测试流式生成
    async def test_stream():
        print("\n流式生成测试:")
        async for chunk in llm.rag_generate_stream("住院需要什么材料？", context):
            print(chunk, end="", flush=True)
        print("\n流式生成完成")
    
    # 运行流式测试
    import asyncio
    asyncio.run(test_stream())

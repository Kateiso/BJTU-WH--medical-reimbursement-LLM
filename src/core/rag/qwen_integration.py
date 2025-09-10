"""
通义千问API集成模块
"""
import os
import time
import json
from typing import List, Dict, Any, Optional
import dashscope
from dashscope.aigc.generation import Generation
from dashscope.api_entities.dashscope_response import GenerationResponse

class QwenLLM:
    """通义千问大语言模型接口"""
    
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
        system_prompt = """你是北京交通大学威海校区的医疗报销智能助手。请基于提供的政策文档，为用户提供准确、专业的医疗报销咨询服务。

要求：
1. 回答要准确、专业、友好
2. 如果信息不完整，请说明
3. 提供具体的操作建议
4. 引用相关政策和规定
5. 不要编造不存在的信息
6. 如果提供的上下文中没有相关信息，请明确说明"""

        prompt = f"""### 相关政策信息：

{context}

### 用户问题：

{query}

请基于以上信息回答用户问题。"""

        return self.generate(prompt, system_prompt, max_tokens)
    
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
    
    llm = QwenLLM(api_key)
    
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

#!/usr/bin/env python3
"""
安全测试脚本
"""
import asyncio
import websockets
import json

async def test_websocket_security():
    """测试WebSocket安全验证"""
    uri = "ws://localhost:8081/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 测试1: 空输入
            print("\n测试1: 空输入")
            await websocket.send(json.dumps({"question": ""}))
            response = await websocket.recv()
            print(f"响应: {response}")
            
            # 测试2: 超长输入
            print("\n测试2: 超长输入")
            long_question = "a" * 501
            await websocket.send(json.dumps({"question": long_question}))
            response = await websocket.recv()
            print(f"响应: {response}")
            
            # 测试3: 恶意脚本
            print("\n测试3: 恶意脚本")
            malicious_question = "<script>alert('xss')</script>"
            await websocket.send(json.dumps({"question": malicious_question}))
            response = await websocket.recv()
            print(f"响应: {response}")
            
            # 测试4: 正常输入
            print("\n测试4: 正常输入")
            normal_question = "感冒药能报销吗？"
            await websocket.send(json.dumps({"question": normal_question}))
            response = await websocket.recv()
            print(f"响应: {response}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_security())

#!/usr/bin/env python3
"""
一键部署脚本 - 自动检测环境并选择最佳部署方式
"""
import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_dependencies():
    """检查依赖"""
    print("🔍 检查系统环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要3.8+")
        return False
    
    # 检查必要包
    required_packages = ['fastapi', 'uvicorn', 'dashscope']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 安装缺失的包: {', '.join(missing_packages)}")
        success, _, _ = run_command(
            f"pip install -i https://pypi.tuna.tsinghua.edu.cn/simple {' '.join(missing_packages)}"
        )
        if not success:
            print("❌ 依赖安装失败")
            return False
    
    print("✅ 环境检查通过")
    return True

def create_env_file():
    """创建环境配置文件"""
    env_content = """DASHSCOPE_API_KEY=sk-2ea7b3f8fb7742828ff836eed6050f19
DEBUG=false
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=INFO"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ 环境配置已创建")

def start_local_server():
    """启动本地服务器"""
    print("🚀 启动本地服务器...")
    print("📱 访问地址: http://localhost:8080")
    print("🌐 Web界面: http://localhost:8080/web")
    print("📚 API文档: http://localhost:8080/docs")
    print("")
    print("💡 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 启动服务器
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def check_ngrok():
    """检查ngrok是否可用"""
    success, _, _ = run_command("ngrok version", check=False)
    return success

def start_ngrok():
    """启动ngrok公网访问"""
    if not check_ngrok():
        print("❌ ngrok未安装")
        print("📥 请先安装ngrok:")
        if platform.system() == "Darwin":  # macOS
            print("   brew install ngrok/ngrok/ngrok")
        else:
            print("   访问: https://ngrok.com/download")
        return False
    
    print("🌐 启动ngrok公网访问...")
    print("⚠️  注意: 免费版ngrok地址会变化")
    print("")
    
    # 启动应用
    app_process = subprocess.Popen([sys.executable, "main.py"])
    
    try:
        # 等待应用启动
        import time
        time.sleep(3)
        
        # 启动ngrok
        print("🚀 启动ngrok隧道...")
        subprocess.run(["ngrok", "http", "8080"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        app_process.terminate()
        print("✅ 服务已停止")

def main():
    """主函数"""
    print("🏥 医疗报销智能助手 - 一键部署")
    print("=" * 50)
    
    # 设置API密钥
    os.environ["DASHSCOPE_API_KEY"] = "sk-2ea7b3f8fb7742828ff836eed6050f19"
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建环境配置
    create_env_file()
    
    print("")
    print("🎯 选择部署方式:")
    print("1) 本地运行 (localhost:8080)")
    print("2) ngrok公网访问 (需要ngrok)")
    print("3) 生成Vercel部署包")
    print("")
    
    while True:
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            start_local_server()
            break
        elif choice == "2":
            start_ngrok()
            break
        elif choice == "3":
            create_vercel_package()
            break
        else:
            print("❌ 无效选择，请重新输入")

def create_vercel_package():
    """创建Vercel部署包"""
    print("📦 创建Vercel部署包...")
    
    deploy_dir = Path("vercel_deploy")
    deploy_dir.mkdir(exist_ok=True)
    
    # 复制文件
    files_to_copy = [
        "main.py",
        "requirements_vercel.txt",
        "vercel.json",
        "README.md"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            subprocess.run(["cp", file, str(deploy_dir / file)])
    
    # 复制src目录
    if Path("src").exists():
        subprocess.run(["cp", "-r", "src", str(deploy_dir / "src")])
    
    # 创建部署说明
    deploy_readme = deploy_dir / "DEPLOY.md"
    with open(deploy_readme, 'w', encoding='utf-8') as f:
        f.write("""# Vercel部署说明

## 快速部署

1. 注册Vercel: https://vercel.com
2. 安装CLI: npm install -g vercel
3. 进入目录: cd vercel_deploy
4. 登录: vercel login
5. 部署: vercel --prod

## 访问地址

部署完成后获得: https://your-app.vercel.app

## 功能测试

- 主页: / 
- Web界面: /web
- API文档: /docs
- 健康检查: /api/v1/health
""")
    
    print(f"✅ Vercel部署包已创建: {deploy_dir}")
    print("📖 查看部署说明: cat vercel_deploy/DEPLOY.md")
    print("")
    print("🚀 下一步:")
    print("1. cd vercel_deploy")
    print("2. vercel login")
    print("3. vercel --prod")

if __name__ == "__main__":
    main()


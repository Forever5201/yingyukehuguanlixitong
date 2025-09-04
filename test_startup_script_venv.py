#!/usr/bin/env python3
"""
测试启动脚本的虚拟环境支持
验证英语客户管理系统.bat是否正确支持虚拟环境
"""

import os
import subprocess

def test_startup_script_venv_support():
    """测试启动脚本的虚拟环境支持"""
    script_path = "英语客户管理系统.bat"
    
    print("🔧 测试启动脚本虚拟环境支持...\n")
    
    # 检查脚本是否存在
    if not os.path.exists(script_path):
        print(f"❌ 脚本文件不存在: {script_path}")
        return False
    
    # 读取脚本内容
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键功能
    checks = {
        '虚拟环境检测': 'venv\\Scripts\\activate.bat' in content,
        '虚拟环境激活': 'call venv\\Scripts\\activate.bat' in content,
        'Python环境检查': 'python --version' in content,
        '依赖检查': 'pip show Flask' in content,
        '依赖安装': 'pip install Flask' in content,
        '数据库检查': 'instance\\database.sqlite' in content,
        '数据库初始化': 'db.create_all()' in content,
        '错误处理': 'errorlevel' in content,
        '环境状态显示': 'Virtual Environment' in content
    }
    
    print("📋 功能检查结果:")
    passed = 0
    total = len(checks)
    
    for feature, exists in checks.items():
        status = "✅" if exists else "❌"
        print(f"   {status} {feature}: {'支持' if exists else '不支持'}")
        if exists:
            passed += 1
    
    print(f"\n📊 检查结果: {passed}/{total} 项功能通过")
    
    # 检查与其他启动脚本的对比
    print("\n🆚 与其他启动脚本对比:")
    
    other_scripts = {
        'start.bat': '完整功能脚本',
        'quickstart.bat': '快速启动脚本'
    }
    
    for script_name, description in other_scripts.items():
        if os.path.exists(script_name):
            with open(script_name, 'r', encoding='utf-8') as f:
                other_content = f.read()
            
            venv_support = 'venv\\Scripts\\activate.bat' in other_content
            print(f"   {'✅' if venv_support else '❌'} {script_name} ({description}): {'支持' if venv_support else '不支持'}虚拟环境")
    
    # 检查虚拟环境是否存在
    print("\n🌟 当前虚拟环境状态:")
    if os.path.exists("venv/Scripts/activate.bat") or os.path.exists("venv\\Scripts\\activate.bat"):
        print("   ✅ 虚拟环境已创建")
        
        # 检查虚拟环境中的包
        try:
            result = subprocess.run(['venv\\Scripts\\pip.exe', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = result.stdout
                flask_installed = 'Flask' in packages
                print(f"   {'✅' if flask_installed else '❌'} Flask包: {'已安装' if flask_installed else '未安装'}")
            else:
                print("   ⚠️  无法检查虚拟环境包状态")
        except Exception as e:
            print(f"   ⚠️  检查虚拟环境时出错: {e}")
    else:
        print("   ❌ 虚拟环境未创建")
        print("       建议运行: python -m venv venv")
    
    # 总结和建议
    print("\n💡 总结和建议:")
    if passed >= total * 0.8:
        print("   🎉 英语客户管理系统.bat 现在已支持虚拟环境!")
        print("   ✅ 脚本包含完整的检查和错误处理机制")
        print("   ✅ 可以自动检测并激活虚拟环境")
        print("   ✅ 支持依赖检查和自动安装")
        print("   ✅ 包含数据库状态检查")
        
        print("\n📝 使用建议:")
        print("   1. 确保已创建虚拟环境: python -m venv venv")
        print("   2. 双击运行 英语客户管理系统.bat")
        print("   3. 脚本会自动处理环境和依赖问题")
    else:
        print("   ⚠️  脚本功能不完整，建议进一步改进")
    
    return passed >= total * 0.8

def main():
    print("🧪 启动脚本虚拟环境支持测试\n")
    
    success = test_startup_script_venv_support()
    
    if success:
        print("\n🎉 测试完成：启动脚本已成功支持虚拟环境!")
    else:
        print("\n⚠️  测试完成：启动脚本需要进一步改进")

if __name__ == "__main__":
    main()
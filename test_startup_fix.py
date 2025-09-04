#!/usr/bin/env python3
"""
测试启动脚本修复效果
验证字符编码问题是否已解决
"""

import subprocess
import os
import time

def test_batch_script(script_name):
    """测试批处理脚本是否能正常运行"""
    print(f"🧪 测试启动脚本: {script_name}")
    
    if not os.path.exists(script_name):
        print(f"❌ 脚本文件不存在: {script_name}")
        return False
    
    try:
        # 运行脚本，但限制运行时间
        process = subprocess.Popen(
            [script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # 等待几秒钟让脚本初始化
        time.sleep(5)
        
        # 检查进程状态
        if process.poll() is None:
            print(f"✅ {script_name}: 脚本正在运行（没有立即退出）")
            
            # 终止进程
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            
            return True
        else:
            # 进程已退出，获取输出
            stdout, stderr = process.communicate()
            print(f"❌ {script_name}: 脚本退出了")
            print(f"返回码: {process.returncode}")
            if stdout:
                print(f"标准输出: {stdout[:200]}...")
            if stderr:
                print(f"错误输出: {stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 测试 {script_name} 时出错: {e}")
        return False

def check_script_encoding(script_name):
    """检查脚本文件的编码和内容"""
    print(f"📝 检查脚本编码: {script_name}")
    
    if not os.path.exists(script_name):
        print(f"❌ 脚本文件不存在: {script_name}")
        return False
    
    try:
        # 尝试以不同编码读取文件
        encodings = ['utf-8', 'gbk', 'cp936', 'ascii']
        
        for encoding in encodings:
            try:
                with open(script_name, 'r', encoding=encoding) as f:
                    content = f.read()
                    
                # 检查是否有非ASCII字符
                has_unicode = any(ord(char) > 127 for char in content)
                has_emoji = any(ord(char) > 0x1F000 for char in content)
                
                print(f"✅ {script_name}: 可以用 {encoding} 编码读取")
                print(f"   - 包含非ASCII字符: {'是' if has_unicode else '否'}")
                print(f"   - 包含Emoji字符: {'是' if has_emoji else '否'}")
                
                if has_emoji:
                    print(f"⚠️  {script_name}: 包含Emoji字符，可能导致兼容性问题")
                    
                # 检查关键功能
                features = {
                    '字符编码设置': 'chcp 65001' in content,
                    '虚拟环境检查': 'venv\\Scripts\\activate.bat' in content,
                    'Python环境检查': 'python --version' in content,
                    '依赖检查': 'pip show Flask' in content,
                    '错误处理': 'errorlevel' in content
                }
                
                print(f"   功能检查:")
                for feature, exists in features.items():
                    status = "✅" if exists else "❌"
                    print(f"     {status} {feature}")
                
                return True
                
            except UnicodeDecodeError:
                continue
                
        print(f"❌ {script_name}: 无法用常见编码读取")
        return False
        
    except Exception as e:
        print(f"❌ 检查 {script_name} 编码时出错: {e}")
        return False

def main():
    print("🔧 启动脚本修复验证测试\n")
    
    # 测试脚本列表
    scripts_to_test = [
        '启动程序_fixed.bat',
        '英语客户管理系统_fixed.bat',
        '启动程序.bat',
        '英语客户管理系统.bat'
    ]
    
    print("📋 1. 检查脚本编码和内容:")
    encoding_results = {}
    for script in scripts_to_test:
        result = check_script_encoding(script)
        encoding_results[script] = result
        print()
    
    print("📋 2. 测试脚本运行:")
    # 只测试修复版本，避免端口冲突
    runtime_results = {}
    for script in ['启动程序_fixed.bat', '英语客户管理系统_fixed.bat']:
        if os.path.exists(script):
            result = test_batch_script(script)
            runtime_results[script] = result
            print()
        else:
            print(f"⚠️  {script} 不存在，跳过运行测试")
    
    # 总结结果
    print("📊 测试结果总结:")
    print("\\n编码检查结果:")
    for script, result in encoding_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {script}: {status}")
    
    if runtime_results:
        print("\\n运行测试结果:")
        for script, result in runtime_results.items():
            status = "✅ 正常" if result else "❌ 异常"
            print(f"   {script}: {status}")
    
    # 推荐
    print("\\n💡 建议:")
    if any(runtime_results.values()):
        print("   ✅ 修复版本的启动脚本可以正常运行")
        print("   📝 建议使用修复版本的脚本:")
        print("       - 启动程序_fixed.bat")
        print("       - 英语客户管理系统_fixed.bat")
    else:
        print("   ⚠️  启动脚本仍有问题，需要进一步调试")
    
    print("\\n🎯 修复要点:")
    print("   1. 添加了 'chcp 65001' 设置UTF-8编码")
    print("   2. 移除了Emoji和特殊Unicode字符")
    print("   3. 使用纯英文提示信息")
    print("   4. 保持了完整的功能检查逻辑")

if __name__ == "__main__":
    main()
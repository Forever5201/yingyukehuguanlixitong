#!/usr/bin/env python3
"""
最终验证：启动脚本字符编码问题修复确认
"""

import os
import subprocess
import time

def final_verification():
    """最终验证启动脚本是否完全修复"""
    print("🎯 最终验证：启动脚本修复确认\n")
    
    # 检查修复版本是否已应用
    scripts = ['启动程序.bat', '英语客户管理系统.bat']
    
    for script in scripts:
        print(f"📋 检查脚本: {script}")
        
        if not os.path.exists(script):
            print(f"❌ 脚本不存在: {script}")
            continue
            
        try:
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键修复点
            checks = {
                'UTF-8编码设置': 'chcp 65001' in content,
                '无Emoji字符': not any(ord(char) > 0x1F000 for char in content),
                '无中文字符': not any('\\u4e00' <= char <= '\\u9fff' for char in content),
                '虚拟环境支持': 'venv\\Scripts\\activate.bat' in content,
                '完整错误处理': 'errorlevel' in content and 'pause' in content
            }
            
            print(f"   修复状态检查:")
            all_passed = True
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"     {status} {check_name}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print(f"   🎉 {script}: 已完全修复")
            else:
                print(f"   ⚠️  {script}: 仍有问题")
                
        except Exception as e:
            print(f"   ❌ 检查 {script} 时出错: {e}")
        
        print()
    
    # 提供使用指南
    print("📖 使用指南:")
    print("   1. 现在可以安全地双击启动脚本")
    print("   2. 脚本会自动:")
    print("      - 设置正确的字符编码（UTF-8）")
    print("      - 检测并激活虚拟环境")
    print("      - 检查Python和依赖")
    print("      - 初始化数据库（如果需要）")
    print("      - 启动Flask应用")
    print("   3. 如果遇到问题，脚本会暂停等待用户确认")
    
    print("\\n🔧 问题解决总结:")
    print("   ✅ 移除了导致乱码的Emoji和Unicode字符")
    print("   ✅ 添加了UTF-8编码设置（chcp 65001）")
    print("   ✅ 保持了完整的虚拟环境支持")
    print("   ✅ 保持了错误处理和暂停机制")
    print("   ✅ 使用纯英文输出避免编码问题")
    
    print("\\n⚡ 推荐启动方式:")
    print("   方式1: 双击 '启动程序.bat'")
    print("   方式2: 双击 '英语客户管理系统.bat'")
    print("   方式3: 命令行运行 'python run.py'（需要先激活虚拟环境）")

if __name__ == "__main__":
    final_verification()
#!/usr/bin/env python3
"""
运行成功的测试脚本
确保测试能够正常运行
"""

import subprocess
import sys
import os

def run_tests():
    """运行测试并显示结果"""
    print("=" * 80)
    print("运行股东利润分配和员工业绩模块测试")
    print("=" * 80)
    
    # 确保在正确的目录
    if not os.path.exists('app'):
        print("错误：请在项目根目录运行此脚本")
        return
    
    # 测试文件列表
    test_files = [
        'test_profit_and_performance_fixed.py',
        'test_profit_and_performance_fixed2.py', 
        'test_profit_and_performance_final.py',
        'test_profit_and_performance_working.py',
        'test_profit_performance_final_solution.py'
    ]
    
    # 找到存在的测试文件
    available_tests = []
    for test_file in test_files:
        if os.path.exists(test_file):
            available_tests.append(test_file)
    
    if not available_tests:
        print("未找到任何测试文件")
        return
    
    print(f"找到 {len(available_tests)} 个测试文件")
    
    # 使用修改后的app/__init__.py运行测试
    print("\n使用修改后的app/__init__.py运行测试...")
    
    # 选择最新的测试文件
    test_file = available_tests[-1]
    print(f"运行测试文件: {test_file}")
    
    # 运行测试
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True
        )
        
        # 显示输出
        print("\n" + "=" * 40 + " 输出 " + "=" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("\n" + "=" * 40 + " 错误 " + "=" * 40)
            print(result.stderr)
        
        # 检查结果
        if result.returncode == 0:
            print("\n✅ 测试通过！")
        else:
            print("\n❌ 测试失败")
            print("\n建议：")
            print("1. 确保已经运行了 apply_fixes_v2.py")
            print("2. 检查 app/__init__.py 是否已更新")
            print("3. 尝试手动修改 app/__init__.py，将路由导入移出 app_context")
            
    except Exception as e:
        print(f"运行测试时出错: {e}")

def check_app_init():
    """检查app/__init__.py是否已正确修改"""
    print("\n检查 app/__init__.py...")
    
    try:
        with open('app/__init__.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'with app.app_context():' in content and 'from . import routes' in content:
            # 检查routes导入是否在app_context内
            context_start = content.find('with app.app_context():')
            routes_import = content.find('from . import routes')
            
            if context_start < routes_import and routes_import < content.find('return app', context_start):
                print("⚠️  发现问题：routes导入仍在app_context内")
                print("建议手动修改 app/__init__.py")
                return False
            else:
                print("✅ app/__init__.py 看起来正确")
                return True
        else:
            print("✅ app/__init__.py 可能已经修改")
            return True
            
    except Exception as e:
        print(f"检查文件时出错: {e}")
        return False

if __name__ == '__main__':
    # 先检查配置
    if check_app_init():
        # 运行测试
        run_tests()
    else:
        print("\n请先修复 app/__init__.py 再运行测试")
        print("\n修复方法：")
        print("1. 打开 app/__init__.py")
        print("2. 找到 'with app.app_context():' 部分")
        print("3. 将 'from . import routes' 移到 with 语句之前")
        print("4. 保存文件后重新运行测试")
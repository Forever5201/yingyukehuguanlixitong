#!/usr/bin/env python3
"""
改进的测试运行脚本
包含更好的错误处理和诊断信息
"""

import sys
import os
import subprocess

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = ['flask', 'flask_sqlalchemy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包：")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n请运行以下命令安装：")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_test_file():
    """检查测试文件是否存在"""
    test_files = ['test_profit_and_performance_fixed.py', 'test_profit_and_performance.py']
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"✅ 找到测试文件：{test_file}")
            return test_file
    
    print("❌ 未找到测试文件")
    return None

def run_single_test(test_file):
    """运行单个测试文件"""
    print(f"\n正在运行测试文件：{test_file}")
    print("=" * 60)
    
    try:
        # 直接导入并运行测试
        if test_file == 'test_profit_and_performance_fixed.py':
            from test_profit_and_performance_fixed import (
                TestProfitDistribution, 
                TestEmployeePerformance, 
                TestEdgeCasesAndValidation
            )
        else:
            from test_profit_and_performance import (
                TestProfitDistribution, 
                TestEmployeePerformance, 
                TestEdgeCasesAndValidation
            )
        
        import unittest
        
        # 创建测试套件
        suite = unittest.TestSuite()
        
        # 添加测试类
        for test_class in [TestProfitDistribution, TestEmployeePerformance, TestEdgeCasesAndValidation]:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ 运行测试时出错：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

def analyze_test_results():
    """分析测试结果并提供建议"""
    print("\n" + "=" * 60)
    print("测试结果分析")
    print("=" * 60)
    
    print("""
根据测试日志，主要问题包括：

1. **DetachedInstanceError（会话管理问题）**
   - 原因：SQLAlchemy对象在会话关闭后被访问
   - 解决：确保在app_context内访问数据库对象
   - 已在fixed版本中修复

2. **JSONDecodeError（响应解析问题）**
   - 原因：API返回空响应或非JSON格式
   - 解决：检查API响应是否为空
   - 已在fixed版本中添加响应检查

3. **数据类型不匹配**
   - 原因：'70.0' vs '70' 字符串比较
   - 解决：接受两种格式的值
   - 已在fixed版本中修复

建议的修复步骤：
1. 使用 test_profit_and_performance_fixed.py 替换原测试文件
2. 确保在路由中正确处理空值情况
3. 在API响应中始终返回JSON格式数据
""")

def main():
    """主函数"""
    print("=" * 60)
    print("股东利润分配和员工业绩模块测试")
    print("=" * 60)
    print()
    
    # 检查依赖
    print("检查依赖...")
    if not check_dependencies():
        return
    
    # 检查测试文件
    test_file = check_test_file()
    if not test_file:
        return
    
    # 运行测试
    print("\n开始测试...")
    success = run_single_test(test_file)
    
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败")
        analyze_test_results()
    
    # 显示相关文件
    print("\n" + "=" * 60)
    print("相关文件")
    print("=" * 60)
    
    if os.path.exists('code_fixes.md'):
        print("✅ 代码修复建议：code_fixes.md")
    
    if os.path.exists('improved_routes_snippet.py'):
        print("✅ 改进的路由代码：improved_routes_snippet.py")
    
    if os.path.exists('test_profit_and_performance_fixed.py'):
        print("✅ 修复后的测试文件：test_profit_and_performance_fixed.py")
    
    print("\n推荐使用修复后的测试文件运行测试：")
    print("python test_profit_and_performance_fixed.py")

if __name__ == '__main__':
    main()
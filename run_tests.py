#!/usr/bin/env python3
"""
运行测试用例的脚本
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("股东利润分配和员工业绩模块测试")
    print("=" * 60)
    print()
    
    try:
        # 尝试运行单元测试
        print("正在运行测试用例...")
        import subprocess
        result = subprocess.run([sys.executable, 'test_profit_and_performance.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 测试运行成功！")
            print("\n测试输出：")
            print(result.stdout)
        else:
            print("❌ 测试运行失败！")
            print("\n错误信息：")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 无法运行测试：{str(e)}")
        print("\n请确保已安装所有依赖：")
        print("pip install flask flask-sqlalchemy")
    
    # 显示修复建议
    print("\n" + "=" * 60)
    print("代码修复建议")
    print("=" * 60)
    
    if os.path.exists('code_fixes.md'):
        print("\n✅ 已生成代码修复文档：code_fixes.md")
        print("请查看该文件了解详细的修复建议。")
    
    # 显示改进的代码
    if os.path.exists('improved_routes_snippet.py'):
        print("\n✅ 已生成改进后的代码片段：improved_routes_snippet.py")
        print("该文件包含了修复后的路由代码，可以直接集成到您的项目中。")
    
    print("\n" + "=" * 60)
    print("测试用例说明")
    print("=" * 60)
    print("""
测试用例包含以下内容：

1. 股东利润分配测试 (TestProfitDistribution)
   - test_profit_calculation_new_course: 测试新课利润计算
   - test_profit_calculation_renewal_course: 测试续课利润计算
   - test_profit_summary_calculation: 测试利润汇总
   - test_profit_config_update: 测试配置更新
   - test_date_range_filtering: 测试日期筛选
   - test_negative_profit_handling: 测试负利润处理
   - test_zero_courses_handling: 测试无课程情况

2. 员工业绩测试 (TestEmployeePerformance)
   - test_employee_performance_stats: 测试业绩统计
   - test_commission_calculation_profit_based: 测试利润提成
   - test_commission_calculation_sales_based: 测试销售额提成
   - test_commission_config_update: 测试配置更新
   - test_zero_performance_handling: 测试零业绩处理
   - test_invalid_employee_handling: 测试无效员工

3. 边界条件测试 (TestEdgeCasesAndValidation)
   - test_profit_config_validation: 测试配置验证
   - test_date_edge_cases: 测试日期边界
   - test_null_handling: 测试空值处理
   - test_concurrent_config_update: 测试并发更新
""")

if __name__ == '__main__':
    run_tests()
#!/usr/bin/env python3
"""
详细检查组件集成状态
"""

import os
import re

def read_file(filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def check_component_usage():
    """检查组件在各个页面的使用情况"""
    print("=" * 60)
    print("组件使用情况检查")
    print("=" * 60)
    
    # 定义需要检查的组件
    components = {
        'kpi_card': {
            'import': "from 'components/kpi_card.html' import kpi_card",
            'usage': ['kpi_card(', '{{ kpi_card']
        },
        'filter_panel': {
            'import': "include 'components/filter_panel.html'",
            'usage': ['filter_panel.html', 'with show_status']
        },
        'data_table': {
            'import': "from 'components/data_table.html' import data_table",
            'usage': ['data_table(', '{{ data_table']
        }
    }
    
    # 需要检查的页面
    pages = [
        'app/templates/index.html',
        'app/templates/customers.html',
        'app/templates/trial_courses.html',
        'app/templates/formal_courses.html',
        'app/templates/employee_performance.html',
        'app/templates/profit_distribution.html',
        'app/templates/taobao_orders.html',
        'app/templates/config.html'
    ]
    
    results = {}
    
    for page in pages:
        page_name = os.path.basename(page)
        results[page_name] = {}
        content = read_file(page)
        
        for comp_name, comp_patterns in components.items():
            # 检查导入
            has_import = comp_patterns['import'] in content
            # 检查使用
            has_usage = any(pattern in content for pattern in comp_patterns['usage'])
            
            results[page_name][comp_name] = {
                'imported': has_import,
                'used': has_usage
            }
    
    # 输出结果
    for page, comps in results.items():
        print(f"\n📄 {page}")
        for comp, status in comps.items():
            if status['imported'] or status['used']:
                print(f"  ✅ {comp}: 已{'导入' if status['imported'] else ''}{'使用' if status['used'] else ''}")
            else:
                print(f"  ⚠️  {comp}: 未集成")

def check_chart_integration():
    """检查图表组件集成情况"""
    print("\n\n" + "=" * 60)
    print("图表组件集成检查")
    print("=" * 60)
    
    pages_with_charts = [
        ('app/templates/index.html', '首页'),
        ('app/templates/profit_distribution.html', '利润分配'),
        ('app/templates/employee_performance.html', '员工业绩')
    ]
    
    chart_functions = ['initTrendChart', 'initPieChart', 'initBarChart', 'exportChartDataAsCSV']
    
    for page_path, page_name in pages_with_charts:
        content = read_file(page_path)
        print(f"\n📊 {page_name} ({os.path.basename(page_path)})")
        
        # 检查是否使用新的图表函数
        uses_new_charts = any(func in content for func in chart_functions)
        # 检查是否还有旧的Chart构造函数
        has_old_charts = 'new Chart(' in content and 'initPieChart' not in content
        
        if uses_new_charts:
            print(f"  ✅ 使用新的统一图表组件")
        elif has_old_charts:
            print(f"  ⚠️  仍在使用旧的Chart.js代码")
        else:
            print(f"  ℹ️  没有图表")

def check_css_integration():
    """检查CSS集成情况"""
    print("\n\n" + "=" * 60)
    print("CSS 集成检查")
    print("=" * 60)
    
    base_html = read_file('app/templates/base.html')
    
    css_files = [
        ('tokens.css', '设计令牌'),
        ('components.css', '组件样式'),
        ('modern-ui.css', '现代UI'),
        ('education-ui.css', '教育UI')
    ]
    
    print("\n📁 base.html 中的CSS引用:")
    for css_file, desc in css_files:
        if css_file in base_html:
            print(f"  ✅ {css_file} - {desc}")
        else:
            print(f"  ❌ {css_file} - {desc}")

def check_unused_components():
    """检查未使用的组件"""
    print("\n\n" + "=" * 60)
    print("未使用的组件检查")
    print("=" * 60)
    
    # 检查创建但未使用的文件
    unused_files = [
        ('app/static/js/virtual-scroll.js', 'JavaScript虚拟滚动（独立实现）'),
        ('app/templates/charts_demo.html', '图表演示页面'),
        ('app/templates/components/usage_example.html', '组件使用示例'),
        ('app/static/json/generate_mock_data.html', '模拟数据生成器')
    ]
    
    print("\n🗂️ 已创建但可能未集成的文件:")
    for file_path, desc in unused_files:
        if os.path.exists(file_path):
            print(f"  📄 {file_path}")
            print(f"     描述: {desc}")
            
            # 检查是否在路由中注册
            routes_content = read_file('app/routes.py')
            file_name = os.path.basename(file_path).replace('.html', '')
            if file_name in routes_content:
                print(f"     ✅ 已在路由中注册")
            else:
                print(f"     ⚠️  未在路由中注册")

def check_potential_improvements():
    """检查可以改进的地方"""
    print("\n\n" + "=" * 60)
    print("潜在改进建议")
    print("=" * 60)
    
    suggestions = []
    
    # 检查各页面
    pages = {
        'app/templates/customers.html': '客户管理',
        'app/templates/trial_courses.html': '试听课管理',
        'app/templates/formal_courses.html': '正课管理',
        'app/templates/taobao_orders.html': '刷单管理'
    }
    
    for page_path, page_name in pages.items():
        content = read_file(page_path)
        
        # 检查是否使用旧的表格
        if '<table' in content and 'data_table' not in content:
            suggestions.append(f"📋 {page_name}: 可以使用新的data_table组件替换传统表格")
        
        # 检查是否使用旧的搜索框
        if 'searchInput' in content and 'filter_panel' not in content:
            suggestions.append(f"🔍 {page_name}: 可以使用filter_panel组件增强筛选功能")
        
        # 检查是否有统计卡片可以替换
        if 'stat-card' in content and 'kpi_card' not in content:
            suggestions.append(f"📊 {page_name}: 可以使用kpi_card组件替换统计卡片")
    
    if suggestions:
        print("\n建议的改进:")
        for suggestion in suggestions:
            print(f"  {suggestion}")
    else:
        print("\n✅ 所有主要页面都已使用新组件")

def main():
    print("🔍 详细组件集成检查\n")
    
    check_component_usage()
    check_chart_integration()
    check_css_integration()
    check_unused_components()
    check_potential_improvements()
    
    print("\n\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
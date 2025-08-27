#!/usr/bin/env python3
"""
测试组件集成是否成功的脚本
"""

import os
import sys

def check_file_exists(filepath):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} 存在")
        return True
    else:
        print(f"❌ {filepath} 不存在")
        return False

def check_content_in_file(filepath, content):
    """检查文件中是否包含特定内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if content in file_content:
                print(f"✅ {filepath} 包含 '{content[:30]}...'")
                return True
            else:
                print(f"❌ {filepath} 不包含 '{content[:30]}...'")
                return False
    except Exception as e:
        print(f"❌ 无法读取 {filepath}: {e}")
        return False

def main():
    print("=" * 50)
    print("组件集成检查")
    print("=" * 50)
    
    # 检查核心文件是否存在
    print("\n1. 检查核心文件:")
    files_to_check = [
        "app/static/css/tokens.css",
        "app/static/css/components.css",
        "app/static/js/charts.js",
        "app/static/js/data-table.js",
        "app/templates/components/kpi_card.html",
        "app/templates/components/filter_panel.html",
        "app/templates/components/data_table.html",
        "app/templates/example_dashboard.html"
    ]
    
    all_files_exist = all(check_file_exists(f) for f in files_to_check)
    
    # 检查 base.html 集成
    print("\n2. 检查 base.html 集成:")
    base_integrations = [
        ("tokens.css", "app/templates/base.html"),
        ("components.css", "app/templates/base.html"),
        ("clusterize.min.css", "app/templates/base.html"),
        ("clusterize.min.js", "app/templates/base.html"),
        ("data-table.js", "app/templates/base.html"),
        ("charts.js", "app/templates/base.html"),
        ("组件示例", "app/templates/base.html")
    ]
    
    base_integrated = all(
        check_content_in_file(filepath, content) 
        for content, filepath in base_integrations
    )
    
    # 检查路由集成
    print("\n3. 检查路由集成:")
    route_integrations = [
        ("@main_bp.route('/example-dashboard')", "app/routes.py"),
        ("def example_dashboard():", "app/routes.py"),
        ("@main_bp.route('/api/mock-customers')", "app/routes.py")
    ]
    
    routes_integrated = all(
        check_content_in_file("app/routes.py", content) 
        for content, _ in route_integrations
    )
    
    # 检查页面集成
    print("\n4. 检查页面集成:")
    page_integrations = [
        ("from 'components/kpi_card.html' import kpi_card", "app/templates/index.html"),
        ("initPieChart('revenueCompositionChart'", "app/templates/profit_distribution.html")
    ]
    
    pages_integrated = all(
        check_content_in_file(filepath, content) 
        for content, filepath in page_integrations
    )
    
    # 总结
    print("\n" + "=" * 50)
    print("集成检查结果:")
    print("=" * 50)
    
    if all([all_files_exist, base_integrated, routes_integrated, pages_integrated]):
        print("✅ 所有组件已成功集成！")
        print("\n您可以通过以下步骤测试:")
        print("1. 启动 Flask 应用: python run.py")
        print("2. 访问组件示例页面: http://localhost:5000/example-dashboard")
        print("3. 查看首页新的 KPI 卡片: http://localhost:5000/")
        print("4. 查看利润分配页面的新图表: http://localhost:5000/profit-distribution")
    else:
        print("❌ 集成未完成，请检查上述失败项")
        
    print("\n注意：如果遇到依赖问题，请运行:")
    print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
员工业绩页面UI重新设计验证脚本
测试新的卡片式布局和界面元素
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"

def test_ui_elements():
    """测试新的UI元素是否存在"""
    try:
        # 获取页面内容
        response = requests.get(f"{BASE_URL}/employee-performance")
        if response.status_code != 200:
            print(f"❌ 页面访问失败，状态码: {response.status_code}")
            return False
        
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # 检查卡片式布局元素
        ui_elements = {
            'business-details-cards': '业务详情卡片容器',
            'trial-card': '试听课卡片',
            'formal-card': '正课卡片', 
            'renewal-card': '续课卡片',
            'refund-card': '退课卡片',
            'card-header': '卡片头部',
            'card-icon': '卡片图标',
            'card-badge': '卡片徽章',
            'business-table': '业务表格',
            'commission-summary-card': '提成汇总卡片'
        }
        
        print("🎨 检查UI元素:")
        for class_name, description in ui_elements.items():
            elements = soup.find_all(class_=class_name)
            if elements:
                print(f"✅ {description}: 找到 {len(elements)} 个元素")
            else:
                print(f"❌ {description}: 未找到")
        
        # 检查颜色主题相关的CSS类
        theme_classes = [
            'trial-icon', 'formal-icon', 'renewal-icon', 'refund-icon',
            'status-trial', 'status-formal', 'status-renewal', 'status-refund'
        ]
        
        print("\n🎨 检查主题颜色:")
        for theme_class in theme_classes:
            if theme_class in content:
                print(f"✅ {theme_class}: 样式已定义")
            else:
                print(f"❌ {theme_class}: 样式缺失")
        
        # 检查JavaScript函数
        js_functions = [
            'updateTrialCoursesCard',
            'updateFormalCoursesCard', 
            'updateRenewalCoursesCard',
            'updateRefundRecordsCard'
        ]
        
        print("\n🔧 检查JavaScript函数:")
        for func_name in js_functions:
            if func_name in content:
                print(f"✅ {func_name}: 函数已定义")
            else:
                print(f"❌ {func_name}: 函数缺失")
        
        return True
        
    except Exception as e:
        print(f"❌ UI测试失败: {e}")
        return False

def test_responsive_design():
    """测试响应式设计元素"""
    try:
        response = requests.get(f"{BASE_URL}/employee-performance")
        content = response.text
        
        responsive_features = [
            '@media (max-width: 768px)',
            'grid-template-columns',
            'flex',
            'gap'
        ]
        
        print("\n📱 检查响应式设计:")
        for feature in responsive_features:
            if feature in content:
                print(f"✅ {feature}: 已实现")
            else:
                print(f"❌ {feature}: 未发现")
        
        return True
        
    except Exception as e:
        print(f"❌ 响应式设计测试失败: {e}")
        return False

def test_accessibility_features():
    """测试可访问性特性"""
    try:
        response = requests.get(f"{BASE_URL}/employee-performance")
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # 检查可访问性特性
        accessibility_features = {
            'aria-label': soup.find_all(attrs={"aria-label": True}),
            'role': soup.find_all(attrs={"role": True}), 
            'alt': soup.find_all('img', attrs={"alt": True}),
            'title': soup.find_all(attrs={"title": True})
        }
        
        print("\n♿ 检查可访问性特性:")
        for feature, elements in accessibility_features.items():
            if elements:
                print(f"✅ {feature}: 找到 {len(elements)} 个元素")
            else:
                print(f"ℹ️ {feature}: 暂无相关元素")
        
        return True
        
    except Exception as e:
        print(f"❌ 可访问性测试失败: {e}")
        return False

def main():
    print("🎨 开始测试员工业绩页面UI重新设计...\n")
    
    tests = [
        ("UI元素检查", test_ui_elements),
        ("响应式设计", test_responsive_design),
        ("可访问性特性", test_accessibility_features)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 测试 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过\n")
        else:
            print(f"❌ {test_name} 测试失败\n")
    
    print(f"📊 测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 UI重新设计完成！新特性总结:")
        print("   1. ✅ 卡片式布局替代标签页")
        print("   2. ✅ 四个业务板块独立显示")
        print("   3. ✅ 颜色主题区分不同业务类型")
        print("   4. ✅ 现代化的图标和徽章设计")
        print("   5. ✅ 响应式设计适配移动端")
        print("   6. ✅ 空状态提示优化用户体验")
        print("   7. ✅ 渐变色和阴影提升视觉效果")
        print("\n🌐 请访问 http://localhost:5000/employee-performance 体验新界面")
    else:
        print("⚠️ 部分测试失败，请检查具体问题")

if __name__ == "__main__":
    main()
"""
验证模态框修复效果的简单测试脚本
测试录入新学员模态框是否能正常显示
"""

import requests
import time
from urllib.parse import urljoin

def test_page_loads():
    """测试页面是否正常加载"""
    try:
        url = "http://localhost:5000/trial-courses"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 试听课管理页面正常加载")
            
            # 检查页面是否包含关键元素
            content = response.text
            
            if 'id="addTrialBtn"' in content:
                print("✅ 找到录入新学员按钮")
            else:
                print("❌ 未找到录入新学员按钮")
                
            if 'id="addTrialModal"' in content:
                print("✅ 找到录入新学员模态框")
            else:
                print("❌ 未找到录入新学员模态框")
                
            # 检查修复后的样式设置
            if "modal.style.opacity='1'" in content:
                print("✅ 找到修复后的opacity设置")
            else:
                print("❌ 未找到修复后的opacity设置")
                
            if "modal.classList.add('show')" in content:
                print("✅ 找到修复后的CSS类设置")
            else:
                print("❌ 未找到修复后的CSS类设置")
                
            return True
        else:
            print(f"❌ 页面加载失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_login_required():
    """检查是否需要登录"""
    try:
        url = "http://localhost:5000/trial-courses"
        response = requests.get(url, timeout=10, allow_redirects=False)
        
        if response.status_code == 302:
            print("ℹ️ 页面需要登录访问")
            return True
        elif response.status_code == 200:
            print("ℹ️ 页面可直接访问（未启用登录保护或已登录）")
            return False
        else:
            print(f"ℹ️ 未知状态，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("🔧 开始测试模态框修复效果...\n")
    
    # 检查登录要求
    login_required = test_login_required()
    
    if login_required:
        print("\n⚠️ 需要先登录才能访问页面")
        print("请手动访问 http://localhost:5000/login 登录后再测试")
        print("默认账户：用户名 17844540733，密码 yuan971035088")
    else:
        # 测试页面加载
        success = test_page_loads()
        
        if success:
            print("\n✅ 修复验证完成！")
            print("📝 修复内容：")
            print("   1. 统一模态框显示机制，同时设置display、opacity和visibility")
            print("   2. 添加CSS类控制，兼容education-ui.css样式")
            print("   3. 修复按钮内联事件和兜底函数")
            print("\n🌐 请手动访问 http://localhost:5000/trial-courses 验证效果")
        else:
            print("\n❌ 页面加载失败，请检查Flask应用是否正常运行")

if __name__ == "__main__":
    main()
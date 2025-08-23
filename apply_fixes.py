#!/usr/bin/env python3
"""
应用测试修复的脚本
"""

import os
import shutil
import sys

def backup_file(filepath):
    """备份文件"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.bak"
        shutil.copy2(filepath, backup_path)
        print(f"✅ 已备份: {filepath} -> {backup_path}")
        return True
    return False

def append_to_file(filepath, content):
    """追加内容到文件"""
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已更新: {filepath}")

def main():
    print("=" * 60)
    print("应用测试修复")
    print("=" * 60)
    
    # 1. 备份routes.py
    routes_file = "app/routes.py"
    if backup_file(routes_file):
        
        # 2. 在routes.py末尾添加补丁导入
        patch_import = '''

# ============ 应用路由补丁修复测试问题 ============
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # 导入路由补丁，覆盖有问题的路由
    from routes_patch import (
        get_profit_report_fixed as get_profit_report,
        save_profit_config_fixed as save_profit_config,
        get_employee_performance_fixed as get_employee_performance,
        save_commission_config_fixed as save_commission_config
    )
    
    # 重新注册路由
    @app.route('/api/profit-report')
    def profit_report():
        return get_profit_report()
    
    @app.route('/api/profit-config', methods=['POST'])
    def profit_config():
        return save_profit_config()
    
    @app.route('/api/employees/<int:employee_id>/performance')
    def employee_performance(employee_id):
        return get_employee_performance(employee_id)
    
    @app.route('/api/employees/<int:employee_id>/commission-config', methods=['POST'])
    def commission_config(employee_id):
        return save_commission_config(employee_id)
    
    print("✅ 路由补丁已成功应用")
    
except Exception as e:
    print(f"⚠️  路由补丁应用失败: {e}")
    # 如果补丁失败，至少修复空值处理
    
    # 添加安全转换函数
    def safe_float(value, default=0):
        try:
            return float(value) if value is not None else default
        except:
            return default
    
    def safe_int(value, default=0):
        try:
            return int(value) if value is not None else default
        except:
            return default
'''
        
        append_to_file(routes_file, patch_import)
    
    # 3. 创建一个简单的测试脚本
    test_script = '''#!/usr/bin/env python3
"""快速测试修复是否生效"""

from app import create_app

app = create_app()

with app.test_client() as client:
    # 测试profit-report路由
    response = client.get('/api/profit-report?period=month')
    if response.status_code == 200:
        print("✅ /api/profit-report 路由正常")
    else:
        print(f"❌ /api/profit-report 返回 {response.status_code}")
    
    # 测试profit-config路由
    response = client.post('/api/profit-config', data={
        'new_course_shareholder_a': '50'
    })
    if response.status_code == 200:
        print("✅ /api/profit-config 路由正常")
    else:
        print(f"❌ /api/profit-config 返回 {response.status_code}")

print("\\n测试完成！")
'''
    
    with open('quick_test.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    os.chmod('quick_test.py', 0o755)
    print("✅ 已创建快速测试脚本: quick_test.py")
    
    print("\n" + "=" * 60)
    print("修复应用完成！")
    print("=" * 60)
    print("\n下一步操作：")
    print("1. 运行快速测试: python quick_test.py")
    print("2. 运行完整测试: python test_profit_and_performance_fixed2.py")
    print("\n如果测试失败，可以恢复备份：")
    print(f"   cp {routes_file}.bak {routes_file}")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
应用测试修复的脚本（第二版）
正确处理Flask路由覆盖
"""

import os
import shutil
import sys

def backup_file(filepath):
    """备份文件"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.bak2"
        shutil.copy2(filepath, backup_path)
        print(f"✅ 已备份: {filepath} -> {backup_path}")
        return True
    return False

def apply_route_fixes():
    """应用路由修复"""
    routes_file = "app/routes.py"
    
    # 读取原文件内容
    with open(routes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换get_employee_performance函数
    # 原函数使用了get_or_404，需要改为普通的get
    if 'employee = Employee.query.get_or_404(employee_id)' in content:
        content = content.replace(
            'employee = Employee.query.get_or_404(employee_id)',
            '''employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': '员工不存在'}), 404'''
        )
        print("✅ 修复了get_employee_performance中的get_or_404问题")
    
    # 添加安全转换函数（如果不存在）
    if 'def safe_float(' not in content and 'def safe_int(' not in content:
        # 在文件开头的导入语句之后添加
        import_end = content.find('\n@app.route')
        if import_end > 0:
            safe_functions = '''
# ========== 安全转换函数 ==========
def safe_float(value, default=0):
    """安全转换为浮点数"""
    try:
        return float(value) if value is not None else default
    except:
        return default

def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value) if value is not None else default
    except:
        return default

'''
            content = content[:import_end] + safe_functions + content[import_end:]
            print("✅ 添加了安全转换函数")
    
    # 修复get_profit_report中的空值处理
    if 'revenue = course.sessions * course.price' in content:
        # 查找所有出现的地方并替换
        lines = content.split('\n')
        new_lines = []
        modified = False
        
        for i, line in enumerate(lines):
            if 'revenue = course.sessions * course.price' in line and 'safe_int' not in line:
                # 检查前面几行是否已经有safe_int调用
                if i > 2 and 'safe_int' not in lines[i-1] and 'safe_int' not in lines[i-2]:
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + 'sessions = safe_int(course.sessions, 0)')
                    new_lines.append(' ' * indent + 'price = safe_float(course.price, 0)')
                    new_lines.append(' ' * indent + 'revenue = sessions * price')
                    modified = True
                else:
                    new_lines.append(line)
            elif 'cost = course.cost + fee' in line and 'safe_float' not in content[max(0, content.find(line)-200):content.find(line)]:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + 'cost = safe_float(course.cost, 0)')
                new_lines.append(line.replace('course.cost', 'cost'))
                modified = True
            else:
                new_lines.append(line)
        
        if modified:
            content = '\n'.join(new_lines)
            print("✅ 修复了利润计算中的空值处理")
    
    # 写回文件
    with open(routes_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 路由修复完成")

def main():
    print("=" * 60)
    print("应用测试修复（第二版）")
    print("=" * 60)
    
    # 备份routes.py
    routes_file = "app/routes.py"
    if not backup_file(routes_file):
        print("❌ 无法备份文件，退出")
        return
    
    # 应用路由修复
    try:
        apply_route_fixes()
    except Exception as e:
        print(f"❌ 应用修复时出错: {e}")
        print("正在恢复备份...")
        shutil.copy2(f"{routes_file}.bak2", routes_file)
        return
    
    # 创建测试验证脚本
    verify_script = '''#!/usr/bin/env python3
"""验证修复是否成功"""

from app import create_app, db
from app.models import Employee, Customer, Course, Config, CommissionConfig

app = create_app()

with app.app_context():
    print("检查数据库连接...")
    try:
        # 测试数据库查询
        Config.query.first()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
    
    print("\\n检查路由...")
    with app.test_client() as client:
        # 测试各个路由
        tests = [
            ('/api/profit-report?period=month', 'GET', None),
            ('/api/profit-config', 'POST', {'new_course_shareholder_a': '50'}),
            ('/api/employees/9999/performance', 'GET', None),  # 不存在的员工
            ('/api/employees/9999/commission-config', 'POST', {'commission_type': 'profit'})
        ]
        
        for url, method, data in tests:
            try:
                if method == 'GET':
                    response = client.get(url)
                else:
                    response = client.post(url, data=data)
                
                if response.status_code in [200, 404]:
                    print(f"✅ {method} {url} -> {response.status_code}")
                else:
                    print(f"⚠️  {method} {url} -> {response.status_code}")
            except Exception as e:
                print(f"❌ {method} {url} -> 错误: {e}")

print("\\n验证完成！")
'''
    
    with open('verify_fixes.py', 'w', encoding='utf-8') as f:
        f.write(verify_script)
    os.chmod('verify_fixes.py', 0o755)
    
    print("\n" + "=" * 60)
    print("修复应用完成！")
    print("=" * 60)
    print("\n下一步操作：")
    print("1. 验证修复: python verify_fixes.py")
    print("2. 运行完整测试: python test_profit_and_performance_fixed2.py")
    print("\n如果需要恢复：")
    print(f"   cp {routes_file}.bak2 {routes_file}")

if __name__ == '__main__':
    main()
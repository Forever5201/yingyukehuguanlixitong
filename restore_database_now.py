#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急恢复数据库
"""

import os
import shutil
from datetime import datetime

def emergency_restore():
    """紧急恢复数据库"""
    
    print("=== 紧急数据库恢复 ===")
    print("-" * 50)
    
    # 可能的备份位置
    backup_files = [
        'instance/database.sqlite.backup',
        'instance/database.sqlite.backup_20250823_202239',  # fix_database_now.py可能创建的
        'database.sqlite.backup',
    ]
    
    # 查找存在的备份
    found_backup = None
    for backup in backup_files:
        if os.path.exists(backup):
            size = os.path.getsize(backup) / 1024
            print(f"✓ 找到备份文件: {backup} ({size:.2f} KB)")
            found_backup = backup
            break
    
    if not found_backup:
        print("✗ 未找到任何备份文件！")
        print("\n请检查以下位置是否有备份：")
        print("1. instance目录下的.backup文件")
        print("2. 项目根目录下的备份文件")
        print("3. Git历史记录中的数据库文件")
        return False
    
    # 确认恢复
    print(f"\n准备从 {found_backup} 恢复数据")
    response = input("确认恢复？(y/n): ")
    
    if response.lower() != 'y':
        print("取消恢复")
        return False
    
    # 备份当前的数据库（如果存在）
    current_db = 'instance/database.sqlite'
    if os.path.exists(current_db):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_backup = f'{current_db}.broken_{timestamp}'
        shutil.move(current_db, temp_backup)
        print(f"✓ 已将当前数据库移动到: {temp_backup}")
    
    # 恢复备份
    shutil.copy2(found_backup, current_db)
    print(f"✓ 已恢复数据库: {found_backup} -> {current_db}")
    
    # 重新添加course_refund表（如果需要）
    print("\n正在检查并添加退费表...")
    os.system("python init_refund_table.py")
    
    print("\n✅ 恢复完成！")
    print("请运行 python run.py 检查数据是否正常")
    
    return True

if __name__ == "__main__":
    emergency_restore()
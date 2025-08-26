#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库备份和数据恢复
"""

import os
import sqlite3
import glob
from datetime import datetime

def check_database_status():
    """检查数据库状态和备份"""
    
    print("=== 数据库状态检查 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. 查找所有数据库文件
    print("\n1. 查找数据库文件：")
    db_files = []
    
    # 查找主数据库
    if os.path.exists('instance/database.sqlite'):
        db_files.append('instance/database.sqlite')
        size = os.path.getsize('instance/database.sqlite') / 1024  # KB
        print(f"  ✓ 主数据库: instance/database.sqlite ({size:.2f} KB)")
    else:
        print("  ✗ 主数据库不存在")
    
    # 查找备份文件
    backup_patterns = [
        'instance/*.backup',
        'instance/*.sqlite.backup',
        '*.backup',
        '*.sqlite.backup',
        'backup/*',
        '*backup*.sqlite'
    ]
    
    all_backups = []
    for pattern in backup_patterns:
        backups = glob.glob(pattern)
        all_backups.extend(backups)
    
    if all_backups:
        print("\n  找到的备份文件：")
        for backup in sorted(set(all_backups)):
            size = os.path.getsize(backup) / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(backup))
            print(f"  - {backup} ({size:.2f} KB, 修改时间: {mtime})")
    
    # 2. 检查主数据库内容
    if os.path.exists('instance/database.sqlite'):
        print("\n2. 检查主数据库内容：")
        try:
            conn = sqlite3.connect('instance/database.sqlite')
            cursor = conn.cursor()
            
            # 检查各表的记录数
            tables = [
                ('course', '课程'),
                ('customer', '客户'),
                ('employee', '员工'),
                ('taobao_order', '淘宝订单'),
                ('config', '配置'),
                ('course_refund', '退费记录')
            ]
            
            for table_name, desc in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  - {desc}表 ({table_name}): {count} 条记录")
                    
                    # 如果是course表且有数据，显示一些样本
                    if table_name == 'course' and count > 0:
                        cursor.execute(f"SELECT id, name, is_trial, created_at FROM {table_name} ORDER BY id DESC LIMIT 3")
                        samples = cursor.fetchall()
                        print(f"    最近的课程记录：")
                        for sample in samples:
                            trial_type = "试听课" if sample[2] else "正课"
                            print(f"      ID:{sample[0]}, {sample[1]}, {trial_type}, {sample[3]}")
                            
                except sqlite3.OperationalError as e:
                    print(f"  - {desc}表: 不存在或无法访问 ({str(e)})")
            
            conn.close()
            
        except Exception as e:
            print(f"  ✗ 无法读取数据库：{str(e)}")
    
    # 3. 数据恢复建议
    print("\n3. 数据恢复建议：")
    if all_backups:
        print("  找到备份文件，可以尝试恢复：")
        print("  1. 先备份当前数据库（如果有重要数据）")
        print("  2. 选择一个备份文件恢复")
        print("  3. 运行恢复命令")
    else:
        print("  ✗ 未找到备份文件")
        print("  可能的恢复方法：")
        print("  1. 检查是否有其他备份位置")
        print("  2. 检查版本控制系统是否有数据库备份")
        print("  3. 检查是否执行了错误的迁移脚本")

def restore_from_backup(backup_file):
    """从备份恢复数据库"""
    if not os.path.exists(backup_file):
        print(f"✗ 备份文件不存在：{backup_file}")
        return False
    
    # 备份当前数据库
    current_db = 'instance/database.sqlite'
    if os.path.exists(current_db):
        backup_current = f'{current_db}.before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename(current_db, backup_current)
        print(f"✓ 已备份当前数据库到：{backup_current}")
    
    # 恢复备份
    import shutil
    shutil.copy2(backup_file, current_db)
    print(f"✓ 已从备份恢复：{backup_file} -> {current_db}")
    
    return True

if __name__ == "__main__":
    check_database_status()
    
    # 如果需要恢复，取消下面的注释并指定备份文件
    # restore_from_backup('instance/database.sqlite.backup')
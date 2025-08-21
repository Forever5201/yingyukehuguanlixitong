#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试30天备份清理功能
"""

import os
import datetime
from backup_database import DatabaseBackup

def test_30day_cleanup():
    """测试30天清理功能"""
    backup_tool = DatabaseBackup()
    
    print("🧪 测试30天备份清理功能")
    print("=" * 50)
    
    # 显示当前配置
    print(f"📋 当前配置:")
    print(f"   • 保留时间: {backup_tool.retention_days} 天")
    print(f"   • 备份目录: {backup_tool.backup_dir}")
    
    # 检查当前备份文件
    if not os.path.exists(backup_tool.backup_dir):
        print("❌ 备份目录不存在")
        return
    
    backup_files = []
    for filename in os.listdir(backup_tool.backup_dir):
        if filename.startswith('database_backup_') and filename.endswith('.zip'):
            file_path = os.path.join(backup_tool.backup_dir, filename)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            backup_files.append((filename, file_time))
    
    backup_files.sort(key=lambda x: x[1])
    
    print(f"\n📁 当前备份文件: {len(backup_files)} 个")
    
    # 显示所有备份文件的时间
    current_time = datetime.datetime.now()
    cutoff_time = current_time - datetime.timedelta(days=backup_tool.retention_days)
    
    print(f"\n📅 时间分析:")
    print(f"   • 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   • 保留截止: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    expired_count = 0
    valid_count = 0
    
    print(f"\n📋 备份文件状态:")
    for filename, file_time in backup_files:
        age_days = (current_time - file_time).days
        age_hours = (current_time - file_time).seconds // 3600
        
        if file_time < cutoff_time:
            status = "❌ 过期"
            expired_count += 1
        else:
            status = "✅ 有效"
            valid_count += 1
        
        if age_days > 0:
            age_str = f"{age_days}天{age_hours}小时前"
        else:
            age_str = f"{age_hours}小时前"
        
        print(f"   {filename:<35} {age_str:<15} {status}")
    
    print(f"\n📊 统计结果:")
    print(f"   • 有效备份: {valid_count} 个")
    print(f"   • 过期备份: {expired_count} 个")
    
    if expired_count > 0:
        print(f"\n🧹 模拟清理过程:")
        print("   下次备份时将删除以下过期文件:")
        for filename, file_time in backup_files:
            if file_time < cutoff_time:
                print(f"   🗑️  {filename}")
    else:
        print(f"\n✅ 所有备份都在30天保留期内，无需清理")
    
    # 测试清理功能
    print(f"\n🔧 测试清理功能:")
    backup_tool.cleanup_old_backups()
    
    print(f"\n✅ 30天清理功能测试完成")

if __name__ == "__main__":
    test_30day_cleanup()
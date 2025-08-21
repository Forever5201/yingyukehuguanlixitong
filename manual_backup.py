#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动备份工具
随时可以执行的备份，不需要一直运行
"""

import os
import sys
from datetime import datetime
from backup_database import DatabaseBackup

def manual_backup():
    """执行手动备份"""
    print("🔒 手动备份工具")
    print("=" * 40)
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查数据库文件
    db_path = 'instance/database.sqlite'
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("💡 请确保在项目根目录运行此脚本")
        input("按回车键退出...")
        return False
    
    # 显示数据库信息
    db_size = os.path.getsize(db_path)
    print(f"📁 数据库文件: {db_path}")
    print(f"📊 文件大小: {db_size} 字节")
    
    # 执行备份
    print("\n🚀 开始备份...")
    backup_tool = DatabaseBackup()
    
    try:
        success = backup_tool.create_backup()
        
        if success:
            print("\n✅ 手动备份完成！")
            
            # 显示备份列表
            print("\n📋 最近的备份文件:")
            backup_tool.list_backups()
            
            # 记录到日志
            with open('backup_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 手动备份成功\n")
            
            print(f"\n💾 备份已保存到: backups/ 目录")
            print(f"📝 操作已记录到: backup_log.txt")
            
        else:
            print("\n❌ 备份失败")
            with open('backup_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 手动备份失败\n")
        
        return success
        
    except Exception as e:
        print(f"\n❌ 备份过程中发生错误: {e}")
        with open('backup_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 备份错误: {e}\n")
        return False

def show_backup_status():
    """显示备份状态"""
    print("\n📊 备份状态:")
    print("-" * 30)
    
    # 检查备份目录
    backup_dir = 'backups'
    if os.path.exists(backup_dir):
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
        print(f"📁 备份文件数量: {len(backup_files)}")
        
        if backup_files:
            # 最新备份
            backup_files.sort(reverse=True)
            latest_backup = backup_files[0]
            backup_path = os.path.join(backup_dir, latest_backup)
            backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
            
            print(f"🕒 最新备份: {latest_backup}")
            print(f"⏰ 备份时间: {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 计算距离现在的时间
            time_diff = datetime.now() - backup_time
            hours_ago = time_diff.total_seconds() / 3600
            
            if hours_ago < 24:
                print(f"📅 距离现在: {hours_ago:.1f} 小时前")
            else:
                print(f"📅 距离现在: {hours_ago/24:.1f} 天前")
        else:
            print("📁 暂无备份文件")
    else:
        print("📁 备份目录不存在")
    
    # 检查日志
    if os.path.exists('backup_log.txt'):
        with open('backup_log.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"📝 备份日志: {len(lines)} 条记录")
    else:
        print("📝 暂无备份日志")

def main():
    """主函数"""
    print("🎯 选择操作:")
    print("1. 立即执行备份")
    print("2. 查看备份状态")
    print("3. 查看备份列表")
    print("4. 退出")
    
    while True:
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1':
            manual_backup()
            break
        elif choice == '2':
            show_backup_status()
            break
        elif choice == '3':
            backup_tool = DatabaseBackup()
            backup_tool.list_backups()
            break
        elif choice == '4':
            print("退出")
            break
        else:
            print("无效选择，请重新输入")
    
    input("\n按回车键退出...")

if __name__ == '__main__':
    main()
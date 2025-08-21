#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速备份脚本
一键备份当前数据库
"""

from backup_database import DatabaseBackup

def quick_backup():
    """快速备份数据库"""
    print("🚀 开始快速备份...")
    print("=" * 40)
    
    backup_tool = DatabaseBackup()
    success = backup_tool.create_backup()
    
    if success:
        print("\n🎉 备份完成！你的数据已安全保存。")
        print("\n📍 备份位置: backups/ 目录")
        print("💡 提示: 建议定期备份重要数据")
    else:
        print("\n❌ 备份失败，请检查数据库文件")
    
    input("\n按回车键退出...")

if __name__ == '__main__':
    quick_backup()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键启动自动备份
默认每天凌晨2点自动备份
"""

import time
import threading
import schedule
from datetime import datetime
from backup_database import DatabaseBackup

def backup_job():
    """执行备份任务"""
    try:
        print(f"\n🕒 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动备份...")
        
        backup_tool = DatabaseBackup()
        success = backup_tool.create_backup()
        
        if success:
            print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 自动备份完成")
            # 记录到日志文件
            with open('backup_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 自动备份成功\n")
        else:
            print(f"❌ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 自动备份失败")
            with open('backup_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 自动备份失败\n")
                
    except Exception as e:
        print(f"❌ 备份过程中发生错误: {e}")
        with open('backup_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 备份错误: {e}\n")

def run_scheduler():
    """运行调度器"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

def main():
    """主函数"""
    print("🚀 启动自动备份服务")
    print("=" * 50)
    
    # 设置每天凌晨2点备份
    schedule.every().day.at("02:00").do(backup_job)
    
    print("📅 已设置每天凌晨 02:00 自动备份")
    print("📁 备份文件保存在 backups/ 目录")
    print("📝 备份日志保存在 backup_log.txt")
    print("\n✅ 自动备份服务已启动！")
    print("💡 程序将在后台持续运行，按 Ctrl+C 停止")
    
    # 显示下次备份时间
    next_run = schedule.next_run()
    if next_run:
        print(f"⏰ 下次备份时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 立即执行一次备份作为测试
    print("\n🧪 执行测试备份...")
    backup_job()
    
    try:
        # 在后台线程中运行调度器
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # 主线程保持运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 自动备份服务已停止")
        schedule.clear()

if __name__ == '__main__':
    main()
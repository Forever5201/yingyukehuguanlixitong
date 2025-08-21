#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的自动备份设置工具
无需管理员权限，使用Python实现定时备份
"""

import os
import time
import threading
import schedule
from datetime import datetime
from backup_database import DatabaseBackup

class AutoBackupScheduler:
    def __init__(self):
        self.backup_tool = DatabaseBackup()
        self.is_running = False
        self.backup_thread = None
        
    def backup_job(self):
        """执行备份任务"""
        try:
            print(f"\n🕒 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动备份...")
            success = self.backup_tool.create_backup()
            
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
    
    def run_scheduler(self):
        """运行调度器"""
        self.is_running = True
        print("🔄 自动备份调度器已启动...")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def start_auto_backup(self, backup_time="02:00", frequency="daily"):
        """启动自动备份"""
        # 清除之前的任务
        schedule.clear()
        
        # 设置备份任务
        if frequency == "daily":
            schedule.every().day.at(backup_time).do(self.backup_job)
            print(f"📅 已设置每天 {backup_time} 自动备份")
        elif frequency == "hourly":
            schedule.every().hour.do(self.backup_job)
            print("📅 已设置每小时自动备份")
        elif frequency == "weekly":
            schedule.every().week.do(self.backup_job)
            print("📅 已设置每周自动备份")
        
        # 在后台线程中运行调度器
        self.backup_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.backup_thread.start()
        
        print("✅ 自动备份已启动！")
        print("💡 程序将在后台持续运行，按 Ctrl+C 停止")
    
    def stop_auto_backup(self):
        """停止自动备份"""
        self.is_running = False
        schedule.clear()
        print("🛑 自动备份已停止")

def main():
    """主函数"""
    scheduler = AutoBackupScheduler()
    
    print("🔒 自动备份设置工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 设置每天自动备份")
        print("2. 设置每小时自动备份") 
        print("3. 设置每周自动备份")
        print("4. 立即执行一次备份")
        print("5. 查看备份日志")
        print("6. 退出")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == '1':
            backup_time = input("请输入备份时间 (格式: HH:MM, 默认 02:00): ").strip()
            if not backup_time:
                backup_time = "02:00"
            
            scheduler.start_auto_backup(backup_time, "daily")
            
            try:
                # 保持程序运行
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                scheduler.stop_auto_backup()
                break
                
        elif choice == '2':
            scheduler.start_auto_backup(frequency="hourly")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                scheduler.stop_auto_backup()
                break
                
        elif choice == '3':
            scheduler.start_auto_backup(frequency="weekly")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                scheduler.stop_auto_backup()
                break
                
        elif choice == '4':
            scheduler.backup_job()
            
        elif choice == '5':
            if os.path.exists('backup_log.txt'):
                print("\n📋 备份日志:")
                print("-" * 40)
                with open('backup_log.txt', 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                print("📋 暂无备份日志")
                
        elif choice == '6':
            scheduler.stop_auto_backup()
            print("退出自动备份设置工具")
            break
        else:
            print("无效选项，请重新选择")

if __name__ == '__main__':
    main()
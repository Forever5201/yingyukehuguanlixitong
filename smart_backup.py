#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能备份脚本 - 解决凌晨关机问题
支持多时段备份和开机自动补偿
"""

import os
import sys
import time
import datetime
from backup_database import DatabaseBackup

class SmartBackup:
    def __init__(self):
        self.backup_tool = DatabaseBackup()
        self.log_file = "smart_backup_log.txt"
        
    def log_message(self, message):
        """记录日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"日志记录失败: {e}")
        
        print(f"{timestamp} - {message}")
    
    def check_last_backup(self):
        """检查最后一次备份时间"""
        try:
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                return None, "无备份记录"
            
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
            if not backup_files:
                return None, "无备份文件"
            
            # 获取最新的备份文件
            backup_files.sort(reverse=True)
            latest_backup = backup_files[0]
            
            # 从文件名提取时间
            try:
                time_str = latest_backup.replace('database_backup_', '').replace('.zip', '')
                last_backup_time = datetime.datetime.strptime(time_str, '%Y%m%d_%H%M%S')
                return last_backup_time, f"最后备份: {latest_backup}"
            except:
                return None, f"无法解析备份时间: {latest_backup}"
                
        except Exception as e:
            return None, f"检查备份失败: {e}"
    
    def should_backup(self):
        """判断是否需要备份"""
        last_backup_time, status = self.check_last_backup()
        current_time = datetime.datetime.now()
        
        self.log_message(f"检查备份状态: {status}")
        
        if last_backup_time is None:
            self.log_message("未找到有效备份，需要立即备份")
            return True, "首次备份"
        
        # 计算时间差
        time_diff = current_time - last_backup_time
        hours_since_backup = time_diff.total_seconds() / 3600
        
        self.log_message(f"距离上次备份: {hours_since_backup:.1f} 小时")
        
        # 如果超过20小时没有备份，则需要备份
        if hours_since_backup >= 20:
            return True, f"超过20小时未备份 ({hours_since_backup:.1f}小时)"
        
        return False, f"备份较新，无需备份 ({hours_since_backup:.1f}小时前)"
    
    def execute_backup(self):
        """执行备份"""
        try:
            self.log_message("开始执行智能备份...")
            
            # 检查是否需要备份
            need_backup, reason = self.should_backup()
            
            if not need_backup:
                self.log_message(f"跳过备份: {reason}")
                return True
            
            self.log_message(f"执行备份: {reason}")
            
            # 执行备份
            backup_file = self.backup_tool.create_backup()
            
            if backup_file:
                self.log_message(f"备份成功: {backup_file}")
                
                # 显示备份信息
                if os.path.exists(backup_file):
                    size = os.path.getsize(backup_file)
                    self.log_message(f"备份文件大小: {size} 字节")
                
                return True
            else:
                self.log_message("备份失败: 未生成备份文件")
                return False
                
        except Exception as e:
            self.log_message(f"备份过程出错: {e}")
            return False
    
    def show_backup_status(self):
        """显示备份状态"""
        print("\n" + "="*50)
        print("智能备份状态")
        print("="*50)
        
        # 检查最后备份
        last_backup_time, status = self.check_last_backup()
        print(f"最后备份: {status}")
        
        if last_backup_time:
            current_time = datetime.datetime.now()
            time_diff = current_time - last_backup_time
            hours_ago = time_diff.total_seconds() / 3600
            print(f"距离现在: {hours_ago:.1f} 小时")
        
        # 检查备份文件数量
        try:
            backup_dir = "backups"
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
                print(f"备份文件数量: {len(backup_files)}")
            else:
                print("备份文件数量: 0")
        except:
            print("备份文件数量: 无法检查")
        
        # 判断备份建议
        need_backup, reason = self.should_backup()
        if need_backup:
            print(f"建议: 需要备份 ({reason})")
        else:
            print(f"状态: 备份正常 ({reason})")
        
        print("="*50)

def main():
    """主函数"""
    smart_backup = SmartBackup()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            smart_backup.show_backup_status()
            return
        elif sys.argv[1] == "force":
            smart_backup.log_message("强制执行备份")
            smart_backup.backup_tool.create_backup()
            return
    
    # 默认执行智能备份
    smart_backup.execute_backup()

if __name__ == "__main__":
    main()
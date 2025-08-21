#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能备份任务设置 - 多时段备份方案
解决凌晨关机问题
"""

import os
import sys
import subprocess
import datetime

class SmartBackupSetup:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.python_path = sys.executable
        self.backup_script = os.path.join(self.script_dir, "smart_backup.py")
        
    def create_task(self, task_name, time_str, description):
        """创建Windows任务计划"""
        try:
            # 删除已存在的任务
            subprocess.run([
                "schtasks", "/delete", "/tn", task_name, "/f"
            ], capture_output=True)
            
            # 创建新任务
            cmd = [
                "schtasks", "/create",
                "/tn", task_name,
                "/tr", f'"{self.python_path}" "{self.backup_script}"',
                "/sc", "daily",
                "/st", time_str,
                "/sd", datetime.datetime.now().strftime("%Y/%m/%d"),
                "/rl", "highest",
                "/f"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 成功创建任务: {task_name} ({time_str})")
                return True
            else:
                print(f"❌ 创建任务失败: {task_name}")
                print(f"错误: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 创建任务异常: {e}")
            return False
    
    def setup_multiple_backups(self):
        """设置多时段备份任务"""
        print("🚀 设置智能多时段备份任务...")
        print("="*50)
        
        # 定义多个备份时间点
        backup_times = [
            ("SmartBackup_Morning", "08:00", "早上8点备份"),
            ("SmartBackup_Noon", "12:00", "中午12点备份"), 
            ("SmartBackup_Evening", "18:00", "晚上6点备份"),
            ("SmartBackup_Night", "22:00", "晚上10点备份")
        ]
        
        success_count = 0
        
        for task_name, time_str, description in backup_times:
            if self.create_task(task_name, time_str, description):
                success_count += 1
        
        print("="*50)
        print(f"📊 任务创建结果: {success_count}/{len(backup_times)} 成功")
        
        if success_count > 0:
            print("\n✅ 智能备份设置完成！")
            print("\n📅 备份时间表:")
            for _, time_str, description in backup_times:
                print(f"   • {time_str} - {description}")
            
            print("\n💡 智能备份特点:")
            print("   • 只有超过20小时未备份才会执行")
            print("   • 多个时间点确保至少一次成功")
            print("   • 自动跳过不必要的备份")
            print("   • 详细的备份日志记录")
            
            print("\n🔧 管理命令:")
            print("   • 查看状态: python smart_backup.py status")
            print("   • 强制备份: python smart_backup.py force")
            print("   • 查看日志: type smart_backup_log.txt")
            
        return success_count > 0
    
    def test_backup(self):
        """测试备份功能"""
        print("\n🧪 测试智能备份功能...")
        try:
            result = subprocess.run([
                self.python_path, self.backup_script, "status"
            ], capture_output=True, text=True, cwd=self.script_dir)
            
            print("📊 备份状态:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ 警告信息:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🎯 智能备份系统设置")
    print("解决凌晨关机备份问题")
    print("="*50)
    
    setup = SmartBackupSetup()
    
    # 设置多时段备份
    if setup.setup_multiple_backups():
        # 测试备份功能
        setup.test_backup()
        
        print("\n🎉 设置完成！现在你的数据有了全天候保护：")
        print("   • 每天4个时间点自动检查")
        print("   • 只在需要时才执行备份")
        print("   • 即使凌晨关机也不影响")
        
    else:
        print("\n❌ 设置失败，请检查管理员权限")

if __name__ == "__main__":
    main()
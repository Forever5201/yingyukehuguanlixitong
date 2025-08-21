#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份管理工具 - 查看和管理备份策略
"""

import os
import datetime
from backup_database import DatabaseBackup

class BackupManager:
    def __init__(self):
        self.backup_tool = DatabaseBackup()
        self.backup_dir = "backups"
        
    def get_backup_info(self):
        """获取备份信息"""
        if not os.path.exists(self.backup_dir):
            return {
                'total_files': 0,
                'total_size': 0,
                'oldest_backup': None,
                'newest_backup': None,
                'files': []
            }
        
        backup_files = []
        total_size = 0
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('database_backup_') and filename.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, filename)
                file_size = os.path.getsize(file_path)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                backup_files.append({
                    'filename': filename,
                    'size': file_size,
                    'time': file_time,
                    'path': file_path
                })
                total_size += file_size
        
        backup_files.sort(key=lambda x: x['time'])
        
        return {
            'total_files': len(backup_files),
            'total_size': total_size,
            'oldest_backup': backup_files[0] if backup_files else None,
            'newest_backup': backup_files[-1] if backup_files else None,
            'files': backup_files
        }
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def show_backup_strategy(self):
        """显示备份策略"""
        print("="*60)
        print("📋 备份策略说明")
        print("="*60)
        
        print("🔄 备份频率:")
        print("   • 智能备份: 超过20小时未备份时自动执行")
        print("   • 执行时间: 每天 8:00, 12:00, 18:00, 22:00")
        print("   • 手动备份: 随时可执行")
        
        print("\n🗂️ 备份保留策略:")
        print(f"   • 保留时间: 最近 {self.backup_tool.retention_days} 天的备份")
        print("   • 自动清理: 超过30天的备份自动删除")
        print("   • 压缩存储: 所有备份都经过ZIP压缩")
        
        print("\n💾 备份内容:")
        print("   • 完整数据库: 每次备份都是完整的数据库副本")
        print("   • 包含所有表: 客户、员工、课程、订单等所有数据")
        print("   • MD5校验: 每个备份都有完整性校验")
        
        print("\n🛡️ 数据安全:")
        print("   • 本地存储: 备份文件存储在 backups/ 目录")
        print("   • 原子操作: 使用SQLite官方备份API")
        print("   • 恢复功能: 支持从任意备份恢复数据")
    
    def show_current_status(self):
        """显示当前备份状态"""
        info = self.get_backup_info()
        
        print("\n" + "="*60)
        print("📊 当前备份状态")
        print("="*60)
        
        print(f"📁 备份文件数量: {info['total_files']}")
        print(f"💾 总占用空间: {self.format_size(info['total_size'])}")
        
        if info['oldest_backup']:
            oldest = info['oldest_backup']
            newest = info['newest_backup']
            
            print(f"📅 最旧备份: {oldest['time'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📅 最新备份: {newest['time'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 计算时间跨度
            time_span = newest['time'] - oldest['time']
            days = time_span.days
            hours = time_span.seconds // 3600
            
            if days > 0:
                print(f"⏱️ 时间跨度: {days}天 {hours}小时")
            else:
                print(f"⏱️ 时间跨度: {hours}小时")
            
            # 检查是否有过期备份
            current_time = datetime.datetime.now()
            cutoff_time = current_time - datetime.timedelta(days=self.backup_tool.retention_days)
            
            expired_count = 0
            for file_info in info['files']:
                if file_info['time'] < cutoff_time:
                    expired_count += 1
            
            if expired_count > 0:
                print(f"⚠️ 状态: 发现 {expired_count} 个过期备份，下次备份时将自动清理")
            else:
                print(f"✅ 状态: 正常 (所有备份都在30天保留期内)")
        else:
            print("❌ 状态: 未找到备份文件")
    
    def show_backup_list(self):
        """显示备份文件列表"""
        info = self.get_backup_info()
        
        if not info['files']:
            print("\n❌ 没有找到备份文件")
            return
        
        print("\n" + "="*80)
        print("📋 备份文件详情")
        print("="*80)
        print(f"{'文件名':<35} {'大小':<10} {'创建时间':<20} {'状态'}")
        print("-" * 80)
        
        # 按时间倒序显示（最新的在前）
        files = sorted(info['files'], key=lambda x: x['time'], reverse=True)
        
        current_time = datetime.datetime.now()
        cutoff_time = current_time - datetime.timedelta(days=self.backup_tool.retention_days)
        
        for i, file_info in enumerate(files):
            filename = file_info['filename']
            size = self.format_size(file_info['size'])
            time_str = file_info['time'].strftime('%Y-%m-%d %H:%M:%S')
            
            # 标记状态
            if i == 0:
                status = "最新"
            elif file_info['time'] < cutoff_time:
                status = "过期"
            else:
                status = "保留"
            
            print(f"{filename:<35} {size:<10} {time_str:<20} {status}")
    
    def estimate_future_usage(self):
        """估算未来存储使用情况"""
        info = self.get_backup_info()
        
        if info['total_files'] < 2:
            print("\n⚠️ 备份文件太少，无法估算增长趋势")
            return
        
        print("\n" + "="*60)
        print("📈 存储使用预估")
        print("="*60)
        
        # 计算平均文件大小
        avg_size = info['total_size'] / info['total_files']
        
        # 估算30天保留期的最大存储使用（假设每天1次备份）
        max_backups_30days = 30  # 30天最多30个备份
        max_usage = avg_size * max_backups_30days
        
        print(f"📊 平均备份大小: {self.format_size(avg_size)}")
        print(f"📊 最大存储使用: {self.format_size(max_usage)} (30天保留期，约30个备份)")
        
        # 估算每月存储增长
        print(f"📊 月增长估算: 0 (自动清理过期备份，总量稳定)")
        print(f"📊 实际存储: 随时间稳定在 {self.format_size(max_usage)} 左右")
        
        print("\n💡 存储优化:")
        print("   • 自动清理确保存储使用稳定")
        print("   • ZIP压缩减少约60-80%存储空间")
        print("   • 可根据需要调整保留数量")

def main():
    """主函数"""
    manager = BackupManager()
    
    print("🔧 备份管理工具")
    
    # 显示备份策略
    manager.show_backup_strategy()
    
    # 显示当前状态
    manager.show_current_status()
    
    # 显示备份列表
    manager.show_backup_list()
    
    # 显示存储预估
    manager.estimate_future_usage()
    
    print("\n" + "="*60)
    print("🎯 总结:")
    print("   • 备份不会无限增长，有自动清理机制")
    print("   • 智能备份避免频繁重复备份")
    print("   • 存储使用量稳定可控")
    print("="*60)

if __name__ == "__main__":
    main()
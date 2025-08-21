#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库备份工具
用于定期备份SQLite数据库，防止数据丢失
"""

import os
import shutil
import sqlite3
import datetime
import zipfile
import hashlib

class DatabaseBackup:
    def __init__(self):
        self.db_path = 'instance/database.sqlite'
        self.backup_dir = 'backups'
        self.retention_days = 30  # 保留最近30天的备份
        
    def ensure_backup_dir(self):
        """确保备份目录存在"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"创建备份目录: {self.backup_dir}")
    
    def get_file_hash(self, file_path):
        """计算文件MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def create_backup(self):
        """创建数据库备份"""
        if not os.path.exists(self.db_path):
            print(f"错误: 数据库文件不存在 - {self.db_path}")
            return False
        
        self.ensure_backup_dir()
        
        # 生成备份文件名（包含时间戳）
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"database_backup_{timestamp}.sqlite"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # 使用SQLite的备份API进行安全备份
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            # 执行备份
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            # 计算文件哈希值
            file_hash = self.get_file_hash(backup_path)
            file_size = os.path.getsize(backup_path)
            
            print(f"✅ 备份成功创建:")
            print(f"   文件: {backup_path}")
            print(f"   大小: {file_size} 字节")
            print(f"   MD5: {file_hash}")
            
            # 创建压缩备份
            zip_path = backup_path.replace('.sqlite', '.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_filename)
            
            # 删除未压缩的备份文件
            os.remove(backup_path)
            print(f"   压缩备份: {zip_path}")
            
            # 清理旧备份
            self.cleanup_old_backups()
            
            return True
            
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
    
    def cleanup_old_backups(self):
        """清理旧的备份文件，只保留最近30天的备份"""
        if not os.path.exists(self.backup_dir):
            return
            
        current_time = datetime.datetime.now()
        cutoff_time = current_time - datetime.timedelta(days=self.retention_days)
        
        deleted_count = 0
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('database_backup_') and filename.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, filename)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # 删除超过30天的备份
                if file_time < cutoff_time:
                    os.remove(file_path)
                    print(f"🗑️  删除过期备份: {filename} (创建于 {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
                    deleted_count += 1
        
        if deleted_count > 0:
            print(f"📊 清理完成，删除了 {deleted_count} 个过期备份文件")
        else:
            print("📊 没有过期的备份文件需要清理")
    
    def list_backups(self):
        """列出所有备份文件"""
        if not os.path.exists(self.backup_dir):
            print("没有找到备份目录")
            return
        
        backup_files = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('database_backup_') and filename.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, filename)
                file_size = os.path.getsize(file_path)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                backup_files.append((filename, file_size, file_time))
        
        if not backup_files:
            print("没有找到备份文件")
            return
        
        backup_files.sort(key=lambda x: x[2], reverse=True)
        
        print("\n📁 数据库备份列表:")
        print("-" * 60)
        for filename, size, time in backup_files:
            print(f"{filename:<35} {size:>8} 字节  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def restore_backup(self, backup_filename):
        """从备份恢复数据库"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"错误: 备份文件不存在 - {backup_path}")
            return False
        
        try:
            # 创建当前数据库的备份
            if os.path.exists(self.db_path):
                current_backup = f"database_before_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
                shutil.copy2(self.db_path, os.path.join(self.backup_dir, current_backup))
                print(f"当前数据库已备份为: {current_backup}")
            
            # 解压备份文件
            temp_db_path = backup_path.replace('.zip', '.sqlite')
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.backup_dir)
            
            # 恢复数据库
            shutil.copy2(temp_db_path, self.db_path)
            
            # 清理临时文件
            os.remove(temp_db_path)
            
            print(f"✅ 数据库恢复成功: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False

def main():
    """主函数"""
    backup_tool = DatabaseBackup()
    
    print("🔒 数据库备份工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 创建备份")
        print("2. 列出备份")
        print("3. 恢复备份")
        print("4. 退出")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            backup_tool.create_backup()
        elif choice == '2':
            backup_tool.list_backups()
        elif choice == '3':
            backup_tool.list_backups()
            backup_name = input("\n请输入要恢复的备份文件名: ").strip()
            if backup_name:
                backup_tool.restore_backup(backup_name)
        elif choice == '4':
            print("退出备份工具")
            break
        else:
            print("无效选项，请重新选择")

if __name__ == '__main__':
    main()
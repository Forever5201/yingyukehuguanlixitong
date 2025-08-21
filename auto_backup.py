#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动备份脚本
可以通过Windows任务计划程序定期执行
"""

import sys
import os
from backup_database import DatabaseBackup

def auto_backup():
    """自动执行备份"""
    print("开始自动备份...")
    
    backup_tool = DatabaseBackup()
    success = backup_tool.create_backup()
    
    if success:
        print("自动备份完成")
        return 0
    else:
        print("自动备份失败")
        return 1

if __name__ == '__main__':
    exit_code = auto_backup()
    sys.exit(exit_code)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows系统级自动备份设置
无需保持程序运行，集成到系统任务计划
"""

import os
import subprocess
import sys
from pathlib import Path

def create_task_xml():
    """创建Windows任务计划XML配置"""
    current_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    script_path = current_dir / "auto_backup.py"
    
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2025-08-02T13:30:00</Date>
    <Author>客户管理系统</Author>
    <Description>数据库自动备份任务</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-08-02T02:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{os.environ.get('USERNAME', 'User')}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{script_path}"</Arguments>
      <WorkingDirectory>{current_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    xml_file = current_dir / "backup_task.xml"
    with open(xml_file, 'w', encoding='utf-16') as f:
        f.write(xml_content)
    
    return xml_file

def setup_windows_task():
    """设置Windows任务计划"""
    print("🔧 正在设置Windows系统级自动备份...")
    
    try:
        # 创建XML配置文件
        xml_file = create_task_xml()
        print(f"✅ 创建任务配置文件: {xml_file}")
        
        # 删除已存在的任务（如果有）
        try:
            subprocess.run([
                'schtasks', '/delete', '/tn', 'DatabaseAutoBackup', '/f'
            ], capture_output=True, check=False)
        except:
            pass
        
        # 创建新任务
        result = subprocess.run([
            'schtasks', '/create', '/xml', str(xml_file), '/tn', 'DatabaseAutoBackup'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Windows任务计划设置成功！")
            print("\n📋 任务详情:")
            print("   任务名称: DatabaseAutoBackup")
            print("   执行时间: 每天凌晨 02:00")
            print("   执行方式: 系统级任务，无需保持程序运行")
            print("   管理位置: 任务计划程序 -> 任务计划程序库")
            
            # 显示任务信息
            info_result = subprocess.run([
                'schtasks', '/query', '/tn', 'DatabaseAutoBackup', '/fo', 'list', '/v'
            ], capture_output=True, text=True)
            
            if info_result.returncode == 0:
                print("\n🔍 任务状态: 已创建并启用")
            
            # 清理XML文件
            xml_file.unlink()
            
            return True
            
        else:
            print(f"❌ 任务创建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        return False

def test_backup():
    """测试备份功能"""
    print("\n🧪 测试备份功能...")
    try:
        result = subprocess.run([
            sys.executable, "auto_backup.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ 备份测试成功")
            print(result.stdout)
        else:
            print("❌ 备份测试失败")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🚀 Windows系统级自动备份设置工具")
    print("=" * 50)
    
    print("\n💡 此方案的优势:")
    print("✅ 无需保持程序运行")
    print("✅ 集成到Windows系统")
    print("✅ 开机自动启用")
    print("✅ 关机重启后自动恢复")
    print("✅ 可通过任务计划程序管理")
    
    choice = input("\n是否继续设置Windows系统级自动备份？(y/n): ").strip().lower()
    
    if choice in ['y', 'yes', '是']:
        # 测试备份功能
        test_backup()
        
        # 设置Windows任务
        success = setup_windows_task()
        
        if success:
            print("\n🎉 设置完成！")
            print("\n📝 使用说明:")
            print("1. 备份将在每天凌晨2点自动执行")
            print("2. 无需保持任何程序运行")
            print("3. 可在'任务计划程序'中查看和管理")
            print("4. 手动测试: 运行 'python auto_backup.py'")
            
            print("\n🔧 管理任务:")
            print("- 查看任务: 任务计划程序 -> DatabaseAutoBackup")
            print("- 手动运行: 右键任务 -> 运行")
            print("- 禁用任务: 右键任务 -> 禁用")
            print("- 删除任务: 右键任务 -> 删除")
            
        else:
            print("\n💡 备选方案:")
            print("如果系统级设置失败，可以使用:")
            print("python start_auto_backup.py  # 需要保持运行")
    else:
        print("取消设置")

if __name__ == '__main__':
    main()
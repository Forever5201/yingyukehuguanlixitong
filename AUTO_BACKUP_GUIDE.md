# 🔒 自动备份设置指南

## 📋 概述
为你的客户管理系统设置了完整的自动备份解决方案，确保数据安全。

## 🎯 备份方案

### 方案一：一键自动备份（推荐）
```bash
python start_auto_backup.py
```

**特点：**
- ✅ 每天凌晨2点自动备份
- ✅ 启动时立即执行测试备份
- ✅ 后台持续运行
- ✅ 自动记录备份日志
- ✅ 简单易用，无需管理员权限

### 方案二：自定义备份设置
```bash
python setup_backup_simple.py
```

**功能：**
- 🕒 自定义备份时间
- 📅 多种备份频率（每天/每小时/每周）
- 📋 查看备份日志
- 🔄 立即执行备份

### 方案三：Windows任务计划程序（高级）
```powershell
# 以管理员权限运行
.\setup_auto_backup.ps1
```

**特点：**
- 🔧 集成到Windows系统
- ⚡ 开机自动启动
- 🎛️ 通过任务计划程序管理

## 📁 文件说明

| 文件名 | 用途 | 说明 |
|--------|------|------|
| `start_auto_backup.py` | 一键启动自动备份 | 默认每天2点备份 |
| `setup_backup_simple.py` | 自定义备份设置 | 交互式配置 |
| `auto_backup.bat` | Windows批处理 | 配合任务计划使用 |
| `setup_auto_backup.ps1` | PowerShell脚本 | 设置Windows任务 |
| `backup_log.txt` | 备份日志 | 记录备份历史 |

## 🚀 快速开始

### 1. 立即启动自动备份
```bash
# 在项目目录下运行
python start_auto_backup.py
```

### 2. 查看备份文件
备份文件保存在 `backups/` 目录：
- 格式：`database_backup_YYYYMMDD_HHMMSS.zip`
- 包含完整的数据库数据
- 自动压缩，节省空间

### 3. 查看备份日志
```bash
# 查看 backup_log.txt 文件
type backup_log.txt
```

## ⚙️ 配置选项

### 修改备份时间
编辑 `start_auto_backup.py` 文件：
```python
# 修改这一行的时间
schedule.every().day.at("02:00").do(backup_job)
```

### 修改备份频率
```python
# 每小时备份
schedule.every().hour.do(backup_job)

# 每周备份
schedule.every().week.do(backup_job)

# 每天指定时间
schedule.every().day.at("14:30").do(backup_job)
```

## 📊 备份状态监控

### 查看当前备份
```bash
python backup_database.py
# 选择选项 2 - 列出备份
```

### 备份日志格式
```
[2025-08-02 13:20:27] 自动备份成功
[2025-08-02 14:00:00] 自动备份成功
```

## 🔧 故障排除

### 常见问题

1. **权限问题**
   - 确保对项目目录有写入权限
   - Windows任务计划需要管理员权限

2. **Python环境**
   - 确保安装了 `schedule` 库：`pip install schedule`
   - 确保Python路径正确

3. **备份失败**
   - 检查数据库文件是否存在
   - 查看 `backup_log.txt` 了解错误详情

### 手动测试
```bash
# 测试备份功能
python quick_backup.py

# 测试自动备份脚本
python auto_backup.py
```

## 💡 最佳实践

1. **定期检查**：每周检查备份日志和备份文件
2. **异地存储**：定期将备份文件复制到其他位置
3. **测试恢复**：定期测试备份恢复功能
4. **监控空间**：确保备份目录有足够空间

## 🎯 推荐使用

**日常使用推荐：**
```bash
python start_auto_backup.py
```

这个命令会：
- ✅ 立即执行一次测试备份
- ✅ 设置每天凌晨2点自动备份
- ✅ 在后台持续运行
- ✅ 记录所有备份操作

**保持程序运行：**
- 可以最小化终端窗口
- 程序会在后台持续运行
- 按 Ctrl+C 可以停止服务

你的数据现在有了完整的自动备份保护！🛡️
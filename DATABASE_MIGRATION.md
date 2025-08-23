# 数据库迁移指南

本项目使用 Flask-Migrate 管理数据库迁移，并配置了 Git Hook 自动迁移功能。

## 自动迁移功能

### Git Hook 自动迁移
当你执行 `git pull` 或 `git merge` 后，系统会自动：
1. 检查是否有数据库模型的更改
2. 自动安装/更新依赖
3. 执行数据库迁移
4. 应用更改到数据库

**注意**：请确保在执行 `git pull` 前已激活 Python 虚拟环境！

## 手动迁移命令

### 1. 快速修复当前问题
如果遇到 "no such column" 错误，可以运行：
```bash
python quick_migrate.py
```

### 2. 完整的自动迁移
运行自动迁移脚本：
```bash
python migrate.py
```

### 3. 初始化迁移系统（首次设置）
```bash
./setup_migrations.sh
```

### 4. 使用 Flask-Migrate 命令

设置环境变量：
```bash
export FLASK_APP=run.py
```

常用命令：
```bash
# 初始化迁移
flask db init

# 生成迁移文件
flask db migrate -m "描述更改内容"

# 应用迁移
flask db upgrade

# 查看当前版本
flask db current

# 查看历史版本
flask db history

# 回滚到上一个版本
flask db downgrade
```

## 工作流程

1. **开发新功能时**：
   - 修改 `app/models.py` 中的模型
   - 运行 `flask db migrate -m "描述更改"`
   - 运行 `flask db upgrade` 应用更改
   - 提交迁移文件到 Git

2. **拉取代码时**：
   - 确保激活虚拟环境
   - 执行 `git pull`
   - Git Hook 会自动执行迁移

3. **遇到问题时**：
   - 运行 `python quick_migrate.py` 快速修复
   - 或运行 `python migrate.py` 完整迁移

## 文件说明

- `migrate.py` - 自动迁移脚本
- `quick_migrate.py` - 快速修复脚本
- `setup_migrations.sh` - 初始化迁移系统
- `.git/hooks/post-merge` - Git 自动迁移钩子
- `migrations/` - 迁移文件目录（自动生成）

## 注意事项

1. **不要手动修改迁移文件**，除非你非常清楚在做什么
2. **始终在激活虚拟环境后**再执行 git pull
3. **定期备份数据库文件** `instance/database.sqlite`
4. 如果迁移失败，检查 `migrations/versions/` 目录中的迁移文件

## 故障排除

### 错误：no such column
运行 `python quick_migrate.py`

### 错误：迁移冲突
1. 删除有问题的迁移文件
2. 运行 `flask db stamp head` 标记当前状态
3. 重新生成迁移

### 错误：数据库锁定
确保没有其他进程在使用数据库，重启 Flask 应用
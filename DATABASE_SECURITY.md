# 数据库安全与备份方案

## 📍 数据库存储位置

**当前位置**: `F:\3454353\instance\database.sqlite`
- **磁盘**: F盘
- **完整路径**: `F:\3454353\instance\database.sqlite`
- **文件大小**: 约36KB
- **存储方式**: SQLite文件数据库（硬盘存储）

## 🔒 安全防护措施

### 1. 版本控制保护
- ✅ 数据库文件已在`.gitignore`中排除
- ✅ 不会意外提交到Git仓库
- ✅ 避免敏感数据泄露

### 2. 备份策略

#### 自动备份工具
使用提供的备份脚本：
```bash
# 手动备份
python backup_database.py

# 自动备份
python auto_backup.py
```

#### 备份特性
- 🔄 **自动压缩**: 备份文件自动ZIP压缩
- 📅 **时间戳**: 文件名包含创建时间
- 🔍 **完整性检查**: MD5哈希值验证
- 🗂️ **版本管理**: 自动保留最近10个备份
- 💾 **安全备份**: 使用SQLite官方备份API

#### 备份文件位置
```
f:\3454353\backups\
├── database_backup_20250102_143022.zip
├── database_backup_20250102_120000.zip
└── ...
```

### 3. 定期备份设置

#### Windows任务计划程序
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（建议每日备份）
4. 操作设置：
   - 程序: `python`
   - 参数: `f:\3454353\auto_backup.py`
   - 起始位置: `f:\3454353`

#### 推荐备份频率
- **开发期间**: 每日备份
- **重要更新前**: 手动备份
- **生产环境**: 每小时备份

## 🛡️ 数据加密建议

### 当前状态
- SQLite文件**未加密**
- 适合开发环境使用
- 文件可直接访问

### 加密选项

#### 1. SQLite加密扩展 (推荐)
```python
# 使用SQLCipher进行数据库加密
pip install pysqlcipher3

# 配置加密连接
SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlcipher://:password@/path/to/database.db'
```

#### 2. 文件系统加密
- 使用Windows BitLocker加密F盘
- 或使用VeraCrypt创建加密容器

#### 3. 应用层加密
```python
# 敏感字段加密存储
from cryptography.fernet import Fernet

class Customer(db.Model):
    phone_encrypted = db.Column(db.Text)  # 加密存储手机号
    
    def set_phone(self, phone):
        cipher = Fernet(key)
        self.phone_encrypted = cipher.encrypt(phone.encode())
```

## 🚨 误删防护

### 1. 文件属性保护
```cmd
# 设置只读属性
attrib +R f:\3454353\instance\database.sqlite
```

### 2. 回收站保护
- 确保F盘启用回收站
- 设置足够的回收站空间

### 3. 版本控制
```bash
# 虽然数据库文件不提交，但可以导出数据
python -c "
import sqlite3
conn = sqlite3.connect('instance/database.sqlite')
with open('data_export.sql', 'w') as f:
    for line in conn.iterdump():
        f.write('%s\n' % line)
"
```

## 📋 日常维护检查清单

### 每日检查
- [ ] 数据库文件是否存在
- [ ] 备份是否正常执行
- [ ] 磁盘空间是否充足

### 每周检查
- [ ] 清理过期备份文件
- [ ] 检查数据库文件大小增长
- [ ] 验证备份文件完整性

### 每月检查
- [ ] 测试备份恢复流程
- [ ] 更新备份策略
- [ ] 检查安全设置

## 🔧 故障恢复

### 数据库损坏
```bash
# 检查数据库完整性
sqlite3 instance/database.sqlite "PRAGMA integrity_check;"

# 从备份恢复
python backup_database.py
# 选择选项3进行恢复
```

### 误删恢复
1. 检查回收站
2. 从最近备份恢复
3. 使用数据恢复软件

## 📞 紧急联系

如遇数据丢失紧急情况：
1. 立即停止所有写操作
2. 不要重启应用程序
3. 联系技术支持
4. 准备最近的备份文件

---

**重要提醒**: 定期测试备份恢复流程，确保备份文件可用！
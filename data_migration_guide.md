# 数据迁移完整指南

## 方案一：直接复制数据库文件（最简单）

### Windows - 使用 WinSCP

1. **安装 WinSCP**
   - 下载地址：https://winscp.net/
   - 选择中文版

2. **连接设置**
   ```
   文件协议：SFTP
   主机名：您的服务器IP
   端口：22
   用户名：ubuntu（或root）
   密码：您的密码
   ```

3. **上传步骤**
   - 左侧窗口：导航到本地项目的 `instance` 文件夹
   - 右侧窗口：导航到 `/home/ubuntu/您的项目/instance/`
   - 找到 `database.sqlite` 文件
   - 右键 → 上传
   - 等待完成

### Mac/Linux - 使用 SCP

```bash
# 1. 打开终端，进入本地项目目录
cd /本地项目路径

# 2. 上传数据库文件
scp instance/database.sqlite ubuntu@服务器IP:~/项目名/instance/

# 3. 如果有多个文件
scp -r instance/* ubuntu@服务器IP:~/项目名/instance/
```

## 方案二：数据导出导入（更专业）

### 第一步：在本地导出数据

创建导出脚本 `export_data.py`：

```python
import sqlite3
import json
import pandas as pd
from datetime import datetime

def export_all_data():
    """导出所有数据到JSON文件"""
    conn = sqlite3.connect('instance/database.sqlite')
    
    # 获取所有表名
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    export_data = {}
    
    for table in tables:
        table_name = table[0]
        print(f"导出表: {table_name}")
        
        # 读取表数据
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # 转换日期列为字符串
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 转换为字典
        export_data[table_name] = df.to_dict('records')
    
    # 保存到JSON文件
    filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    conn.close()
    print(f"数据已导出到: {filename}")
    return filename

if __name__ == "__main__":
    export_all_data()
```

运行导出：
```bash
python export_data.py
```

### 第二步：上传JSON文件

```bash
# 使用 WinSCP 上传生成的 JSON 文件
# 或使用 scp
scp data_export_*.json ubuntu@服务器IP:~/
```

### 第三步：在服务器导入数据

创建导入脚本 `import_data.py`：

```python
import sqlite3
import json
import pandas as pd

def import_all_data(json_file):
    """从JSON文件导入所有数据"""
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 连接数据库
    conn = sqlite3.connect('instance/database.sqlite')
    
    for table_name, records in data.items():
        print(f"导入表: {table_name}")
        
        if records:
            # 转换为DataFrame
            df = pd.DataFrame(records)
            
            # 导入到数据库（替换现有数据）
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"  导入 {len(records)} 条记录")
    
    conn.close()
    print("数据导入完成！")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        import_all_data(sys.argv[1])
    else:
        print("用法: python import_data.py data_export_xxx.json")
```

在服务器上运行：
```bash
python import_data.py data_export_20241226_143022.json
```

## 方案三：增量同步（适合持续更新）

### 创建同步脚本 `sync_data.py`：

```python
#!/usr/bin/env python3
import os
import subprocess
import datetime

# 配置
LOCAL_DB = "instance/database.sqlite"
REMOTE_HOST = "ubuntu@您的服务器IP"
REMOTE_PATH = "~/项目名/instance/database.sqlite"
BACKUP_DIR = "backups"

def backup_remote():
    """备份远程数据库"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"remote_backup_{timestamp}.sqlite"
    
    print("备份远程数据库...")
    cmd = f"ssh {REMOTE_HOST} 'cp {REMOTE_PATH} ~/backups/{backup_name}'"
    subprocess.run(cmd, shell=True)
    print(f"远程备份完成: {backup_name}")

def sync_database():
    """同步本地数据库到远程"""
    print("开始同步数据库...")
    
    # 1. 备份远程数据库
    backup_remote()
    
    # 2. 上传本地数据库
    print("上传本地数据库...")
    cmd = f"scp {LOCAL_DB} {REMOTE_HOST}:{REMOTE_PATH}"
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("✅ 数据库同步成功！")
    else:
        print("❌ 同步失败！")

if __name__ == "__main__":
    sync_database()
```

## 方案四：使用 FileZilla（图形界面）

1. **下载 FileZilla**
   - 官网：https://filezilla-project.org/
   - 选择 FileZilla Client

2. **快速连接**
   ```
   主机：sftp://您的服务器IP
   用户名：ubuntu
   密码：您的密码
   端口：22
   ```

3. **传输文件**
   - 找到本地的 `instance/database.sqlite`
   - 拖到远程对应目录

## 重要提示 ⚠️

### 1. 传输前备份
```bash
# 在服务器上备份现有数据（如果有）
cd ~/项目名
cp instance/database.sqlite instance/database.sqlite.backup
```

### 2. 检查文件权限
```bash
# 上传后，确保权限正确
cd ~/项目名
chmod 644 instance/database.sqlite
chmod 755 instance
```

### 3. 验证数据
```bash
# 进入项目目录
cd ~/项目名

# 激活Python环境
source venv/bin/activate

# 创建验证脚本
cat > check_data.py << 'EOF'
import sqlite3
conn = sqlite3.connect('instance/database.sqlite')
cursor = conn.cursor()

# 检查表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表：")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  {table[0]}: {count} 条记录")

conn.close()
EOF

# 运行验证
python check_data.py
```

## 快速检查清单 ✅

1. **上传前**
   - [ ] 本地应用已停止运行
   - [ ] 数据库文件没有被占用
   - [ ] 记录本地数据量（对比用）

2. **上传后**
   - [ ] 文件大小一致
   - [ ] 权限设置正确
   - [ ] 应用能正常启动
   - [ ] 数据能正常显示

## 常见问题

### Q: 上传很慢怎么办？
A: 可以先压缩：
```bash
# 本地压缩
zip -r data.zip instance/

# 上传压缩包
scp data.zip ubuntu@服务器IP:~/

# 服务器解压
unzip data.zip
```

### Q: 数据库很大（>100MB）？
A: 使用分片上传：
```bash
# 分割文件
split -b 50M database.sqlite database_part_

# 上传所有分片
scp database_part_* ubuntu@服务器IP:~/

# 服务器合并
cat database_part_* > database.sqlite
```

### Q: 如何自动定期同步？
A: 可以设置定时任务（cron）或使用 rsync：
```bash
# 使用 rsync 增量同步
rsync -avz instance/database.sqlite ubuntu@服务器IP:~/项目名/instance/
```

需要帮助请告诉我具体遇到什么问题！
# 客户管理系统 - 云端部署指南

## 问题描述
在云端服务器上运行时出现错误：
```
ModuleNotFoundError: No module named 'flask'
```

## 解决方案

### 方案1：使用部署脚本（推荐）

#### Windows服务器
1. 上传项目文件到云端服务器
2. 在项目目录中运行：
```cmd
deploy_cloud.bat
```

#### Linux/macOS服务器
1. 上传项目文件到云端服务器
2. 给脚本执行权限：
```bash
chmod +x deploy_cloud.sh
```
3. 运行脚本：
```bash
./deploy_cloud.sh
```

### 方案2：手动安装依赖

#### 步骤1：检查Python环境
```bash
# Windows
python --version

# Linux/macOS
python3 --version
```

#### 步骤2：安装依赖包
```bash
# 方法1：使用requirements.txt（推荐）
pip install -r requirements.txt

# 方法2：手动安装
pip install Flask Flask-SQLAlchemy Flask-Migrate pandas openpyxl XlsxWriter
```

#### 步骤3：创建必要目录
```bash
# 创建数据库目录
mkdir -p instance
```

#### 步骤4：启动应用
```bash
python run.py
```

### 方案3：使用虚拟环境（生产环境推荐）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python run.py
```

## 常见问题解决

### 1. pip命令不存在
```bash
# 安装pip
python -m ensurepip --upgrade
```

### 2. 权限问题
```bash
# Linux/macOS使用sudo
sudo pip3 install -r requirements.txt
```

### 3. 网络问题
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 4. Python版本问题
确保使用Python 3.6或更高版本：
```bash
python --version
```

## 验证安装

运行以下命令验证所有依赖是否正确安装：
```bash
python -c "import flask; print('Flask版本:', flask.__version__)"
python -c "import flask_sqlalchemy; print('Flask-SQLAlchemy已安装')"
python -c "import pandas; print('pandas版本:', pandas.__version__)"
```

## 生产环境建议

1. **使用虚拟环境**：避免依赖冲突
2. **使用WSGI服务器**：如gunicorn或uwsgi
3. **配置反向代理**：如nginx
4. **设置环境变量**：配置生产环境参数
5. **数据库备份**：定期备份SQLite数据库

## 启动命令示例

### 开发环境
```bash
python run.py
```

### 生产环境（Linux）
```bash
# 使用gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# 后台运行
nohup gunicorn -w 4 -b 0.0.0.0:5000 run:app &
```

### 生产环境（Windows）
```bash
# 使用waitress
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 run:app
```

## 访问地址

部署成功后，可以通过以下地址访问：
- 本地访问：`http://localhost:5000`
- 远程访问：`http://服务器IP:5000`

## 注意事项

1. **防火墙设置**：确保5000端口开放
2. **安全配置**：生产环境建议使用HTTPS
3. **数据库路径**：确保instance目录有写权限
4. **日志监控**：监控应用运行状态
5. **定期更新**：保持依赖包版本更新



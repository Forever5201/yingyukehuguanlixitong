# 云服务器部署详细教程

## 第一步：连接到服务器

### Windows 用户使用 PuTTY：

1. **下载 PuTTY**
   - 访问：https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
   - 下载 putty.exe（64位版本）

2. **连接服务器**
   - 打开 PuTTY
   - Host Name：输入您的服务器IP
   - Port：22（默认）
   - Connection type：SSH
   - 点击 "Open"

3. **登录**
   - 出现黑窗口后
   - login as：输入 `ubuntu` 或 `root`
   - password：输入您的密码（输入时不显示）

### Mac/Linux 用户：

打开终端，直接输入：
```bash
ssh ubuntu@您的服务器IP
# 或
ssh root@您的服务器IP
```

## 第二步：更新系统和安装基础软件

连接成功后，复制粘贴以下命令（一行一行执行）：

```bash
# 1. 更新系统包列表
sudo apt update

# 2. 升级已安装的包
sudo apt upgrade -y

# 3. 安装 Python 和必要工具
sudo apt install python3-pip python3-venv git nginx -y

# 4. 安装其他有用工具
sudo apt install htop tree nano screen -y
```

## 第三步：上传您的项目代码

### 方法一：使用 Git（推荐）

如果您的代码在 GitHub/Gitee：
```bash
# 进入 home 目录
cd ~

# 克隆您的项目
git clone https://github.com/您的用户名/您的项目.git
# 或
git clone https://gitee.com/您的用户名/您的项目.git

# 进入项目目录
cd 您的项目名称
```

### 方法二：使用 SCP 上传

如果代码在本地电脑：

**Windows 用户（使用 WinSCP）：**
1. 下载 WinSCP：https://winscp.net/
2. 连接信息：
   - 主机名：您的服务器IP
   - 用户名：ubuntu
   - 密码：您的密码
3. 将项目文件夹拖拽上传到 `/home/ubuntu/`

**Mac/Linux 用户：**
```bash
# 在本地电脑执行
scp -r /本地项目路径 ubuntu@服务器IP:/home/ubuntu/
```

### 方法三：创建一个上传脚本

在服务器上创建接收文件的脚本：
```bash
# 创建上传目录
mkdir -p ~/project

# 创建一个简单的上传说明
cat > ~/upload_guide.txt << 'EOF'
请使用以下方法之一上传代码：
1. 使用 FileZilla 等 FTP 工具
2. 使用 WinSCP（Windows）
3. 使用 scp 命令（Mac/Linux）
EOF
```

## 第四步：安装项目依赖

```bash
# 1. 进入项目目录
cd ~/您的项目名称

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装项目依赖
pip install -r requirements.txt

# 如果没有 requirements.txt，手动安装：
pip install flask sqlalchemy flask-sqlalchemy pandas openpyxl xlsxwriter
```

## 第五步：配置并运行应用

### 1. 创建必要目录
```bash
# 创建 instance 目录（用于 SQLite 数据库）
mkdir -p instance

# 创建日志目录
mkdir -p logs
```

### 2. 测试运行
```bash
# 直接运行看是否正常
python run.py
```

如果看到类似输出：
```
* Running on http://127.0.0.1:5000
```
说明运行成功！按 `Ctrl+C` 停止。

### 3. 配置防火墙

**在腾讯云/阿里云控制台：**
1. 找到安全组/防火墙设置
2. 添加规则：
   - 协议：TCP
   - 端口：5000
   - 来源：0.0.0.0/0

**或在服务器上：**
```bash
# 开放 5000 端口
sudo ufw allow 5000
sudo ufw allow 22
sudo ufw allow 80
sudo ufw enable
```

## 第六步：使用 Screen 保持应用运行

```bash
# 1. 启动 screen
screen -S flask

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行应用
python run.py --host=0.0.0.0

# 4. 按 Ctrl+A, 然后按 D 分离会话

# 查看运行中的会话
screen -ls

# 重新连接到会话
screen -r flask
```

## 第七步：配置 Nginx（可选，但推荐）

```bash
# 1. 创建 Nginx 配置
sudo nano /etc/nginx/sites-available/flask_app

# 2. 粘贴以下内容：
```

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/ubuntu/您的项目名称/app/static;
        expires 30d;
    }
}
```

```bash
# 3. 按 Ctrl+O 保存，Ctrl+X 退出

# 4. 启用配置
sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# 5. 测试配置
sudo nginx -t

# 6. 重启 Nginx
sudo systemctl restart nginx
```

## 第八步：创建系统服务（高级，可选）

```bash
# 创建 systemd 服务文件
sudo nano /etc/systemd/system/flask_app.service
```

粘贴以下内容：
```ini
[Unit]
Description=Flask Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/您的项目名称
Environment="PATH=/home/ubuntu/您的项目名称/venv/bin"
ExecStart=/home/ubuntu/您的项目名称/venv/bin/python run.py --host=0.0.0.0

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl enable flask_app
sudo systemctl start flask_app
sudo systemctl status flask_app
```

## 🎉 完成！

现在您可以通过以下地址访问：
- 如果配置了 Nginx：`http://您的服务器IP/`
- 如果没有配置 Nginx：`http://您的服务器IP:5000/`

## 🔧 常用维护命令

```bash
# 查看应用日志
tail -f logs/app.log

# 查看系统资源
htop

# 重启应用（如果使用 systemd）
sudo systemctl restart flask_app

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log

# 备份数据库
cp instance/database.sqlite ~/backup_$(date +%Y%m%d).sqlite
```

## ❗ 常见问题解决

### 1. 端口被占用
```bash
# 查看 5000 端口占用
sudo lsof -i :5000
# 杀死进程
sudo kill -9 进程ID
```

### 2. 权限问题
```bash
# 给予执行权限
chmod +x run.py
# 修改文件所有者
sudo chown -R ubuntu:ubuntu ~/您的项目名称
```

### 3. 数据库错误
```bash
# 确保 instance 目录存在且有写权限
mkdir -p instance
chmod 755 instance
```

## 📱 手机管理

1. 下载云服务商的手机 APP
2. 可以随时：
   - 重启服务器
   - 查看运行状态
   - 查看资源使用

需要帮助请随时告诉我！
# 腾讯云轻量服务器域名说明

## 🎉 好消息：不需要购买域名！

### 腾讯云会提供：

1. **公网 IP 地址**
   ```
   例如：http://43.xxx.xxx.xxx:5000
   直接通过 IP 访问您的应用
   ```

2. **使用方法**
   ```python
   # run.py 修改
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   ```

   访问：`http://您的服务器IP:5000`

## 📋 完整部署流程（无域名版）

### 1. 购买服务器
- 腾讯云轻量应用服务器
- 新用户活动：48元/年
- 选择系统：Ubuntu 20.04

### 2. 连接服务器
```bash
# Windows 使用 PuTTY 或 PowerShell
ssh ubuntu@你的服务器IP

# Mac/Linux 直接使用终端
ssh ubuntu@你的服务器IP
```

### 3. 安装环境
```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install python3-pip python3-venv -y

# 安装 Git
sudo apt install git -y
```

### 4. 部署应用
```bash
# 克隆代码
git clone 你的代码仓库
cd 你的项目目录

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py
```

### 5. 配置防火墙
在腾讯云控制台：
- 轻量应用服务器 → 防火墙
- 添加规则：TCP 5000 端口

### 6. 保持应用运行
```bash
# 安装 screen
sudo apt install screen -y

# 创建新会话
screen -S flask

# 运行应用
python run.py

# 按 Ctrl+A+D 分离会话
# 重新连接：screen -r flask
```

## 🌐 可选：免费域名方案

### 如果您想要域名（都是免费的）：

#### 1. **免费二级域名**
- **Freenom**：.tk/.ml/.ga 等免费域名
- **eu.org**：免费 .eu.org 子域名
- **Duck DNS**：免费动态域名

#### 2. **使用示例（Duck DNS）**
```bash
# 1. 注册 duckdns.org
# 2. 创建子域名：yourapp.duckdns.org
# 3. 安装更新脚本
echo "*/5 * * * * curl -s 'https://www.duckdns.org/update?domains=yourapp&token=你的token&ip=' >/dev/null 2>&1" | crontab -
```

#### 3. **腾讯云子域名**
如果后续购买了腾讯云域名，可以：
```
主域名：example.com（需购买）
子域名：app.example.com（免费创建）
```

## 💰 成本对比

| 项目 | 必需？ | 成本 |
|------|--------|------|
| 轻量服务器 | ✅ 必需 | 48元/年 |
| 域名 | ❌ 可选 | 0-55元/年 |
| SSL证书 | ❌ 可选 | 0元（Let's Encrypt） |

## 🚀 使用 Nginx 优化（可选）

如果想去掉端口号，可以安装 Nginx：

```bash
# 安装 Nginx
sudo apt install nginx -y

# 配置反向代理
sudo nano /etc/nginx/sites-available/default
```

配置文件：
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 重启 Nginx
sudo systemctl restart nginx

# 现在可以直接访问
http://您的IP/
```

## 📱 实际使用场景

### 1. **个人/内部使用**
- 直接使用 IP 地址
- 加入书签方便访问
- 完全够用

### 2. **给客户演示**
- 使用免费域名服务
- 或临时购买便宜域名（首年9.9元）

### 3. **正式上线**
- 购买正式域名
- 配置 HTTPS
- 使用 CDN 加速

## 🎯 总结

- **不需要域名**即可使用
- 48元/年就能拥有稳定服务器
- IP地址访问完全可行
- 域名是锦上添花，不是必需品

## 快速命令汇总

```bash
# 一键部署脚本
#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git screen nginx -y
git clone 你的仓库
cd 项目目录
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

您只需要 48元，就能拥有一个稳定运行的服务器，不需要额外购买域名！
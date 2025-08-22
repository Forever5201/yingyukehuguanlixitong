# 英语客户管理系统

一个基于 Flask 的英语培训机构客户管理系统，支持试听课程管理、正式课程管理、客户信息维护和订单跟踪等功能。

## ✨ 主要功能

- **课程管理**：试听课程和正式课程的添加、修改、删除
- **客户管理**：客户信息维护与订单跟踪
- **订单管理**：支持淘宝订单的查看与处理
- **数据导出**：提供数据导出功能用于报表分析
- **系统配置**：支持页面配置与功能调试

## 🚀 快速开始

### 环境要求
- Python 3.6 或更高版本
- Windows 操作系统（推荐）
- 网络连接（首次运行时安装依赖）

### 一键启动（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/Forever5201/yingyukehuguanlixitong.git
   cd yingyukehuguanlixitong
   ```

2. **Windows 批处理启动**
   ```bash
   # 双击运行
   start.bat
   ```

3. **手动启动**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 初始化数据库（首次运行）
   python init_database.py
   
   # 启动应用
   python run.py
   ```

4. **访问系统**
   打开浏览器访问：http://localhost:5000

## 📁 项目结构

```
yingyukehuguanlixitong/
├── start.bat              # Windows批处理启动脚本
├── init_database.py       # 数据库初始化脚本
├── schema.sql             # 数据库表结构定义
├── run.py                 # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # Python依赖列表
├── app/                   # 应用程序目录
│   ├── models.py          # 数据模型
│   ├── routes.py          # 路由处理
│   ├── api/               # API控制器
│   ├── services/          # 业务逻辑层
│   ├── static/            # 静态资源
│   └── templates/         # 网页模板
└── tools/                 # 工具脚本
```

## 🗄️ 数据库

项目使用 SQLite 数据库，包含以下主要表：
- `customer` - 客户信息
- `course` - 课程信息（试听课和正式课）
- `employee` - 员工信息
- `taobao_order` - 淘宝订单
- `config` - 系统配置

### 数据库初始化
```bash
# 创建空的数据库表结构
python init_database.py
```

## 🛠️ 技术栈

- **后端框架**：Flask
- **数据库**：SQLite + SQLAlchemy ORM
- **前端**：HTML + CSS + JavaScript (jQuery)
- **模板引擎**：Jinja2

## 📝 开发说明

### 添加新功能
1. 在 `app/models.py` 中定义数据模型
2. 在 `app/api/` 中添加API控制器
3. 在 `app/services/` 中实现业务逻辑
4. 在 `app/templates/` 中创建前端页面
5. 更新 `schema.sql` 保持数据库结构同步

### 备份与恢复
```bash
# 手动备份
python backup_database.py

# 设置自动备份
python setup_auto_backup.py
```

## 📋 系统要求

- Python 3.6+
- Flask 2.0+
- SQLAlchemy 1.4+
- 其他依赖见 `requirements.txt`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

**注意**：首次启动可能需要几分钟时间来安装依赖和初始化数据库，请耐心等待。
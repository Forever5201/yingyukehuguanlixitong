# 技术栈与开发规范

## 技术选型

- **后端**: Python 3.x + Flask
- **数据库**: SQLite
- **数据访问层**: SQLAlchemy (ORM)
- **前端**: 基础 HTML, CSS, JavaScript
- **依赖管理**: `requirements.txt`

## 开发规范

### 1. 代码风格
- **Python**: 遵循 PEP 8 规范。
- **HTML/CSS**: 使用 Prettier 进行格式化。
- **JavaScript**: 遵循 StandardJS 规范。

### 2. Git 工作流
- 使用 Git 进行版本控制。
- **分支策略**:
  - `main`: 主分支，用于部署生产环境。
  - `develop`: 开发分支，集成所有已完成的功能。
  - `feature/<feature-name>`: 功能分支，用于开发新功能。
- **提交信息**: 遵循 Conventional Commits 规范，格式为 `feat: add user login functionality`。

### 3. 目录结构

```
/
├── app/                  # 应用主目录
│   ├── __init__.py
│   ├── models.py         # 数据库模型
│   ├── routes.py         # 路由定义
│   ├── static/           # 静态文件 (CSS, JS, images)
│   └── templates/        # HTML 模板
├── instance/             # 实例文件夹，存放数据库文件等
│   └── database.sqlite
├── tests/                # 测试目录
├── venv/                 # Python 虚拟环境
├── .gitignore
├── config.py             # 配置文件
├── requirements.txt      # 依赖列表
└── run.py                # 应用启动脚本
```

### 4. 环境配置
- 所有开发者应使用 Python 虚拟环境 (`venv`) 来隔离项目依赖。
- 敏感信息（如密钥）应通过环境变量或配置文件管理，不应硬编码在代码中。
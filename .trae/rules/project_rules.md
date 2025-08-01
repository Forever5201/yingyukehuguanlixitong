---
description: "客户管理系统项目开发规则"
globs: ["**/*.py", "**/*.html"]
alwaysApply: true
---

# 项目基础说明

- 本项目是一个基于 Flask 的客户管理系统。
- 主要技术栈: Python, Flask, SQLAlchemy, SQLite。
- 前端使用基础的 HTML/CSS/JavaScript。

# 编码规范

- **Python**: 严格遵循 PEP 8 规范。
- **命名约定**:
  - 变量和函数名: `snake_case` (小写+下划线)
  - 类名: `PascalCase` (驼峰式)
  - 常量: `UPPER_CASE` (大写+下划线)
- **注释**: 为复杂的函数或逻辑添加清晰的中文注释。

# 技术栈

- **后端**: Python 3.x + Flask
- **数据库**: SQLite
- **ORM**: SQLAlchemy + Flask-SQLAlchemy
- **前端**: HTML, CSS, JavaScript

# 开发流程

- **Git 工作流**: 
  - `main`: 主分支，用于部署生产环境。
  - `develop`: 开发分支，集成新功能。
  - `feature/xxx`: 功能分支，开发新功能。
- **Commit 规范**: 遵循 Conventional Commits 规范 (e.g., `feat: 添加用户登录功能`, `fix: 修复客户列表显示bug`)。

# 数据库

- **模型定义**: 所有数据库模型统一定义在 `app/models.py` 文件中。
- **数据库文件**: 数据库文件位于 `instance/database.sqlite`。

# 文件结构

- **配置文件**: `config.py`
- **应用入口**: `run.py`
- **应用初始化**: `app/__init__.py`
- **路由**: `app/routes.py`
- **模型**: `app/models.py`
- **模板**: `app/templates/`
- **静态文件**: `app/static/`

# 代码修改原则

- **分析先行**: 在修改代码前，使用 Sequential thinking 工具分析最优方案。
- **谨慎修改**: 深度剖析相关代码，在保持对原有功能正常的前提下进行修改优化，确保不会引入新的缺陷或引发连锁反应。请仔细考虑所有关联模块，避免孤立地进行更改，以维护系统整体的稳定性和兼容性。

# 代码质量与项目稳定性

- **自动化规范检查**:
  - **Linter & Formatter**: 使用 `flake8` 或 `pylint` 进行代码规范检查，使用 `black` 或 `autopep8` 统一代码风格。
  - **自动化扫描**: 集成 `SonarQube` 或类似工具进行静态代码分析，发现潜在的 bug 和安全漏洞。

- **代码审查 (Code Review)**:
  - **强制审查**: 所有代码变更（尤其是 `feature` 分支合并到 `develop`）必须经过至少一位团队成员的审查。
  - **明确重点**: 审查重点包括代码逻辑、可读性、可维护性、性能和安全性。

- **测试驱动开发 (TDD)**:
  - **单元测试**: 为核心功能和复杂逻辑编写单元测试，确保代码的正确性。
  - **持续集成 (CI)**: 使用 Jenkins, GitHub Actions 或类似工具，在每次代码提交后自动运行测试，确保代码质量。

- **设计与重构**:
  - **模块化设计**: 遵循高内聚、低耦合的原则，将功能模块化，提高代码的可维护性和可扩展性。
  - **定期重构**: 定期对现有代码进行重构，优化代码结构，消除技术债务。
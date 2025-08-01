# Git 管理策略

## 项目初始化
✅ 已完成项目的Git初始化，包括：
- 初始化Git仓库
- 配置用户信息
- 创建 `.gitignore` 文件
- 创建初始提交

## 分支策略

### 主分支
- **master**: 主分支，包含稳定的生产代码

### 功能分支
- **feature/optimize-customer-management**: 当前工作分支，用于优化客户管理功能

## 当前状态
- 当前分支: `feature/optimize-customer-management`
- 工作目录: 干净（无未提交的更改）
- 已提交文件: 33个文件，6302行代码

## 分支管理命令

### 查看分支
```bash
git branch -a          # 查看所有分支
git status             # 查看当前状态
```

### 切换分支
```bash
git checkout master                           # 切换到主分支
git checkout feature/optimize-customer-management  # 切换到功能分支
```

### 创建新分支
```bash
git checkout -b feature/new-feature-name     # 创建并切换到新分支
```

### 合并分支
```bash
git checkout master                          # 切换到主分支
git merge feature/optimize-customer-management  # 合并功能分支
```

## 提交规范

### 提交消息格式
```
<type>: <description>

<body>

<footer>
```

### 类型说明
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 示例
```bash
git commit -m "feat: 添加客户录入功能"
git commit -m "fix: 修复导航高亮问题"
git commit -m "docs: 更新API文档"
```

## 工作流程

1. **开发新功能**
   ```bash
   git checkout -b feature/new-feature
   # 进行开发
   git add .
   git commit -m "feat: 添加新功能"
   ```

2. **测试功能**
   ```bash
   # 运行测试
   python test_new_customer_feature.py
   ```

3. **合并到主分支**
   ```bash
   git checkout master
   git merge feature/new-feature
   git branch -d feature/new-feature  # 删除已合并的功能分支
   ```

## 已完成的改进记录

### 初始提交 (bee3cb4)
- 客户管理系统基础功能
- 试听课管理
- 正课管理
- 导航系统
- 数据库模型
- 前端界面

### 当前分支目标
在 `feature/optimize-customer-management` 分支中继续优化：
- 客户管理功能增强
- 用户体验改进
- 性能优化
- 代码重构

## 注意事项
- 始终在功能分支上开发新功能
- 定期提交代码，保持提交历史清晰
- 合并前确保功能测试通过
- 保持代码质量和文档更新
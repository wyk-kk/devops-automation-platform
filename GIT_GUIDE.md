# Git 仓库上传指南

本指南将帮助你把运维自动化平台上传到 GitHub、GitLab 或其他 Git 仓库。

## 📋 准备工作

### 1. 确认已安装 Git

```bash
git --version
```

如果未安装，运行：
```bash
# macOS
brew install git

# 或下载安装: https://git-scm.com/
```

### 2. 配置 Git 用户信息（首次使用）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

---

## 🚀 方法一：上传到 GitHub（推荐）

### 步骤 1: 在 GitHub 创建新仓库

1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - **Repository name**: `devops-automation-platform`
   - **Description**: `运维自动化平台 - 基于 FastAPI + Vue3`
   - **Public/Private**: 选择公开或私有
   - **⚠️ 不要勾选** "Add README" 和 ".gitignore"（我们已有）
4. 点击 "Create repository"

### 步骤 2: 初始化本地仓库

```bash
cd /Users/DZ0400191/project_2

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 创建首次提交
git commit -m "Initial commit: 运维自动化平台完整项目"
```

### 步骤 3: 连接到 GitHub 并推送

```bash
# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/devops-automation-platform.git

# 推送到 GitHub（首次推送）
git branch -M main
git push -u origin main
```

### 步骤 4: 输入凭证

GitHub 会要求输入凭证：
- **用户名**: 你的 GitHub 用户名
- **密码**: ⚠️ 使用 **Personal Access Token**（不是登录密码）

#### 如何获取 Personal Access Token:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)"
3. 设置:
   - Note: `devops-platform-upload`
   - Expiration: `90 days` 或自定义
   - 勾选: `repo` (全部)
4. 点击 "Generate token"
5. **立即复制 token**（只显示一次）
6. 在终端粘贴作为密码

---

## 🦊 方法二：上传到 GitLab

### 步骤 1: 在 GitLab 创建项目

1. 访问 https://gitlab.com
2. 点击 "New project" → "Create blank project"
3. 填写：
   - **Project name**: `devops-automation-platform`
   - **Visibility**: Public/Private
   - 取消勾选 "Initialize with README"
4. "Create project"

### 步骤 2: 推送代码

```bash
cd /Users/DZ0400191/project_2

git init
git add .
git commit -m "Initial commit: 运维自动化平台"

# 替换为你的 GitLab 仓库地址
git remote add origin https://gitlab.com/YOUR_USERNAME/devops-automation-platform.git
git branch -M main
git push -u origin main
```

---

## 🔧 常用 Git 命令

### 查看状态
```bash
git status                    # 查看文件状态
git log --oneline            # 查看提交历史
git remote -v                # 查看远程仓库
```

### 日常更新
```bash
# 修改代码后
git add .                    # 添加所有更改
git add 文件名               # 添加特定文件
git commit -m "更新说明"     # 提交更改
git push                     # 推送到远程仓库
```

### 查看差异
```bash
git diff                     # 查看未暂存的更改
git diff --staged            # 查看已暂存的更改
```

### 撤销操作
```bash
git checkout -- 文件名       # 撤销文件修改
git reset HEAD 文件名        # 取消暂存
git reset --soft HEAD^       # 撤销上次提交（保留更改）
```

---

## 📝 提交信息规范

使用清晰的提交信息：

```bash
# 好的提交信息
git commit -m "feat: 添加服务器批量操作功能"
git commit -m "fix: 修复脚本执行超时问题"
git commit -m "docs: 更新API文档"
git commit -m "style: 优化前端界面布局"

# 提交类型
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 重构代码
test:     测试相关
chore:    构建/工具变动
```

---

## 🌿 分支管理

### 创建和切换分支
```bash
git branch                   # 查看所有分支
git branch dev               # 创建 dev 分支
git checkout dev             # 切换到 dev 分支
git checkout -b feature-name # 创建并切换到新分支

# 合并分支
git checkout main            # 切换回主分支
git merge dev                # 合并 dev 分支
```

### 推荐的分支策略
- `main` - 主分支（稳定版本）
- `dev` - 开发分支
- `feature-xxx` - 功能分支
- `hotfix-xxx` - 紧急修复分支

---

## 🔒 .gitignore 说明

项目已包含 `.gitignore` 文件，以下文件不会被提交：

```gitignore
# Python
__pycache__/
*.pyc
*.db
*.sqlite

# Node
node_modules/
dist/

# IDE
.vscode/
.idea/

# 环境配置
.env
.env.local
```

### 查看被忽略的文件
```bash
git status --ignored
```

---

## 📦 添加 README 徽章

在 GitHub 仓库的 README.md 中添加徽章：

```markdown
# 运维自动化平台

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Vue](https://img.shields.io/badge/Vue-3.4-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

基于 FastAPI + Vue 3 的运维自动化管理平台
```

---

## 🚨 常见问题

### Q1: 推送时提示 "failed to push"

**A**: 可能是远程仓库有更新，先拉取：
```bash
git pull origin main --rebase
git push
```

### Q2: 提示 "Permission denied"

**A**: 检查：
1. GitHub token 权限是否足够
2. 仓库地址是否正确
3. 是否有推送权限

### Q3: 文件太大无法推送

**A**: 
```bash
# 查看大文件
find . -type f -size +50M

# 从历史中删除大文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch 大文件路径" \
  --prune-empty --tag-name-filter cat -- --all
```

### Q4: 想要忽略已提交的文件

**A**:
```bash
# 从 Git 移除但保留文件
git rm --cached 文件名
git commit -m "Remove from git"

# 添加到 .gitignore
echo "文件名" >> .gitignore
```

### Q5: 推送到多个远程仓库

**A**:
```bash
# 添加第二个远程仓库
git remote add gitlab https://gitlab.com/YOUR_USERNAME/repo.git

# 推送到不同仓库
git push origin main      # GitHub
git push gitlab main      # GitLab
```

---

## 📚 完整工作流程示例

### 首次上传
```bash
# 1. 创建本地仓库
cd /Users/DZ0400191/project_2
git init
git add .
git commit -m "Initial commit: 运维自动化平台完整实现"

# 2. 连接 GitHub（先在网站创建仓库）
git remote add origin https://github.com/YOUR_USERNAME/devops-platform.git
git branch -M main
git push -u origin main
```

### 日常开发
```bash
# 1. 修改代码...

# 2. 查看修改
git status
git diff

# 3. 提交更改
git add .
git commit -m "feat: 添加批量服务器操作功能"

# 4. 推送到远程
git push
```

### 多人协作
```bash
# 1. 拉取最新代码
git pull

# 2. 创建功能分支
git checkout -b feature-new-function

# 3. 开发并提交
git add .
git commit -m "feat: 新功能开发"

# 4. 推送分支
git push origin feature-new-function

# 5. 在 GitHub 创建 Pull Request
# 6. 审核后合并到 main
```

---

## 🎯 推荐的项目结构展示

在 GitHub 上，你的仓库将这样展示：

```
devops-automation-platform/
├── 📁 backend/          后端代码（FastAPI）
├── 📁 frontend/         前端代码（Vue 3）
├── 📁 docs/            详细文档
├── 📄 README.md        项目介绍
├── 📄 LICENSE          MIT 许可证
├── 📄 .gitignore       Git 忽略规则
└── 📄 启动指南.md      快速开始
```

---

## 🌟 GitHub 仓库优化建议

### 1. 添加 Topics（标签）

在 GitHub 仓库页面添加标签：
- `python`
- `fastapi`
- `vue3`
- `devops`
- `automation`
- `ssh`
- `monitoring`

### 2. 创建 Release

```bash
# 打标签
git tag -a v1.0.0 -m "Version 1.0.0 - 初始版本"
git push origin v1.0.0

# 在 GitHub 创建 Release
# Releases → Create a new release → 选择标签 → 发布
```

### 3. 添加项目描述

在 GitHub 仓库页面：
- About → Edit
- Description: `基于 FastAPI + Vue 3 的运维自动化管理平台`
- Website: `http://localhost:5173`（或部署地址）
- Topics: 添加相关标签

---

## 🔐 SSH 方式推送（可选）

使用 SSH 更方便（不需要每次输入密码）：

### 生成 SSH 密钥
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按回车使用默认路径
# 可以设置密码或直接回车

# 添加到 ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### 添加到 GitHub
```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub | pbcopy

# 或手动查看
cat ~/.ssh/id_ed25519.pub
```

在 GitHub:
1. Settings → SSH and GPG keys → New SSH key
2. 粘贴公钥
3. Add SSH key

### 使用 SSH URL
```bash
# 更改远程仓库为 SSH
git remote set-url origin git@github.com:YOUR_USERNAME/devops-platform.git

# 推送
git push
```

---

## 📖 学习资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 快速入门](https://docs.github.com/cn/get-started)
- [Git 教程 - 廖雪峰](https://www.liaoxuefeng.com/wiki/896043488029600)

---

## ✅ 上传检查清单

在推送前确认：

- [ ] 已创建 `.gitignore` 文件
- [ ] 已删除敏感信息（密码、密钥等）
- [ ] README.md 内容完整
- [ ] 代码可以正常运行
- [ ] 文档已更新
- [ ] 提交信息清晰明确

---

**现在你可以开始上传你的项目了！** 🚀

如有问题，查看上面的常见问题部分或搜索相关错误信息。


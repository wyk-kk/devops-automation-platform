# 贡献指南

感谢你对运维自动化平台的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告Bug

如果你发现了Bug，请创建一个Issue，包含以下信息：

1. Bug的详细描述
2. 复现步骤
3. 预期行为
4. 实际行为
5. 环境信息（操作系统、Python版本、Node版本等）
6. 截图或日志（如有）

### 提出新功能

如果你有新功能的想法：

1. 先查看Issue列表，确认该功能未被提出
2. 创建一个Feature Request Issue
3. 详细描述功能需求和使用场景
4. 等待讨论和反馈

### 提交代码

1. **Fork项目**

```bash
git clone https://github.com/yourusername/project_2.git
cd project_2
```

2. **创建特性分支**

```bash
git checkout -b feature/your-feature-name
```

3. **编写代码**

遵循项目的代码规范：
- Python: PEP 8
- JavaScript: ESLint配置
- 添加必要的注释
- 编写测试用例

4. **提交更改**

```bash
git add .
git commit -m "feat: 添加新功能描述"
```

提交信息格式：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具变动

5. **推送到GitHub**

```bash
git push origin feature/your-feature-name
```

6. **创建Pull Request**

- 在GitHub上创建PR
- 描述你的更改
- 链接相关Issue
- 等待代码审查

## 开发环境设置

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov  # 测试工具
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## 代码规范

### Python

- 遵循PEP 8
- 使用类型注解
- 编写文档字符串
- 保持函数简洁（不超过50行）

示例：

```python
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        用户对象，如果不存在返回None
    """
    return db.query(User).filter(User.id == user_id).first()
```

### JavaScript/Vue

- 使用ES6+语法
- 组件使用Composition API
- 保持组件功能单一
- 使用有意义的变量名

示例：

```vue
<script setup>
import { ref, onMounted } from 'vue'

const items = ref([])
const loading = ref(false)

const fetchItems = async () => {
  loading.value = true
  try {
    const response = await api.get('/items')
    items.value = response.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchItems()
})
</script>
```

## 测试

### 运行测试

```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端测试
cd frontend
npm run test
```

### 编写测试

为新功能添加测试用例：

```python
# backend/tests/test_server.py
def test_create_server(client):
    response = client.post("/api/servers", json={
        "name": "Test Server",
        "host": "192.168.1.1",
        "username": "admin"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test Server"
```

## 文档

如果你的更改涉及到：
- API接口：更新 `docs/API_DOCUMENTATION.md`
- 用户功能：更新 `docs/USER_MANUAL.md`
- 开发相关：更新 `docs/DEVELOPMENT.md`
- 部署配置：更新 `docs/DEPLOYMENT.md`

## 审查流程

1. 自动化检查（如有CI/CD）
2. 代码审查
3. 功能测试
4. 合并到主分支

## 行为准则

- 尊重所有贡献者
- 保持建设性的讨论
- 接受建设性的批评
- 专注于对项目最有利的事情

## 许可证

提交代码即表示你同意你的贡献使用MIT许可证。

## 联系方式

如有任何问题，可以：
- 创建Issue
- 发送邮件至维护者
- 在讨论区提问

## 致谢

感谢所有为这个项目做出贡献的开发者！

---

再次感谢你的贡献！


# 开发指南

## 项目架构

### 技术栈

**后端**:
- FastAPI - Web框架
- SQLAlchemy - ORM
- Paramiko - SSH客户端
- APScheduler - 任务调度
- Pydantic - 数据验证
- JWT - 身份认证

**前端**:
- Vue 3 - 前端框架
- Vue Router - 路由管理
- Pinia - 状态管理
- Element Plus - UI组件库
- Axios - HTTP客户端
- Vite - 构建工具

### 目录结构

```
project_2/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── servers.py     # 服务器接口
│   │   │   ├── scripts.py     # 脚本接口
│   │   │   ├── tasks.py       # 任务接口
│   │   │   ├── alerts.py      # 告警接口
│   │   │   └── users.py       # 用户接口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── security.py    # 安全相关
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py
│   │   │   ├── server.py
│   │   │   ├── script.py
│   │   │   ├── task.py
│   │   │   ├── alert.py
│   │   │   └── log.py
│   │   ├── schemas/           # Pydantic模型
│   │   │   └── ...
│   │   ├── services/          # 业务逻辑
│   │   │   ├── server_service.py
│   │   │   ├── script_service.py
│   │   │   ├── task_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── user_service.py
│   │   │   └── scheduler_service.py
│   │   └── utils/             # 工具函数
│   │       ├── ssh_client.py
│   │       └── dependencies.py
│   ├── main.py                # 应用入口
│   └── requirements.txt       # Python依赖
├── frontend/                  # 前端代码
│   ├── src/
│   │   ├── api/              # API调用
│   │   ├── components/       # 公共组件
│   │   ├── layouts/          # 布局组件
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # 状态管理
│   │   ├── views/            # 页面视图
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docs/                      # 文档
└── README.md
```

## 后端开发

### 添加新的API接口

1. **创建数据模型** (`app/models/`)

```python
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class NewModel(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

2. **创建Pydantic Schema** (`app/schemas/`)

```python
from pydantic import BaseModel

class NewModelBase(BaseModel):
    name: str

class NewModelCreate(NewModelBase):
    pass

class NewModel(NewModelBase):
    id: int
    
    class Config:
        from_attributes = True
```

3. **创建服务层** (`app/services/`)

```python
from sqlalchemy.orm import Session
from app.models.new_model import NewModel

class NewModelService:
    @staticmethod
    def get_items(db: Session):
        return db.query(NewModel).all()
    
    @staticmethod
    def create_item(db: Session, item: NewModelCreate):
        db_item = NewModel(**item.model_dump())
        db.add(db_item)
        db.commit()
        return db_item
```

4. **创建API路由** (`app/api/`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.new_model_service import NewModelService

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("")
def get_items(db: Session = Depends(get_db)):
    return NewModelService.get_items(db)

@router.post("")
def create_item(item: NewModelCreate, db: Session = Depends(get_db)):
    return NewModelService.create_item(db, item)
```

5. **注册路由** (`main.py`)

```python
from app.api import new_api

app.include_router(new_api.router, prefix="/api")
```

### 数据库迁移

使用Alembic进行数据库迁移:

```bash
# 初始化迁移
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Add new table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 添加认证保护

使用依赖注入添加认证:

```python
from app.utils.dependencies import get_current_active_user

@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": "Protected data"}
```

### 添加定时任务

在 `scheduler_service.py` 中添加任务:

```python
def add_custom_job(self):
    self.scheduler.add_job(
        func=self._custom_task,
        trigger='cron',
        hour=2,
        minute=0
    )

def _custom_task(self):
    # 任务逻辑
    pass
```

## 前端开发

### 添加新页面

1. **创建视图组件** (`src/views/NewPage.vue`)

```vue
<template>
  <div class="new-page">
    <h1>New Page</h1>
    <!-- 页面内容 -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const data = ref([])

const fetchData = async () => {
  const response = await api.get('/items')
  data.value = response.data
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.new-page {
  padding: 20px;
}
</style>
```

2. **添加路由** (`src/router/index.js`)

```javascript
{
  path: 'newpage',
  name: 'NewPage',
  component: () => import('@/views/NewPage.vue')
}
```

3. **添加导航菜单** (`src/layouts/MainLayout.vue`)

```vue
<el-menu-item index="/newpage">
  <el-icon><Document /></el-icon>
  <span>New Page</span>
</el-menu-item>
```

### 创建API服务

在 `src/api/index.js` 中添加API方法:

```javascript
export const itemsApi = {
  getList: () => api.get('/items'),
  getItem: (id) => api.get(`/items/${id}`),
  create: (data) => api.post('/items', data),
  update: (id, data) => api.put(`/items/${id}`, data),
  delete: (id) => api.delete(`/items/${id}`)
}
```

### 状态管理

创建新的Store (`src/stores/items.js`):

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useItemsStore = defineStore('items', () => {
  const items = ref([])
  
  const fetchItems = async () => {
    const response = await api.get('/items')
    items.value = response.data
  }
  
  return {
    items,
    fetchItems
  }
})
```

使用Store:

```vue
<script setup>
import { useItemsStore } from '@/stores/items'

const itemsStore = useItemsStore()
itemsStore.fetchItems()
</script>
```

### 创建公共组件

创建组件 (`src/components/MyComponent.vue`):

```vue
<template>
  <div class="my-component">
    <slot></slot>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  data: Array
})

const emit = defineEmits(['update', 'delete'])
</script>
```

使用组件:

```vue
<template>
  <MyComponent 
    :title="title" 
    :data="data"
    @update="handleUpdate"
  />
</template>

<script setup>
import MyComponent from '@/components/MyComponent.vue'
</script>
```

## 代码规范

### Python代码规范

遵循PEP 8规范:

```python
# 好的命名
class UserService:
    def get_user_by_id(self, user_id: int) -> User:
        pass

# 类型注解
def process_data(data: List[Dict[str, Any]]) -> Dict[str, int]:
    return {"count": len(data)}

# 文档字符串
def calculate_total(items: List[Item]) -> float:
    """
    计算项目总价
    
    Args:
        items: 项目列表
        
    Returns:
        总价格
    """
    return sum(item.price for item in items)
```

### JavaScript代码规范

使用ESLint和Prettier:

```javascript
// 使用const/let，避免var
const items = []
let count = 0

// 箭头函数
const handleClick = () => {
  console.log('clicked')
}

// 解构
const { name, age } = user
const [first, ...rest] = items

// 模板字符串
const message = `Hello, ${name}!`

// 可选链
const value = data?.user?.profile?.name
```

### Git提交规范

```bash
# 类型
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式化
refactor: 重构
test: 测试
chore: 构建/工具变动

# 示例
git commit -m "feat: 添加服务器监控功能"
git commit -m "fix: 修复脚本执行失败的问题"
git commit -m "docs: 更新API文档"
```

## 测试

### 后端测试

使用pytest:

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_servers():
    response = client.get("/api/servers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_server():
    data = {
        "name": "Test Server",
        "host": "192.168.1.100",
        "username": "admin"
    }
    response = client.post("/api/servers", json=data)
    assert response.status_code == 200
```

运行测试:

```bash
pytest tests/
pytest tests/test_api.py -v
pytest --cov=app tests/
```

### 前端测试

使用Vitest:

```javascript
// tests/component.test.js
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent, {
      props: { title: 'Test' }
    })
    expect(wrapper.text()).toContain('Test')
  })
})
```

## 调试

### 后端调试

使用VSCode调试配置 (`.vscode/launch.json`):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

### 前端调试

使用浏览器开发者工具:
1. Chrome DevTools
2. Vue Devtools扩展

## 性能优化

### 后端优化

1. **数据库查询优化**
```python
# 使用索引
class Server(Base):
    name = Column(String(100), index=True)

# 预加载关联数据
servers = db.query(Server).options(
    joinedload(Server.scripts)
).all()

# 分页查询
servers = db.query(Server).offset(skip).limit(limit).all()
```

2. **缓存**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_config():
    return expensive_operation()
```

### 前端优化

1. **懒加载**
```javascript
const Dashboard = () => import('@/views/Dashboard.vue')
```

2. **组件缓存**
```vue
<keep-alive>
  <router-view />
</keep-alive>
```

3. **防抖和节流**
```javascript
import { debounce } from 'lodash-es'

const handleSearch = debounce((keyword) => {
  // 搜索逻辑
}, 300)
```

## 常见问题

### Q: CORS错误？

A: 检查后端CORS配置，确保允许前端域名

### Q: 数据库连接失败？

A: 检查DATABASE_URL配置和数据库服务状态

### Q: 前端API调用失败？

A: 检查Vite代理配置和后端服务状态

### Q: 如何重置数据库？

A: 删除数据库文件后重启服务自动重建

## 资源链接

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Vue 3文档](https://vuejs.org/)
- [Element Plus文档](https://element-plus.org/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Pinia文档](https://pinia.vuejs.org/)


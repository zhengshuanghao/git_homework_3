# GitHub Actions 自动构建配置指南

## 📋 前置准备

### 1. 阿里云容器镜像服务设置

#### 步骤1：开通容器镜像服务

1. 访问 [阿里云容器镜像服务](https://cr.console.aliyun.com/)
2. 选择"个人实例"（免费）或"企业版"
3. 选择地域（建议：华东1-杭州）

#### 步骤2：创建命名空间

1. 进入"命名空间"页面
2. 点击"创建命名空间"
3. 输入命名空间名称：`ai-travel-planner`
4. 设置为"公开"（方便他人拉取）或"私有"

#### 步骤3：创建镜像仓库

1. 进入"镜像仓库"页面
2. 点击"创建镜像仓库"
3. 填写信息：
   - 命名空间：`ai-travel-planner`
   - 仓库名称：`ai-travel-planner`
   - 仓库类型：公开
   - 摘要：AI旅行规划师应用
4. 点击"下一步"，选择"本地仓库"
5. 完成创建

#### 步骤4：获取访问凭证

1. 点击右上角头像 → "AccessKey管理"
2. 创建AccessKey（如果没有）
3. 记录：
   - AccessKey ID（用户名）
   - AccessKey Secret（密码）

⚠️ **重要**：妥善保管AccessKey，不要泄露！

### 2. GitHub仓库设置

#### 步骤1：添加Secrets

1. 进入GitHub仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加以下secrets：

| Name | Value | 说明 |
|------|-------|------|
| `ALIYUN_REGISTRY_USERNAME` | 阿里云AccessKey ID | 阿里云容器镜像服务用户名 |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云AccessKey Secret | 阿里云容器镜像服务密码 |

#### 步骤2：验证配置

确保`.github/workflows/docker-publish.yml`文件已存在并正确配置。

## 🚀 触发构建

### 自动触发

以下操作会自动触发Docker镜像构建：

1. **推送到主分支**
   ```bash
   git push origin main
   ```

2. **创建标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **创建Pull Request**
   向main分支创建PR

### 手动触发

1. 进入GitHub仓库
2. 点击 `Actions` 标签
3. 选择 `Build and Push Docker Image to Aliyun`
4. 点击 `Run workflow`
5. 选择分支，点击 `Run workflow`

## 📊 查看构建状态

### GitHub Actions

1. 进入仓库的 `Actions` 标签
2. 查看最新的workflow运行
3. 点击查看详细日志

### 阿里云镜像仓库

1. 访问 [阿里云容器镜像服务控制台](https://cr.console.aliyun.com/)
2. 进入"镜像仓库" → `ai-travel-planner/ai-travel-planner`
3. 查看"镜像版本"标签

## 🏷️ 镜像标签说明

GitHub Actions会自动生成以下标签：

| 标签格式 | 示例 | 说明 |
|---------|------|------|
| `latest` | `latest` | 最新的main分支构建 |
| `main` | `main` | main分支最新构建 |
| `v1.0.0` | `v1.0.0` | 版本标签 |
| `1.0` | `1.0` | 主次版本号 |
| `main-abc123` | `main-abc123` | 分支名-commit SHA |

## 📦 拉取镜像

### 公开仓库

```bash
docker pull crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest
```

### 私有仓库

```bash
# 登录
docker login --username=<AccessKey ID> registry.cn-hangzhou.aliyuncs.com

# 拉取
docker pull crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest
```

## 🔧 自定义配置

### 修改镜像仓库地址

编辑 `.github/workflows/docker-publish.yml`：

```yaml
env:
  REGISTRY: registry.cn-hangzhou.aliyuncs.com  # 修改地域
  NAMESPACE: your-namespace                     # 修改命名空间
  IMAGE_NAME: your-image-name                   # 修改镜像名
```

### 修改触发条件

```yaml
on:
  push:
    branches:
      - main
      - develop  # 添加其他分支
    tags:
      - 'v*'
```

### 添加构建参数

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    build-args: |
      VERSION=${{ github.ref_name }}
      BUILD_DATE=${{ github.event.head_commit.timestamp }}
```

## 🐛 故障排查

### 构建失败

1. **检查Secrets配置**
   - 确认`ALIYUN_REGISTRY_USERNAME`和`ALIYUN_REGISTRY_PASSWORD`正确
   - 检查AccessKey是否有效

2. **检查Dockerfile**
   ```bash
   # 本地测试构建
   docker build -t test .
   ```

3. **查看详细日志**
   - 在GitHub Actions中查看完整构建日志
   - 检查具体错误信息

### 推送失败

1. **检查仓库权限**
   - 确认命名空间和仓库已创建
   - 检查AccessKey权限

2. **检查网络**
   - GitHub Actions可能需要访问阿里云
   - 检查是否有网络限制

### 镜像拉取失败

1. **公开仓库**
   - 确认仓库设置为"公开"
   - 检查镜像地址是否正确

2. **私有仓库**
   - 确认已登录：`docker login`
   - 检查凭证是否正确

## 📝 完整工作流程

### 开发流程

```bash
# 1. 开发功能
git checkout -b feature/new-feature

# 2. 提交代码
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# 3. 创建PR并合并到main
# （GitHub网页操作）

# 4. 自动触发构建
# GitHub Actions自动构建并推送镜像

# 5. 拉取最新镜像
docker pull crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:latest
```

### 发布流程

```bash
# 1. 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 2. 自动构建版本镜像
# GitHub Actions自动构建v1.0.0标签的镜像

# 3. 拉取特定版本
docker pull crpi-t07boaz31v5le95c.cn-hangzhou.personal.cr.aliyuncs.com/ai_travel_planner_zsh/ai_travel_planner_zsh_522025720032:v1.0.0
```

## 🎯 最佳实践

1. **使用语义化版本**
   - v1.0.0（主版本.次版本.修订版本）
   - 遵循[语义化版本规范](https://semver.org/lang/zh-CN/)

2. **保护主分支**
   - 设置分支保护规则
   - 要求PR审核后才能合并

3. **定期清理旧镜像**
   - 在阿里云控制台设置镜像保留策略
   - 避免占用过多存储空间

4. **监控构建状态**
   - 添加GitHub Actions徽章到README
   - 设置构建失败通知

5. **安全性**
   - 定期轮换AccessKey
   - 使用最小权限原则
   - 不要在代码中硬编码密钥

## 🔗 相关资源

- [阿里云容器镜像服务文档](https://help.aliyun.com/product/60716.html)
- [GitHub Actions文档](https://docs.github.com/cn/actions)
- [Docker官方文档](https://docs.docker.com/)
- [Docker Buildx文档](https://docs.docker.com/buildx/working-with-buildx/)

## ✅ 检查清单

部署前请确认：

- [ ] 阿里云容器镜像服务已开通
- [ ] 命名空间已创建
- [ ] 镜像仓库已创建
- [ ] AccessKey已获取
- [ ] GitHub Secrets已配置
- [ ] Dockerfile已创建
- [ ] .dockerignore已创建
- [ ] GitHub Actions workflow已配置
- [ ] 本地Docker构建测试通过

完成以上步骤后，推送代码即可自动构建Docker镜像！

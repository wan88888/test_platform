# TestHub 智能测试管理平台

<div align="center">

**基于 AI 驱动的全栈测试管理平台**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.3-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-GPL_v3-blue.svg)](LICENSE)

</div>

## 📖 项目简介

TestHub 是一个 AI 驱动的全栈测试管理平台，覆盖测试全流程，包含：**AI 需求分析与用例生成**、**测试用例管理与评审**、**API 测试**、**UI 自动化测试（Web）**、**APP 自动化测试（Android）**、**性能测试**、**数据工厂**等模块，助力测试团队全面提效。

## ✨ 核心特性

### 🤖 AI 智能化
- **需求分析**: 上传需求文档（PDF/Word/TXT），AI 自动提取业务需求并生成测试用例
- **智能助手**: 集成 Dify AI 助手，提供测试咨询和问题解答
- **AI 智能模式**: 基于 Browser-use 的智能浏览器自动化，AI 理解页面并自动完成测试（支持文本/视觉两种模式）
- **多模型支持**: DeepSeek、通义千问、硅基流动、OpenAI、Anthropic、Google Gemini 等

### 📋 用例管理与评审
- 完整的用例生命周期管理：创建、编辑、版本控制、归档
- 多维度组织：项目、版本、标签分类；步骤化设计（前置条件 / 操作步骤 / 预期结果）
- 附件与团队协作评论
- 评审流程：多人评审、评审模板与检查清单、多层级评审意见、状态跟踪

### 🌐 API 测试
- 支持 HTTP / WebSocket 协议，树形集合组织，环境变量与变量替换
- 测试套件批量执行，支持断言与执行顺序配置
- 请求历史记录、定时任务（邮件 / Webhook 通知）、Allure 测试报告

### 🖥️ UI 自动化测试（Web）
- Selenium / Playwright 双引擎，多浏览器支持（Chrome / Firefox / Edge）
- 元素库（多种定位策略）+ 页面对象模式（POM）
- 可视化脚本编辑、测试套件批量执行、执行日志 / 截图 / 视频录制
- 定时任务：Cron 表达式、固定间隔、单次执行
- AI 智能模式：AI 理解页面结构自动完成测试任务

### 📱 APP 自动化测试（Android）
- 基于 Airtest 图像识别，支持本地模拟器与远程设备，设备锁定避免资源冲突
- 元素管理（图片 / 坐标 / 区域）与多分辨率适配
- 组件化编排 + UI Flow 流程编排，变量管理（global / local / outputs）
- Celery 异步执行 + Allure 报告，WebSocket 实时进度追踪

### 🚀 性能测试
- 基于 Locust 的压测任务管理与执行，性能指标统计与报告

### 🏭 数据工厂
- 50+ 实用工具：字符处理、编码转换、随机数据、加密解密、测试数据生成、JSON 处理、Crontab 表达式等
- 标签管理与使用记录，支持在 API 测试与 UI 测试中直接引用数据

### 🔐 安全与协作
- JWT 双 Token 机制：自动刷新续期、登出黑名单、防重放攻击
- 多项目管理、成员角色权限控制、版本规划
- 统一通知：邮件 + 企业微信 / 钉钉 / 飞书 Webhook 机器人

## 🏗️ 技术架构

### 后端
- **框架**: Django 4.2 + Django REST Framework
- **数据库**: MySQL 8.0+
- **认证**: JWT（rest_framework_simplejwt）+ Token 黑名单
- **自动化**: Selenium、Playwright、Airtest + OCR、Allure
- **异步与任务**: Celery、APScheduler、Channels + Daphne（WebSocket）
- **AI 集成**: browser-use、langchain-openai，多模型提供商
- **API 文档**: drf-spectacular（Swagger / ReDoc）

### 前端
- Vue 3 + Vite + Element Plus
- Pinia 状态管理、Vue Router、Axios
- ECharts 可视化、Monaco Editor、vue-i18n 国际化

在进行 Web、API 及自动化测试时，不同地区的网络环境可能带来不同的访问体验。IPWO住宅代理，支持多地区网络环境配置，可用于海外网站访问、区域测试及自动化测试场景。

<u>[IPWO](https://www.ipwo.net/?ref=githubplatform)</u>为 TestHub 用户提供更多测试环境选择，让跨地区测试更加灵活。覆盖全球195+地区动静态IP资源，支持免费测试入口，90折扣码：0204
![img.png](static_files/img.png)

## 📁 项目结构

```
testhub_platform/
├── apps/                           # Django 应用模块
│   ├── users/                      # 用户认证与管理
│   ├── projects/                   # 项目管理
│   ├── testcases/                  # 测试用例管理
│   ├── testsuites/                 # 测试套件
│   ├── executions/                 # 测试计划与执行
│   ├── reports/                    # 测试报告
│   ├── defects/                    # 缺陷管理
│   ├── reviews/                    # 用例评审
│   ├── versions/                   # 版本管理
│   ├── core/                       # 核心模块（管理命令、变量解析、通知配置）
│   ├── api_testing/                # API 测试
│   ├── ui_automation/              # UI 自动化测试（含 AI 智能模式）
│   ├── app_automation/             # APP 自动化测试
│   ├── perf_testing/               # 性能测试
│   ├── requirement_analysis/       # AI 需求分析
│   ├── assistant/                  # Dify 智能助手
│   ├── data_factory/               # 数据工厂
│   └── llm_judge/                  # LLM 评测
├── backend/                        # Django 项目配置（settings / urls / asgi）
├── frontend/                       # Vue 3 前端（src: views / api / stores / router）
├── media/                          # 媒体文件（上传文件、截图等）
├── logs/                           # 日志文件
├── allure/                         # Allure 报告工具
├── requirements.txt                # Python 依赖
└── manage.py                       # Django 管理脚本
```

## 🚀 快速开始

### 环境要求

- **Python**: 推荐 3.12，其他版本可能存在兼容性问题
- **Node.js**: 18+（前端构建必需，生产环境可不安装）
- **MySQL**: 8.0+
- **Java**: 17+（可选，Allure 报告生成需要）
- **Redis**: 6.0+（可选，APP 自动化 WebSocket / Celery 需要）
- **浏览器驱动**: ChromeDriver / GeckoDriver（UI 自动化，也可通过管理命令自动下载）

### 后端部署

#### macOS / Linux 本地体验（无需 MySQL）

安装下述 Python 依赖和前端依赖（`cd frontend && npm ci`）后，在项目根目录运行：

```bash
bash scripts/start-local.sh
```

脚本使用 `venv/`（或 `.venv/`）虚拟环境，生成迁移并初始化独立的 SQLite 数据库，
创建 `localadmin` 管理员和「本地体验项目」，然后启动 Daphne 和 Vite。
前端地址为 http://127.0.0.1:3001 ，API 文档为 http://127.0.0.1:8001/api/docs/ 。
随机初始密码保存在 `.local/admin-password.txt`，重复启动不会重置密码或清空数据。
前台启动后按 Ctrl+C 停止两个服务。端口被占用时脚本会退出。

此配置仅供本机体验：数据和密钥保存在 Git 忽略的 `.local/` 目录，WebSocket 使用单进程内存通道，
LLM Judge 使用模拟评分。脚本不启动 Celery worker 或定时任务调度器，
AI 用例生成需另配模型，浏览器和手机自动化需另配驱动、设备及异步执行服务。
正式部署请使用下面的 MySQL / Redis 配置。
单独启动前端时，可以通过 `TESTHUB_BACKEND_URL` 环境变量调整代理目标；默认仍为 8000 端口。

#### 标准部署

1. **克隆项目**
```bash
git clone <repository-url>
cd testhub_platform
```

2. **创建虚拟环境并安装依赖**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制模板并按需修改数据库、Redis、邮箱等配置
cp .env.example .env
```

4. **初始化数据库**
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE testhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行迁移并创建超级用户
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. **初始化模块数据（可选）**
```bash
# UI 自动化元素定位策略
python manage.py init_locator_strategies
# APP 自动化组件库
python manage.py load_component_pack
```

6. **启动服务**
```bash
# Django 开发服务器（仅 HTTP）
python manage.py runserver

# 如需 WebSocket（APP 自动化实时进度），改用 Daphne 启动
daphne -b 0.0.0.0 -p 8000 backend.asgi:application

# 定时任务调度器（API / UI 定时任务，可选）
python manage.py run_all_scheduled_tasks

# Celery worker（APP 自动化异步任务，可选）
celery -A backend worker -l info
```

### 前端部署

```bash
cd frontend
npm install
npm run dev        # 开发模式
npm run build      # 生产构建
```

### 访问应用

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs/
- **Admin 后台**: http://localhost:8000/admin/

### 飞书账号登录配置（企业自建应用）

登录页统一通过「使用飞书账号登录」按钮进入飞书官方 OAuth 授权页，同意后返回 TestHub 首页。
授权链接设置 `prompt=consent`，明确展示授权确认；飞书已有登录态时可确认当前账号，未登录时由飞书提供扫码等登录方式。
未配置应用时会提示「尚未配置」，密码和短信登录仍然保留。

1. 打开 [飞书开发者后台](https://open.feishu.cn/app)，选择 **创建企业自建应用**，名称可填 `TestHub 测试平台`。
2. 在 **应用能力 → 添加应用能力** 中添加 **网页应用**。本机调试时，桌面端主页填 `http://127.0.0.1:3001`。
3. 在 **安全设置 → 重定向 URL** 中添加完整地址：
   `http://127.0.0.1:3001/auth/feishu/callback`。
   使用 `localhost`、不同端口或正式域名时，必须同步修改此处和下方环境变量，保持访问入口与回调同源。
4. 在 **凭证与基础信息** 获取 **App ID / App Secret**。Secret 仅放在服务端环境变量中，不填入前端代码，也不要提交到 Git。
5. 设置应用可用范围为测试团队，创建版本并申请发布，由企业管理员按企业审批规则审核。
   登录仅获取基本身份，不需要消息、审批、文档、手机号、邮箱或 `offline_access` 权限。
6. 确认本企业的 `tenant_key`。可以在飞书官方 API 调试台选择 **获取用户信息**，使用该应用和已知本企业成员的用户身份调用，读取返回的 `data.tenant_key`。
   它不是 App ID，也不是用户的 open_id。将确认的值加入下方白名单；白名单为空时不会开放登录。
7. 在项目根目录的 `.env` 中追加或更新下列配置（不要覆盖已有其他配置）：

   ```dotenv
   FEISHU_LOGIN_ENABLED=True
   FEISHU_APP_ID=cli_替换为应用ID
   FEISHU_APP_SECRET=替换为应用Secret
   FEISHU_REDIRECT_URI=http://127.0.0.1:3001/auth/feishu/callback
   FEISHU_ALLOWED_TENANT_KEYS=替换为本企业tenant_key
   FEISHU_AUTO_CREATE_USER=True
   ```

8. 执行数据库迁移并重启后端。本地体验可先停止原启动脚本，再运行 `bash scripts/start-local.sh`，脚本会自动迁移。
   标准部署执行 `python manage.py makemigrations users`、`python manage.py migrate`，然后重启 Django / Daphne。
9. 从 `http://127.0.0.1:3001/login` 打开登录页，点击「使用飞书账号登录」，在飞书官方页面确认账号并同意授权，成功后返回平台首页。
   不要让手机直接访问电脑的 `127.0.0.1` 地址；团队使用时需部署为成员可访问的 HTTPS 域名。

账号按 **App ID + open_id** 关联，额外检查企业白名单；不会根据姓名、手机号或邮箱自动合并已有账号。
默认首次登录创建无密码、无管理员权限的普通用户，由管理员按原项目成员管理流程分配权限。
每次飞书登录会同步名称和头像，首页及模块顶部优先展示飞书资料；内部用户名保持稳定，本地上传的头像不被覆盖。
如需关联已有平台用户，可由管理员在 Django Admin 的「飞书账号关联」中选择目标用户，核对应用、企业和 open_id 后保存。
设置 `FEISHU_AUTO_CREATE_USER=False` 时，仅允许已经关联的账号登录；平台停用的用户无法通过飞书重新登录。
此接入只负责登录，不会自动同步飞书任务、多维表格、审批或成员权限，也不会保留飞书访问令牌。
现有 TestHub JWT 生命周期不变，飞书离职/禁用会在下一次飞书认证时被拒绝，已签发的平台会话不会自动实时撤销。

登录请求使用 5 分钟有效的一次性 state、HttpOnly 浏览器绑定 Cookie 和 PKCE S256；重放、跨浏览器回调、企业不匹配均会被拒绝。
令牌交换使用飞书授权页文档指定的 PKCE 配套 v2 接口；v3 在当前流程中返回 `20049`，因此未采用。失败提示仅包含安全的固定说明和数字错误码，不记录授权码或令牌。
刷新或取消后请重新发起授权，多个窗口同时发起登录时以最后一次请求为准。
正式部署要求 HTTPS，同源反向代理 `/api/` 并将 `/auth/feishu/callback` 回落到前端 `index.html`，不要把回调查询参数写入访问日志。
若使用 Cookie / 跟踪拦截插件导致浏览器绑定 Cookie 丢失，重新允许本站必要 Cookie 后再试。

验证命令（飞书 HTTP 响应使用 mock，不需要真实密钥）：

```bash
DJANGO_SETTINGS_MODULE=backend.test_settings python manage.py test apps.users.test_feishu
```

官方参考：[创建自建网页应用](https://open.feishu.cn/document/client-docs/h5/development-guide/step1)、
[配置重定向 URL](https://open.feishu.cn/document/develop-web-apps/configure-redirect-urls)、
[获取授权码](https://open.feishu.cn/document/authentication-management/access-token/obtain-oauth-code)、
[获取用户信息](https://open.feishu.cn/document/server-docs/authentication-management/login-state-management/get)。

### Docker 部署（可选）

```bash
./build-and-push.sh    # 构建并推送镜像
docker-compose up -d   # 一键启动全栈服务
```

## 🔧 配置说明

环境变量统一在 `.env` 中配置（参考 `.env.example`），主要包括：

- **数据库**: `DB_NAME`、`DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`
- **Redis**: `REDIS_URL`（APP 自动化 WebSocket / Celery 需要）
- **AI 模型**: 在「统一配置中心」管理多家提供商的 API Key / Base URL / 模型参数，支持按角色配置（用例编写、用例评审、Browser Use），并提供连接测试
- **UI 自动化**: 执行引擎（Selenium / Playwright）、浏览器、有头 / 无头模式
- **通知**: 邮件（SMTP）与 Webhook 机器人（企业微信 / 钉钉 / 飞书）

## 📄 文档

更多使用说明见 [docs/docs-center](./docs/docs-center/)：

- **[数据工厂使用说明](./docs/docs-center/数据工厂使用说明.md)** / **[快速开始](./docs/docs-center/数据工厂快速开始.md)** / **[功能说明](./docs/docs-center/数据工厂功能说明.md)** / **[API 接口文档](./docs/docs-center/数据工厂API接口文档.md)**
- **[UI 自动化测试执行说明](./docs/docs-center/UI自动化测试执行说明.md)** / **[UI 自动化测试用户使用手册](./docs/docs-center/UI%20自动化测试用户使用手册.md)**
- **[WebDriver 驱动管理优化说明](./docs/docs-center/WebDriver驱动管理优化说明.md)**
- **[用例评审管理功能说明](./docs/docs-center/用例评审管理功能说明.md)**
- **[I18N 国际化使用说明](./docs/docs-center/I18N国际化使用说明.md)**
- **[问题排查指南](./docs/docs-center/问题排查指南.md)**



## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 GPL 3.0 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

如有问题或建议，欢迎通过 Issue 反馈，也可以扫码添加作者，加入官方交流群。
![img_1.png](static_files/img_1.png)

<u>[TestHub 官网](https://testhub.aisky.cloud)</u>

使用手册、视频教程、学习中心、Skills商店，欢迎访问TestHub官网。
![img_2.png](static_files/img_2.png)
---

<div align="center">
Made with ❤️ by 大刚（公众号：测试开发实战）
</div>

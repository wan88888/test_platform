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
普通登录不会自动同步飞书任务、多维表格、审批或成员权限，也不保留飞书访问令牌。独立的文档授权与用例表格输出见下方说明。
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

### Kimi K3：AI 用例生成模型配置

在「配置中心 → AI 模型配置」中添加或编辑配置。本地体验入口：
[AI 模型配置](http://127.0.0.1:3001/configuration/ai-model)。

| 字段 | 填写要求 |
| --- | --- |
| 模型类型 | 选择「其他」（OpenAI Chat Completions 兼容接口） |
| Base URL | `https://api.moonshot.cn/v1` |
| 模型名称 | `kimi-k3` |
| API Key | 填写 Kimi 开放平台的 API Key，不要写入说明文档或提交到 Git |
| 角色 | 按用途选择「用例编写」或「用例评审」 |
| Temperature／温度 | **固定为 `1`** |
| Top P | **固定为 `0.95`** |

Kimi K3 的采样参数不能沿用平台通用默认值。官方建议不显式传入固定参数，
但当前平台会发送 `temperature` 和 `top_p`，因此需要在配置页面填写上述值；平台尚未自动适配这些限制。
「用例编写」和「用例评审」如果都使用 `kimi-k3`，两条配置都要调整。
修改后点击「测试连接」，成功后保存并启用配置。

**常见报错：**

```text
invalid temperature: only 1 is allowed for this model
```

该错误表示请求中的温度不符合模型要求。将 Temperature 改为 `1`，同时检查 Top P 为 `0.95`，然后重新测试。
这一步解决采样参数校验问题，不代表其他参数、账号额度或实际用例生成已经验证通过。

以上要求针对 **Kimi 官方接口的 `kimi-k3`**，不要直接套用到其他模型或第三方网关。
核对日期：2026-10-28。官方参考：[Kimi K3 接入说明（含重要限制）](https://platform.kimi.com/docs/guide/kimi-k3-quickstart)。

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

<u>[TestHub 官网](https://testhub.aisky.cloud)</u>

使用手册、视频教程、学习中心、Skills商店，欢迎访问TestHub官网。
![img_2.png](static_files/img_2.png)
---

### 飞书需求文档 → AI 用例 → 飞书电子表格 / 思维笔记

在「AI用例生成」页面的「复制粘贴飞书文档链接」区域，粘贴飞书 `/docx/` 或 `/wiki/` 链接，选择「飞书表格」或「飞书思维笔记」，点击生成按钮。标题可不填，默认取文档标题。生成结果同时保留在平台，页面及生成记录详情提供飞书结果链接。

- **飞书表格**：在本人的飞书云空间新建电子表格（不是多维表格）。
- **飞书思维笔记**：自动保存到当前账号云空间的「我的空间」根目录，与表格默认保存位置一致，无需填写目标知识库页面。后台先定位当前用户的 `my_library` 个人文档库，在其根目录新建原生 `mindnote`，按「需求标题 → 用例 → 各字段」写入并校验，然后仅将这份新笔记移到「我的空间」。步骤、预期结果、优先级等原表格列均保留。需求链接只用于读取正文，不在原需求下创建子页面；支持普通 `/docx/` 和 `/wiki/` 需求链接。该流程使用原生思维笔记节点 API，不会创建画板代替思维笔记。

**首次配置（沿用登录用企业自建应用和回调地址，不需要新 App Secret）：**

1. 在飞书开放平台打开该应用，进入「权限管理」，申请以下**用户身份权限**：

   | 权限 | 用途 |
   | --- | --- |
   | `docx:document:readonly` | 读取需求文档标题及正文 |
   | `wiki:node:read` | 将知识库链接解析为实际文档 |
   | `sheets:spreadsheet` | 创建、读写和校验结果电子表格 |
   | `wiki:node:create` | 思维笔记输出额外需要：在个人文档库新建笔记 |
   | `mindnote:node:read` | 思维笔记输出额外需要：读取根节点及回读校验 |
   | `mindnote:node:create` | 思维笔记输出额外需要：创建用例和字段节点 |
   | `wiki:space:read` | 思维笔记输出额外需要：定位自己的文档库、查询移动任务结果 |
   | `space:document:move` | 思维笔记输出额外需要：将本次新建的笔记移到自己的云空间 |

2. 创建应用版本，提交并发布生效，确保团队成员在应用可用范围内。
3. 使用飞书账号登录 TestHub，先选择输出方式，再点击「授权飞书文档访问」，同意后自动返回生成页。已有表格授权不会自动获得思维笔记权限，首次切换需要重新授权。每位成员分别授权，且必须使用当前平台账号关联的同一个飞书账号。选择表格仅申请原来的三项权限；选择思维笔记申请表中全部权限。如果应用后台无法申请 `mindnote` 权限，需向飞书确认该应用的接口开放范围，不能仅靠前端按钮完成接入。
4. 配好编写模型、评审模型、提示词和生成行为配置。编写/评审提示词应输出 Markdown 用例表格；内置提示词可直接使用。Kimi K3 的采样参数要求见上文。
5. 粘贴本人有阅读权限的需求文档链接并生成。正文交给平台配置的 AI 服务，生成结果使用本人的用户凭证写入飞书；不扩大文档共享范围。

若授权页提示 `20027`，以页面列出的权限为准检查该应用的**用户身份权限**（不是应用身份权限），并确认版本已发布；完成后从 TestHub 重新发起授权，不要刷新旧回调页。

若旧版本的思维笔记任务在原需求下新建时报 `131006`，这是原知识库/父页面的资源权限不足；仅能阅读正文不足以创建子页面。新流程默认保存到本人空间，不再依赖原需求的写权限。历史任务保留原目标和已有笔记，不能直接批量重置；只有确认尚未创建笔记且处于失败状态的任务，才可调整为本人空间后重试。用例不必重新生成。

**正文与输出范围：**

- 支持新版云文档及其知识库包装链接；不支持旧版 `/docs/`、以表格/思维笔记/多维表格为底层内容的知识库节点。
- 使用文档纯文本接口读取正文，不自动下载图片、附件或递归读取嵌入资源，也不进行 OCR。关键需求应写入正文；超过 10 万字符会明确拒绝，不会静默截断。
- Markdown 表格各列保留（包括测试类型、关联需求），支持转义竖线和单元格 `<br>` 换行；上限 4999 条用例、26 列，每格 4 万字符。不合规表格明确报错，平台仍保留原始结果。
- 飞书同步发生在生成完成后，不依赖浏览器一直打开。平台服务重启可能中断既有的后台生成线程；生成记录用于追踪结果。该流程复用现有线程执行机制，尚非持久化任务队列。
- 写入后回读校验；失败可在当前页或「AI生成用例记录 → 详情」重试。已知表格 ID 时继续写入同一表格，不重复创建。重试会恢复该次导出的固定内容快照，可能覆盖目标范围内的手动编辑；输出成功后不再重复同步平台编辑。
- 思维笔记在新建后立即保存目标标识；节点每次写入前保存原始请求及 `client_token`，网络中断时用同一幂等请求重试，已完成的批次不重复发送。每批回读确认节点内容和父子关系，最终再校验全部已写节点。同步期间不要手动修改或删除节点，否则会明确报校验失败。知识库新建本身无已确认的幂等参数，创建结果不明时禁止自动重建。
- 移到云空间是异步任务：保存完整任务 ID，有限轮询并验证成功结果指向本次笔记。查询超时后重试仅继续查询同一移动任务，不再创建笔记或重新移动。移动请求结果不明且未取得任务 ID 时暂停重试，需人工核对。只有确认移到「我的空间」并取得可信结果链接后才显示同步成功。
- 若新建请求超时且无法确定是否创建成功，会显示「新建结果待核对」，不会盲目再次新建；请到飞书云空间检查。同步中的进程异常退出也应先人工核对，避免重复写入。

**凭证与访问：**

普通飞书登录不保存飞书访问令牌。只有用户单独同意文档授权后，才把该用户的短期访问令牌加密保存在后端，最长保留有效期 2 小时（提前 60 秒失效），不保存刷新令牌。查询到过期授权时清除；可点击「取消授权」主动清除本地凭证，或在飞书撤销应用授权。过期后重新授权即可重试写入已有用例，无需重新生成。加密密钥从部署的 Django `SECRET_KEY` 派生，务必保持密钥私密且稳定；更换后需重新授权。飞书凭证不会进入前端或日志。飞书导入任务及其结果接口按发起人隔离，不因其他成员知道任务 ID 就允许访问。

**部署及验证：**

按本仓库现有迁移方式，在后端环境执行 `python manage.py makemigrations users requirement_analysis` 和 `python manage.py migrate`，然后重启后端；本地 `scripts/start-local.sh` 会执行迁移。前端重新构建或使用 Vite 开发服务。

```bash
DJANGO_SETTINGS_MODULE=backend.local_settings venv/bin/python manage.py test apps.users.test_feishu apps.requirement_analysis.test_feishu_documents --noinput
cd frontend
npm run build
```

接口规范：[获取文档正文](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/raw_content)、[解析知识库节点](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node)、[创建知识空间节点](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/create)、[官方 CLI 思维笔记 API 定义](https://github.com/larksuite/cli/blob/main/internal/registry/catalog/services/mindnotes.json)、[创建电子表格](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet/create)、[写入单个范围](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-data-to-a-single-range)、[读取单个范围](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-a-single-range)。

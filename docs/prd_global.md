# Flori PRD Global

> 文档定位：产品背景、用户故事、价值和指标。  
> Project: `flori`  
> CLI: `fi`

---

## 背景与目标

Flori 是一个面向单节点服务器的 Frappe 应用部署与管理 CLI 工具。

它不复刻 Frappe Press，也不做完整 PaaS，而是基于官方 `frappe_docker`，把 Frappe 应用的镜像构建、bench 创建、site 创建、domain 绑定和 Traefik 公网入口管理标准化。

核心目标：

1. 降低单节点 Frappe 部署复杂度。
2. 严格区分 `bench`、`site`、`domain`，避免状态混乱和错误暴露。
3. 用 SQLite 记录本地部署状态，让部署过程可追踪、可恢复、可脚本化。
4. 使用显式命令行参数，不把环境变量作为主要输入方式。

核心概念：

```text
bench  = Docker Compose runtime environment
site   = internal Frappe site name
domain = external public access domain
```

V1 范围：

- 多 bench 管理。
- 多 internal site 管理。
- external domain 到 internal site 的显式映射。
- 一个全局 Traefik reverse proxy。
- Cloudflare DNS-01 TLS 证书。
- SQLite 本地状态。
- CLI 输出保持 minimal、script-friendly。

V1 非目标：

- Web UI
- Frappe Press 集成
- Kubernetes / 多节点调度
- billing / marketplace
- 自动备份
- 复杂权限
- remote agent
- async worker
- bench/site/domain 删除

---

## 故事介绍

一个开发者有一个 Frappe 应用，例如 wiki、CRM、ERPNext 扩展或内部业务系统。他希望把应用部署到自己的服务器，并逐步维护多个环境、多个客户站点或多个内部站点。

如果直接使用原始 `frappe_docker`，他需要自己处理 Compose 文件、Traefik labels、TLS、DNS、Frappe site name、external domain mapping 等细节。

Flori 把这些步骤收敛为一组稳定命令：

```text
fi init
  -> fi build-image
  -> fi bench-create -b <bench>
  -> fi site-create -b <bench> -s <site>
  -> fi domain-create -b <bench> -s <site> -d <domain>
```

关键设计原则：

- `bench-create` 只创建运行环境，不创建 site。
- `site-create` 只创建 internal site，不创建公网路由。
- `domain-create` 才创建 external domain mapping 和 Traefik route。
- internal `.lan` site 不直接暴露到公网。
- external `.cloud` domain 必须显式映射到 internal site。

### 用户场景

#### 1. 初始化服务器

```bash
fi init \
  --email admin@floribird.cloud \
  --cf-dns-api-token <token> \
  --cf-zone-api-token <token> \
  --up
```

结果：创建 `~/.flori`、拉取 `frappe_docker`、创建 `flori-public` network、生成 Traefik proxy、初始化 SQLite。

#### 2. 构建应用镜像

```bash
fi build-image wiki v3.0.0 \
  --apps apps/wiki.json \
  --repo flori \
  --frappe-branch version-15
```

输出：

```text
flori:wiki-v3.0.0
```

#### 3. 创建 bench

```bash
fi bench-create -b wiki \
  --image flori \
  --tag wiki-v3.0.0 \
  --app wiki \
  --up
```

结果：创建 bench runtime、`.env`、`compose.yml` 和 SQLite bench 记录。

#### 4. 创建 internal site

```bash
fi site-create -b wiki -s docs \
  --admin-password change-me
```

输出：

```text
docs.a.s.dev.floribird.lan
```

#### 5. 绑定 external domain

```bash
fi domain-create -b wiki -s docs -d docs
```

映射：

```text
docs.a.s.dev.floribird.cloud -> docs.a.s.dev.floribird.lan
```

#### 6. 运维排查

```bash
fi bench-list
fi site-list -b wiki
fi domain-list -b wiki
fi bench-logs -b wiki --service backend --follow
fi shell -b wiki
```

### 价值分析

对用户：

- 不需要手写 Compose merge 命令。
- 不需要手写 Traefik labels。
- 不需要手动维护 domain 到 site 的映射。
- 降低 internal site 错误暴露到公网的风险。

对研发：

- 命令参数显式，测试和复现更容易。
- `-b`、`-s`、`-d` 统一表达 bench、site、domain。
- SQLite 本地状态便于排查和自动化验收。

对交付：

- 部署流程可以固化为脚本。
- 命令输出最小化，便于 CI/CD 或自动化系统解析。
- V1 范围清晰，不引入 Web UI、多节点、备份等复杂能力。

### 核心体验路径

主路径：

```text
准备服务器
  -> fi init
  -> fi build-image
  -> fi bench-create -b <bench>
  -> fi site-create -b <bench> -s <site>
  -> fi domain-create -b <bench> -s <site> -d <domain>
  -> external domain 可访问
```

异常路径：

```text
Docker/Git 缺失 -> init 失败
bench 不存在 -> site/domain/shell/logs 失败
site 不存在或不属于 bench -> domain-create 失败
-b/-s/-d 缺失 -> Click 参数校验失败
Compose 生成失败 -> 命令失败并输出底层错误
```

### 产品指标

激活指标：

- `fi init --up` 成功率。
- 从空服务器到第一个 external domain 可访问的成功率。
- 首次完整部署平均耗时。

效率指标：

- 手动修改 Compose 文件次数。
- 手动修改 Traefik labels 次数。
- 从 image build 到 domain ready 的命令数量。

可靠性指标：

- `build-image / bench-create / site-create / domain-create` 失败率。
- SQLite state 与真实 Docker/Frappe 状态不一致次数。

安全指标：

- internal `.lan` site 被错误暴露到公网的次数必须为 0。
- `domain-create` 缺少 `-s` 或 `-d` 被阻止比例。
- proxy `.env` 和 bench `.env` 权限检查通过率。

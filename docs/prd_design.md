# Flori PRD Design

> 文档定位：概要设计、交互设计和详细设计。  
> Project: `flori`  
> CLI: `fi`

---

## 概要设计

Flori 采用单 CLI、单本地状态库、单全局代理、多 bench runtime 的结构。

```text
fi CLI
  -> SQLite state
  -> frappe_docker vendor files
  -> generated compose per bench
  -> global Traefik proxy
  -> Docker runtime
```

资源边界：

```text
image  -> 用于创建 bench 的应用镜像
bench  -> Docker Compose runtime
site   -> Frappe internal site
domain -> public external domain mapping
```

### 模块

#### CLI 入口模块

- 提供 flat command structure。
- 统一 Click 参数解析。
- 统一错误输出。
- 输出 minimal、script-friendly。

统一参数：

```text
-b, --bench   指定 bench
-s, --site    指定 site
-d, --domain  指定 domain
```

#### 状态管理模块

使用 SQLite 保存：

```text
settings / images / benches / sites / domains
```

状态文件：

```text
~/.flori/state.db
```

#### 镜像构建模块

- 校验 `apps.json`。
- 使用官方 `frappe_docker` Containerfile。
- 执行 `docker build`。
- 写入 image metadata。

#### Bench 管理模块

- 创建 bench runtime。
- 生成 `.env`、`flori.override.yml`、`compose.yml`。
- 支持 up/down/logs。
- 不创建 site/domain/public route。

#### Site 管理模块

- 在已有 bench 中创建 internal Frappe site。
- 解析 short site name。
- 安装 bench default apps 或指定 apps。
- 不创建 external domain。
- 不更新 Traefik route。

#### Domain 管理模块

- 创建 external domain 到 internal site 的映射。
- 校验 site 存在且属于指定 bench。
- 调用 `bench setup add-domain`。
- 写入 domains 表。
- 重新生成 Traefik labels 和 compose。
- 重启 frontend。

#### Proxy 模块

- 管理全局 Traefik reverse proxy。
- 使用 Cloudflare DNS-01 签发证书。
- 提供 `flori-public` Docker network。

### 功能

V1 commands：

```text
fi init
fi build-image
fi bench-create
fi bench-up
fi bench-down
fi bench-logs
fi site-create
fi domain-create
fi shell
fi bench-list
fi site-list
fi domain-list
fi image-list
fi db-path
```

核心命令：

```bash
fi init ...
fi build-image <app> <version> --apps <apps.json>
fi bench-create -b <bench> ...
fi site-create -b <bench> -s <site> ...
fi domain-create -b <bench> -s <site> -d <domain>
```

运维命令：

```bash
fi bench-up -b <bench>
fi bench-down -b <bench>
fi bench-logs -b <bench> [--service <service>] [--follow]
fi shell -b <bench> [command...]
```

查询命令：

```bash
fi bench-list
fi site-list [-b <bench>]
fi domain-list [-b <bench>]
fi image-list
fi db-path
```

### 页面

Flori 是 CLI 产品，没有 Web 页面。本文中的“页面”指 CLI 信息界面。

#### 帮助界面

```bash
fi --help
fi init --help
fi bench-create --help
fi site-create --help
fi domain-create --help
```

帮助信息必须说明：

- 哪些参数 required。
- `-b` 表示 bench。
- `-s` 表示 site。
- `-d` 表示 domain。
- 哪些参数有默认值。

#### 命令结果界面

成功输出保持最小化：

```text
fi init          -> ~/.flori
fi build-image   -> flori:wiki-v3.0.0
fi bench-create  -> ~/.flori/benches/wiki/compose.yml
fi site-create   -> docs.a.s.dev.floribird.lan
fi domain-create -> docs.a.s.dev.floribird.cloud
fi db-path       -> ~/.flori/state.db
```

#### 列表界面

列表输出使用 tab-separated rows，便于脚本解析。

```bash
fi bench-list
fi site-list -b wiki
fi domain-list -b wiki
fi image-list
```

---

## 详细设计

#### 1. 默认常量

```python
DEFAULT_BASE_DIR = Path.home() / ".flori"
DEFAULT_FRAPPE_DOCKER_REF = "v3.2.0"
DEFAULT_INTERNAL_DOMAIN_ROOT = "a.s.dev.floribird.lan"
DEFAULT_EXTERNAL_DOMAIN_ROOT = "a.s.dev.floribird.cloud"
PUBLIC_NETWORK = "flori-public"
```

#### 2. Runtime Layout

```text
~/.flori/
  state.db
  vendor/frappe_docker/
  proxy/compose.yml
  proxy/.env
  proxy/letsencrypt/
  benches/<bench>/.env
  benches/<bench>/flori.override.yml
  benches/<bench>/compose.yml
  benches/<bench>/sites/
  benches/<bench>/logs/
```

#### 3. SQLite Tables

```text
settings: key, value, updated_at
images: image_tag, app, version, repo, apps_file, frappe_branch, pushed, timestamps
benches: name, path, image, tag, default_site, apps_json, status, timestamps
sites: name, bench, status, timestamps
domains: domain, bench, site, status, timestamps
```

约束：

- `sites.bench` 关联 `benches.name`。
- `domains.bench` 关联 `benches.name`。
- `domains.site` 关联 `sites.name`。
- `domain-create` 必须校验 site 属于指定 bench。

#### 4. 状态流转

```text
bench:  created -> running -> stopped
site:   active
domain: active
```

后续可扩展：

```text
creating -> active -> failed -> deleting
```

#### 5. 命令设计

`fi init`：

```bash
fi init \
  --email <email> \
  --cf-dns-api-token <token> \
  [--cf-zone-api-token <token>] \
  [--http-port 80] \
  [--https-port 443] \
  [--base-dir ~/.flori] \
  [--force] \
  [--up]
```

`fi build-image`：

```bash
fi build-image <app> <version> \
  --apps <apps.json> \
  [--repo flori] \
  [--frappe-branch version-15] \
  [--builder layered|custom] \
  [--platform linux/amd64] \
  [--push]
```

`fi bench-create`：

```bash
fi bench-create -b <bench> \
  [--image frappe/erpnext] \
  [--tag version-15] \
  [--default-site <site>] \
  [--app <app>]... \
  [--up] \
  [--force]
```

规则：不创建 site、不创建 domain、不创建 public route。

`fi site-create`：

```bash
fi site-create -b <bench> \
  [-s <site>] \
  --admin-password <password> \
  [--app <app>]... \
  [--migrate/--no-migrate]
```

规则：只创建 internal site，不创建 external domain，不更新 Traefik labels。

`fi domain-create`：

```bash
fi domain-create -b <bench> -s <site> -d <domain>
```

规则：

- `-b/-s/-d` required。
- site 必须存在。
- site 必须属于指定 bench。
- 只有 domains 表中的 external domain 进入 Traefik labels。

#### 6. 域名设计

Internal root：

```text
a.s.dev.floribird.lan
```

External root：

```text
a.s.dev.floribird.cloud
```

解析规则：

```text
-s docs -> docs.a.s.dev.floribird.lan
-d docs -> docs.a.s.dev.floribird.cloud
```

映射规则：

```text
external domain -> internal site
```

#### 7. Compose 与 Traefik

每个 bench 使用官方 Compose 文件：

```text
frappe_docker/compose.yaml
frappe_docker/overrides/compose.mariadb.yaml
frappe_docker/overrides/compose.redis.yaml
```

叠加 Flori override：

```text
~/.flori/benches/<bench>/flori.override.yml
```

生成最终 Compose：

```text
~/.flori/benches/<bench>/compose.yml
```

Traefik labels 只基于 `domains` 表生成。Internal `.lan` sites 不进入 public router。

#### 8. 安全设计

参数策略：

- V1 使用命令行显式参数作为主要输入方式。
- 不建议依赖环境变量作为主路径。
- 敏感参数通过命令行传入可能进入 shell history 或 process list，这是已知风险。
- 后续可支持 prompt、secret file 或 secret manager。

文件权限：

```text
~/.flori/proxy/.env      0600
~/.flori/benches/*/.env  0600
```

路由安全：

- `site-create` 不创建公网入口。
- `domain-create` 是唯一创建公网入口的命令。
- Traefik routes 只能来自 `domains` 表。
- `.lan` internal sites 不应直接出现在 Traefik Host rule 中。

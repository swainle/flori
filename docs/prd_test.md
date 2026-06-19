# Flori PRD Test & Delivery

> 文档定位：交付计划、测试策略和验收标准。  
> Project: `flori`  
> CLI: `fi`

---

## 交付设计

### 1. 交付原则

Flori V1 以“单节点 Frappe 部署闭环”为交付目标。

交付要求：

- 命令结构保持 flat。
- 输出保持 minimal。
- 参数使用显式 CLI option。
- bench/site/domain 参数统一为 `-b/-s/-d`。
- 不依赖环境变量作为主要验收路径。
- 不把 internal `.lan` site 暴露到公网。
- 每个功能都能通过命令行输出和 SQLite 状态验证。

### 2. 里程碑

#### 里程碑 1：MVP 闭环

交付：

```text
fi init
fi build-image
fi bench-create -b
fi site-create -b -s
fi domain-create -b -s -d
fi bench-up/down/logs -b
fi shell -b
list commands
SQLite schema
Jinja2 templates
README quickstart
```

验收目标：从空服务器部署到第一个 external domain 可访问。

#### 里程碑 2：参数风格统一

交付：

- bench 统一为 `-b, --bench`。
- site 统一为 `-s, --site`。
- domain 统一为 `-d, --domain`。
- 移除 bench/site/domain 相关位置参数。
- 环境变量不作为 V1 主验收路径。
- 更新 README、示例命令和测试用例。

#### 里程碑 3：稳定性补强

交付：

- Docker/Git/Compose preflight check。
- `require_bench`。
- `require_site_for_bench`。
- `require_slug`。
- `normalize_domain`。
- compose generation failure handling。
- `.env` 权限检查。

#### 里程碑 4：文档与排障

交付：

- Quickstart。
- DNS setup guide。
- Cloudflare token permission guide。
- Troubleshooting。
- Recovery guide。
- End-to-end smoke test。

### 3. 端到端交付路径

```bash
fi init \
  --email admin@floribird.cloud \
  --cf-dns-api-token <token> \
  --cf-zone-api-token <token> \
  --up

fi build-image wiki v3.0.0 \
  --apps apps/wiki.json \
  --frappe-branch version-15

fi bench-create -b wiki \
  --image flori \
  --tag wiki-v3.0.0 \
  --app wiki \
  --up

fi site-create -b wiki -s docs \
  --admin-password change-me

fi domain-create -b wiki -s docs -d docs

fi shell -b wiki bench --site docs.a.s.dev.floribird.lan migrate
```

期望关键输出：

```text
~/.flori
flori:wiki-v3.0.0
~/.flori/benches/wiki/compose.yml
docs.a.s.dev.floribird.lan
docs.a.s.dev.floribird.cloud
```

期望映射：

```text
docs.a.s.dev.floribird.cloud -> docs.a.s.dev.floribird.lan
```

### 4. 功能验收标准

#### Init

- 创建 `~/.flori`。
- 克隆 `frappe_docker` 到 `~/.flori/vendor/frappe_docker`。
- checkout `v3.2.0`。
- 创建 proxy `compose.yml` 和 `.env`。
- proxy `.env` 权限为 `0600`。
- `fi init --up` 启动 Traefik。
- V1 验收路径不依赖环境变量。

#### Build Image

- `fi build-image wiki v3.0.0 --apps apps/wiki.json` 构建 `flori:wiki-v3.0.0`。
- 使用 official `frappe_docker` Containerfile。
- 使用 BuildKit secret。
- image metadata 保存到 SQLite。

#### Bench Create

- `fi bench-create -b wiki ...` 创建 bench files。
- 插入一条 `benches` 记录。
- 不插入 `sites`。
- 不插入 `domains`。
- 不运行 `bench new-site`。
- 不创建 Traefik route。

#### Site Create

- `fi site-create -b wiki -s docs ...` 创建 `docs.a.s.dev.floribird.lan`。
- 插入一条 `sites` 记录。
- 不插入 `domains`。
- 不添加 Traefik route labels。
- 未传 `--app` 时安装 bench default apps。

#### Domain Create

- `fi domain-create -b wiki -s docs -d docs` 创建映射：

```text
external: docs.a.s.dev.floribird.cloud
internal: docs.a.s.dev.floribird.lan
```

- `-b/-s/-d` required。
- site 必须存在且属于 bench。
- 执行 `bench setup add-domain`。
- 插入一条 `domains` 记录。
- 重新生成 `flori.override.yml` 和 `compose.yml`。
- 重启 frontend。
- Traefik routes 只包含 domains，不包含 sites。

#### Shell & List

- `fi shell -b wiki` 打开 backend shell。
- `fi shell -b wiki bench --site docs.a.s.dev.floribird.lan migrate` 可执行。
- `fi bench-list` 输出 benches。
- `fi site-list -b wiki` 输出 sites。
- `fi domain-list -b wiki` 输出 domains。
- `fi image-list` 输出 image metadata。
- `fi db-path` 输出 SQLite 路径。

### 5. 测试策略

#### Unit Tests

覆盖：

- `slug` / `require_slug`
- `normalize_domain`
- site/domain name resolution
- image tag generation
- `host_rule`
- SQLite upsert
- bench/site/domain relationship validation

#### CLI Tests

覆盖：

- required 参数校验。
- `-b/-s/-d` 参数解析。
- 缺少 `-s` 的 `domain-create` 必须失败。
- 缺少 `-d` 的 `domain-create` 必须失败。
- list commands 输出格式。
- 错误信息可读性。

#### Integration Tests

在具备 Docker 的环境中覆盖：

- `fi init` 生成 runtime layout。
- `fi bench-create` 生成 compose 文件。
- `fi site-create` 创建 site。
- `fi domain-create` 更新 mapping 和 Traefik labels。
- `fi bench-up/down/logs` 可执行。

#### Manual Smoke Test

完整执行：

```text
init -> build-image -> bench-create -> site-create -> domain-create -> shell migrate
```

### 6. 风险与回滚

已知风险：

- 敏感参数通过命令行传入，可能进入 shell history 或 process list。
- Docker/Compose/frappe_docker 版本变化可能导致配置生成失败。
- DNS 生效存在延迟。
- Cloudflare token 权限不足会导致证书签发失败。
- SQLite state 可能与真实 Docker/Frappe 状态不一致。

回滚策略：

- 保留生成的 `compose.yml` 便于手动排查。
- 使用 `fi db-path` 定位 SQLite。
- 使用 list commands 对比本地状态。
- 使用 `docker compose` 原生命令排查 runtime。
- 失败命令不应静默污染 sites/domains 状态。

### 7. 交付物清单

```text
prd_global.md
prd_design.md
prd_test.md
README.md
src/flori/cli.py
src/flori/templates/
pyproject.toml
uv.lock
tests/
```

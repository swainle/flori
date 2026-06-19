from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, TypeVar

import click
from jinja2 import Environment, FileSystemLoader, PackageLoader, TemplateNotFound


# -----------------------------------------------------------------------------
# Defaults from PRD
# -----------------------------------------------------------------------------

DEFAULT_BASE_DIR = Path.home() / ".flori"
DEFAULT_FRAPPE_DOCKER_URL = "https://github.com/frappe/frappe_docker.git"
DEFAULT_FRAPPE_DOCKER_REF = "v3.2.0"

DEFAULT_INTERNAL_DOMAIN_ROOT = "a.s.dev.floribird.lan"
DEFAULT_EXTERNAL_DOMAIN_ROOT = "a.s.dev.floribird.cloud"

PUBLIC_NETWORK = "flori-public"

SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

F = TypeVar("F", bound=Callable[..., object])


@dataclass(frozen=True)
class Ctx:
    base_dir: Path
    frappe_docker_path: Path
    internal_domain_root: str
    external_domain_root: str
    db_path: Path


# -----------------------------------------------------------------------------
# Runtime options
# -----------------------------------------------------------------------------


def runtime_options(func: F) -> F:
    """Add explicit runtime options to commands.

    The PRD asks not to use environment variables as the main input path.
    These options keep all runtime configuration explicit and scriptable.
    """

    options = [
        click.option(
            "--base-dir",
            type=click.Path(path_type=Path),
            default=DEFAULT_BASE_DIR,
            show_default=str(DEFAULT_BASE_DIR),
            help="Flori runtime directory.",
        ),
        click.option(
            "--frappe-docker-path",
            type=click.Path(path_type=Path),
            default=None,
            help="Path to frappe_docker checkout. Defaults to <base-dir>/vendor/frappe_docker.",
        ),
        click.option(
            "--internal-domain-root",
            default=DEFAULT_INTERNAL_DOMAIN_ROOT,
            show_default=True,
            help="Internal Frappe site root.",
        ),
        click.option(
            "--external-domain-root",
            default=DEFAULT_EXTERNAL_DOMAIN_ROOT,
            show_default=True,
            help="External public domain root.",
        ),
    ]

    for option in reversed(options):
        func = option(func)
    return func


def build_ctx(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
) -> Ctx:
    base_dir = normalize_path(base_dir)

    if frappe_docker_path is None:
        frappe_docker_path = base_dir / "vendor" / "frappe_docker"
    else:
        frappe_docker_path = normalize_path(frappe_docker_path)

    return Ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=normalize_domain_root(internal_domain_root, "internal-domain-root"),
        external_domain_root=normalize_domain_root(external_domain_root, "external-domain-root"),
        db_path=base_dir / "state.db",
    )


# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_path(path: Path) -> Path:
    return path.expanduser().resolve()


def normalize_short_name(value: str, label: str) -> str:
    candidate = value.strip().lower()

    if not candidate:
        raise click.ClickException(f"{label} cannot be empty")

    if "." in candidate:
        raise click.ClickException(f"{label} must be a short slug, not a domain: {value}")

    if not SLUG_RE.match(candidate):
        raise click.ClickException(
            f"Invalid {label}: {value}. Use lowercase letters, digits and hyphens only."
        )

    return candidate


def normalize_app_name(value: str) -> str:
    return normalize_short_name(value, "app")


def normalize_domain(value: str, label: str) -> str:
    domain = value.strip().lower().rstrip(".")

    if not domain:
        raise click.ClickException(f"{label} cannot be empty")

    labels = domain.split(".")
    if len(labels) < 2:
        raise click.ClickException(f"{label} must be a full domain: {value}")

    for part in labels:
        if not DOMAIN_LABEL_RE.match(part):
            raise click.ClickException(f"Invalid {label}: {value}")

    return domain


def normalize_domain_root(value: str, label: str) -> str:
    return normalize_domain(value, label)


def render(name: str, **ctx: object) -> str:
    """Render template from package, with a filesystem fallback for local testing."""

    try:
        env = Environment(
            loader=PackageLoader("flori", "templates"),
            autoescape=False,
            keep_trailing_newline=True,
        )
        return env.get_template(name).render(**ctx)
    except (ModuleNotFoundError, TemplateNotFound):
        template_dir = Path(__file__).resolve().parent / "templates"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False,
            keep_trailing_newline=True,
        )
        return env.get_template(name).render(**ctx)


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    proc_env = os.environ.copy()
    proc_env.setdefault("DOCKER_BUILDKIT", "1")

    if env:
        proc_env.update(env)

    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=proc_env,
            text=True,
            check=True,
            capture_output=capture,
        )
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            message = exc.stderr.strip()
        elif exc.stdout:
            message = exc.stdout.strip()
        else:
            message = f"Command failed: {' '.join(cmd)}"
        raise click.ClickException(message) from exc


def require_executable(name: str) -> None:
    if shutil.which(name) is None:
        raise click.ClickException(f"Missing required executable: {name}")


def require_docker_compose() -> None:
    require_executable("docker")
    run(["docker", "compose", "version"], capture=True)


def chmod_0600(path: Path) -> None:
    path.chmod(0o600)


def read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        raise click.ClickException(f"Missing env file: {path}")

    data: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def directory_is_empty(path: Path) -> bool:
    return not path.exists() or not any(path.iterdir())


# -----------------------------------------------------------------------------
# SQLite state
# -----------------------------------------------------------------------------


def db(ctx: Ctx) -> sqlite3.Connection:
    conn = sqlite3.connect(ctx.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)


def init_db(ctx: Ctx) -> None:
    ctx.base_dir.mkdir(parents=True, exist_ok=True)

    with db(ctx) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS images (
              image_tag TEXT PRIMARY KEY,
              app TEXT NOT NULL,
              version TEXT NOT NULL,
              repo TEXT NOT NULL,
              apps_file TEXT NOT NULL,
              frappe_branch TEXT NOT NULL,
              frappe_path TEXT NOT NULL,
              builder TEXT NOT NULL,
              platform TEXT,
              pushed INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS benches (
              name TEXT PRIMARY KEY,
              path TEXT NOT NULL,
              image TEXT NOT NULL,
              tag TEXT NOT NULL,
              default_site TEXT NOT NULL,
              apps_json TEXT NOT NULL DEFAULT '[]',
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sites (
              name TEXT PRIMARY KEY,
              bench TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY (bench) REFERENCES benches(name) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_sites_bench
              ON sites (bench);

            CREATE TABLE IF NOT EXISTS domains (
              domain TEXT PRIMARY KEY,
              bench TEXT NOT NULL,
              site TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY (bench) REFERENCES benches(name) ON DELETE CASCADE,
              FOREIGN KEY (site) REFERENCES sites(name) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_domains_bench
              ON domains (bench);

            CREATE INDEX IF NOT EXISTS idx_domains_site
              ON domains (site);
            """
        )

        if not column_exists(conn, "benches", "apps_json"):
            conn.execute("ALTER TABLE benches ADD COLUMN apps_json TEXT NOT NULL DEFAULT '[]'")


def set_setting(ctx: Ctx, key: str, value: str) -> None:
    ts = now()

    with db(ctx) as conn:
        conn.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
              value = excluded.value,
              updated_at = excluded.updated_at
            """,
            (key, value, ts),
        )


def get_bench(ctx: Ctx, bench: str) -> sqlite3.Row | None:
    bench_name = normalize_short_name(bench, "bench")

    with db(ctx) as conn:
        return conn.execute(
            "SELECT * FROM benches WHERE name = ?",
            (bench_name,),
        ).fetchone()


def require_bench(ctx: Ctx, bench: str) -> sqlite3.Row:
    bench_name = normalize_short_name(bench, "bench")
    row = get_bench(ctx, bench_name)

    if not row:
        raise click.ClickException(f"Bench not found: {bench_name}")

    return row


def get_site(ctx: Ctx, site: str) -> sqlite3.Row | None:
    with db(ctx) as conn:
        return conn.execute(
            "SELECT * FROM sites WHERE name = ?",
            (site,),
        ).fetchone()


def get_site_for_bench(ctx: Ctx, bench: str, site: str) -> sqlite3.Row | None:
    bench_name = normalize_short_name(bench, "bench")

    with db(ctx) as conn:
        return conn.execute(
            "SELECT * FROM sites WHERE bench = ? AND name = ?",
            (bench_name, site),
        ).fetchone()


def require_site_for_bench(ctx: Ctx, bench: str, site: str) -> sqlite3.Row:
    bench_name = normalize_short_name(bench, "bench")
    row = get_site_for_bench(ctx, bench_name, site)

    if not row:
        raise click.ClickException(f"Site not found for bench {bench_name}: {site}")

    return row


def get_image(ctx: Ctx, image: str, tag: str) -> sqlite3.Row | None:
    image_tag = f"{image}:{tag}"

    with db(ctx) as conn:
        return conn.execute(
            "SELECT * FROM images WHERE image_tag = ?",
            (image_tag,),
        ).fetchone()


def bench_apps(ctx: Ctx, bench: str) -> list[str]:
    row = require_bench(ctx, bench)

    try:
        data = json.loads(str(row["apps_json"]))
    except json.JSONDecodeError:
        return []

    return [str(item) for item in data if str(item).strip()]


def upsert_bench(
    ctx: Ctx,
    *,
    name: str,
    path: Path,
    image: str,
    tag: str,
    default_site: str,
    apps: list[str],
    status: str,
) -> None:
    ts = now()

    with db(ctx) as conn:
        conn.execute(
            """
            INSERT INTO benches (
              name, path, image, tag, default_site, apps_json, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
              path = excluded.path,
              image = excluded.image,
              tag = excluded.tag,
              default_site = excluded.default_site,
              apps_json = excluded.apps_json,
              status = excluded.status,
              updated_at = excluded.updated_at
            """,
            (
                name,
                str(path),
                image,
                tag,
                default_site,
                json.dumps(apps),
                status,
                ts,
                ts,
            ),
        )


def update_bench_status(ctx: Ctx, bench: str, status: str) -> None:
    bench_name = normalize_short_name(bench, "bench")

    with db(ctx) as conn:
        conn.execute(
            "UPDATE benches SET status = ?, updated_at = ? WHERE name = ?",
            (status, now(), bench_name),
        )


def upsert_site(ctx: Ctx, *, bench: str, site: str, status: str) -> None:
    bench_name = normalize_short_name(bench, "bench")
    ts = now()

    with db(ctx) as conn:
        conn.execute(
            """
            INSERT INTO sites (name, bench, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
              bench = excluded.bench,
              status = excluded.status,
              updated_at = excluded.updated_at
            """,
            (site, bench_name, status, ts, ts),
        )


def upsert_domain(ctx: Ctx, *, bench: str, site: str, domain: str, status: str) -> None:
    bench_name = normalize_short_name(bench, "bench")
    ts = now()

    with db(ctx) as conn:
        conn.execute(
            """
            INSERT INTO domains (domain, bench, site, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(domain) DO UPDATE SET
              bench = excluded.bench,
              site = excluded.site,
              status = excluded.status,
              updated_at = excluded.updated_at
            """,
            (domain, bench_name, site, status, ts, ts),
        )


def upsert_image(
    ctx: Ctx,
    *,
    image_tag: str,
    app: str,
    version: str,
    repo: str,
    apps_file: Path,
    frappe_branch: str,
    frappe_path: str,
    builder: str,
    platform: str | None,
    pushed: bool,
) -> None:
    ts = now()

    with db(ctx) as conn:
        conn.execute(
            """
            INSERT INTO images (
              image_tag, app, version, repo, apps_file, frappe_branch,
              frappe_path, builder, platform, pushed, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(image_tag) DO UPDATE SET
              app = excluded.app,
              version = excluded.version,
              repo = excluded.repo,
              apps_file = excluded.apps_file,
              frappe_branch = excluded.frappe_branch,
              frappe_path = excluded.frappe_path,
              builder = excluded.builder,
              platform = excluded.platform,
              pushed = excluded.pushed,
              updated_at = excluded.updated_at
            """,
            (
                image_tag,
                app,
                version,
                repo,
                str(apps_file),
                frappe_branch,
                frappe_path,
                builder,
                platform,
                int(pushed),
                ts,
                ts,
            ),
        )


# -----------------------------------------------------------------------------
# Paths and domain resolution
# -----------------------------------------------------------------------------


def bench_path(ctx: Ctx, bench: str) -> Path:
    return ctx.base_dir / "benches" / normalize_short_name(bench, "bench")


def proxy_path(ctx: Ctx) -> Path:
    return ctx.base_dir / "proxy"


def env_path(ctx: Ctx, bench: str) -> Path:
    return bench_path(ctx, bench) / ".env"


def override_path(ctx: Ctx, bench: str) -> Path:
    return bench_path(ctx, bench) / "flori.override.yml"


def compose_path(ctx: Ctx, bench: str) -> Path:
    return bench_path(ctx, bench) / "compose.yml"


def proxy_compose_path(ctx: Ctx) -> Path:
    return proxy_path(ctx) / "compose.yml"


def host_rule(domains: list[str]) -> str:
    return " || ".join(f"Host(`{domain}`)" for domain in domains)


def internal_site_url(ctx: Ctx, name: str) -> str:
    short = normalize_short_name(name, "site")
    return f"{short}.{ctx.internal_domain_root}"


def external_domain_url(ctx: Ctx, name: str) -> str:
    short = normalize_short_name(name, "domain")
    return f"{short}.{ctx.external_domain_root}"


def resolve_internal_site_name(ctx: Ctx, site: str) -> str:
    if "." in site.strip():
        return normalize_domain(site, "site")

    return internal_site_url(ctx, site)


def resolve_external_domain_name(ctx: Ctx, domain: str) -> str:
    if "." in domain.strip():
        return normalize_domain(domain, "domain")

    return external_domain_url(ctx, domain)


def resolve_default_site_name(ctx: Ctx, bench: str) -> str:
    bench_name = normalize_short_name(bench, "bench")
    row = get_bench(ctx, bench_name)

    if row:
        return str(row["default_site"])

    return internal_site_url(ctx, bench_name)


# -----------------------------------------------------------------------------
# Compose / Traefik helpers
# -----------------------------------------------------------------------------


def compose_cmd(ctx: Ctx, bench: str) -> list[str]:
    bench_name = normalize_short_name(bench, "bench")
    return [
        "docker",
        "compose",
        "--project-directory",
        str(bench_path(ctx, bench_name)),
        "-f",
        str(compose_path(ctx, bench_name)),
    ]


def official_compose_files(ctx: Ctx) -> list[Path]:
    fd = ctx.frappe_docker_path

    files = [
        fd / "compose.yaml",
        fd / "overrides" / "compose.mariadb.yaml",
        fd / "overrides" / "compose.redis.yaml",
    ]

    for file in files:
        if not file.exists():
            raise click.ClickException(f"Missing frappe_docker file: {file}")

    return files


def route_domains(ctx: Ctx, bench: str) -> list[str]:
    bench_name = normalize_short_name(bench, "bench")

    with db(ctx) as conn:
        rows = conn.execute(
            "SELECT domain FROM domains WHERE bench = ? ORDER BY domain",
            (bench_name,),
        ).fetchall()

    return [str(row["domain"]) for row in rows]


def write_bench_override(ctx: Ctx, bench: str) -> None:
    bench_name = normalize_short_name(bench, "bench")
    domains = route_domains(ctx, bench_name)

    override_path(ctx, bench_name).write_text(
        render(
            "bench.override.yml.j2",
            bench_name=bench_name,
            router_name=bench_name,
            domains_rule=host_rule(domains),
        )
    )


def write_compose(ctx: Ctx, bench: str) -> None:
    bench_name = normalize_short_name(bench, "bench")

    cmd = [
        "docker",
        "compose",
        "--project-directory",
        str(bench_path(ctx, bench_name)),
        "--env-file",
        str(env_path(ctx, bench_name)),
    ]

    for file in official_compose_files(ctx):
        cmd.extend(["-f", str(file)])

    cmd.extend(["-f", str(override_path(ctx, bench_name)), "config"])

    result = run(cmd, capture=True)
    compose_path(ctx, bench_name).write_text(result.stdout)


def refresh_bench_compose(ctx: Ctx, bench: str) -> None:
    write_bench_override(ctx, bench)
    write_compose(ctx, bench)


def ensure_public_network() -> None:
    inspected = subprocess.run(
        ["docker", "network", "inspect", PUBLIC_NETWORK],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    if inspected.returncode != 0:
        run(["docker", "network", "create", PUBLIC_NETWORK])


def ensure_frappe_docker(
    ctx: Ctx,
    *,
    repo_url: str,
    ref: str,
    force: bool,
) -> None:
    require_executable("git")

    target = ctx.frappe_docker_path
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not directory_is_empty(target):
        if force:
            shutil.rmtree(target)
        elif (target / ".git").exists():
            run(["git", "fetch", "--tags", "origin"], cwd=target)
            run(["git", "checkout", ref], cwd=target)
            run(["git", "submodule", "update", "--init", "--recursive"], cwd=target)
            return
        else:
            raise click.ClickException(f"Directory exists and is not a git repo: {target}")

    run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            ref,
            repo_url,
            str(target),
        ]
    )

    run(["git", "submodule", "update", "--init", "--recursive"], cwd=target)


def infer_apps_from_image(ctx: Ctx, image: str, tag: str) -> list[str]:
    row = get_image(ctx, image, tag)

    if row:
        return [str(row["app"])]

    if image == "frappe/erpnext" or image.endswith("/erpnext"):
        return ["erpnext"]

    match = re.match(r"^([a-z0-9][a-z0-9-]*)-v?\d", tag)
    if match:
        return [match.group(1)]

    return []


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Flori: single-node Frappe deployment manager."""


@cli.command("init")
@runtime_options
@click.option("--email", required=True, help="Let's Encrypt account email.")
@click.option("--cf-dns-api-token", required=True, help="Cloudflare DNS API token.")
@click.option("--cf-zone-api-token", default="", help="Optional Cloudflare Zone API token.")
@click.option("--http-port", default=80, type=int, show_default=True)
@click.option("--https-port", default=443, type=int, show_default=True)
@click.option("--frappe-docker-url", default=DEFAULT_FRAPPE_DOCKER_URL, show_default=True)
@click.option("--frappe-docker-ref", default=DEFAULT_FRAPPE_DOCKER_REF, show_default=True)
@click.option("--force", is_flag=True, help="Replace existing frappe_docker checkout.")
@click.option("--up", is_flag=True, help="Start global Traefik proxy after initialization.")
def init(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    email: str,
    cf_dns_api_token: str,
    cf_zone_api_token: str,
    http_port: int,
    https_port: int,
    frappe_docker_url: str,
    frappe_docker_ref: str,
    force: bool,
    up: bool,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    require_docker_compose()

    ctx.base_dir.mkdir(parents=True, exist_ok=True)
    (ctx.base_dir / "benches").mkdir(exist_ok=True)
    (ctx.base_dir / "vendor").mkdir(exist_ok=True)

    ensure_frappe_docker(
        ctx,
        repo_url=frappe_docker_url,
        ref=frappe_docker_ref,
        force=force,
    )

    ensure_public_network()

    target = proxy_path(ctx)
    target.mkdir(parents=True, exist_ok=True)
    (target / "letsencrypt").mkdir(exist_ok=True)

    env_file = target / ".env"
    env_file.write_text(
        f"LETSENCRYPT_EMAIL={email}\n"
        f"CF_DNS_API_TOKEN={cf_dns_api_token}\n"
        f"CF_ZONE_API_TOKEN={cf_zone_api_token}\n"
        f"HTTP_PORT={http_port}\n"
        f"HTTPS_PORT={https_port}\n"
    )
    chmod_0600(env_file)

    proxy_compose_path(ctx).write_text(render("proxy.compose.yml.j2"))

    set_setting(ctx, "letsencrypt_email", email)
    set_setting(ctx, "http_port", str(http_port))
    set_setting(ctx, "https_port", str(https_port))
    set_setting(ctx, "public_network", PUBLIC_NETWORK)
    set_setting(ctx, "internal_domain_root", ctx.internal_domain_root)
    set_setting(ctx, "external_domain_root", ctx.external_domain_root)
    set_setting(ctx, "dns_provider", "cloudflare")
    set_setting(ctx, "frappe_docker_url", frappe_docker_url)
    set_setting(ctx, "frappe_docker_ref", frappe_docker_ref)
    set_setting(ctx, "frappe_docker_path", str(ctx.frappe_docker_path))

    if up:
        run(
            [
                "docker",
                "compose",
                "--project-directory",
                str(target),
                "-f",
                str(proxy_compose_path(ctx)),
                "up",
                "-d",
            ]
        )

    click.echo(str(ctx.base_dir))


@cli.command("build-image")
@runtime_options
@click.argument("app")
@click.argument("version")
@click.option(
    "--apps",
    "apps_file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
    help="Path to apps.json.",
)
@click.option("--repo", default="flori", show_default=True)
@click.option("--frappe-branch", default="version-15", show_default=True)
@click.option("--frappe-path", default="https://github.com/frappe/frappe", show_default=True)
@click.option("--builder", type=click.Choice(["layered", "custom"]), default="layered", show_default=True)
@click.option("--platform")
@click.option("--no-cache", is_flag=True)
@click.option("--push", is_flag=True)
def build_image(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    app: str,
    version: str,
    apps_file: Path,
    repo: str,
    frappe_branch: str,
    frappe_path: str,
    builder: str,
    platform: str | None,
    no_cache: bool,
    push: bool,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    require_docker_compose()

    app_name = normalize_app_name(app)
    repo_name = repo.strip()
    if not repo_name:
        raise click.ClickException("repo cannot be empty")

    fd = ctx.frappe_docker_path
    containerfile = fd / "images" / builder / "Containerfile"

    if not containerfile.exists():
        raise click.ClickException(f"Missing Containerfile: {containerfile}")

    try:
        data = json.loads(apps_file.read_text())
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid apps json: {exc}") from exc

    if not isinstance(data, list):
        raise click.ClickException("apps file must be a JSON array")

    normalized_version = version if version.startswith("v") else f"v{version}"
    image_tag = f"{repo_name}:{app_name}-{normalized_version}"

    cmd = [
        "docker",
        "build",
        "--build-arg",
        f"FRAPPE_PATH={frappe_path}",
        "--build-arg",
        f"FRAPPE_BRANCH={frappe_branch}",
        "--secret",
        f"id=apps_json,src={apps_file.resolve()}",
        "-t",
        image_tag,
        "-f",
        str(containerfile),
    ]

    if platform:
        cmd.extend(["--platform", platform])

    if no_cache:
        cmd.append("--no-cache")

    cmd.append(".")

    run(cmd, cwd=fd)

    if push:
        run(["docker", "push", image_tag])

    upsert_image(
        ctx,
        image_tag=image_tag,
        app=app_name,
        version=normalized_version,
        repo=repo_name,
        apps_file=apps_file.resolve(),
        frappe_branch=frappe_branch,
        frappe_path=frappe_path,
        builder=builder,
        platform=platform,
        pushed=push,
    )

    click.echo(image_tag)


@cli.command("bench-create")
@runtime_options
@click.option("-b", "--bench", required=True, help="Bench name.")
@click.option("--image", default="frappe/erpnext", show_default=True)
@click.option("--tag", default="version-15", show_default=True)
@click.option("--default-site")
@click.option("--app", "apps", multiple=True)
@click.option("--up", is_flag=True)
@click.option("--force", is_flag=True)
def bench_create(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str,
    image: str,
    tag: str,
    default_site: str | None,
    apps: tuple[str, ...],
    up: bool,
    force: bool,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    require_docker_compose()
    ensure_public_network()

    bench_name = normalize_short_name(bench, "bench")
    default_site_name = (
        resolve_internal_site_name(ctx, default_site)
        if default_site
        else internal_site_url(ctx, bench_name)
    )
    default_apps = (
        [normalize_app_name(app) for app in apps]
        if apps
        else infer_apps_from_image(ctx, image, tag)
    )

    target = bench_path(ctx, bench_name)
    target.mkdir(parents=True, exist_ok=True)
    (target / "sites").mkdir(exist_ok=True)
    (target / "logs").mkdir(exist_ok=True)

    files = [
        env_path(ctx, bench_name),
        override_path(ctx, bench_name),
        compose_path(ctx, bench_name),
    ]

    if not force:
        existing = [file for file in files if file.exists()]
        if existing:
            raise click.ClickException(f"File exists: {existing[0]}")

    env_file = env_path(ctx, bench_name)
    env_file.write_text(
        render(
            "bench.env.j2",
            image=image,
            tag=tag,
            db_password=secrets.token_urlsafe(32),
            site_name=default_site_name,
            apps_csv=",".join(default_apps),
        )
    )
    chmod_0600(env_file)

    upsert_bench(
        ctx,
        name=bench_name,
        path=target,
        image=image,
        tag=tag,
        default_site=default_site_name,
        apps=default_apps,
        status="created",
    )

    refresh_bench_compose(ctx, bench_name)

    if up:
        run(compose_cmd(ctx, bench_name) + ["up", "-d"])
        update_bench_status(ctx, bench_name, "running")

    click.echo(str(compose_path(ctx, bench_name)))


@cli.command("bench-up")
@runtime_options
@click.option("-b", "--bench", required=True, help="Bench name.")
def bench_up(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    bench_name = normalize_short_name(bench, "bench")
    require_bench(ctx, bench_name)
    require_docker_compose()
    run(compose_cmd(ctx, bench_name) + ["up", "-d"])
    update_bench_status(ctx, bench_name, "running")
    click.echo(bench_name)


@cli.command("bench-down")
@runtime_options
@click.option("-b", "--bench", required=True, help="Bench name.")
def bench_down(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    bench_name = normalize_short_name(bench, "bench")
    require_bench(ctx, bench_name)
    require_docker_compose()
    run(compose_cmd(ctx, bench_name) + ["down"])
    update_bench_status(ctx, bench_name, "stopped")
    click.echo(bench_name)


@cli.command("bench-logs")
@runtime_options
@click.option("-b", "--bench", required=True, help="Bench name.")
@click.option("--service")
@click.option("--follow", "-f", is_flag=True)
def bench_logs(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str,
    service: str | None,
    follow: bool,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    bench_name = normalize_short_name(bench, "bench")
    require_bench(ctx, bench_name)
    require_docker_compose()

    cmd = compose_cmd(ctx, bench_name) + ["logs"]

    if follow:
        cmd.append("-f")

    if service:
        cmd.append(service)

    run(cmd)


@cli.command("site-create")
@runtime_options
@click.option("-b", "--bench", required=True, help="Bench name.")
@click.option("-s", "--site", help="Short site name or full internal site domain.")
@click.option("--admin-password", required=True)
@click.option("--app", "apps", multiple=True)
@click.option("--migrate/--no-migrate", default=True, show_default=True)
def site_create(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str,
    site: str | None,
    admin_password: str,
    apps: tuple[str, ...],
    migrate: bool,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    bench_name = normalize_short_name(bench, "bench")
    bench_row = require_bench(ctx, bench_name)

    env = read_env_file(env_path(ctx, bench_name))
    db_password = env.get("DB_PASSWORD")

    if not db_password:
        raise click.ClickException("Missing DB_PASSWORD")

    internal_site = (
        resolve_internal_site_name(ctx, site)
        if site
        else str(bench_row["default_site"])
    )
    install_apps = (
        [normalize_app_name(app) for app in apps]
        if apps
        else bench_apps(ctx, bench_name)
    )

    require_docker_compose()

    cmd = compose_cmd(ctx, bench_name) + [
        "exec",
        "-T",
        "backend",
        "bench",
        "new-site",
        internal_site,
        "--no-mariadb-socket",
        "--mariadb-root-password",
        db_password,
        "--admin-password",
        admin_password,
    ]

    for app in install_apps:
        cmd.extend(["--install-app", app])

    run(cmd)

    if migrate:
        run(
            compose_cmd(ctx, bench_name)
            + ["exec", "-T", "backend", "bench", "--site", internal_site, "migrate"]
        )

    upsert_site(ctx, bench=bench_name, site=internal_site, status="active")
    click.echo(internal_site)


@cli.command("domain-create")
@runtime_options
@click.option("-b", "--bench", required=True, help="Bench name.")
@click.option("-s", "--site", required=True, help="Short site name or full internal site domain.")
@click.option("-d", "--domain", required=True, help="Short domain name or full external domain.")
def domain_create(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str,
    site: str,
    domain: str,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    bench_name = normalize_short_name(bench, "bench")
    require_bench(ctx, bench_name)

    internal_site = resolve_internal_site_name(ctx, site)
    external_domain = resolve_external_domain_name(ctx, domain)

    require_site_for_bench(ctx, bench_name, internal_site)
    require_docker_compose()

    run(
        compose_cmd(ctx, bench_name)
        + [
            "exec",
            "-T",
            "backend",
            "bench",
            "setup",
            "add-domain",
            external_domain,
            "--site",
            internal_site,
        ]
    )

    upsert_domain(
        ctx,
        bench=bench_name,
        site=internal_site,
        domain=external_domain,
        status="active",
    )

    refresh_bench_compose(ctx, bench_name)
    run(compose_cmd(ctx, bench_name) + ["up", "-d", "frontend"])

    click.echo(external_domain)


@cli.command(
    "shell",
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    },
)
@runtime_options
@click.option("-b", "--bench", required=True, help="Bench name.")
@click.option("--service", default="backend", show_default=True)
@click.option("-T", "--no-tty", is_flag=True)
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
def shell(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str,
    service: str,
    no_tty: bool,
    command: tuple[str, ...],
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    bench_name = normalize_short_name(bench, "bench")
    require_bench(ctx, bench_name)
    require_docker_compose()

    cmd = compose_cmd(ctx, bench_name) + ["exec"]

    if no_tty:
        cmd.append("-T")

    cmd.append(service)

    if command:
        cmd.extend(command)
    else:
        cmd.append("bash")

    run(cmd)


@cli.command("bench-list")
@runtime_options
def bench_list(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    with db(ctx) as conn:
        rows = conn.execute(
            "SELECT name, image, tag, default_site, apps_json, status FROM benches ORDER BY name"
        ).fetchall()

    for row in rows:
        try:
            apps = ",".join(json.loads(str(row["apps_json"])))
        except json.JSONDecodeError:
            apps = ""
        click.echo(
            f"{row['name']}\t{row['image']}:{row['tag']}\t{row['default_site']}\t{apps}\t{row['status']}"
        )


@cli.command("site-list")
@runtime_options
@click.option("-b", "--bench", help="Filter by bench.")
def site_list(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str | None,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    with db(ctx) as conn:
        if bench:
            bench_name = normalize_short_name(bench, "bench")
            rows = conn.execute(
                "SELECT name, bench, status FROM sites WHERE bench = ? ORDER BY name",
                (bench_name,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT name, bench, status FROM sites ORDER BY bench, name"
            ).fetchall()

    for row in rows:
        click.echo(f"{row['name']}\t{row['bench']}\t{row['status']}")


@cli.command("domain-list")
@runtime_options
@click.option("-b", "--bench", help="Filter by bench.")
def domain_list(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
    bench: str | None,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    with db(ctx) as conn:
        if bench:
            bench_name = normalize_short_name(bench, "bench")
            rows = conn.execute(
                "SELECT domain, site, bench, status FROM domains WHERE bench = ? ORDER BY domain",
                (bench_name,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT domain, site, bench, status FROM domains ORDER BY bench, site, domain"
            ).fetchall()

    for row in rows:
        click.echo(f"{row['domain']}\t{row['site']}\t{row['bench']}\t{row['status']}")


@cli.command("image-list")
@runtime_options
def image_list(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)

    with db(ctx) as conn:
        rows = conn.execute(
            "SELECT image_tag, apps_file, frappe_branch, pushed FROM images ORDER BY image_tag"
        ).fetchall()

    for row in rows:
        click.echo(
            f"{row['image_tag']}\t{row['frappe_branch']}\t{row['apps_file']}\tpushed={row['pushed']}"
        )


@cli.command("db-path")
@runtime_options
def db_path(
    *,
    base_dir: Path,
    frappe_docker_path: Path | None,
    internal_domain_root: str,
    external_domain_root: str,
) -> None:
    ctx = build_ctx(
        base_dir=base_dir,
        frappe_docker_path=frappe_docker_path,
        internal_domain_root=internal_domain_root,
        external_domain_root=external_domain_root,
    )
    init_db(ctx)
    click.echo(str(ctx.db_path))


if __name__ == "__main__":
    cli()

# UISL 规范

- 规范版本：v0.4.0
- 状态：Draft
- 更新时间：2026-07-10
- 兼容性：兼容 v0.3.x 的单行路径语法，新增 `content`、`trace`、`target/targets`、`platformAdapter`、`targetOverride`、`accessibility`、`motion`、`typeRegistry`、Dashboard / Chart 类型族；强化目标框架原生组件和推荐样式语言优先原则。

## 版本说明

UISL 规范文档使用 `vMAJOR.MINOR.PATCH` 格式，例如 `v0.4.0`。

- `MAJOR`：不兼容的语法变化。
- `MINOR`：新增能力、字段、type 或推荐写法。
- `PATCH`：修正文档、补充示例、修复描述问题。

`.uisl` 文件内部默认不维护规范版本号。页面、布局、组件和主题版本通过目录、Git 分支、Git tag 或规范文档版本管理。

推荐目录：

```text
ui/v1.uisl/            # UI 源描述版本
ui/v1.web.nextjs/      # 基于 v1.uisl 生成或维护的 Next.js 实现
ui/v1.web.vue/         # 基于 v1.uisl 生成或维护的 Vue 实现
ui/v1.mobile.flutter/  # 基于 v1.uisl 生成或维护的 Flutter 实现
```

如项目同时存在多版规范，可在文档或生成配置中声明：

```text
uisl.version: v0.4.0
```

不建议在每个页面文件中重复声明版本，除非需要跨规范版本共存。

---

## 0. v0.4.0 主要变化

相对 v0.3.0，v0.4.0 重点解决从概念稿到目标产物的可追踪、可复用、可校验和可跨平台问题。

新增内容：

```text
content          # 静态文案、演示数据、默认展示内容
trace            # 生成追踪，支持目标产物 data-uisl 反查 UISL 路径
target / targets  # 单目标或多目标平台输出策略，例如 Next.js、Vue、Flutter、单文件 HTML
accessibility    # 可访问性语义，例如 aria-label、alt、role、lang
motion           # 轻量动效和交互反馈，例如 hover、press、toast 动效
typeRegistry     # 内置 type 与自定义 type 扩展机制
chart            # 图表结构、图表语义、series 数据、pathHint
componentPolicy  # 目标框架组件优先级，例如 framework-native-first / ui-library-first
stylePolicy      # 目标框架推荐样式语言优先级，例如 tailwind / less / material-theme
```

新增推荐 type：

```text
MobileDashboardPage, DashboardPage, TopAppBar, BottomNav, NavItem,
MetricGrid, MetricCard, ResponsiveGrid, ChartCard, AreaChartCard,
AreaChart, LineChart, Sparkline, AlertList, AlertItem, IconButton,
DropdownButton, Avatar, Text
```

v0.4.0 的核心目标：

```text
概念稿可追踪
Token 可复用
组件类型可扩展
图表数据可跨平台
目标产物可反查
AI 修改可最小变更
目标框架生态优先
```

---

## 1. 定位

UISL（UI Structure Language）用于描述 UI 的结构、内容、显示语义、行为、数据绑定、状态、权限、校验、可访问性和响应式规则。

它适合作为 AI 生成多平台前端代码的中间描述：

```text
ui/idea 概念稿（HTML / 图片 / 截图 / PRD / 低保真线框图）
        ↓
      UISL
        ↓
Next.js / Vue / Flutter / 原生 HTML / 其他平台
```

UISL 主要负责：

```text
1. 页面、布局和组件结构。
2. 静态内容、文案、演示数据和默认展示值。
3. 跨平台稳定的视觉意图，例如布局、密度、字体层级、圆角、阴影和 token。
4. 行为、事件、跳转、API 调用、弹窗、toast、状态更新。
5. 数据源、字段绑定、响应映射、图表 series。
6. 运行时状态。
7. 权限、校验、可访问性和响应式。
8. 单目标或多目标代码生成策略。
9. 目标产物追踪和反查。
```

UISL 不负责完整复刻每一个 CSS 细节。复杂 CSS hack、平台私有样式、精确动画曲线、三方组件库内部 className、特殊浏览器兼容处理，仍建议放在目标平台代码中。

当项目存在 `ui/idea` 概念文件时，UISL 的样式语义、阴影、边距、布局、字体、字重、圆角、密度、动效倾向等应优先与概念文件保持一致。UISL 不强行记录所有 CSS 细节，但要把跨平台稳定的视觉意图沉淀为 `style`、`responsive`、`token`、`motion` 和 `target`。

---

## 2. 推荐项目布局

推荐在项目根目录中组织 `ui` 与 `docs`：

```text
project/
├─ ui/
│  ├─ idea/
│  │  ├─ overview.html
│  │  ├─ dashboard.html
│  │  ├─ product-list.html
│  │  ├─ dashboard.png
│  │  └─ README.md
│  ├─ v1.uisl/
│  │  ├─ pages/
│  │  │  ├─ dashboard.uisl
│  │  │  └─ product-list.uisl
│  │  ├─ layouts/
│  │  │  └─ admin-layout.uisl
│  │  ├─ design/
│  │  │  └─ light-token.uisl
│  │  ├─ components/
│  │  │  └─ pagination-card.uisl
│  │  └─ types/
│  │     └─ dashboard-types.uisl
│  ├─ v1.web.html/
│  ├─ v1.web.nextjs/
│  ├─ v1.web.vue/
│  └─ v1.mobile.flutter/
├─ docs/
│  └─ UISL-SPEC.md
├─ README.md
└─ package.json / pyproject.toml / ...
```

约定：

```text
docs/UISL-SPEC.md      存放 UISL 规范文档
ui/idea/               存放概念文件，例如概览 HTML 页面、页面草图、截图、图片参考
ui/v1.uisl/            存放 UISL 源文件
ui/v1.uisl/pages/      存放页面 UISL
ui/v1.uisl/layouts/    存放布局 UISL
ui/v1.uisl/design/     存放 DesignToken UISL
ui/v1.uisl/components/ 存放可复用组件 UISL
ui/v1.uisl/types/      存放自定义 type registry
ui/v1.web.*            存放由 UISL 生成或维护的 Web 目标实现
ui/v1.mobile.*         存放由 UISL 生成或维护的移动端目标实现
```

`docs/` 管规范，`ui/` 管具体 UI 概念稿、UISL 描述和目标平台实现。

### 2.1 `ui/idea` 概念文件

`ui/idea` 用于保存 UISL 生成前的概念文件。它可以是概览 HTML 页面、静态页面草图、截图、设计图片、低保真线框图，或其他能表达 UI 风格和布局方向的参考材料。

推荐文件：

```text
ui/idea/overview.html        # 全局概览或设计方向
ui/idea/dashboard.html       # Dashboard 概念 HTML
ui/idea/product-list.html    # 某个页面的概念 HTML
ui/idea/dashboard.png        # 图片参考或截图
ui/idea/README.md            # 概念说明、风格关键词、适用范围
```

推荐约定：

```text
1. UISL 可以由 ui/idea 中的概念文件生成。
2. 当概念文件与默认 token 冲突时，优先参考概念文件。
3. 样式、阴影、边距、布局、字体、字号、字重、圆角、密度等视觉语义，应尽量与概念文件一致。
4. UISL 只沉淀跨平台稳定的视觉意图，不强行记录每一个 CSS 细节。
5. 如果概念文件只是参考方向，而非最终视觉稿，可以在 ui/idea/README.md 中说明。
6. 如果目标产物由概念稿和 UISL 共同生成，应在 meta.source 与 trace 中记录来源。
```

### 2.2 视觉优先级

当生成或修改页面时，建议按以下优先级判断视觉实现：

```text
1. 用户明确指令
2. ui/idea 概念文件
3. UISL 中的 content / style / responsive / token / motion
4. target 输出策略
5. 目标平台已有页面代码
6. 目标组件库默认样式
```

如果用户明确要求“按照概念图 / 概览页 / 图片效果生成”，则概念文件优先级最高。

---

## 3. 基础语法

UISL 使用单行路径语法：

```text
path.to.property: value
```

示例：

```text
meta.name: pageProductList
meta.title: 产品管理
meta.type: Page

structure.page.type: AdminCrudPage
style.tableProduct.columns["status"].label: 状态
data.tableProduct.sources["getProductList"].method: GET
```

每一行只描述一个属性，方便 Git diff 和 AI 最小修改。

### 3.1 值类型

UISL 是文本格式，但推荐按以下逻辑解释值：

```text
字符串：默认按原文处理，例如 产品管理
数字：纯数字尺寸默认按 px 处理，除非字段语义不是尺寸
布尔：true / false
空值：null
数组：简单列表用英文逗号，例如 active,disabled
对象集合：使用 ["key"] 表示
引用：使用 token.* / state.* / data.* / content.* / ../relative/path.uisl
```

示例：

```text
style.topAppBar.height: 64        # 尺寸字段，默认 64px
state.table.page: 1               # 状态字段，数字 1
style.page.width: 100%
style.card.maxHeight: calc(100vh - 240px)
validation.form.status.enum: active,disabled
```

### 3.2 注释

使用 `#`：

```text
# 产品管理页
meta.name: pageProductList

data.tableProduct.sources["getProductList"].path: /api/v1/products  # 产品列表接口
```

---

## 4. 命名规则

### 4.1 基础命名

```text
页面/组件 name：camelCase
type：PascalCase
后端字段：保持接口原名
权限码：dot.case
状态 key：camelCase
内容 key：camelCase
action key：动词或动词短语
```

统一使用 `name`，不使用 `id`。

### 4.2 页面、布局、组件实例命名

推荐使用以下模式：

```text
页面 name：page + Domain + Scene
布局 name：layout + Domain
组件实例 name：type + Domain
```

示例：

```text
meta.name: pageProductList
meta.name: pageDashboardOverview
meta.name: layoutAdmin

structure.page.slots["main"].children["toolbarProduct"].type: Toolbar
structure.page.slots["main"].children["tableProduct"].type: Table
structure.page.slots["main"].children["metricGridDashboard"].type: MetricGrid
structure.page.slots["footer"].children["bottomNavDashboard"].type: BottomNav
```

不推荐：

```text
meta.name: pageProductPage
```

因为 `page` 与 `Page` 语义重复。

### 4.3 集合 key 命名

不是所有 key 都使用 `type + Domain`。推荐规则：

```text
组件实例：tableProduct, formProduct, metricGridDashboard
columns：使用后端字段名，例如 name, status, created_at
fields：使用后端字段名，例如 name, price, status
actions：使用动作名，例如 create, submit, cancel, timeRange, viewAll
rowActions：使用动作名，例如 view, edit, delete
sources：使用接口动作名，例如 getProductList, createProduct, getDashboardMetrics
series：使用业务语义，例如 businessGrowth, revenueTrend
nav：使用目标语义，例如 navOverview, navSettings
```

---

## 5. 分层

UISL 推荐分层：

```text
meta
source
target
targets
platformAdapter
targetOverride
trace
typeRegistry
structure
content
style
motion
data
state
behavior
permission
validation
accessibility
responsive
```

其中 `source` 可写在 `meta.source.*` 下，也可独立作为 `source.*`。推荐优先使用 `meta.source.*`。

各层职责：

```text
meta           文件自身信息
source         概念稿、设计稿、PRD、截图等来源引用
target/targets 目标平台和生成策略；单目标用 target，多目标用 targets["profileName"]
platformAdapter 平台组件映射
targetOverride 目标平台局部覆写
trace          目标产物反查 UISL 路径
typeRegistry   内置和自定义组件 type 声明
structure      页面、布局和组件树
content        静态文案、演示内容、默认展示值
style          跨平台稳定视觉语义
motion         轻量动效与交互反馈
data           API、字段绑定、响应映射、图表数据源
state          运行时状态
behavior       事件和动作流水线
permission     权限
validation     校验规则
accessibility  可访问性
responsive     响应式
```

推荐边界：

```text
文案、标题、演示数值：优先 content
真实运行数据：data + state
布局、颜色、字体、圆角、阴影：style + token
hover、press、toast 动效：motion
点击、跳转、API、弹窗：behavior
aria、alt、role、lang：accessibility
目标框架、输出形态、外部资源策略：target / targets
平台组件映射：platformAdapter
少量平台差异：targetOverride
目标产物定位：trace
```

---

## 6. meta 与 source

`meta` 描述文件自身的基本信息，但默认不包含版本号。

页面示例：

```text
meta.name: pageDashboardOverview
meta.title: 数据大屏
meta.type: Page
meta.description: 移动优先的数据大屏页面，展示关键指标、业务增长趋势、实时预警和底部导航。
```

布局示例：

```text
meta.name: layoutAdmin
meta.title: 后台管理布局
meta.type: Layout
```

组件示例：

```text
meta.name: paginationCard
meta.type: Component
```

DesignToken 示例：

```text
meta.name: lightToken
meta.title: 浅色主题 Token
meta.type: DesignToken
```

来源引用示例：

```text
meta.source.ideaRef: ../../idea/dash.html
meta.source.tokenRef: ../design/light-token.uisl
meta.source.prdRef: ../../docs/dashboard-prd.md
meta.source.note: 根据移动端 Dashboard 概念 HTML 生成 UISL
```

---

## 7. target / targets 目标产物策略

`target` / `targets` 描述 UISL 生成目标平台代码时的输出策略。它不是 UI 结构的一部分，而是生成器约束。

v0.4.0 推荐把 UISL 分成两部分理解：

```text
UISL Core       # structure / content / style / data / state / behavior / responsive 等平台无关语义
Target Profile  # Next.js / Vue / Flutter / HTML 等平台相关生成策略
```

因此，概念图不应该直接绑定某一个目标平台。推荐流程是：

```text
ui/idea/dash.html 或 dashboard.png
        ↓
抽取跨平台稳定语义
        ↓
ui/v1.uisl/pages/dashboard.uisl
        ↓
按 target profile 生成不同平台代码
        ↓
ui/v1.web.nextjs / ui/v1.web.vue / ui/v1.mobile.flutter / ui/v1.web.html
```

### 7.1 单目标写法

当一个 `.uisl` 文件只服务一个当前目标时，可以继续使用 `target.*`：

```text
target.name: webNextjs
target.platform: web
target.framework: nextjs
target.language: typescript
target.ui: shadcn
target.css: tailwind
target.iconSet: lucide
target.componentMode: AppRouter
target.componentPolicy: framework-native-first
target.uiPolicy: ui-library-when-native-missing
target.stylePolicy: framework-recommended
target.traceAttribute: data-uisl
```

这种写法简单，适合小项目或一次性生成。

### 7.2 多目标写法

当同一份 UISL 需要生成多个平台时，推荐使用 `targets["profileName"]`：

```text
target.default: webNextjs

targets["webHtml"].platform: web
targets["webHtml"].framework: html
targets["webHtml"].ui: custom-css
targets["webHtml"].bundle: SingleFile
targets["webHtml"].cssMode: InlineCSS
targets["webHtml"].componentPolicy: semantic-html-first
targets["webHtml"].stylePolicy: css-variables
targets["webHtml"].iconMode: InlineSvg
targets["webHtml"].assetMode: InlineOrLocal
targets["webHtml"].externalAssets: Avoid
targets["webHtml"].traceAttribute: data-uisl

targets["webNextjs"].platform: web
targets["webNextjs"].framework: nextjs
targets["webNextjs"].language: typescript
targets["webNextjs"].ui: shadcn
targets["webNextjs"].css: tailwind
targets["webNextjs"].router: app-router
targets["webNextjs"].componentMode: ClientComponent
targets["webNextjs"].componentPolicy: framework-native-first
targets["webNextjs"].uiPolicy: shadcn-when-native-missing
targets["webNextjs"].stylePolicy: tailwind-first
targets["webNextjs"].iconSet: lucide
targets["webNextjs"].chartAdapter: recharts
targets["webNextjs"].traceAttribute: data-uisl

targets["webVue"].platform: web
targets["webVue"].framework: vue
targets["webVue"].language: typescript
targets["webVue"].ui: ant-design-vue
targets["webVue"].css: less
targets["webVue"].componentPolicy: framework-native-first
targets["webVue"].uiPolicy: ant-design-vue-when-native-missing
targets["webVue"].stylePolicy: less-and-css-vars-first
targets["webVue"].iconSet: ant-design-icons
targets["webVue"].chartAdapter: echarts
targets["webVue"].traceAttribute: data-uisl

targets["mobileFlutter"].platform: mobile
targets["mobileFlutter"].framework: flutter
targets["mobileFlutter"].language: dart
targets["mobileFlutter"].themeMode: MaterialTheme
targets["mobileFlutter"].componentPolicy: material-widgets-first
targets["mobileFlutter"].stylePolicy: material-theme-first
targets["mobileFlutter"].iconSet: material
targets["mobileFlutter"].chartAdapter: fl_chart
targets["mobileFlutter"].traceMode: comments
```

生成时通过 profile 选择目标：

```bash
uisl gen ui/v1.uisl/pages/dashboard.uisl --target webNextjs --out ui/v1.web.nextjs
uisl gen ui/v1.uisl/pages/dashboard.uisl --target webVue --out ui/v1.web.vue
uisl gen ui/v1.uisl/pages/dashboard.uisl --target mobileFlutter --out ui/v1.mobile.flutter
uisl gen ui/v1.uisl/pages/dashboard.uisl --target webHtml --out ui/v1.web.html
```

### 7.3 推荐目标 profile 命名

```text
webHtml
webNextjs
webVue
webReact
webNuxt
mobileFlutter
mobileReactNative
desktopElectron
miniProgramWechat
```

命名建议使用 `platform + framework`，不要把 UI 组件库写进 profile 名称。组件库应写在 `targets[...].ui` 中。

### 7.4 平台适配层 platformAdapter

同一个 UISL type 在不同平台可能映射到不同组件。推荐使用 `platformAdapter` 或 target 内部映射说明。

```text
platformAdapter.types["MetricCard"].webNextjs.component: components/dashboard/MetricCard.tsx
platformAdapter.types["MetricCard"].webVue.component: components/dashboard/MetricCard.vue
platformAdapter.types["MetricCard"].mobileFlutter.widget: MetricCard

platformAdapter.types["BottomNav"].webNextjs.component: BottomNavigation
platformAdapter.types["BottomNav"].mobileFlutter.widget: NavigationBar
```

也可以在 target 中声明默认映射策略：

```text
targets["webNextjs"].componentMapping: shadcn-first
targets["webNextjs"].customComponentDir: components/uisl

targets["mobileFlutter"].componentMapping: material-first
targets["mobileFlutter"].customWidgetDir: lib/widgets/uisl
```

原则：

```text
1. structure 中的 type 保持平台无关，例如 MetricCard / AreaChart / BottomNav。
2. 平台组件库名称不要进入 structure.type。
3. shadcn Card、Ant Design Card、Flutter Card 应由 target adapter 负责映射。
4. 如果某个平台没有对应组件，生成器可以退化为自定义组件。
5. 生成特定框架页面时，优先使用该框架或声明 UI 库提供的原生组件，不优先手写低层 HTML / CSS。
```

### 7.5 框架原生组件与推荐样式语言优先

当用户要求生成特定框架页面时，UISL 生成器应优先遵循目标框架生态，而不是机械复刻概念稿中的 HTML 标签、Tailwind class、CSS 变量或 SVG 细节。

推荐在 target profile 中显式声明组件和样式优先级：

```text
targets["webNextjs"].componentPolicy: framework-native-first
targets["webNextjs"].uiPolicy: shadcn-when-native-missing
targets["webNextjs"].stylePolicy: tailwind-first

targets["webVue"].componentPolicy: framework-native-first
targets["webVue"].uiPolicy: ant-design-vue-when-native-missing
targets["webVue"].stylePolicy: less-and-css-vars-first

targets["mobileFlutter"].componentPolicy: material-widgets-first
targets["mobileFlutter"].stylePolicy: material-theme-first
```

组件选择优先级：

```text
1. 用户明确指定的框架 / UI 库组件。
2. 目标框架官方原生能力，例如 Next.js 的 Link / Image / App Router、Vue 的 component / script setup、Flutter 的 Material Widget。
3. target.ui 声明的组件库组件，例如 shadcn/ui、Ant Design Vue、Element Plus、Naive UI、Flutter Material。
4. 项目已有组件或 platformAdapter 中声明的封装组件。
5. 自定义组件封装。
6. 最后才退化为低层 div / span / 手写 CSS。
```

样式语言优先级：

```text
1. 用户明确指定的样式方案。
2. target 声明的推荐样式语言，例如 tailwind、less、scss、css-modules、material-theme、dart-theme。
3. 目标 UI 库推荐的主题机制，例如 shadcn + Tailwind CSS、Ant Design Vue + Less / CSS Variable、Flutter + ThemeData / ColorScheme。
4. UISL token 编译后的平台主题文件。
5. 平台私有少量样式补丁。
6. 最后才写大量内联 style 或逐像素 CSS。
```

示例：同一个 UISL 组件语义：

```text
structure.metricGridDashboard.children["metricRevenue"].type: MetricCard
style.metricGridDashboard.children["metricRevenue"].radius: token.radius.lg
```

生成到不同平台时应采用不同落地方式：

```text
Next.js + shadcn: 优先生成 Card / CardHeader / CardContent，并用 Tailwind class 与 CSS variable 承接 token。
Vue + Ant Design Vue: 优先生成 a-card / a-statistic 等组件，并用 Less / CSS variable 承接 token。
Flutter: 优先生成 Card / Container / ThemeData / ColorScheme，不生成 Web CSS。
HTML: 优先生成语义 HTML + CSS Variables。
```

禁止把某个平台样式直接污染 UISL Core：

```text
# 不推荐
style.metricCard.className: rounded-xl shadow-sm bg-white
style.metricCard.antClass: ant-card-small
style.metricCard.flutterWidget: Card

# 推荐
style.metricCard.radius: token.radius.lg
style.metricCard.shadow: token.shadow.xs
platformAdapter.types["MetricCard"].webNextjs.component: shadcn/Card
platformAdapter.types["MetricCard"].webVue.component: ant-design-vue/Card
platformAdapter.types["MetricCard"].mobileFlutter.widget: Card
```

### 7.6 样式 token 的多平台编译

UISL 中的 token 应是语义化的，不应直接等于 Tailwind class、CSS 变量或 Flutter Theme 字段。

推荐：

```text
token.colors.primary: #1a73e8
token.colors.surface: #ffffff
token.radius.lg: 18px
token.shadow.xs: 0 10px 24px rgba(24, 40, 72, 0.08)
```

不同 target 的编译结果可以不同：

```text
targets["webNextjs"].tokenOutput: tailwind-theme
targets["webVue"].tokenOutput: less-variables
targets["webHtml"].tokenOutput: css-variables
targets["mobileFlutter"].tokenOutput: dart-theme
```

示例映射：

```text
UISL token.colors.primary
  → Next.js: theme.extend.colors.primary / var(--primary)
  → Vue: @primary-color / CSS variable
  → Flutter: ColorScheme.primary
  → HTML: --primary
```

### 7.7 图标、图片和字体的多平台策略

概念稿中的图标、图片和字体往往是平台相关的。UISL 应保留语义，不强绑定具体资源。

```text
style.topAppBarDashboard.actions["notifications"].icon: Notifications
style.bottomNavDashboard.children["navOverview"].icon: Dashboard
style.topAppBarDashboard.children["avatarUser"].imageRole: UserAvatar
```

由 target 决定映射：

```text
targets["webNextjs"].iconSet: lucide
targets["webVue"].iconSet: ant-design-icons
targets["mobileFlutter"].iconSet: material
targets["webHtml"].iconMode: InlineSvg
```

图片建议使用资源语义：

```text
content.topAppBarDashboard.children["avatarUser"].assetRef: assets/avatar-user.svg
content.topAppBarDashboard.children["avatarUser"].alt: 专业商务头像
```

如果概念稿使用远程图片，生成器可以根据 target 决定：

```text
targets["webHtml"].externalAssets: Avoid       # 转成本地或内联占位
targets["webNextjs"].externalAssets: Allow     # 可使用 next/image 远程配置
```

### 7.8 target override 局部覆写

少量平台差异可以使用 `targetOverride`，但不建议大量使用，否则 UISL 会变成平台代码的混合体。

```text
targetOverride.webNextjs.chartBusinessGrowth.children["areaChart"].library: recharts
targetOverride.webVue.chartBusinessGrowth.children["areaChart"].library: echarts
targetOverride.mobileFlutter.chartBusinessGrowth.children["areaChart"].library: fl_chart

targetOverride.webNextjs.bottomNavDashboard.render: hidden-on-desktop-mobile-bottom-nav
targetOverride.mobileFlutter.bottomNavDashboard.render: NavigationBar
```

适合写进 `targetOverride` 的内容：

```text
组件库选择
图表库选择
平台文件路径
平台私有导入路径
SSR / CSR / hydration 策略
资源加载策略
```

不适合写进 `targetOverride` 的内容：

```text
业务字段
页面结构
组件增删
API 行为
权限和校验
跨平台稳定视觉意图
```

### 7.9 Next.js 生成建议

当目标是 Next.js 时，建议明确 App Router、组件拆分、服务端 / 客户端边界和资源策略。

```text
targets["webNextjs"].framework: nextjs
targets["webNextjs"].router: app-router
targets["webNextjs"].language: typescript
targets["webNextjs"].ui: shadcn
targets["webNextjs"].css: tailwind
targets["webNextjs"].componentMode: ClientComponent
targets["webNextjs"].componentPolicy: framework-native-first
targets["webNextjs"].uiPolicy: shadcn-when-native-missing
targets["webNextjs"].stylePolicy: tailwind-first
targets["webNextjs"].pageFile: app/dashboard/page.tsx
targets["webNextjs"].componentDir: components/dashboard
targets["webNextjs"].tokenFile: app/globals.css
targets["webNextjs"].dataMode: mock-first
targets["webNextjs"].chartAdapter: recharts
targets["webNextjs"].traceAttribute: data-uisl
```

建议生成目录：

```text
ui/v1.web.nextjs/
├─ app/
│  ├─ dashboard/
│  │  └─ page.tsx
│  └─ globals.css
├─ components/
│  └─ dashboard/
│     ├─ MetricCard.tsx
│     ├─ BusinessGrowthChart.tsx
│     └─ AlertList.tsx
└─ lib/
   └─ uisl-trace.ts
```

### 7.10 Vue 生成建议

```text
targets["webVue"].framework: vue
targets["webVue"].language: typescript
targets["webVue"].ui: ant-design-vue
targets["webVue"].css: less
targets["webVue"].componentPolicy: framework-native-first
targets["webVue"].uiPolicy: ant-design-vue-when-native-missing
targets["webVue"].stylePolicy: less-and-css-vars-first
targets["webVue"].pageFile: src/views/dashboard/index.vue
targets["webVue"].componentDir: src/components/dashboard
targets["webVue"].tokenFile: src/styles/tokens.less
targets["webVue"].chartAdapter: echarts
targets["webVue"].traceAttribute: data-uisl
```

### 7.11 Flutter 生成建议

```text
targets["mobileFlutter"].framework: flutter
targets["mobileFlutter"].language: dart
targets["mobileFlutter"].themeMode: MaterialTheme
targets["mobileFlutter"].componentPolicy: material-widgets-first
targets["mobileFlutter"].stylePolicy: material-theme-first
targets["mobileFlutter"].pageFile: lib/pages/dashboard_page.dart
targets["mobileFlutter"].widgetDir: lib/widgets/dashboard
targets["mobileFlutter"].tokenFile: lib/theme/uisl_theme.dart
targets["mobileFlutter"].chartAdapter: fl_chart
targets["mobileFlutter"].traceMode: comments
```

Flutter 没有 DOM 属性，因此 `traceAttribute` 不适用，推荐生成注释或 debug key：

```dart
// uisl: metricGridDashboard.children["metricRevenue"]
MetricCard(...)
```

或：

```dart
MetricCard(key: const ValueKey('metricGridDashboard.metricRevenue'))
```

### 7.12 生成策略建议

```text
1. 如果使用多目标生成，优先写 targets["profileName"]，不要只写单个 target.*。
2. target.default 只表示默认生成目标，不代表 UISL 只支持该目标。
3. target / targets 不能改变 UISL 的结构语义，只能影响代码生成方式。
4. 平台私有实现细节写在 target、targets、platformAdapter、targetOverride 或目标代码中，不要污染 structure。
5. 如果 target.bundle 为 SingleFile，应尽量避免远程图片、远程字体和外部 JS。
6. 如果 target.traceAttribute 存在，目标产物中的主要 DOM / 组件应输出对应追踪属性。
7. 对 Next.js、Vue、Flutter 等多目标，优先保证结构、内容、token、数据和行为一致，再处理平台特有视觉细节。
8. 生成特定框架页面时，优先使用框架官方能力、target.ui 组件库和推荐样式语言；只有缺少合适组件时才手写低层实现。
```

---

## 8. trace 生成追踪

`trace` 用于把目标产物中的元素反查回 UISL 路径，方便 AI 后续做最小修改。

推荐配置：

```text
trace.enabled: true
trace.attribute: data-uisl
trace.pathFormat: componentPath
trace.includeChildren: true
trace.includeActions: true
```

目标 HTML 示例：

```html
<section data-uisl="metricGridDashboard">
  <article data-uisl='metricGridDashboard.children["metricRevenue"]'>...</article>
</section>
```

UISL 对应结构：

```text
structure.page.slots["main"].children["metricGridDashboard"].type: MetricGrid
structure.metricGridDashboard.children["metricRevenue"].type: MetricCard
```

推荐追踪规则：

```text
1. 页面级、区块级、重要组件、可交互元素都应输出 trace。
2. trace 路径应尽量稳定，避免依赖数组下标。
3. 使用 children["key"] / actions["key"] / columns["key"] / fields["key"] 表达集合成员。
4. 对纯装饰元素可省略 trace。
5. 目标产物更新后，trace 路径必须仍能在 UISL 中找到。
```

反向修改示例：

```text
用户：把第一个指标卡的圆角调小。
AI 定位：data-uisl='metricGridDashboard.children["metricRevenue"]'
优先修改：style.metricGridDashboard.children["metricRevenue"].radius
```

---

## 9. structure

`structure` 只描述页面、布局和组件结构。

页面示例：

```text
structure.page.type: AdminCrudPage
structure.page.layoutRef: ../layouts/admin-layout.uisl

structure.page.slots["main"].children["toolbarProduct"].type: Toolbar
structure.page.slots["main"].children["filterProduct"].type: FilterForm
structure.page.slots["main"].children["tableProduct"].type: Table
structure.page.slots["main"].children["paginationProduct"].type: PaginationCard
structure.page.slots["main"].children["modalProduct"].type: Modal
structure.page.slots["main"].children["formProduct"].type: Form
```

Dashboard 示例：

```text
structure.page.type: MobileDashboardPage
structure.page.slots["header"].children["topAppBarDashboard"].type: TopAppBar
structure.page.slots["main"].children["metricGridDashboard"].type: MetricGrid
structure.page.slots["main"].children["contentGridDashboard"].type: ResponsiveGrid
structure.page.slots["footer"].children["bottomNavDashboard"].type: BottomNav
```

通用组件树使用 `children`，不使用 `items`：

```text
structure.sidebar.children["menuProduct"].type: MenuItem
structure.metricGridDashboard.children["metricRevenue"].type: MetricCard
```

有明确语义时使用专用集合：

```text
structure.tableProduct.columns["status"].type: TableColumn
structure.formProduct.fields["name"].type: Input
structure.toolbarProduct.actions["create"].type: Button
structure.tableProduct.rowActions["edit"].type: Action
structure.chartBusinessGrowth.series["businessGrowth"].type: ChartSeries
```

顺序使用 `order`：

```text
structure.page.slots["main"].children["toolbarProduct"].order: 10
structure.page.slots["main"].children["filterProduct"].order: 20
structure.page.slots["main"].children["tableProduct"].order: 30
structure.page.slots["main"].children["paginationProduct"].order: 40
```

---

## 10. content

`content` 用于描述静态文案、演示内容、默认展示值和可被替换的数据占位。

它解决以下问题：

```text
1. 避免把文案写进 style。
2. 避免把演示数据误认为真实 state。
3. 让静态页面、概念稿还原、真实数据绑定之间可以平滑迁移。
```

### 10.1 页面文案

```text
content.page.title: 数据大屏
content.page.subtitle: 业务运行概览
```

### 10.2 指标卡内容

```text
content.metricGridDashboard.children["metricRevenue"].label: 今日营收
content.metricGridDashboard.children["metricRevenue"].displayValue: ¥42,850
content.metricGridDashboard.children["metricRevenue"].trendLabel: +12%
content.metricGridDashboard.children["metricRevenue"].trendDirection: Up

content.metricGridDashboard.children["metricConversionRate"].label: 转化率
content.metricGridDashboard.children["metricConversionRate"].displayValue: 3.42%
content.metricGridDashboard.children["metricConversionRate"].trendLabel: -2%
content.metricGridDashboard.children["metricConversionRate"].trendDirection: Down
```

### 10.3 图表默认内容

```text
content.chartBusinessGrowth.title: 业务增长趋势
content.chartBusinessGrowth.subtitle: 最近7天
content.chartBusinessGrowth.actions["timeRange"].label: 最近7天
content.chartBusinessGrowth.children["areaChart"].xAxisLabels: 周一,周二,周三,周四,周五,周六,周日
```

### 10.4 预警列表内容

```text
content.alertListRealtime.title: 实时预警
content.alertListRealtime.actions["viewAll"].label: 查看全部
content.alertListRealtime.children["alertStock"].title: 库存预警: 核心组件
content.alertListRealtime.children["alertStock"].description: SKU-2930 当前库存低于安全水平 (15/100)。
content.alertListRealtime.children["alertStock"].time: 10:24
```

### 10.5 content 与 data / state 的关系

推荐规则：

```text
静态展示：content 即可
演示页面：content + state.mock
真实接口：data.sources + state
接口失败占位：content.empty / content.error
```

示例：

```text
content.tableProduct.emptyText: 暂无数据
content.tableProduct.errorText: 数据加载失败
content.tableProduct.loadingText: 加载中
```

---

## 11. style

`style` 描述组件的显示语义和基础视觉意图，不等同于完整 CSS。

UISL 可以描述对多端生成有稳定价值的视觉语义，例如布局方向、尺寸策略、圆角等级、轻微阴影、字体层级、密度、留白和基础色彩 token。

如果 UISL 是根据 `ui/idea` 概念文件生成的，`style` 应优先表达概念稿中的视觉方向，例如更紧凑的边距、更轻的阴影、更小的圆角、更粗的标题、更舒展的卡片布局等。

具体颜色值、复杂动画、精确阴影参数、特殊 CSS hack、平台组件库私有样式，仍建议在目标平台代码中处理。

```text
style.<componentName>.<property>: value
style.<componentName>.<collection>["key"].<property>: value
```

### 11.1 页面与工具栏

```text
style.page.padding: token.spacing.lg
style.page.background: token.colors.pageBackground
style.page.minHeight: 100vh
style.page.maxWidth: 100%

style.toolbarProduct.layout: Horizontal
style.toolbarProduct.align: Right
style.toolbarProduct.height: 48
style.toolbarProduct.gap: token.spacing.sm
style.toolbarProduct.actions["create"].variant: Primary
style.toolbarProduct.actions["create"].icon: Plus
```

### 11.2 尺寸与空间

推荐使用语义化尺寸，必要时允许使用 `px`、`%`、`vw`、`vh`、`calc(...)` 等值。

```text
style.<component>.width: 100%
style.<component>.height: Auto
style.<component>.minHeight: 320
style.<component>.maxHeight: calc(100vh - 240px)
style.<component>.padding: token.spacing.md
style.<component>.gap: token.spacing.sm
style.<component>.overflow: Auto
```

纯数字尺寸默认按 `px` 处理：

```text
style.topAppBarDashboard.height: 64    # 64px
style.avatarUser.size: 40              # 40px
```

推荐尺寸策略枚举：

```text
Auto,Fill,Hug,Fixed,FullWidth,FullHeight,ViewportHeight,Content,Scroll
```

### 11.3 圆角

推荐 token：

```text
token.radius.xs      # 极小圆角，例如 2px
token.radius.sm      # 小圆角，例如 4px 或 8px
token.radius.smMd    # 中等偏小圆角，例如 6px
token.radius.md      # 中等圆角，例如 8px 或 12px
token.radius.lg      # 大圆角，例如 12px 或 18px
token.radius.full    # 胶囊或圆形
```

后台管理类页面默认：

```text
style.default.radius: token.radius.smMd
```

移动端 Dashboard 或偏营销展示的卡片可使用更大圆角：

```text
style.metricGridDashboard.children["metricRevenue"].radius: token.radius.lg
style.bottomNavDashboard.radius: token.radius.lg
```

### 11.4 阴影与层次

推荐 token：

```text
token.shadow.none
token.shadow.xs      # 极轻微阴影，适合卡片、表单容器
token.shadow.sm      # 轻微阴影，适合弹窗、底部导航、浮层
token.shadow.md      # 中等阴影，谨慎使用
```

示例：

```text
style.card.shadow: token.shadow.xs
style.modalProduct.shadow: token.shadow.sm
style.dropdown.shadow: token.shadow.sm
style.tableProduct.shadow: token.shadow.none
style.bottomNavDashboard.shadow: token.shadow.sm
```

### 11.5 字体样式与大小

字体不建议直接绑定某个平台字体类名，而应描述文本层级、字号、字重、行高。

推荐 token：

```text
token.font.family.base
token.font.family.mono

token.font.size.xs
token.font.size.sm
token.font.size.md
token.font.size.lg
token.font.size.xl

token.font.weight.regular
token.font.weight.medium
token.font.weight.semibold
token.font.weight.bold

token.font.lineHeight.tight
token.font.lineHeight.normal
token.font.lineHeight.relaxed
```

页面字体建议：

```text
style.page.fontFamily: token.font.family.base
style.page.fontSize: token.font.size.sm
style.page.lineHeight: token.font.lineHeight.normal
style.page.titleFontSize: token.font.size.xl
style.page.titleFontWeight: token.font.weight.semibold
```

### 11.6 状态样式

组件状态样式可以写入 `style.<component>.state.<stateName>.*`。

```text
style.bottomNavDashboard.children["navOverview"].state.active.background: token.colors.primary
style.bottomNavDashboard.children["navOverview"].state.active.color: token.colors.onPrimary
style.alertListRealtime.children["alertStock"].state.hover.background: token.colors.surfaceBlue
style.button.state.disabled.opacity: 0.5
```

状态名推荐：

```text
default,hover,active,pressed,focus,disabled,selected,loading,error,success,warning
```

---

## 12. DesignToken

DesignToken 可以独立成 `.uisl` 文件，供页面、布局和组件复用。

### 12.1 token 文件示例

```text
meta.name: lightToken
meta.title: 浅色主题 Token
meta.type: DesignToken
meta.description: 浅色主题颜色、间距、圆角、阴影和字体 token。

token.colors.primary: #1a73e8
token.colors.primaryDeep: #005bbf
token.colors.primarySoft: #d8e7ff
token.colors.surface: #ffffff
token.colors.pageBackground: #f4f8fd
token.colors.border: #cbd8ea
token.colors.textPrimary: #18202b
token.colors.textSecondary: #4c5b70
token.colors.success: #07883f
token.colors.danger: #ba1a1a

token.spacing.xs: 4px
token.spacing.sm: 12px
token.spacing.md: 16px
token.spacing.lg: 24px
token.spacing.xl: 32px

token.radius.sm: 8px
token.radius.md: 12px
token.radius.lg: 18px
token.radius.full: 999px

token.shadow.none: none
token.shadow.xs: 0 10px 24px rgba(24, 40, 72, 0.08)
token.shadow.sm: 0 18px 42px rgba(24, 40, 72, 0.12)

token.font.family.base: Inter, Segoe UI, PingFang SC, Microsoft YaHei, Arial, sans-serif
token.font.size.xs: 12px
token.font.size.sm: 14px
token.font.size.md: 16px
token.font.size.lg: 20px
token.font.size.xl: 24px
token.font.weight.regular: 400
token.font.weight.medium: 600
token.font.weight.semibold: 700
token.font.weight.bold: 760
token.font.lineHeight.normal: 1.45
```

页面引用：

```text
meta.design.tokenRef: ../design/light-token.uisl
```

### 12.2 raw token 与 semantic token

对于大型项目，推荐区分原始 token 与语义 token。

```text
token.raw.colors.blue500: #1a73e8
token.raw.colors.green600: #07883f

token.semantic.colors.primary: token.raw.colors.blue500
token.semantic.colors.success: token.raw.colors.green600

token.component.card.radius: token.radius.lg
token.component.card.shadow: token.shadow.xs
```

小项目可以直接使用 `token.colors.primary` 等简化写法。

### 12.3 token 编译建议

不同目标平台可把 token 编译为：

```text
HTML / CSS：CSS variables
Tailwind：theme.extend
Next.js：CSS variables + Tailwind config
Vue：CSS variables / Less variables
Flutter：ThemeData / ColorScheme / TextTheme
```

---

## 13. motion

`motion` 描述轻量动效和交互反馈，不描述复杂动画实现细节。

示例：

```text
motion.card.press.scale: 0.98
motion.card.press.duration: 100ms
motion.button.hover.translateY: -1px
motion.button.hover.duration: 160ms
motion.toast.enter.duration: 160ms
motion.toast.visible.duration: 1400ms
motion.chart.fadeIn.delay: 300ms
motion.chart.fadeIn.duration: 1000ms
```

组件级动效：

```text
motion.metricGridDashboard.children["metricRevenue"].press.scale: 0.98
motion.bottomNavDashboard.children["navOverview"].press.scale: 0.95
motion.alertListRealtime.children["alertStock"].hover.background: token.colors.surfaceBlue
```

推荐原则：

```text
1. motion 只记录跨平台稳定的动效意图。
2. 精确 cubic-bezier、关键帧、复杂过渡优先放目标平台代码。
3. 移动端 press 反馈可写入 motion。
4. hover 样式可写 style.state.hover，也可写 motion.hover；纯视觉状态优先 style，动效变化优先 motion。
```

---

## 14. data

数据源放在组件作用域下。

`sources` key 推荐使用动作型命名，例如 `getProductList`、`createProduct`、`updateProduct`、`deleteProduct`、`getDashboardMetrics`。

### 14.1 查询列表

```text
data.tableProduct.sources["getProductList"].method: GET
data.tableProduct.sources["getProductList"].path: /api/v1/products

data.tableProduct.source: getProductList
data.tableProduct.rowKey: id
```

查询参数：

```text
data.tableProduct.sources["getProductList"].query["keyword"].from: state.filterProduct.keyword
data.tableProduct.sources["getProductList"].query["status"].from: state.filterProduct.status
data.tableProduct.sources["getProductList"].query["page"].from: state.tableProduct.pagination.currentPage
data.tableProduct.sources["getProductList"].query["page_size"].from: state.tableProduct.pagination.pageSize
```

响应映射：

```text
data.tableProduct.sources["getProductList"].response.rows.from: data.items
data.tableProduct.sources["getProductList"].response.rows.to: state.tableProduct.rows
data.tableProduct.sources["getProductList"].response.total.from: data.total
data.tableProduct.sources["getProductList"].response.total.to: state.tableProduct.total
```

字段绑定：

```text
data.tableProduct.columns["name"].field: name
data.tableProduct.columns["status"].field: status
data.tableProduct.columns["created_at"].field: created_at
```

### 14.2 创建、更新、删除

```text
data.formProduct.sources["createProduct"].method: POST
data.formProduct.sources["createProduct"].path: /api/v1/products
data.formProduct.sources["createProduct"].body.from: state.formProduct.values

data.formProduct.sources["updateProduct"].method: PUT
data.formProduct.sources["updateProduct"].path: /api/v1/products/{id}
data.formProduct.sources["updateProduct"].pathParams["id"].from: state.tableProduct.selectedRow.id
data.formProduct.sources["updateProduct"].body.from: state.formProduct.values

data.tableProduct.sources["deleteProduct"].method: DELETE
data.tableProduct.sources["deleteProduct"].path: /api/v1/products/{id}
data.tableProduct.sources["deleteProduct"].pathParams["id"].from: state.tableProduct.selectedRow.id
```

行为中调用：

```text
callApi:tableProduct.getProductList
callApi:formProduct.createProduct
callApi:formProduct.updateProduct
callApi:tableProduct.deleteProduct
```

推荐 API source 命名：

```text
GET 列表：getProductList
GET 详情：getProductDetail
POST 创建：createProduct
PUT/PATCH 更新：updateProduct
DELETE 删除：deleteProduct
POST 批量删除：batchDeleteProduct
POST 导入：importProduct
GET 导出：exportProduct
GET Dashboard 指标：getDashboardMetrics
GET 图表数据：getBusinessGrowthSeries
GET 通知列表：getAlertList
```

### 14.3 Dashboard 数据绑定

```text
data.metricGridDashboard.sources["getDashboardMetrics"].method: GET
data.metricGridDashboard.sources["getDashboardMetrics"].path: /api/v1/dashboard/metrics
data.metricGridDashboard.sources["getDashboardMetrics"].response.revenueToday.to: state.metricGridDashboard.revenueToday
data.metricGridDashboard.sources["getDashboardMetrics"].response.activeUsers.to: state.metricGridDashboard.activeUsers

data.metricGridDashboard.children["metricRevenue"].field: revenueToday
data.metricGridDashboard.children["metricActiveUsers"].field: activeUsers
```

---

## 15. chart 与 Sparkline

图表应优先描述跨平台数据和显示语义，不应只依赖 SVG path。

### 15.1 AreaChart

```text
structure.chartBusinessGrowth.children["areaChart"].type: AreaChart

content.chartBusinessGrowth.title: 业务增长趋势
content.chartBusinessGrowth.subtitle: 最近7天
content.chartBusinessGrowth.children["areaChart"].xAxisLabels: 周一,周二,周三,周四,周五,周六,周日

style.chartBusinessGrowth.children["areaChart"].render: Area
style.chartBusinessGrowth.children["areaChart"].lineColor: token.colors.primary
style.chartBusinessGrowth.children["areaChart"].fillColor: token.colors.primaryAlpha12
style.chartBusinessGrowth.children["areaChart"].showGrid: true
style.chartBusinessGrowth.children["areaChart"].curve: Smooth
style.chartBusinessGrowth.children["areaChart"].height: 226

data.chartBusinessGrowth.series["businessGrowth"].label: 业务增长
data.chartBusinessGrowth.series["businessGrowth"].x: 周一,周二,周三,周四,周五,周六,周日
data.chartBusinessGrowth.series["businessGrowth"].y: 130,110,140,90,40,70,50,30,10
```

### 15.2 Sparkline

```text
structure.metricGridDashboard.children["metricRevenue"].children["sparkline"].type: Sparkline

style.metricGridDashboard.children["metricRevenue"].children["sparkline"].render: Line
style.metricGridDashboard.children["metricRevenue"].children["sparkline"].lineColor: token.colors.primary
style.metricGridDashboard.children["metricRevenue"].children["sparkline"].height: 24

data.metricGridDashboard.children["metricRevenue"].sparkline.y: 25,5,20,10,25,15
```

### 15.3 pathHint

如果概念稿中已有 SVG path，允许作为生成提示保留，但应标明它是提示而不是唯一数据源。

```text
style.metricGridDashboard.children["metricRevenue"].sparkline.pathHint: M0,25 Q15,5 30,20 T60,10 T90,25 T100,15
style.metricGridDashboard.children["metricRevenue"].sparkline.pathHintScope: web.svg
```

推荐原则：

```text
1. 跨平台图表优先写 data.series。
2. SVG path 只作为 pathHint。
3. 生成 Web SVG 时可以使用 pathHint。
4. 生成 ECharts、Recharts、Flutter charts 时应优先使用 series 数据。
5. 图表标题、时间范围、坐标轴标签属于 content。
```

---

## 16. state

`state` 描述运行时状态。

CRUD 示例：

```text
state.tableProduct.rows: []
state.tableProduct.total: 0
state.tableProduct.selectedRow: null
state.tableProduct.pagination.currentPage: 1
state.tableProduct.pagination.pageSize: 20

state.filterProduct.keyword: ""
state.filterProduct.status: null

state.modalProduct.visible: false
state.modalProduct.mode: create
state.formProduct.values: {}
```

Dashboard 示例：

```text
state.dashboard.activeNav: overview
state.dashboard.timeRange: recent7Days

state.metricGridDashboard.revenueToday.value: 42850
state.metricGridDashboard.revenueToday.displayValue: ¥42,850
state.metricGridDashboard.revenueToday.trendPercent: 12

state.chartBusinessGrowth.series["businessGrowth"].label: 业务增长
state.chartBusinessGrowth.series["businessGrowth"].points: 130,110,140,90,40,70,50,30,10
state.chartBusinessGrowth.xAxisLabels: 周一,周二,周三,周四,周五,周六,周日
```

推荐规则：

```text
1. content 放默认展示内容，state 放运行时可变内容。
2. 如果页面只是静态 demo，可以只写 content。
3. 如果 demo 需要模拟交互，可写 state.mock.*。
4. 如果接入真实 API，data.sources 的 response 应映射到 state。
```

---

## 17. behavior

```text
behavior.<component>.<event>: action1, action2, action3
```

常用动作：

```text
setState:<statePath>=<value>
callApi:<componentName>.<sourceName>
openModal:<modalName>:<mode>
closeModal:<modalName>
reloadTable:<tableName>
toast:<message>
toastSuccess
toastError
navigate:<path>
confirmDelete:<actionName>
emit:<eventName>
```

事件变量：

```text
$event.page
$event.pageSize
$event.row
$event.value
$event.target
$event.key
```

页面加载：

```text
behavior.page.onLoad: callApi:tableProduct.getProductList
```

Dashboard 示例：

```text
behavior.topAppBarDashboard.actions["notifications"].onClick: toast:通知中心
behavior.chartBusinessGrowth.actions["timeRange"].onClick: toast:切换时间范围
behavior.alertListRealtime.actions["viewAll"].onClick: navigate:/alerts
behavior.bottomNavDashboard.children["navAnalytics"].onClick: setState:state.dashboard.activeNav=analytics, navigate:/analytics
```

点击编辑：

```text
behavior.tableProduct.rowActions["edit"].onClick: setState:state.tableProduct.selectedRow=$event.row, openModal:modalProduct:edit
```

删除：

```text
behavior.tableProduct.rowActions["delete"].onClick: setState:state.tableProduct.selectedRow=$event.row, confirmDelete:deleteProduct
behavior.tableProduct.rowActions["delete"].onConfirm: callApi:tableProduct.deleteProduct
behavior.tableProduct.sources["deleteProduct"].onSuccess: callApi:tableProduct.getProductList, toastSuccess
behavior.tableProduct.sources["deleteProduct"].onError: toastError
```

表单提交：

```text
behavior.formProduct.onSubmit.create: callApi:formProduct.createProduct
behavior.formProduct.sources["createProduct"].onSuccess: closeModal:modalProduct, setState:state.tableProduct.pagination.currentPage=1, callApi:tableProduct.getProductList, toastSuccess
behavior.formProduct.sources["createProduct"].onError: toastError

behavior.formProduct.onSubmit.edit: callApi:formProduct.updateProduct
behavior.formProduct.sources["updateProduct"].onSuccess: closeModal:modalProduct, callApi:tableProduct.getProductList, toastSuccess
behavior.formProduct.sources["updateProduct"].onError: toastError
```

---

## 18. permission

```text
permission.page.required: product.read
permission.sidebar.children["menuProduct"].required: product.read
permission.toolbarProduct.actions["create"].required: product.create
permission.tableProduct.rowActions["edit"].required: product.update
permission.tableProduct.rowActions["delete"].required: product.delete
```

Dashboard 示例：

```text
permission.page.required: dashboard.read
permission.topAppBarDashboard.actions["notifications"].required: notification.read
permission.alertListRealtime.actions["viewAll"].required: alert.read
permission.bottomNavDashboard.children["navOverview"].required: dashboard.read
permission.bottomNavDashboard.children["navAnalytics"].required: analytics.read
permission.bottomNavDashboard.children["navReports"].required: report.read
permission.bottomNavDashboard.children["navSettings"].required: settings.read
```

支持任一权限：

```text
permission.tableProduct.rowActions["delete"].required.any: product.delete,admin
```

支持全部权限：

```text
permission.tableProduct.rowActions["delete"].required.all: product.delete,product.audit
```

---

## 19. validation

```text
validation.formProduct.fields["name"].required: true
validation.formProduct.fields["name"].minLength: 2
validation.formProduct.fields["name"].maxLength: 64
validation.formProduct.fields["name"].message.required: 请输入产品名称

validation.formProduct.fields["price"].type: Number
validation.formProduct.fields["price"].min: 0

validation.formProduct.fields["status"].required: true
validation.formProduct.fields["status"].enum: active,disabled
```

校验规则应绑定到存在的字段。

---

## 20. accessibility

`accessibility` 描述可访问性语义，例如语言、ARIA、alt、role、键盘行为。

页面语言：

```text
accessibility.page.lang: zh-CN
```

区块语义：

```text
accessibility.metricGridDashboard.ariaLabel: 关键指标
accessibility.chartBusinessGrowth.ariaLabel: 业务增长趋势
accessibility.alertListRealtime.ariaLabel: 实时预警
accessibility.bottomNavDashboard.ariaLabel: 底部导航
```

图片和图标：

```text
accessibility.topAppBarDashboard.children["avatarUser"].alt: 专业商务头像
accessibility.topAppBarDashboard.actions["notifications"].ariaLabel: 通知
accessibility.chartBusinessGrowth.children["areaChart"].role: img
accessibility.chartBusinessGrowth.children["areaChart"].ariaLabel: 业务增长趋势折线面积图
accessibility.icon.ariaHidden: true
```

键盘与焦点：

```text
accessibility.bottomNavDashboard.children["navOverview"].focusable: true
accessibility.bottomNavDashboard.children["navOverview"].role: link
accessibility.button.focusRing: true
```

推荐规则：

```text
1. alt / ariaLabel 不应写在 style 中。
2. 图标如果只是装饰，应 ariaHidden: true。
3. 可点击区域应具备 role 或目标平台等价语义。
4. 图表应至少提供 ariaLabel 或文字摘要。
```

---

## 21. responsive

`responsive` 用于描述不同屏幕尺寸下的显示方式、宽度、高度、最大高度、间距、布局方向、溢出策略和组件密度。

它不要求完整复刻 CSS media query，而是描述多端生成时需要保持一致的自适应意图。

### 21.1 断点

```text
responsive.breakpoints["mobile"].maxWidth: 767
responsive.breakpoints["tablet"].minWidth: 768
responsive.breakpoints["tablet"].maxWidth: 1023
responsive.breakpoints["desktop"].minWidth: 1024
responsive.breakpoints["wide"].minWidth: 1440
```

### 21.2 推荐属性

```text
responsive.<screen>.<component>.display: Table
responsive.<screen>.<component>.layout: Horizontal
responsive.<screen>.<component>.width: 100%
responsive.<screen>.<component>.minWidth: 320
responsive.<screen>.<component>.maxWidth: 1200
responsive.<screen>.<component>.height: Auto
responsive.<screen>.<component>.minHeight: 320
responsive.<screen>.<component>.maxHeight: calc(100vh - 240px)
responsive.<screen>.<component>.padding: token.spacing.md
responsive.<screen>.<component>.gap: token.spacing.sm
responsive.<screen>.<component>.overflow: Auto
responsive.<screen>.<component>.density: Compact
responsive.<screen>.<component>.columns: 2
responsive.<screen>.<component>.columnRatio: 1.55fr 0.8fr
```

推荐属性含义：

```text
display     显示形态，例如 Table、CardList、Grid、Hidden、FixedBottom
layout      布局方向，例如 Horizontal、Vertical、Dropdown、Wrap
width       宽度
height      高度
minWidth    最小宽度
maxWidth    最大宽度
minHeight   最小高度
maxHeight   最大高度
overflow    内容溢出策略，例如 Visible、Hidden、Auto、Scroll
density     组件密度，例如 Compact、Normal、Comfortable
columns     栅格列数
columnRatio 栅格列比例
```

### 21.3 Dashboard 响应式示例

```text
responsive.mobile.page.width: 100vw
responsive.mobile.page.minHeight: 100vh
responsive.mobile.page.padding: token.spacing.md
responsive.mobile.metricGridDashboard.layout: Grid
responsive.mobile.metricGridDashboard.columns: 2
responsive.mobile.contentGridDashboard.layout: Vertical
responsive.mobile.contentGridDashboard.columns: 1
responsive.mobile.bottomNavDashboard.display: FixedBottom
responsive.mobile.bottomNavDashboard.height: 80

responsive.tablet.metricGridDashboard.columns: 4
responsive.tablet.contentGridDashboard.layout: Grid
responsive.tablet.contentGridDashboard.columns: 2

responsive.desktop.page.maxWidth: 1440
responsive.desktop.metricGridDashboard.columns: 4
responsive.desktop.contentGridDashboard.layout: Grid
responsive.desktop.contentGridDashboard.columns: 2
responsive.desktop.contentGridDashboard.columnRatio: 1.55fr 0.8fr
responsive.desktop.bottomNavDashboard.display: Hidden
```

### 21.4 自适应原则

```text
1. 桌面端优先展示完整信息，例如 Table、Horizontal Toolbar、双栏 Dashboard。
2. 平板端允许换行和收缩，例如 Wrap FilterForm、两栏卡片。
3. 移动端优先纵向布局，例如 CardList、Vertical Form、FixedBottom Nav。
4. 大面积列表组件应设置 maxHeight 与 overflow，避免页面整体失控。
5. 弹窗在移动端可接近全屏，圆角应比桌面端更小。
6. 宽高控制使用语义属性，具体 CSS 由目标平台生成。
```

---

## 22. typeRegistry

`typeRegistry` 用于声明内置 type 或自定义 type 的用途、基础结构和生成提示。

### 22.1 自定义 type 示例

```text
typeRegistry.types["MetricCard"].category: Display
typeRegistry.types["MetricCard"].description: 展示单个关键指标、趋势和迷你图。
typeRegistry.types["MetricCard"].slots["main"].required: true
typeRegistry.types["MetricCard"].supports.children: Sparkline,Text,Icon
typeRegistry.types["MetricCard"].default.radius: token.radius.lg
typeRegistry.types["MetricCard"].default.shadow: token.shadow.xs
```

### 22.2 type 扩展

```text
typeRegistry.types["AreaChartCard"].extends: ChartCard
typeRegistry.types["AreaChartCard"].supports.children: AreaChart
```

### 22.3 推荐规则

```text
1. 规范内置 type 不必每个文件重复声明。
2. 项目级自定义 type 推荐放在 ui/v1.uisl/types/。
3. AI 生成时如果需要新 type，应优先检查 typeRegistry。
4. 未声明的新 type 可以临时生成，但 validate 应给出 warning。
```

---

## 23. Type 使用示例

每个 type 推荐单独提供用途、常用位置、最小示例和扩展示例。这样 AI 生成时可以按 type 查找模板。

### 23.1 Page

用途：描述一个完整页面。

```text
meta.name: pageProductList
meta.title: 产品管理
meta.type: Page
meta.description: 产品管理列表页

structure.page.type: AdminCrudPage
structure.page.layoutRef: ../layouts/admin-layout.uisl
structure.page.slots["main"].children["toolbarProduct"].type: Toolbar
structure.page.slots["main"].children["filterProduct"].type: FilterForm
structure.page.slots["main"].children["tableProduct"].type: Table
structure.page.slots["main"].children["paginationProduct"].type: PaginationCard

behavior.page.onLoad: callApi:tableProduct.getProductList
permission.page.required: product.read
```

### 23.2 Layout

用途：描述页面公共布局。

```text
meta.name: layoutAdmin
meta.title: 后台管理布局
meta.type: Layout

structure.layout.type: AdminLayout
structure.layout.regions["sidebar"].type: Sidebar
structure.layout.regions["header"].type: Header
structure.layout.regions["main"].type: Content
```

### 23.3 MobileDashboardPage

用途：描述移动优先的数据概览页。

```text
meta.name: pageDashboardOverview
meta.title: 数据大屏
meta.type: Page

structure.page.type: MobileDashboardPage
structure.page.slots["header"].children["topAppBarDashboard"].type: TopAppBar
structure.page.slots["main"].children["metricGridDashboard"].type: MetricGrid
structure.page.slots["main"].children["contentGridDashboard"].type: ResponsiveGrid
structure.page.slots["footer"].children["bottomNavDashboard"].type: BottomNav
```

### 23.4 TopAppBar

用途：移动端或 Web App 顶部栏。

```text
structure.page.slots["header"].children["topAppBarDashboard"].type: TopAppBar
structure.topAppBarDashboard.children["avatarUser"].type: Avatar
structure.topAppBarDashboard.children["title"].type: Text
structure.topAppBarDashboard.actions["notifications"].type: IconButton

content.topAppBarDashboard.children["title"].text: 数据大屏
style.topAppBarDashboard.position: StickyTop
style.topAppBarDashboard.height: 64
style.topAppBarDashboard.layout: Horizontal
style.topAppBarDashboard.align: Between
behavior.topAppBarDashboard.actions["notifications"].onClick: toast:通知中心
accessibility.topAppBarDashboard.actions["notifications"].ariaLabel: 通知
```

### 23.5 MetricGrid

用途：展示多个关键指标卡片。

```text
structure.page.slots["main"].children["metricGridDashboard"].type: MetricGrid
structure.metricGridDashboard.children["metricRevenue"].type: MetricCard
structure.metricGridDashboard.children["metricActiveUsers"].type: MetricCard

style.metricGridDashboard.layout: Grid
style.metricGridDashboard.gap: token.spacing.md
responsive.mobile.metricGridDashboard.columns: 2
responsive.desktop.metricGridDashboard.columns: 4
```

### 23.6 MetricCard

用途：展示单个指标、趋势和迷你图。

```text
structure.metricGridDashboard.children["metricRevenue"].type: MetricCard

content.metricGridDashboard.children["metricRevenue"].label: 今日营收
content.metricGridDashboard.children["metricRevenue"].displayValue: ¥42,850
content.metricGridDashboard.children["metricRevenue"].trendLabel: +12%
content.metricGridDashboard.children["metricRevenue"].trendDirection: Up

style.metricGridDashboard.children["metricRevenue"].render: Currency
style.metricGridDashboard.children["metricRevenue"].radius: token.radius.lg
style.metricGridDashboard.children["metricRevenue"].shadow: token.shadow.xs
```

### 23.7 ResponsiveGrid

用途：根据屏幕宽度切换列数或布局。

```text
structure.page.slots["main"].children["contentGridDashboard"].type: ResponsiveGrid
structure.contentGridDashboard.children["chartBusinessGrowth"].type: AreaChartCard
structure.contentGridDashboard.children["alertListRealtime"].type: AlertList

style.contentGridDashboard.layout: Grid
responsive.mobile.contentGridDashboard.columns: 1
responsive.desktop.contentGridDashboard.columns: 2
responsive.desktop.contentGridDashboard.columnRatio: 1.55fr 0.8fr
```

### 23.8 AreaChartCard

用途：图表卡片容器。

```text
structure.contentGridDashboard.children["chartBusinessGrowth"].type: AreaChartCard
structure.chartBusinessGrowth.children["areaChart"].type: AreaChart
structure.chartBusinessGrowth.actions["timeRange"].type: DropdownButton

content.chartBusinessGrowth.title: 业务增长趋势
content.chartBusinessGrowth.subtitle: 最近7天
content.chartBusinessGrowth.actions["timeRange"].label: 最近7天
style.chartBusinessGrowth.card: true
style.chartBusinessGrowth.radius: token.radius.lg
style.chartBusinessGrowth.shadow: token.shadow.xs
```

### 23.9 AreaChart

用途：展示面积图。

```text
structure.chartBusinessGrowth.children["areaChart"].type: AreaChart
style.chartBusinessGrowth.children["areaChart"].lineColor: token.colors.primary
style.chartBusinessGrowth.children["areaChart"].fillColor: token.colors.primaryAlpha12
style.chartBusinessGrowth.children["areaChart"].showGrid: true
data.chartBusinessGrowth.series["businessGrowth"].y: 130,110,140,90,40,70,50,30,10
```

### 23.10 AlertList

用途：展示实时预警、通知或动态列表。

```text
structure.contentGridDashboard.children["alertListRealtime"].type: AlertList
structure.alertListRealtime.children["alertStock"].type: AlertItem
structure.alertListRealtime.actions["viewAll"].type: Button

content.alertListRealtime.title: 实时预警
content.alertListRealtime.actions["viewAll"].label: 查看全部
style.alertListRealtime.card: true
style.alertListRealtime.overflow: Hidden
behavior.alertListRealtime.actions["viewAll"].onClick: navigate:/alerts
```

### 23.11 AlertItem

用途：展示单条预警、通知或动态。

```text
structure.alertListRealtime.children["alertStock"].type: AlertItem
content.alertListRealtime.children["alertStock"].title: 库存预警: 核心组件
content.alertListRealtime.children["alertStock"].description: SKU-2930 当前库存低于安全水平 (15/100)。
content.alertListRealtime.children["alertStock"].time: 10:24
style.alertListRealtime.children["alertStock"].icon: Warning
style.alertListRealtime.children["alertStock"].severity: Error
behavior.alertListRealtime.children["alertStock"].onClick: navigate:/alerts/stock
```

### 23.12 BottomNav

用途：移动端底部导航。

```text
structure.page.slots["footer"].children["bottomNavDashboard"].type: BottomNav
structure.bottomNavDashboard.children["navOverview"].type: NavItem
structure.bottomNavDashboard.children["navAnalytics"].type: NavItem

style.bottomNavDashboard.position: FixedBottom
style.bottomNavDashboard.height: 80
style.bottomNavDashboard.radius: token.radius.lg
style.bottomNavDashboard.shadow: token.shadow.sm
responsive.desktop.bottomNavDashboard.display: Hidden
```

### 23.13 NavItem

用途：导航项。

```text
structure.bottomNavDashboard.children["navOverview"].type: NavItem
content.bottomNavDashboard.children["navOverview"].label: Overview
style.bottomNavDashboard.children["navOverview"].icon: Dashboard
style.bottomNavDashboard.children["navOverview"].active: true
behavior.bottomNavDashboard.children["navOverview"].onClick: setState:state.dashboard.activeNav=overview, navigate:/dashboard
permission.bottomNavDashboard.children["navOverview"].required: dashboard.read
```

### 23.14 Toolbar

用途：承载页面级操作。

```text
structure.page.slots["main"].children["toolbarProduct"].type: Toolbar
structure.toolbarProduct.actions["create"].type: Button

content.toolbarProduct.actions["create"].label: 新增产品
style.toolbarProduct.layout: Horizontal
style.toolbarProduct.align: Right
style.toolbarProduct.height: 48
style.toolbarProduct.gap: token.spacing.sm
style.toolbarProduct.actions["create"].variant: Primary
style.toolbarProduct.actions["create"].icon: Plus

behavior.toolbarProduct.actions["create"].onClick: openModal:modalProduct:create
permission.toolbarProduct.actions["create"].required: product.create
```

### 23.15 Table

用途：展示列表数据。

```text
structure.page.slots["main"].children["tableProduct"].type: Table
structure.tableProduct.columns["name"].type: TableColumn
structure.tableProduct.columns["status"].type: TableColumn
structure.tableProduct.columns["created_at"].type: TableColumn
structure.tableProduct.rowActions["edit"].type: Action
structure.tableProduct.rowActions["delete"].type: Action

style.tableProduct.size: Compact
style.tableProduct.bordered: true
content.tableProduct.emptyText: 暂无数据
style.tableProduct.radius: token.radius.sm
style.tableProduct.shadow: token.shadow.none
style.tableProduct.fontSize: token.font.size.sm

data.tableProduct.sources["getProductList"].method: GET
data.tableProduct.sources["getProductList"].path: /api/v1/products
data.tableProduct.source: getProductList
data.tableProduct.rowKey: id

state.tableProduct.rows: []
state.tableProduct.total: 0
```

### 23.16 Form

用途：描述新增、编辑、详情等表单。

```text
structure.modalProduct.children["formProduct"].type: Form
structure.formProduct.fields["name"].type: Input
structure.formProduct.fields["price"].type: NumberInput
structure.formProduct.fields["status"].type: Select
structure.formProduct.actions["submit"].type: Button
structure.formProduct.actions["cancel"].type: Button

content.formProduct.fields["name"].label: 产品名称
content.formProduct.fields["price"].label: 价格
content.formProduct.fields["status"].label: 状态
content.formProduct.actions["submit"].label: 保存
content.formProduct.actions["cancel"].label: 取消

state.formProduct.values: {}

behavior.formProduct.onSubmit.create: callApi:formProduct.createProduct
behavior.formProduct.onSubmit.edit: callApi:formProduct.updateProduct
behavior.formProduct.actions["cancel"].onClick: closeModal:modalProduct
```

---

## 24. layout.uisl

```text
meta.name: layoutAdmin
meta.title: 后台管理布局
meta.type: Layout

structure.layout.type: AdminLayout
structure.layout.regions["sidebar"].type: Sidebar
structure.layout.regions["header"].type: Header
structure.layout.regions["main"].type: Content

structure.layout.regions["sidebar"].slot: sidebar
structure.layout.regions["header"].slot: header
structure.layout.regions["main"].slot: main

style.layout.mode: Side
style.layout.regions["sidebar"].width: 240
style.layout.regions["header"].height: 56
style.layout.regions["main"].padding: token.spacing.lg
```

---

## 25. 可复用组件

`pagination-card.uisl`：

```text
meta.name: paginationCard
meta.type: Component

structure.component.type: PaginationCard
structure.component.children["total"].type: Text
structure.component.children["pageSize"].type: Select
structure.component.children["pager"].type: Pagination
structure.component.children["jumper"].type: NumberInput
structure.component.children["jumpButton"].type: Button

style.component.layout: Horizontal
style.component.card: true
content.component.children["total"].textTemplate: 共 {total} 条
content.component.children["pageSize"].options: 10,20,50,100
content.component.children["jumper"].placeholder: 页码
content.component.children["jumpButton"].label: 跳转

behavior.component.children["pager"].onChange: emit:pageChange
behavior.component.children["pageSize"].onChange: emit:pageSizeChange
behavior.component.children["jumper"].onEnter: emit:pageJump
behavior.component.children["jumpButton"].onClick: emit:pageJump
```

---

## 26. 平台页面元素定位

参考已生成页面修改纯视觉样式时，可以使用视觉路径或 trace 路径。

视觉路径示例：

```text
product.grid[0][2].card
product.header.actions[0].button
product.grid[0][2].card.title
```

trace 路径示例：

```text
metricGridDashboard.children["metricRevenue"]
chartBusinessGrowth.children["areaChart"]
bottomNavDashboard.children["navOverview"]
```

约定：

```text
结构、行为、数据修改：更新 UISL
通用视觉语义修改：优先更新 UISL style / token / responsive / motion
纯平台私有视觉细节：可以直接修改目标平台代码
```

示例：

```text
把 metricGridDashboard.children["metricRevenue"] 的圆角调小：更新 UISL style
把 chartBusinessGrowth 的数据换成近 30 天：更新 UISL data / state
把 bottomNavDashboard 在桌面端隐藏：更新 UISL responsive
某个 shadcn Button 的 className 微调：直接修改目标平台代码
```

---

## 27. CLI 工具建议

UISL CLI 可以支持读取、校验、编译、生成代码、追踪检查和反查。

```bash
uisl validate ui/v1.uisl
uisl compile ui/v1.uisl --out ui/v1.uisl.json
uisl gen ui/v1.uisl ui/v1.web.nextjs --framework nextjs --ui shadcn
uisl gen ui/v1.uisl ui/v1.web.vue --framework vue --ui ant-design-vue
uisl gen ui/v1.uisl ui/v1.mobile.flutter --framework flutter
uisl gen ui/v1.uisl ui/v1.web.html --framework html --bundle single-file
uisl trace ui/v1.web.html/dashboard.html --uisl ui/v1.uisl/pages/dashboard.uisl
uisl locate ui/v1.web.html/dashboard.html --selector '[data-uisl="metricGridDashboard"]'
```

推荐流程：

```text
创建页面：
PRD / 截图 / 描述 / ui/idea
    ↓
AI 生成 UISL
    ↓
uisl validate
    ↓
uisl gen --target web.nextjs / web.vue / web.html / flutter
    ↓
人工运行页面并调整视觉
    ↓
结构 / 行为 / 数据 / 可访问性问题回写 UISL
    ↓
纯平台私有视觉问题直接改目标平台代码
```

`.uisl` 适合人和 AI 编辑，但生成代码前最好转成 JSON / AST：

```text
product-list.uisl
        ↓ parse
product-list.uisl.json
        ↓ generate
Next.js / Vue / Flutter / HTML
```

---

## 28. 校验建议

`uisl validate` 建议检查：

```text
meta.name 是否存在
meta.type 是否合法
meta.source.* 引用的文件是否存在
meta.design.tokenRef 是否存在
target.framework / target.ui 或 targets[profile].framework / targets[profile].ui 是否支持
trace.attribute 是否在目标产物中存在
structure 是否引用了不存在的组件
type 是否在内置 type 或 typeRegistry 中存在
content 路径是否能对应 structure 中的组件或合法全局路径
style token 引用是否能找到对应 token
data.source 是否能找到对应 sources
behavior 里 callApi 是否指向存在的数据源
behavior 里 navigate / toast / setState 是否语法合法
permission 是否格式正确
validation 是否绑定了存在的字段
accessibility 是否绑定了存在的组件或动作
responsive 组件路径是否在 structure 中存在
chart series 是否同时具备可渲染数据或明确 pathHint
目标产物 data-uisl 路径是否能反查 UISL
```

警告级检查：

```text
1. 文案写在 style 中，建议迁移到 content。
2. ariaLabel / alt 写在 style 中，建议迁移到 accessibility。
3. 图表只有 SVG path，没有 data.series。
4. 自定义 type 未在 typeRegistry 中声明。
5. 目标产物缺少 trace。
6. 纯数字尺寸字段未能确认单位。
```

---

## 29. 修改策略

```text
结构变化：更新 UISL structure
内容文案变化：更新 UISL content
行为变化：更新 UISL behavior
数据接口变化：更新 UISL data
运行状态变化：更新 UISL state
权限变化：更新 UISL permission
校验变化：更新 UISL validation
可访问性变化：更新 UISL accessibility
响应式变化：更新 UISL responsive
概念文件变化：必要时重新生成或调整 UISL
通用视觉语义变化：更新 UISL style / token / motion
目标平台输出策略变化：更新 UISL target / targets
目标产物反查规则变化：更新 UISL trace
平台私有视觉细节：优先直接修改目标平台代码
```

示例：

```text
增加一列产品状态：更新 UISL structure / data / content
新增删除按钮：更新 UISL structure / behavior / permission
修改 getProductList 接口参数：更新 UISL data
概念稿中的卡片边距更紧凑：更新 UISL style / token
概念稿中的整体阴影更轻：更新 UISL style / token
统一页面组件圆角为中等偏小：更新 UISL style / token
统一表格移动端改为 CardList：更新 UISL responsive
统一字体层级和字号：更新 UISL style / token
图表从 SVG path 改为 ECharts：优先保持 UISL data.series，修改 target generator
某个 CSS 阴影参数精确调试：直接修改目标平台代码
```

判断标准：

```text
概念文件中的稳定视觉方向：优先提炼到 UISL
跨平台、可复用、可解释的视觉意图：写入 UISL
只服务某个框架或某个页面细节的视觉实现：修改目标平台代码
```

---

## 30. Dashboard 示例

以下示例展示 v0.4.0 推荐写法。

```text
# 数据大屏页面，参考 ui/idea/dash.html。
meta.name: pageDashboardOverview
meta.title: 数据大屏
meta.type: Page
meta.description: 移动优先的数据大屏页面，展示关键指标、业务增长趋势、实时预警和底部导航。
meta.source.ideaRef: ../../idea/dash.html
meta.design.tokenRef: ../design/light-token.uisl

target.platform: web
target.framework: html
target.bundle: SingleFile
target.cssMode: InlineCSS
target.iconMode: InlineSvg
target.traceAttribute: data-uisl

trace.enabled: true
trace.attribute: data-uisl
trace.pathFormat: componentPath

structure.page.type: MobileDashboardPage
structure.page.slots["header"].children["topAppBarDashboard"].type: TopAppBar
structure.page.slots["main"].children["metricGridDashboard"].type: MetricGrid
structure.page.slots["main"].children["contentGridDashboard"].type: ResponsiveGrid
structure.page.slots["footer"].children["bottomNavDashboard"].type: BottomNav

structure.metricGridDashboard.children["metricRevenue"].type: MetricCard
structure.metricGridDashboard.children["metricActiveUsers"].type: MetricCard
structure.metricGridDashboard.children["metricConversionRate"].type: MetricCard
structure.metricGridDashboard.children["metricTodo"].type: MetricCard

structure.contentGridDashboard.children["chartBusinessGrowth"].type: AreaChartCard
structure.chartBusinessGrowth.children["areaChart"].type: AreaChart
structure.contentGridDashboard.children["alertListRealtime"].type: AlertList

content.page.title: 数据大屏
content.metricGridDashboard.children["metricRevenue"].label: 今日营收
content.metricGridDashboard.children["metricRevenue"].displayValue: ¥42,850
content.metricGridDashboard.children["metricRevenue"].trendLabel: +12%
content.metricGridDashboard.children["metricRevenue"].trendDirection: Up
content.chartBusinessGrowth.title: 业务增长趋势
content.chartBusinessGrowth.subtitle: 最近7天
content.chartBusinessGrowth.children["areaChart"].xAxisLabels: 周一,周二,周三,周四,周五,周六,周日
content.alertListRealtime.title: 实时预警

style.page.platform: MobileWeb
style.page.maxWidth: 1440px
style.page.background: token.colors.pageBackground
style.page.fontFamily: token.font.family.base
style.metricGridDashboard.layout: Grid
style.metricGridDashboard.gap: token.spacing.md
style.metricGridDashboard.children["metricRevenue"].radius: token.radius.lg
style.metricGridDashboard.children["metricRevenue"].shadow: token.shadow.xs
style.chartBusinessGrowth.card: true
style.chartBusinessGrowth.radius: token.radius.lg
style.chartBusinessGrowth.shadow: token.shadow.xs
style.chartBusinessGrowth.children["areaChart"].render: Area
style.chartBusinessGrowth.children["areaChart"].lineColor: token.colors.primary
style.chartBusinessGrowth.children["areaChart"].showGrid: true
style.bottomNavDashboard.position: FixedBottom
style.bottomNavDashboard.height: 80

style.metricGridDashboard.children["metricRevenue"].sparkline.pathHint: M0,25 Q15,5 30,20 T60,10 T90,25 T100,15
style.metricGridDashboard.children["metricRevenue"].sparkline.pathHintScope: web.svg

data.chartBusinessGrowth.series["businessGrowth"].label: 业务增长
data.chartBusinessGrowth.series["businessGrowth"].x: 周一,周二,周三,周四,周五,周六,周日
data.chartBusinessGrowth.series["businessGrowth"].y: 130,110,140,90,40,70,50,30,10

state.dashboard.activeNav: overview
state.dashboard.timeRange: recent7Days

behavior.topAppBarDashboard.actions["notifications"].onClick: toast:通知中心
behavior.chartBusinessGrowth.actions["timeRange"].onClick: toast:切换时间范围
behavior.bottomNavDashboard.children["navAnalytics"].onClick: setState:state.dashboard.activeNav=analytics, navigate:/analytics

accessibility.page.lang: zh-CN
accessibility.metricGridDashboard.ariaLabel: 关键指标
accessibility.chartBusinessGrowth.children["areaChart"].role: img
accessibility.chartBusinessGrowth.children["areaChart"].ariaLabel: 业务增长趋势折线面积图
accessibility.topAppBarDashboard.actions["notifications"].ariaLabel: 通知

motion.card.press.scale: 0.98
motion.button.hover.translateY: -1px
motion.toast.visible.duration: 1400ms

responsive.breakpoints["mobile"].maxWidth: 767
responsive.breakpoints["tablet"].minWidth: 768
responsive.breakpoints["desktop"].minWidth: 1024
responsive.mobile.metricGridDashboard.columns: 2
responsive.desktop.metricGridDashboard.columns: 4
responsive.desktop.contentGridDashboard.columns: 2
responsive.desktop.contentGridDashboard.columnRatio: 1.55fr 0.8fr
responsive.desktop.bottomNavDashboard.display: Hidden
```

---

## 31. 核心原则

```text
1. UISL 主要描述结构、内容、显示语义和跨平台稳定视觉意图。
2. UISL 可由 ui/idea 概念文件生成。
3. 当概念文件存在时，样式、阴影、边距、布局、字体、字重、圆角、密度和轻量动效优先与概念文件相符。
4. 每一行只描述一个属性。
5. type 使用 PascalCase。
6. name 使用 camelCase。
7. 组件实例名推荐 type + Domain，例如 tableProduct、metricGridDashboard。
8. 通用树使用 children。
9. 表格使用 columns。
10. 表单使用 fields。
11. 操作使用 actions / rowActions。
12. API sources 使用动作型命名，例如 getProductList。
13. 数据源放在组件作用域下。
14. 静态文案和演示内容放在 content。
15. 运行时状态统一放在 state。
16. 行为使用动作流水线。
17. 组件 / 页面 / Layout 内部默认不维护 meta.version。
18. responsive 可描述不同屏幕下的宽度、高度、布局、溢出、显示形态和列数。
19. 圆角、阴影、字体等通用视觉语义可使用 token 描述。
20. 后台系统默认圆角建议中等偏小；如果概念文件不同，以概念文件为准。
21. Dashboard、移动端卡片和底部导航可以使用更大的圆角和更明显的层次。
22. 阴影建议少量使用，默认优先 token.shadow.xs 或 token.shadow.none。
23. 字体建议使用 token 描述字号、字重、行高和文本层级。
24. 图表优先使用 data.series 描述，SVG path 只作为 pathHint。
25. accessibility 独立成层，不混入 style。
26. motion 只描述轻量且跨平台稳定的动效意图。
27. target / targets 只描述目标平台生成策略，不改变 UI 结构语义。
28. 同一份 UISL 需要生成多个平台时，推荐使用 targets["profileName"]。
29. Next.js、Vue、Flutter 等平台差异应放在 platformAdapter 或 targetOverride，不应污染 structure。
30. 生成特定框架页面时，应优先使用该框架或 target.ui 声明组件库的原生组件，并优先使用框架推荐的样式语言和主题机制。
28. trace 用于目标产物反查 UISL，建议默认开启。
29. 纯平台私有视觉细节可以直接修改目标平台页面代码。
30. 结构、内容、行为、数据、权限、校验和可访问性变化应回写 UISL。
```

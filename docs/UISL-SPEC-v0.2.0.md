# UISL 规范

- 规范版本：v0.2.0
- 状态：Draft
- 更新时间：2026-07-10

## 版本说明

UISL 规范文档使用 `vMAJOR.MINOR.PATCH` 格式，例如 `v0.2.0`。

- `MAJOR`：不兼容的语法变化。
- `MINOR`：新增能力、字段、type 或推荐写法。
- `PATCH`：修正文档、补充示例、修复描述问题。

`.uisl` 文件内部不维护版本号。页面、布局、组件的版本通过目录、Git 分支、Git tag 或规范文档版本管理。

```text
ui/v1.uisl/            # UI 源描述版本
ui/v1.web.nextjs/      # 基于 v1.uisl 生成或维护的 Next.js 实现
ui/v1.web.vue/         # 基于 v1.uisl 生成或维护的 Vue 实现
ui/v1.mobile.flutter/  # 基于 v1.uisl 生成或维护的 Flutter 实现
```

## 1. 定位

UISL（UI Structure Language）用于描述 UI 的结构、显示语义、行为、数据绑定、状态、权限和校验。

它适合作为 AI 生成多平台前端代码的中间描述：

```text
网页设计 / 截图 / PRD
        ↓
      UISL
        ↓
Next.js / Vue / Flutter / 其他平台
```

UISL 主要负责页面和组件结构、文案和基础显示意图、组件行为、数据源与字段绑定、运行时状态、权限与校验。

具体颜色、阴影、微小间距和平台视觉细节，可以直接参考目标平台已经生成的页面代码继续修改。

## 2. 推荐项目布局

推荐在项目根目录中组织 `ui` 与 `docs`：

```text
project/
├─ ui/
│  ├─ v1.uisl/
│  │  ├─ pages/
│  │  │  └─ product-list.uisl
│  │  ├─ layouts/
│  │  │  └─ admin-layout.uisl
│  │  └─ components/
│  │     └─ pagination-card.uisl
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
ui/v1.uisl/            存放 UISL 源文件
ui/v1.web.nextjs/      存放由 UISL 生成或维护的 Next.js 实现
ui/v1.web.vue/         存放由 UISL 生成或维护的 Vue 实现
ui/v1.mobile.flutter/  存放由 UISL 生成或维护的 Flutter 实现
```

`docs/` 管规范，`ui/` 管具体 UI 描述和目标平台实现。

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

## 4. 注释

使用 `#`：

```text
# 产品管理页
meta.name: pageProductList

data.tableProduct.sources["getProductList"].path: /api/v1/products  # 产品列表接口
```

## 5. 命名规则

### 5.1 基础命名

```text
页面/组件 name：camelCase
type：PascalCase
后端字段：保持接口原名
权限码：dot.case
```

统一使用 `name`，不使用 `id`。

### 5.2 页面、布局、组件实例命名

推荐使用以下模式：

```text
页面 name：page + Domain + Scene
布局 name：layout + Domain
组件实例 name：type + Domain
```

示例：

```text
meta.name: pageProductList
meta.name: pageProductDetail
meta.name: pageProductEdit
meta.name: layoutAdmin

structure.page.slots["main"].children["toolbarProduct"].type: Toolbar
structure.page.slots["main"].children["filterProduct"].type: FilterForm
structure.page.slots["main"].children["tableProduct"].type: Table
structure.page.slots["main"].children["paginationProduct"].type: PaginationCard
structure.page.slots["main"].children["modalProduct"].type: Modal
structure.page.slots["main"].children["formProduct"].type: Form
```

不推荐：

```text
meta.name: pageProductPage
```

因为 `page` 与 `Page` 语义重复。

### 5.3 集合 key 命名

不是所有 key 都使用 `type + Domain`。推荐规则：

```text
组件实例：tableProduct, formProduct, filterProduct
columns：使用后端字段名，例如 name, status, created_at
fields：使用后端字段名，例如 name, price, status
actions：使用动作名，例如 create, submit, cancel
rowActions：使用动作名，例如 view, edit, delete
sources：使用接口动作名，例如 getProductList, createProduct, updateProduct
```

## 6. 分层

UISL 推荐分层：

```text
meta
structure
style
behavior
data
state
permission
validation
responsive
```

其中 `responsive` 可选。

## 7. meta

`meta` 描述文件自身的基本信息，但不包含版本号。

页面示例：

```text
meta.name: pageProductList
meta.title: 产品管理
meta.type: Page
meta.description: 产品管理列表页
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

## 8. structure

`structure` 只描述页面和组件结构。

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

通用组件树使用 `children`，不使用 `items`：

```text
structure.sidebar.children["menuProduct"].type: MenuItem
```

有明确语义时使用专用集合：

```text
structure.tableProduct.columns["status"].type: TableColumn
structure.formProduct.fields["name"].type: Input
structure.toolbarProduct.actions["create"].type: Button
structure.tableProduct.rowActions["edit"].type: Action
```

顺序使用 `order`：

```text
structure.page.slots["main"].children["toolbarProduct"].order: 10
structure.page.slots["main"].children["filterProduct"].order: 20
structure.page.slots["main"].children["tableProduct"].order: 30
structure.page.slots["main"].children["paginationProduct"].order: 40
```

## 9. style

`style` 描述组件的显示语义和基础视觉意图，不等同于完整 CSS。

UISL 可以描述对多端生成有稳定价值的视觉语义，例如布局方向、尺寸策略、圆角等级、轻微阴影、字体层级、密度、留白和基础色彩 token。

具体颜色值、复杂动画、精确阴影参数、特殊 CSS hack、平台组件库私有样式，仍建议在目标平台代码中处理。

```text
style.<componentName>.<property>: value
style.<componentName>.<collection>["key"].<property>: value
```

### 9.1 页面与工具栏

```text
style.page.title: 产品管理
style.page.padding: token.spacing.lg
style.page.background: token.colors.pageBackground
style.page.minHeight: 100vh
style.page.maxWidth: 100%

style.toolbarProduct.layout: Horizontal
style.toolbarProduct.align: Right
style.toolbarProduct.height: 48
style.toolbarProduct.gap: token.spacing.sm
style.toolbarProduct.actions["create"].label: 新增产品
style.toolbarProduct.actions["create"].variant: Primary
style.toolbarProduct.actions["create"].icon: Plus
```

### 9.2 尺寸与空间

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

推荐尺寸策略枚举：

```text
Auto,Fill,Hug,Fixed,FullWidth,FullHeight,ViewportHeight,Content,Scroll
```

示例：

```text
style.tableProduct.width: 100%
style.tableProduct.height: Auto
style.tableProduct.maxHeight: calc(100vh - 280px)
style.tableProduct.overflow: Auto
```

### 9.3 圆角

组件圆角推荐使用中等偏小的默认风格，避免过大导致后台系统显得松散。

推荐 token：

```text
token.radius.xs      # 极小圆角，例如 2px
token.radius.sm      # 小圆角，例如 4px
token.radius.smMd    # 中等偏小圆角，例如 6px
token.radius.md      # 中等圆角，例如 8px
token.radius.lg      # 大圆角，例如 12px
```

推荐默认：

```text
style.card.radius: token.radius.smMd
style.modalProduct.radius: token.radius.smMd
style.tableProduct.radius: token.radius.sm
style.toolbarProduct.actions["create"].radius: token.radius.smMd
```

如果没有特殊设计诉求，后台管理类页面优先使用：

```text
style.default.radius: token.radius.smMd
```

### 9.4 阴影与轻微层次感

UISL 可以描述“少许阴影效果”或轻微层次感，但不建议在 UISL 中写复杂 box-shadow 细节。

推荐 token：

```text
token.shadow.none
token.shadow.xs      # 极轻微阴影，适合卡片、表单容器
token.shadow.sm      # 轻微阴影，适合弹窗、浮层
token.shadow.md      # 中等阴影，谨慎使用
```

示例：

```text
style.card.shadow: token.shadow.xs
style.modalProduct.shadow: token.shadow.sm
style.dropdown.shadow: token.shadow.sm
style.tableProduct.shadow: token.shadow.none
```

推荐原则：

```text
后台页面：优先 token.shadow.xs 或 token.shadow.none
弹窗浮层：优先 token.shadow.sm
重要悬浮层：可使用 token.shadow.md
```

### 9.5 字体样式与大小

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

组件字体建议：

```text
style.tableProduct.fontSize: token.font.size.sm
style.tableProduct.columns["name"].fontWeight: token.font.weight.medium
style.formProduct.fields["name"].labelFontSize: token.font.size.sm
style.formProduct.fields["name"].labelFontWeight: token.font.weight.medium
style.toolbarProduct.actions["create"].fontWeight: token.font.weight.medium
```

后台管理页面推荐整体偏紧凑：

```text
style.default.fontSize: token.font.size.sm
style.default.labelFontWeight: token.font.weight.medium
style.default.titleFontWeight: token.font.weight.semibold
```

### 9.6 表格

```text
style.tableProduct.size: Compact
style.tableProduct.bordered: true
style.tableProduct.emptyText: 暂无数据
style.tableProduct.radius: token.radius.sm
style.tableProduct.shadow: token.shadow.none
style.tableProduct.fontSize: token.font.size.sm

style.tableProduct.columns["name"].label: 产品名称
style.tableProduct.columns["name"].width: 220
style.tableProduct.columns["status"].label: 状态
style.tableProduct.columns["status"].render: Tag

style.tableProduct.rowActions["edit"].label: 编辑
style.tableProduct.rowActions["edit"].variant: Link
style.tableProduct.rowActions["delete"].label: 删除
style.tableProduct.rowActions["delete"].variant: Danger
```

推荐 `render` 枚举：

```text
Text,Tag,Badge,Currency,Date,DateTime,Boolean,Image,Avatar,Link,Progress,Switch,Custom
```

Tag 映射：

```text
style.tableProduct.columns["status"].tagMap["active"].label: 启用
style.tableProduct.columns["status"].tagMap["active"].color: Success
style.tableProduct.columns["status"].tagMap["disabled"].label: 禁用
style.tableProduct.columns["status"].tagMap["disabled"].color: Danger
```

### 9.7 Design Token 汇总

```text
token.colors.primary
token.colors.surface
token.colors.pageBackground
token.colors.border
token.colors.textPrimary
token.colors.textSecondary

token.spacing.xs
token.spacing.sm
token.spacing.md
token.spacing.lg
token.spacing.xl

token.radius.xs
token.radius.sm
token.radius.smMd
token.radius.md
token.radius.lg

token.shadow.none
token.shadow.xs
token.shadow.sm
token.shadow.md

token.font.family.base
token.font.size.xs
token.font.size.sm
token.font.size.md
token.font.size.lg
token.font.size.xl
token.font.weight.regular
token.font.weight.medium
token.font.weight.semibold
token.font.weight.bold
token.font.lineHeight.normal
```

## 10. data

数据源放在组件作用域下。

`sources` key 推荐使用动作型命名，例如 `getProductList`、`createProduct`、`updateProduct`、`deleteProduct`。

### 10.1 查询列表

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

### 10.2 创建、更新、删除

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
```

## 11. state

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

## 12. behavior

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
toastSuccess
toastError
confirmDelete:<actionName>
```

事件变量：

```text
$event.page
$event.pageSize
$event.row
$event.value
```

页面加载：

```text
behavior.page.onLoad: callApi:tableProduct.getProductList
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

## 13. 分页刷新表格

```text
behavior.paginationProduct.onPageChange: setState:state.tableProduct.pagination.currentPage=$event.page, callApi:tableProduct.getProductList

behavior.paginationProduct.onPageSizeChange: setState:state.tableProduct.pagination.pageSize=$event.pageSize, setState:state.tableProduct.pagination.currentPage=1, callApi:tableProduct.getProductList

behavior.paginationProduct.onJump: setState:state.tableProduct.pagination.currentPage=$event.page, callApi:tableProduct.getProductList
```

## 14. permission

```text
permission.page.required: product.read
permission.sidebar.children["menuProduct"].required: product.read
permission.toolbarProduct.actions["create"].required: product.create
permission.tableProduct.rowActions["edit"].required: product.update
permission.tableProduct.rowActions["delete"].required: product.delete
```

## 15. validation

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

## 16. list 规则

简单列表使用英文逗号：

```text
validation.formProduct.fields["status"].enum: active,disabled
permission.tableProduct.rowActions["delete"].required.any: product.delete, admin
```

对象列表使用 `["key"]`，顺序使用 `order`。

## 17. layout.uisl

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

## 18. 可复用组件

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
style.component.children["total"].textTemplate: 共 {total} 条
style.component.children["pageSize"].options: 10,20,50,100
style.component.children["jumper"].placeholder: 页码
style.component.children["jumpButton"].label: 跳转

behavior.component.children["pager"].onChange: emit:pageChange
behavior.component.children["pageSize"].onChange: emit:pageSizeChange
behavior.component.children["jumper"].onEnter: emit:pageJump
behavior.component.children["jumpButton"].onClick: emit:pageJump
```

## 19. responsive（可选）

`responsive` 用于描述不同屏幕尺寸下的显示方式、宽度、高度、最大高度、间距、布局方向、溢出策略和组件密度。

它不要求完整复刻 CSS media query，而是描述多端生成时需要保持一致的自适应意图。

### 19.1 断点

```text
responsive.breakpoints["mobile"].maxWidth: 767
responsive.breakpoints["tablet"].minWidth: 768
responsive.breakpoints["tablet"].maxWidth: 1023
responsive.breakpoints["desktop"].minWidth: 1024
responsive.breakpoints["wide"].minWidth: 1440
```

### 19.2 推荐属性

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
```

推荐属性含义：

```text
display     显示形态，例如 Table、CardList、Grid、Hidden
layout      布局方向，例如 Horizontal、Vertical、Dropdown
width       宽度
height      高度
minWidth    最小宽度
maxWidth    最大宽度
minHeight   最小高度
maxHeight   最大高度
overflow    内容溢出策略，例如 Visible、Hidden、Auto、Scroll
density     组件密度，例如 Compact、Normal、Comfortable
```

### 19.3 桌面端示例

```text
responsive.desktop.page.width: 100%
responsive.desktop.page.minHeight: 100vh
responsive.desktop.page.padding: token.spacing.lg
responsive.desktop.page.maxWidth: 100%

responsive.desktop.toolbarProduct.layout: Horizontal
responsive.desktop.toolbarProduct.height: 48
responsive.desktop.toolbarProduct.gap: token.spacing.sm

responsive.desktop.filterProduct.layout: Horizontal
responsive.desktop.filterProduct.width: 100%
responsive.desktop.filterProduct.height: Auto

responsive.desktop.tableProduct.display: Table
responsive.desktop.tableProduct.width: 100%
responsive.desktop.tableProduct.maxHeight: calc(100vh - 280px)
responsive.desktop.tableProduct.overflow: Auto

responsive.desktop.paginationProduct.layout: Horizontal
responsive.desktop.paginationProduct.height: 48
```

### 19.4 平板端示例

```text
responsive.tablet.page.padding: token.spacing.md
responsive.tablet.toolbarProduct.layout: Horizontal
responsive.tablet.filterProduct.layout: Wrap
responsive.tablet.tableProduct.display: Table
responsive.tablet.tableProduct.width: 100%
responsive.tablet.tableProduct.maxHeight: calc(100vh - 260px)
responsive.tablet.tableProduct.overflow: Auto
responsive.tablet.modalProduct.width: 80vw
responsive.tablet.modalProduct.maxHeight: 80vh
```

### 19.5 移动端示例

```text
responsive.mobile.page.padding: token.spacing.sm
responsive.mobile.page.width: 100vw
responsive.mobile.page.minHeight: 100vh

responsive.mobile.toolbarProduct.layout: Dropdown
responsive.mobile.toolbarProduct.width: 100%
responsive.mobile.toolbarProduct.height: Auto

responsive.mobile.filterProduct.layout: Vertical
responsive.mobile.filterProduct.width: 100%
responsive.mobile.filterProduct.gap: token.spacing.sm

responsive.mobile.tableProduct.display: CardList
responsive.mobile.tableProduct.width: 100%
responsive.mobile.tableProduct.height: Auto
responsive.mobile.tableProduct.maxHeight: none
responsive.mobile.tableProduct.overflow: Visible

responsive.mobile.paginationProduct.layout: Vertical
responsive.mobile.paginationProduct.width: 100%
responsive.mobile.paginationProduct.height: Auto

responsive.mobile.modalProduct.width: 100vw
responsive.mobile.modalProduct.height: 100vh
responsive.mobile.modalProduct.radius: token.radius.sm
```

### 19.6 自适应原则

```text
1. 桌面端优先展示完整信息，例如 Table、Horizontal Toolbar。
2. 平板端允许换行和收缩，例如 Wrap FilterForm。
3. 移动端优先纵向布局，例如 CardList、Vertical Form。
4. 大面积列表组件应设置 maxHeight 与 overflow，避免页面整体失控。
5. 弹窗在移动端可接近全屏，圆角应比桌面端更小。
6. 宽高控制使用语义属性，具体 CSS 由目标平台生成。
```

## 20. 平台页面元素定位

参考已生成页面修改纯视觉样式时，可以使用视觉路径：

```text
product.grid[0][2].card
product.header.actions[0].button
product.grid[0][2].card.title
```

约定：

```text
结构、行为、数据修改：更新 UISL
纯视觉细节修改：直接修改目标平台代码
```

示例：

```text
把 product.grid[0][2].card 的圆角调大一点
把 product.header.actions[0].button 改成更明显的主按钮
把 product.grid[0][2].card.title 字体加粗
```

这类纯视觉改动不强制回写 UISL。

## 21. Type 使用示例

每个 type 推荐单独提供用途、常用位置、最小示例和扩展示例。这样 AI 生成时可以按 type 查找模板。

### 21.1 Page

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

### 21.2 Layout

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

### 21.3 Toolbar

用途：承载页面级操作。

```text
structure.page.slots["main"].children["toolbarProduct"].type: Toolbar
structure.toolbarProduct.actions["create"].type: Button

style.toolbarProduct.layout: Horizontal
style.toolbarProduct.align: Right
style.toolbarProduct.height: 48
style.toolbarProduct.gap: token.spacing.sm
style.toolbarProduct.actions["create"].label: 新增产品
style.toolbarProduct.actions["create"].variant: Primary
style.toolbarProduct.actions["create"].icon: Plus

behavior.toolbarProduct.actions["create"].onClick: openModal:modalProduct:create
permission.toolbarProduct.actions["create"].required: product.create
```

### 21.4 Button

用途：触发用户操作。

```text
structure.toolbarProduct.actions["create"].type: Button
style.toolbarProduct.actions["create"].label: 新增产品
style.toolbarProduct.actions["create"].variant: Primary
style.toolbarProduct.actions["create"].icon: Plus
behavior.toolbarProduct.actions["create"].onClick: openModal:modalProduct:create
```

### 21.5 FilterForm

用途：承载列表筛选条件。

```text
structure.page.slots["main"].children["filterProduct"].type: FilterForm
structure.filterProduct.fields["keyword"].type: Input
structure.filterProduct.fields["status"].type: Select
structure.filterProduct.actions["search"].type: Button
structure.filterProduct.actions["reset"].type: Button

style.filterProduct.fields["keyword"].label: 关键词
style.filterProduct.fields["keyword"].placeholder: 搜索产品名称
style.filterProduct.fields["status"].label: 状态
style.filterProduct.actions["search"].label: 查询
style.filterProduct.actions["reset"].label: 重置

state.filterProduct.keyword: ""
state.filterProduct.status: null

behavior.filterProduct.actions["search"].onClick: setState:state.tableProduct.pagination.currentPage=1, callApi:tableProduct.getProductList
behavior.filterProduct.actions["reset"].onClick: setState:state.filterProduct.keyword="", setState:state.filterProduct.status=null, setState:state.tableProduct.pagination.currentPage=1, callApi:tableProduct.getProductList
```

### 21.6 Table

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
style.tableProduct.emptyText: 暂无数据
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

### 21.7 TableColumn

用途：描述表格字段列。

```text
structure.tableProduct.columns["name"].type: TableColumn
structure.tableProduct.columns["status"].type: TableColumn

style.tableProduct.columns["name"].label: 产品名称
style.tableProduct.columns["name"].width: 220
style.tableProduct.columns["status"].label: 状态
style.tableProduct.columns["status"].render: Tag

data.tableProduct.columns["name"].field: name
data.tableProduct.columns["status"].field: status
```

### 21.8 RowAction

用途：描述表格行操作。

```text
structure.tableProduct.rowActions["edit"].type: Action
structure.tableProduct.rowActions["delete"].type: Action

style.tableProduct.rowActions["edit"].label: 编辑
style.tableProduct.rowActions["edit"].variant: Link
style.tableProduct.rowActions["delete"].label: 删除
style.tableProduct.rowActions["delete"].variant: Danger

behavior.tableProduct.rowActions["edit"].onClick: setState:state.tableProduct.selectedRow=$event.row, openModal:modalProduct:edit
behavior.tableProduct.rowActions["delete"].onClick: setState:state.tableProduct.selectedRow=$event.row, confirmDelete:deleteProduct
```

### 21.9 Modal

用途：承载弹窗内容，例如新增或编辑表单。

```text
structure.page.slots["main"].children["modalProduct"].type: Modal
structure.modalProduct.children["formProduct"].type: Form

style.modalProduct.title.create: 新增产品
style.modalProduct.title.edit: 编辑产品
style.modalProduct.width: 720
style.modalProduct.radius: token.radius.smMd
style.modalProduct.shadow: token.shadow.sm

state.modalProduct.visible: false
state.modalProduct.mode: create

behavior.modalProduct.onCancel: closeModal:modalProduct
```

### 21.10 Form

用途：描述新增、编辑、详情等表单。

```text
structure.modalProduct.children["formProduct"].type: Form
structure.formProduct.fields["name"].type: Input
structure.formProduct.fields["price"].type: NumberInput
structure.formProduct.fields["status"].type: Select
structure.formProduct.actions["submit"].type: Button
structure.formProduct.actions["cancel"].type: Button

style.formProduct.fields["name"].label: 产品名称
style.formProduct.fields["price"].label: 价格
style.formProduct.fields["status"].label: 状态
style.formProduct.actions["submit"].label: 保存
style.formProduct.actions["cancel"].label: 取消

state.formProduct.values: {}

behavior.formProduct.onSubmit.create: callApi:formProduct.createProduct
behavior.formProduct.onSubmit.edit: callApi:formProduct.updateProduct
behavior.formProduct.actions["cancel"].onClick: closeModal:modalProduct
```

### 21.11 FormField

用途：描述表单字段。

```text
structure.formProduct.fields["name"].type: Input
style.formProduct.fields["name"].label: 产品名称
style.formProduct.fields["name"].placeholder: 请输入产品名称

data.formProduct.fields["name"].field: name
validation.formProduct.fields["name"].required: true
validation.formProduct.fields["name"].minLength: 2
validation.formProduct.fields["name"].message.required: 请输入产品名称
```

### 21.12 PaginationCard

用途：描述分页组件。

```text
structure.page.slots["main"].children["paginationProduct"].type: PaginationCard

style.paginationProduct.layout: Horizontal
style.paginationProduct.card: true
style.paginationProduct.radius: token.radius.smMd
style.paginationProduct.shadow: token.shadow.xs

behavior.paginationProduct.onPageChange: setState:state.tableProduct.pagination.currentPage=$event.page, callApi:tableProduct.getProductList
behavior.paginationProduct.onPageSizeChange: setState:state.tableProduct.pagination.pageSize=$event.pageSize, setState:state.tableProduct.pagination.currentPage=1, callApi:tableProduct.getProductList
behavior.paginationProduct.onJump: setState:state.tableProduct.pagination.currentPage=$event.page, callApi:tableProduct.getProductList
```

### 21.13 Sidebar

用途：描述侧边导航区域。

```text
structure.layout.regions["sidebar"].type: Sidebar
structure.sidebar.children["menuProduct"].type: MenuItem
structure.sidebar.children["menuOrder"].type: MenuItem

style.sidebar.width: 240
style.sidebar.children["menuProduct"].label: 产品管理
style.sidebar.children["menuProduct"].icon: Package
style.sidebar.children["menuOrder"].label: 订单管理
style.sidebar.children["menuOrder"].icon: ShoppingCart

permission.sidebar.children["menuProduct"].required: product.read
```

### 21.14 MenuItem

用途：描述菜单项。

```text
structure.sidebar.children["menuProduct"].type: MenuItem
style.sidebar.children["menuProduct"].label: 产品管理
style.sidebar.children["menuProduct"].icon: Package
behavior.sidebar.children["menuProduct"].onClick: navigate:/products
permission.sidebar.children["menuProduct"].required: product.read
```

## 22. CLI 工具建议

UISL CLI 可以先支持读取、校验、编译和生成代码。

```bash
uisl validate ui/v1.uisl
uisl compile ui/v1.uisl --out ui/v1.uisl.json
uisl gen ui/v1.uisl ui/v1.web.nextjs --framework nextjs --ui shadcn
uisl gen ui/v1.uisl ui/v1.web.vue --framework vue --ui ant-design-vue
uisl gen ui/v1.uisl ui/v1.mobile.flutter --framework flutter
```

推荐流程：

```text
创建页面：
PRD / 截图 / 描述
    ↓
AI 生成 UISL
    ↓
uisl validate
    ↓
uisl gen --target web.nextjs
    ↓
人工运行页面并调整视觉
    ↓
结构 / 行为 / 数据问题回写 UISL
    ↓
纯视觉问题直接改目标平台代码
```

`.uisl` 适合人和 AI 编辑，但生成代码前最好转成 JSON / AST：

```text
product-list.uisl
        ↓ parse
product-list.uisl.json
        ↓ generate
Next.js / Vue / Flutter
```

## 23. 校验建议

`uisl validate` 建议检查：

```text
meta.name 是否存在
meta.type 是否合法
structure 是否引用了不存在的组件
data.source 是否能找到对应 sources
behavior 里 callApi 是否指向存在的数据源
permission 是否格式正确
validation 是否绑定了存在的字段
```

## 24. 修改策略

```text
结构变化：更新 UISL
行为变化：更新 UISL
数据接口变化：更新 UISL
权限变化：更新 UISL
校验变化：更新 UISL
通用视觉语义变化：可以更新 UISL
平台私有视觉细节：优先直接修改目标平台代码
```

示例：

```text
增加一列产品状态：更新 UISL
新增删除按钮：更新 UISL
修改 getProductList 接口参数：更新 UISL
统一页面组件圆角为中等偏小：可以更新 UISL style / token
统一表格移动端改为 CardList：可以更新 UISL responsive
统一字体层级和字号：可以更新 UISL style / token
某个 shadcn Button 的 className 微调：直接修改目标平台代码
某个 CSS 阴影参数精确调试：直接修改目标平台代码
```

判断标准：

```text
跨平台、可复用、可解释的视觉意图：写入 UISL
只服务某个框架或某个页面细节的视觉实现：修改目标平台代码
```

## 25. 核心原则

```text
1. UISL 主要描述结构、显示语义和跨平台稳定视觉意图。
2. 每一行只描述一个属性。
3. type 使用 PascalCase。
4. name 使用 camelCase。
5. 组件实例名推荐 type + Domain，例如 tableProduct。
6. 通用树使用 children。
7. 表格使用 columns。
8. 表单使用 fields。
9. 操作使用 actions / rowActions。
10. API sources 使用动作型命名，例如 getProductList。
11. 数据源放在组件作用域下。
12. 状态统一放在 state 层。
13. 行为使用动作流水线。
14. 组件 / 页面 / Layout 内部不维护 meta.version。
15. responsive 可描述不同屏幕下的宽度、高度、布局、溢出和显示形态。
16. 圆角、阴影、字体等通用视觉语义可使用 token 描述。
17. 后台系统默认圆角建议中等偏小，例如 token.radius.smMd。
18. 阴影建议少量使用，默认优先 token.shadow.xs 或 token.shadow.none。
19. 字体建议使用 token 描述字号、字重、行高和文本层级。
20. 纯平台私有视觉细节可以直接修改目标平台页面代码。
21. 结构、行为、数据变化必须回写 UISL。
```

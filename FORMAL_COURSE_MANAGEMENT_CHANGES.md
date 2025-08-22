## 正课管理（Formal Courses）本次修改说明

更新时间：自动生成于近期改造；模块：正课管理页面与相关后端。

### 1. 计算口径统一
- 总收入：购买节数 × 单节售价（不在前端扣减手续费）。
- 总成本：`course.cost + 手续费`（其中 `course.cost` 已含课时成本与其他成本）。
- 手续费：仅当支付渠道为“淘宝”时，按费率计算；优先使用课程快照 `snapshot_fee_rate`，缺失时回退配置费率。
- 利润：总收入 − 总成本。

涉及文件：
- `app/templates/formal_courses.html`（表格单行渲染改为由后端API返回数据）
- `app/routes.py` → `api_formal_courses_stats`（新增API统一计算）

### 2. 列表展示调整
- 隐藏“含手续费：¥xx.xx”提示（避免与总成本重复表达）。
- 移除整列“来源”。
- 保留“其他成本”独立列，便于核对。
- 在“操作”列新增“小眼睛”按钮，跳转到详情页。

涉及文件：
- `app/templates/formal_courses.html`

### 3. 详情页与路由新增
- 新增路由：`GET /formal-courses/<id>/details`
  - 直读数据库，展示：学员录入信息、试听课信息（若由试听转化）、正课信息、计算口径与结果、扩展信息（meta）。
- 新增模板：`app/templates/formal_course_details.html`
  - 计算口径基于快照：`snapshot_course_cost`（单节成本）、`snapshot_fee_rate`（手续费率，小数）。
  - 展示：总收入、课时成本、其他成本、手续费、总成本、净利润。

涉及文件：
- `app/routes.py`（新增 `formal_course_details` 路由）
- `app/templates/formal_course_details.html`（新增模板）

### 4. 转正保存逻辑增强
- 在试听转正时写入快照与表单快照：
  - `snapshot_course_cost`：转正当时的单节成本。
  - `snapshot_fee_rate`：转正当时的手续费率（小数）。
  - `meta`：转正表单的键值对 JSON，便于未来字段增减后仍可在详情页展示。

涉及文件：
- `app/routes.py` → `convert_trial_to_course`（POST 分支）
- `app/models.py` → `Course` 新增字段：`snapshot_course_cost`、`snapshot_fee_rate`、`meta`
- `run.py`（启动自迁移）

### 5. 后端统计API（降卡顿）
- 新增：`GET /api/formal-courses/stats`
  - 返回 `summary`（总收入、总成本、总利润、总手续费、条数）与 `rows`（逐行明细）。
  - 费率优先采用快照，淘宝且无快照时回退配置费率。
- 前端 `formal_courses.html` 在 `DOMContentLoaded` 时调用该API，
  - 用 `summary` 更新顶部五个统计卡（`fc_total_*`），
  - 用 `rows` 重绘表格 `#formal_tbody`。

涉及文件：
- `app/routes.py` → `api_formal_courses_stats`
- `app/templates/formal_courses.html`（新增前端渲染脚本、标记ID）

### 6. 页面加载体验优化
- `app/templates/base.html`：移除遮罩由 `window.load` 改为 `DOMContentLoaded + 3s 兜底`，避免外部资源阻塞导致“无限转圈”。

### 7. 验证步骤
1) 进入“正课管理”页面：顶部统计卡加载完成，表格填充无卡顿；
2) 随机点选“查看”小眼睛：详情页显示学员/试听/正课信息，以及基于快照的计算结果；
3) 执行一次试听转正：保存后在正课列表与详情页口径一致，利润=收入−(课程成本+其他成本+手续费)；
4) 刷新页面观察性能：不出现加载遮罩长期不消失/转圈问题；
5) 导出/编辑/删除功能不受影响（已有按钮保持可用）。

### 8. 兼容性与注意事项
- 旧数据无快照时，手续费回退到配置费率；
- `course.cost` 继续保存“课时成本+其他成本”的合计，手续费不入 `course.cost`，仅用于计算与展示；
- `meta` 用于动态扩展字段的只读展示，避免频繁调整数据库结构。





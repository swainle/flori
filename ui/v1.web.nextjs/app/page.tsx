"use client";

import { useState } from "react";

type IconName =
  | "notifications"
  | "trending_up"
  | "trending_down"
  | "expand_more"
  | "warning"
  | "info"
  | "check_circle"
  | "dashboard"
  | "insights"
  | "description"
  | "settings";

type Metric = {
  uisl: string;
  label: string;
  value: string;
  trend?: string;
  trendDirection?: "up" | "down";
  status?: string;
  path: string;
};

type Alert = {
  uisl: string;
  icon: IconName;
  tone: "error" | "info" | "success";
  title: string;
  description: string;
  time: string;
};

type NavItem = {
  uisl: string;
  icon: IconName;
  label: string;
  active?: boolean;
};

const metrics: Metric[] = [
  {
    uisl: "metricGridDashboard.children[\"metricRevenue\"]",
    label: "今日营收",
    value: "¥42,850",
    trend: "+12%",
    trendDirection: "up",
    path: "M0,25 Q15,5 30,20 T60,10 T90,25 T100,15",
  },
  {
    uisl: "metricGridDashboard.children[\"metricActiveUsers\"]",
    label: "活跃用户",
    value: "1,284",
    trend: "+8%",
    trendDirection: "up",
    path: "M0,15 Q20,25 40,15 T70,20 T100,5",
  },
  {
    uisl: "metricGridDashboard.children[\"metricConversionRate\"]",
    label: "转化率",
    value: "3.42%",
    trend: "-2%",
    trendDirection: "down",
    path: "M0,5 Q20,10 40,25 T70,15 T100,20",
  },
  {
    uisl: "metricGridDashboard.children[\"metricTodo\"]",
    label: "待办事项",
    value: "12",
    status: "进行中",
    path: "M0,20 L20,15 L40,22 L60,10 L80,18 L100,5",
  },
];

const alerts: Alert[] = [
  {
    uisl: "alertListRealtime.children[\"alertStock\"]",
    icon: "warning",
    tone: "error",
    title: "库存预警: 核心组件",
    description: "SKU-2930 当前库存低于安全水平 (15/100)。",
    time: "10:24",
  },
  {
    uisl: "alertListRealtime.children[\"alertOrder\"]",
    icon: "info",
    tone: "info",
    title: "新订单已生成",
    description: "来自华东区的批量采购订单已进入待审核队列。",
    time: "09:15",
  },
  {
    uisl: "alertListRealtime.children[\"alertSync\"]",
    icon: "check_circle",
    tone: "success",
    title: "同步任务完成",
    description: "昨日财务数据已全量同步至管理后台。",
    time: "08:00",
  },
];

const navItems: NavItem[] = [
  { uisl: "bottomNavDashboard.children[\"navOverview\"]", icon: "dashboard", label: "Overview", active: true },
  { uisl: "bottomNavDashboard.children[\"navAnalytics\"]", icon: "insights", label: "Analytics" },
  { uisl: "bottomNavDashboard.children[\"navReports\"]", icon: "description", label: "Reports" },
  { uisl: "bottomNavDashboard.children[\"navSettings\"]", icon: "settings", label: "Settings" },
];

const iconPaths: Record<IconName, React.ReactNode> = {
  notifications: (
    <path d="M18 16v-5c0-3.1-1.6-5.4-4.5-6.2V3a1.5 1.5 0 0 0-3 0v1.8C7.6 5.6 6 7.9 6 11v5l-1.7 1.7A.8.8 0 0 0 4.9 19h14.2a.8.8 0 0 0 .6-1.3L18 16Zm-8 5h4a2 2 0 0 1-4 0Z" />
  ),
  trending_up: <path d="m4 15 5-5 4 4 7-8v5h-2V9.4l-4.9 5.5-4-4L5.4 16.6 4 15Z" />,
  trending_down: <path d="m4 9 5 5 4-4 7 8v-5h-2v1.6l-4.9-5.5-4 4L5.4 7.4 4 9Z" />,
  expand_more: <path d="m7 9 5 5 5-5H7Z" />,
  warning: <path d="M12 3 2.6 20h18.8L12 3Zm1 14h-2v-2h2v2Zm0-4h-2V8h2v5Z" />,
  info: <path d="M11 17h2v-6h-2v6Zm0-8h2V7h-2v2Zm1 13a10 10 0 1 1 0-20 10 10 0 0 1 0 20Z" />,
  check_circle: <path d="m10.6 15.3 6-6-1.4-1.4-4.6 4.6-1.8-1.8-1.4 1.4 3.2 3.2ZM12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20Z" />,
  dashboard: <path d="M4 4h7v7H4V4Zm9 0h7v7h-7V4ZM4 13h7v7H4v-7Zm9 0h7v7h-7v-7Z" />,
  insights: <path d="M4 18h16v2H4v-2Zm1-3 4-4 3 3 6-7 1.5 1.3-7.5 8.8-3-3-2.6 2.6L5 15Z" />,
  description: <path d="M6 2h9l5 5v15H6V2Zm8 1.8V8h4.2L14 3.8ZM8 12h8v2H8v-2Zm0 4h8v2H8v-2Z" />,
  settings: <path d="m19.4 13.5.1-1.5-.1-1.5 2-1.5-2-3.5-2.4 1a7.7 7.7 0 0 0-2.6-1.5L14 2h-4l-.4 3a7.7 7.7 0 0 0-2.6 1.5l-2.4-1-2 3.5 2 1.5L4.5 12l.1 1.5-2 1.5 2 3.5 2.4-1a7.7 7.7 0 0 0 2.6 1.5l.4 3h4l.4-3a7.7 7.7 0 0 0 2.6-1.5l2.4 1 2-3.5-2-1.5ZM12 15.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7Z" />,
};

function Icon({ name, className = "" }: { name: IconName; className?: string }) {
  return (
    <svg className={`icon ${className}`} viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      {iconPaths[name]}
    </svg>
  );
}

function TopAppBar({ onNotify }: { onNotify: () => void }) {
  return (
    <header className="top-app-bar" data-uisl="topAppBarDashboard">
      <div className="brand-group">
        <div className="avatar" data-uisl="topAppBarDashboard.children[&quot;avatarUser&quot;]" aria-label="专业商务头像">
          <span aria-hidden="true" />
        </div>
        <h1 data-uisl="topAppBarDashboard.children[&quot;title&quot;]">数据大屏</h1>
      </div>
      <button
        className="icon-button"
        type="button"
        aria-label="通知"
        data-uisl="topAppBarDashboard.actions[&quot;notifications&quot;]"
        onClick={onNotify}
      >
        <Icon name="notifications" />
      </button>
    </header>
  );
}

function MetricCard({ metric }: { metric: Metric }) {
  const isDown = metric.trendDirection === "down";

  return (
    <article className="metric-card" data-uisl={metric.uisl}>
      <div className="metric-heading">
        <span className="metric-label">{metric.label}</span>
        {metric.trend ? (
          <span className={isDown ? "metric-trend danger" : "metric-trend success"}>
            {metric.trend}
            <Icon name={isDown ? "trending_down" : "trending_up"} />
          </span>
        ) : (
          <span className="metric-status">{metric.status}</span>
        )}
      </div>
      <strong className="metric-value">{metric.value}</strong>
      <svg className="sparkline" viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true">
        <path d={metric.path} className={isDown ? "sparkline-path danger-stroke" : "sparkline-path"} />
      </svg>
    </article>
  );
}

function MetricGrid() {
  return (
    <section className="metric-grid" aria-label="关键指标" data-uisl="metricGridDashboard">
      {metrics.map((metric) => (
        <MetricCard metric={metric} key={metric.uisl} />
      ))}
    </section>
  );
}

function GrowthChartCard({ rangeLabel, onRangeClick }: { rangeLabel: string; onRangeClick: () => void }) {
  const labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];

  return (
    <section className="panel chart-card" aria-label="业务增长趋势" data-uisl="chartBusinessGrowth">
      <div className="panel-header">
        <h2>业务增长趋势</h2>
        <button className="range-button" type="button" data-uisl="chartBusinessGrowth.actions[&quot;timeRange&quot;]" onClick={onRangeClick}>
          {rangeLabel}
          <Icon name="expand_more" />
        </button>
      </div>
      <div className="chart-wrap" data-uisl="chartBusinessGrowth.children[&quot;areaChart&quot;]" role="img" aria-label="业务增长趋势折线面积图">
        <svg viewBox="0 0 400 150" preserveAspectRatio="none">
          <defs>
            <linearGradient id="blueGradient" x1="0%" x2="0%" y1="0%" y2="100%">
              <stop offset="0%" stopColor="#1a73e8" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#1a73e8" stopOpacity="0" />
            </linearGradient>
          </defs>
          <line className="grid-line" x1="0" x2="400" y1="0" y2="0" />
          <line className="grid-line" x1="0" x2="400" y1="50" y2="50" />
          <line className="grid-line" x1="0" x2="400" y1="100" y2="100" />
          <line className="grid-line" x1="0" x2="400" y1="150" y2="150" />
          <path
            className="area-fill"
            d="M0,130 C50,110 100,140 150,90 C200,40 250,70 300,50 C350,30 400,10 400,10 L400,150 L0,150 Z"
          />
          <path className="area-line" d="M0,130 C50,110 100,140 150,90 C200,40 250,70 300,50 C350,30 400,10" />
          <circle cx="150" cy="90" r="4" />
          <circle cx="400" cy="10" r="4" />
        </svg>
        <div className="axis-labels" aria-hidden="true">
          {labels.map((label) => (
            <span key={label}>{label}</span>
          ))}
        </div>
      </div>
    </section>
  );
}

function AlertList({ onViewAll, onAlertClick }: { onViewAll: () => void; onAlertClick: (title: string) => void }) {
  return (
    <section className="panel alert-list" aria-label="实时预警" data-uisl="alertListRealtime">
      <div className="panel-header alert-header">
        <h2>实时预警</h2>
        <a
          href="/alerts"
          data-uisl="alertListRealtime.actions[&quot;viewAll&quot;]"
          onClick={(event) => {
            event.preventDefault();
            onViewAll();
          }}
        >
          查看全部
        </a>
      </div>
      <div className="alert-items">
        {alerts.map((alert) => (
          <a
            className="alert-item"
            href="#"
            data-uisl={alert.uisl}
            key={alert.uisl}
            onClick={(event) => {
              event.preventDefault();
              onAlertClick(alert.title);
            }}
          >
            <span className={`alert-icon ${alert.tone}`}>
              <Icon name={alert.icon} />
            </span>
            <span className="alert-copy">
              <span className="alert-title-row">
                <strong>{alert.title}</strong>
                <time>{alert.time}</time>
              </span>
              <span>{alert.description}</span>
            </span>
          </a>
        ))}
      </div>
    </section>
  );
}

function BottomNav({ activeNav, onSelect }: { activeNav: string; onSelect: (label: string) => void }) {
  return (
    <nav className="bottom-nav" aria-label="底部导航" data-uisl="bottomNavDashboard">
      {navItems.map((item) => (
        <a
          className={activeNav === item.label ? "nav-item active" : "nav-item"}
          href="#"
          data-uisl={item.uisl}
          key={item.uisl}
          onClick={(event) => {
            event.preventDefault();
            onSelect(item.label);
          }}
          aria-current={activeNav === item.label ? "page" : undefined}
        >
          <Icon name={item.icon} />
          <span>{item.label}</span>
        </a>
      ))}
    </nav>
  );
}

export default function DashboardPage() {
  const [toast, setToast] = useState("就绪");
  const [activeNav, setActiveNav] = useState("Overview");
  const [rangeLabel, setRangeLabel] = useState("最近7天");

  function showToast(message: string) {
    setToast(message);
  }

  function toggleRange() {
    const nextRange = rangeLabel === "最近7天" ? "最近30天" : "最近7天";
    setRangeLabel(nextRange);
    showToast(`已切换为${nextRange}`);
  }

  function selectNav(label: string) {
    setActiveNav(label);
    showToast(`已切换到 ${label}`);
  }

  return (
    <>
      <TopAppBar onNotify={() => showToast("通知中心")} />
      <main className="dashboard-shell" data-uisl="page">
        <MetricGrid />
        <div className="content-grid" data-uisl="contentGridDashboard">
          <GrowthChartCard rangeLabel={rangeLabel} onRangeClick={toggleRange} />
          <AlertList onViewAll={() => showToast("查看全部预警")} onAlertClick={(title) => showToast(title)} />
        </div>
      </main>
      <BottomNav activeNav={activeNav} onSelect={selectNav} />
      <div className="toast" role="status" aria-live="polite" data-uisl="toast">
        {toast}
      </div>
    </>
  );
}

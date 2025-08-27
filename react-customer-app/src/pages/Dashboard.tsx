// /src/pages/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, TrendingUp, DollarSign, Target } from 'lucide-react';
import { KpiCard } from '../components/KpiCard';
import { api, KpiStats } from '../api/mockData';
import tokens from '../design/tokens.json';

// 简单的图表组件（实际项目中应使用 Chart.js 或 ECharts）
const SimpleChart: React.FC<{ data: Array<{ date: string; value: number }> }> = ({ data }) => {
  const maxValue = Math.max(...data.map(d => d.value));
  const chartHeight = 200;
  
  const chartStyles: React.CSSProperties = {
    height: `${chartHeight}px`,
    display: 'flex',
    alignItems: 'flex-end',
    gap: '2px',
    padding: `${tokens.spacing.md}px`,
    background: tokens.color.background.default,
    borderRadius: `${tokens.borderRadius.base}px`,
    boxShadow: tokens.shadow.sm
  };
  
  return (
    <div style={chartStyles}>
      {data.map((item, index) => {
        const height = (item.value / maxValue) * (chartHeight - 32);
        return (
          <div
            key={index}
            style={{
              flex: 1,
              height: `${height}px`,
              background: tokens.color.primary[500],
              borderRadius: `${tokens.borderRadius.sm}px ${tokens.borderRadius.sm}px 0 0`,
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = tokens.color.primary[600];
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = tokens.color.primary[500];
            }}
            title={`${item.date}: ¥${item.value.toLocaleString()}`}
          />
        );
      })}
    </div>
  );
};

const PieChart: React.FC<{ data: Array<{ channel: string; percentage: number }> }> = ({ data }) => {
  const colors = [
    tokens.color.primary[500],
    tokens.color.success[500],
    tokens.color.warning[500],
    tokens.color.danger[500],
    tokens.color.gray[500]
  ];
  
  const chartStyles: React.CSSProperties = {
    padding: `${tokens.spacing.lg}px`,
    background: tokens.color.background.default,
    borderRadius: `${tokens.borderRadius.base}px`,
    boxShadow: tokens.shadow.sm
  };
  
  const legendStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: `${tokens.spacing.sm}px`,
    marginTop: `${tokens.spacing.md}px`
  };
  
  return (
    <div style={chartStyles}>
      <h3 style={{ 
        fontSize: `${tokens.typography.fontSize.lg}px`,
        fontWeight: tokens.typography.fontWeight.semibold,
        marginBottom: `${tokens.spacing.md}px`
      }}>
        渠道分布
      </h3>
      <div style={legendStyles}>
        {data.map((item, index) => (
          <div key={item.channel} style={{ display: 'flex', alignItems: 'center', gap: `${tokens.spacing.sm}px` }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: colors[index % colors.length]
            }} />
            <span style={{ fontSize: `${tokens.typography.fontSize.sm}px` }}>
              {item.channel}: {item.percentage}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [kpiStats, setKpiStats] = useState<KpiStats | null>(null);
  const [trendData, setTrendData] = useState<Array<{ date: string; value: number }>>([]);
  const [channelData, setChannelData] = useState<Array<{ channel: string; value: number; percentage: number }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [stats, trend, channels] = await Promise.all([
        api.getKpiStats(),
        api.getTrendData('week'),
        api.getChannelData()
      ]);
      
      setKpiStats(stats);
      setTrendData(trend);
      setChannelData(channels);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const containerStyles: React.CSSProperties = {
    padding: `${tokens.spacing.lg}px`,
    background: tokens.color.background.secondary,
    minHeight: '100vh'
  };

  const headerStyles: React.CSSProperties = {
    marginBottom: `${tokens.spacing.xl}px`
  };

  const titleStyles: React.CSSProperties = {
    fontSize: `${tokens.typography.fontSize['3xl']}px`,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.color.text.primary,
    marginBottom: `${tokens.spacing.sm}px`
  };

  const subtitleStyles: React.CSSProperties = {
    fontSize: `${tokens.typography.fontSize.base}px`,
    color: tokens.color.text.secondary
  };

  const kpiGridStyles: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: `${tokens.spacing.lg}px`,
    marginBottom: `${tokens.spacing.xl}px`
  };

  const chartsGridStyles: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: `${tokens.spacing.lg}px`,
    marginBottom: `${tokens.spacing.xl}px`
  };

  const linkButtonStyles: React.CSSProperties = {
    display: 'inline-block',
    padding: `${tokens.spacing.md}px ${tokens.spacing.lg}px`,
    background: tokens.color.primary[500],
    color: tokens.color.text.inverse,
    borderRadius: `${tokens.borderRadius.base}px`,
    textDecoration: 'none',
    fontWeight: tokens.typography.fontWeight.medium,
    fontSize: `${tokens.typography.fontSize.base}px`,
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    border: 'none'
  };

  return (
    <div style={containerStyles}>
      <header style={headerStyles}>
        <h1 style={titleStyles}>客户管理系统</h1>
        <p style={subtitleStyles}>实时监控业务数据，优化客户体验</p>
      </header>

      {/* KPI 卡片 */}
      <div style={kpiGridStyles}>
        <KpiCard
          title="总客户数"
          value={kpiStats?.totalCustomers || 0}
          trend={{ value: 12.5, isPositive: true }}
          icon={<Users size={20} />}
          onClick={() => navigate('/customers')}
          loading={loading}
        />
        <KpiCard
          title="活跃客户"
          value={kpiStats?.activeCustomers || 0}
          trend={{ value: 8.3, isPositive: true }}
          icon={<Target size={20} />}
          onClick={() => navigate('/customers?status=active')}
          loading={loading}
        />
        <KpiCard
          title="总收入"
          value={`¥${(kpiStats?.totalRevenue || 0).toLocaleString()}`}
          trend={{ value: 15.7, isPositive: true }}
          icon={<DollarSign size={20} />}
          onClick={() => navigate('/customers?sort=revenue')}
          loading={loading}
        />
        <KpiCard
          title="转化率"
          value={`${(kpiStats?.conversionRate || 0).toFixed(1)}%`}
          trend={{ value: -2.3, isPositive: false }}
          icon={<TrendingUp size={20} />}
          onClick={() => navigate('/customers?status=active')}
          loading={loading}
        />
      </div>

      {/* 图表区域 */}
      <div style={chartsGridStyles}>
        <div>
          <h3 style={{ 
            fontSize: `${tokens.typography.fontSize.lg}px`,
            fontWeight: tokens.typography.fontWeight.semibold,
            marginBottom: `${tokens.spacing.md}px`
          }}>
            收入趋势（最近7天）
          </h3>
          <SimpleChart data={trendData} />
        </div>
        <PieChart data={channelData} />
      </div>

      {/* 快速操作 */}
      <div style={{ textAlign: 'center' }}>
        <button
          style={linkButtonStyles}
          onClick={() => navigate('/customers')}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = tokens.color.primary[600];
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = tokens.color.primary[500];
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          查看所有客户 →
        </button>
      </div>
    </div>
  );
};
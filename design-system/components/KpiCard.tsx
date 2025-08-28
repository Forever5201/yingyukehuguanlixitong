import React from 'react';
import type { FC } from 'react';

export interface KpiCardProps {
  value: string | number;
  label: string;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  icon?: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export const KpiCard: FC<KpiCardProps> = ({
  value,
  label,
  trend,
  icon,
  onClick,
  className = '',
}) => {
  return (
    <div
      className={`kpi-card ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {icon && (
        <div className="kpi-card__icon" aria-hidden="true">
          {icon}
        </div>
      )}
      <div className="kpi-card__content">
        <div className="kpi-card__value">{value}</div>
        <div className="kpi-card__label">{label}</div>
        {trend && (
          <div
            className={`kpi-card__trend kpi-card__trend--${trend.direction}`}
            aria-label={`${trend.direction === 'up' ? '上升' : '下降'} ${Math.abs(trend.value)}%`}
          >
            <span className="kpi-card__trend-icon" aria-hidden="true">
              {trend.direction === 'up' ? '↑' : '↓'}
            </span>
            <span className="kpi-card__trend-value">
              {trend.value > 0 ? '+' : ''}{trend.value}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

// Storybook Story
export default {
  title: 'Components/KpiCard',
  component: KpiCard,
  argTypes: {
    onClick: { action: 'clicked' },
  },
};

const Template = (args: KpiCardProps) => <KpiCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  value: '1,856',
  label: '总客户数',
};

export const WithTrendUp = Template.bind({});
WithTrendUp.args = {
  value: '¥486,750',
  label: '总收入',
  trend: {
    value: 12.5,
    direction: 'up',
  },
};

export const WithTrendDown = Template.bind({});
WithTrendDown.args = {
  value: '68.5%',
  label: '转化率',
  trend: {
    value: -3.2,
    direction: 'down',
  },
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  value: '23',
  label: '今日新增',
  icon: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
      <path d="M15 12c0 1.654-1.346 3-3 3s-3-1.346-3-3 1.346-3 3-3 3 1.346 3 3zm9-.449s-4.252 8.449-11.985 8.449c-7.18 0-12.015-8.449-12.015-8.449s4.446-7.551 12.015-7.551c7.694 0 11.985 7.551 11.985 7.551zm-7 .449c0-2.757-2.243-5-5-5s-5 2.243-5 5 2.243 5 5 5 5-2.243 5-5z"/>
    </svg>
  ),
  trend: {
    value: 8.3,
    direction: 'up',
  },
};

export const Clickable = Template.bind({});
Clickable.args = {
  value: '156',
  label: '待处理订单',
  onClick: () => console.log('KPI Card clicked'),
};

// CSS for the component
export const kpiCardStyles = `
.kpi-card {
  position: relative;
  background: var(--color-kpi-bg);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-kpi);
  transition: all var(--duration-normal) var(--easing-smooth);
  cursor: default;
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
}

.kpi-card[role="button"] {
  cursor: pointer;
}

.kpi-card[role="button"]:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.kpi-card[role="button"]:active {
  transform: translateY(0);
  box-shadow: var(--shadow-md);
}

.kpi-card[role="button"]:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.kpi-card__icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-base);
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-card__content {
  flex: 1;
}

.kpi-card__value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-kpi-value);
  line-height: var(--line-height-tight);
  margin-bottom: var(--spacing-xs);
}

.kpi-card__label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
}

.kpi-card__trend {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.kpi-card__trend--up {
  color: var(--color-kpi-trend-up);
}

.kpi-card__trend--down {
  color: var(--color-kpi-trend-down);
}

.kpi-card__trend-icon {
  font-size: var(--font-size-base);
}
`;
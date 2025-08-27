// /src/components/KpiCard.tsx
import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import tokens from '../design/tokens.json';

interface KpiCardProps {
  title: string;
  value: string | number;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  onClick?: () => void;
  loading?: boolean;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  trend,
  icon,
  onClick,
  loading = false
}) => {
  const cardStyles: React.CSSProperties = {
    background: tokens.color.background.default,
    border: `1px solid ${tokens.color.border.default}`,
    borderRadius: `${tokens.borderRadius.base}px`,
    padding: `${tokens.spacing.lg}px`,
    cursor: onClick ? 'pointer' : 'default',
    transition: 'all 0.3s ease',
    boxShadow: tokens.shadow.sm,
    position: 'relative',
    overflow: 'hidden'
  };

  const titleStyles: React.CSSProperties = {
    fontSize: `${tokens.typography.fontSize.sm}px`,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.color.text.secondary,
    marginBottom: `${tokens.spacing.sm}px`
  };

  const valueStyles: React.CSSProperties = {
    fontSize: `${tokens.typography.fontSize['2xl']}px`,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.color.text.primary,
    lineHeight: tokens.typography.lineHeight.tight
  };

  const trendStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: `${tokens.spacing.xs}px`,
    marginTop: `${tokens.spacing.sm}px`,
    fontSize: `${tokens.typography.fontSize.sm}px`,
    fontWeight: tokens.typography.fontWeight.medium,
    color: trend?.isPositive ? tokens.color.success[600] : tokens.color.danger[600]
  };

  const iconStyles: React.CSSProperties = {
    position: 'absolute',
    top: `${tokens.spacing.lg}px`,
    right: `${tokens.spacing.lg}px`,
    width: '40px',
    height: '40px',
    borderRadius: `${tokens.borderRadius.full}px`,
    background: tokens.color.primary[50],
    color: tokens.color.primary[600],
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  const handleClick = () => {
    if (onClick) onClick();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick();
    }
  };

  if (loading) {
    return (
      <div style={cardStyles}>
        <div style={{ ...titleStyles, background: tokens.color.gray[200], width: '60%', height: '16px', borderRadius: '4px' }}></div>
        <div style={{ ...valueStyles, background: tokens.color.gray[200], width: '80%', height: '32px', borderRadius: '4px', marginTop: '8px' }}></div>
      </div>
    );
  }

  return (
    <div
      style={cardStyles}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.boxShadow = tokens.shadow.md;
          e.currentTarget.style.transform = 'translateY(-2px)';
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          e.currentTarget.style.boxShadow = tokens.shadow.sm;
          e.currentTarget.style.transform = 'translateY(0)';
        }
      }}
    >
      {icon && (
        <div style={iconStyles}>
          {icon}
        </div>
      )}
      
      <div style={titleStyles}>{title}</div>
      <div style={valueStyles}>{value}</div>
      
      {trend && (
        <div style={trendStyles}>
          {trend.isPositive ? (
            <TrendingUp size={16} />
          ) : (
            <TrendingDown size={16} />
          )}
          <span>{trend.isPositive ? '+' : ''}{trend.value}%</span>
        </div>
      )}
    </div>
  );
};
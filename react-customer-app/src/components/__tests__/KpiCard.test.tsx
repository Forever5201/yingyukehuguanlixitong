// /src/components/__tests__/KpiCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { KpiCard } from '../KpiCard';
import { Users } from 'lucide-react';

describe('KpiCard Component', () => {
  const defaultProps = {
    title: 'Total Customers',
    value: '1,234'
  };

  it('renders the value correctly', () => {
    render(<KpiCard {...defaultProps} />);
    
    const valueElement = screen.getByText('1,234');
    expect(valueElement).toBeInTheDocument();
  });

  it('renders the title correctly', () => {
    render(<KpiCard {...defaultProps} />);
    
    const titleElement = screen.getByText('Total Customers');
    expect(titleElement).toBeInTheDocument();
  });

  it('renders trend when provided', () => {
    const props = {
      ...defaultProps,
      trend: { value: 12.5, isPositive: true }
    };
    
    render(<KpiCard {...props} />);
    
    const trendElement = screen.getByText('+12.5%');
    expect(trendElement).toBeInTheDocument();
  });

  it('renders negative trend correctly', () => {
    const props = {
      ...defaultProps,
      trend: { value: -5.3, isPositive: false }
    };
    
    render(<KpiCard {...props} />);
    
    const trendElement = screen.getByText('-5.3%');
    expect(trendElement).toBeInTheDocument();
  });

  it('renders icon when provided', () => {
    const props = {
      ...defaultProps,
      icon: <Users data-testid="users-icon" />
    };
    
    render(<KpiCard {...props} />);
    
    const iconElement = screen.getByTestId('users-icon');
    expect(iconElement).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    const props = {
      ...defaultProps,
      onClick: handleClick
    };
    
    render(<KpiCard {...props} />);
    
    const card = screen.getByRole('button');
    fireEvent.click(card);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('triggers onClick with keyboard Enter', () => {
    const handleClick = jest.fn();
    const props = {
      ...defaultProps,
      onClick: handleClick
    };
    
    render(<KpiCard {...props} />);
    
    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: 'Enter' });
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('triggers onClick with keyboard Space', () => {
    const handleClick = jest.fn();
    const props = {
      ...defaultProps,
      onClick: handleClick
    };
    
    render(<KpiCard {...props} />);
    
    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: ' ' });
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders loading state', () => {
    const props = {
      ...defaultProps,
      loading: true
    };
    
    render(<KpiCard {...props} />);
    
    // 加载状态下不应该显示实际值
    const valueElement = screen.queryByText('1,234');
    expect(valueElement).not.toBeInTheDocument();
  });

  it('does not have button role when onClick is not provided', () => {
    render(<KpiCard {...defaultProps} />);
    
    const card = screen.queryByRole('button');
    expect(card).not.toBeInTheDocument();
  });

  it('renders with number value', () => {
    const props = {
      ...defaultProps,
      value: 5678
    };
    
    render(<KpiCard {...props} />);
    
    const valueElement = screen.getByText('5678');
    expect(valueElement).toBeInTheDocument();
  });
});

// Vitest 版本示例（如果使用 Vitest 替代 Jest）:
/*
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { KpiCard } from '../KpiCard';
import { Users } from 'lucide-react';

describe('KpiCard Component', () => {
  const defaultProps = {
    title: 'Total Customers',
    value: '1,234'
  };

  it('renders the value correctly', () => {
    render(<KpiCard {...defaultProps} />);
    
    const valueElement = screen.getByText('1,234');
    expect(valueElement).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    const props = {
      ...defaultProps,
      onClick: handleClick
    };
    
    render(<KpiCard {...props} />);
    
    const card = screen.getByRole('button');
    fireEvent.click(card);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
*/
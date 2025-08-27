// /src/components/CustomerTable.tsx
import React, { useState, useCallback, useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';
import { MoreVertical, Eye, Edit, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import tokens from '../design/tokens.json';

export interface Customer {
  id: number;
  name: string;
  phone: string;
  email?: string;
  status: 'active' | 'inactive' | 'pending';
  source: string;
  revenue: number;
  createdAt: string;
  region?: string;
  grade?: string;
  gender?: string;
}

interface Column {
  key: keyof Customer;
  title: string;
  width?: number;
  sortable?: boolean;
  collapsible?: boolean;
}

interface CustomerTableProps {
  data: Customer[];
  onRowClick?: (customer: Customer) => void;
  onAction?: (action: string, customer: Customer) => void;
  loading?: boolean;
}

const columns: Column[] = [
  { key: 'name', title: '客户姓名', width: 150, sortable: true },
  { key: 'phone', title: '联系电话', width: 150 },
  { key: 'email', title: '邮箱', width: 200, collapsible: true },
  { key: 'status', title: '状态', width: 100, sortable: true },
  { key: 'source', title: '来源', width: 120, collapsible: true },
  { key: 'revenue', title: '收入', width: 120, sortable: true },
  { key: 'region', title: '地区', width: 100, collapsible: true },
  { key: 'createdAt', title: '创建时间', width: 150, sortable: true }
];

export const CustomerTable: React.FC<CustomerTableProps> = ({
  data,
  onRowClick,
  onAction,
  loading = false
}) => {
  const [sortConfig, setSortConfig] = useState<{ key: keyof Customer; direction: 'asc' | 'desc' } | null>(null);
  const [collapsedColumns, setCollapsedColumns] = useState<Set<string>>(new Set());
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  const ROW_HEIGHT = 48;

  // 列收缩切换
  const toggleColumn = (key: string) => {
    const newSet = new Set(collapsedColumns);
    if (newSet.has(key)) {
      newSet.delete(key);
    } else {
      newSet.add(key);
    }
    setCollapsedColumns(newSet);
  };

  // 排序逻辑
  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [data, sortConfig]);

  // 处理排序
  const handleSort = (key: keyof Customer) => {
    setSortConfig(current => {
      if (current?.key === key) {
        return {
          key,
          direction: current.direction === 'asc' ? 'desc' : 'asc'
        };
      }
      return { key, direction: 'asc' };
    });
  };

  // 过滤显示的列
  const visibleColumns = columns.filter(col => !collapsedColumns.has(col.key));

  // 表格样式
  const tableStyles: React.CSSProperties = {
    background: tokens.color.background.default,
    borderRadius: `${tokens.borderRadius.base}px`,
    boxShadow: tokens.shadow.md,
    overflow: 'hidden'
  };

  const headerStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    background: tokens.color.background.secondary,
    borderBottom: `1px solid ${tokens.color.border.default}`,
    fontWeight: tokens.typography.fontWeight.semibold,
    fontSize: `${tokens.typography.fontSize.sm}px`,
    color: tokens.color.text.secondary,
    height: `${ROW_HEIGHT}px`,
    paddingLeft: `${tokens.spacing.md}px`,
    paddingRight: `${tokens.spacing.lg + 40}px` // 为操作列留空间
  };

  const cellStyles: React.CSSProperties = {
    padding: `0 ${tokens.spacing.md}px`,
    display: 'flex',
    alignItems: 'center',
    fontSize: `${tokens.typography.fontSize.sm}px`,
    color: tokens.color.text.primary,
    borderRight: `1px solid ${tokens.color.border.secondary}`
  };

  // 行渲染
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const customer = sortedData[index];
    
    const rowStyles: React.CSSProperties = {
      ...style,
      display: 'flex',
      alignItems: 'center',
      borderBottom: `1px solid ${tokens.color.border.default}`,
      cursor: 'pointer',
      transition: 'background-color 0.2s',
      paddingLeft: `${tokens.spacing.md}px`,
      paddingRight: `${tokens.spacing.md}px`
    };

    const statusStyles: React.CSSProperties = {
      padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px`,
      borderRadius: `${tokens.borderRadius.full}px`,
      fontSize: `${tokens.typography.fontSize.xs}px`,
      fontWeight: tokens.typography.fontWeight.medium,
      ...(customer.status === 'active' ? {
        background: tokens.color.success[50],
        color: tokens.color.success[700]
      } : customer.status === 'inactive' ? {
        background: tokens.color.gray[100],
        color: tokens.color.gray[600]
      } : {
        background: tokens.color.warning[50],
        color: tokens.color.warning[700]
      })
    };

    const kebabMenuStyles: React.CSSProperties = {
      position: 'absolute',
      right: `${tokens.spacing.md}px`,
      top: '50%',
      transform: 'translateY(-50%)',
      background: tokens.color.background.default,
      border: `1px solid ${tokens.color.border.default}`,
      borderRadius: `${tokens.borderRadius.sm}px`,
      boxShadow: tokens.shadow.lg,
      zIndex: 10,
      minWidth: '120px'
    };

    const menuItemStyles: React.CSSProperties = {
      padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
      display: 'flex',
      alignItems: 'center',
      gap: `${tokens.spacing.sm}px`,
      cursor: 'pointer',
      fontSize: `${tokens.typography.fontSize.sm}px`,
      color: tokens.color.text.primary,
      transition: 'background-color 0.2s'
    };

    return (
      <div
        style={rowStyles}
        onClick={() => onRowClick?.(customer)}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = tokens.color.background.secondary;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        {visibleColumns.map(column => (
          <div
            key={column.key}
            style={{ ...cellStyles, width: column.width || 'auto', flex: column.width ? 'none' : 1 }}
          >
            {column.key === 'status' ? (
              <span style={statusStyles}>
                {customer.status === 'active' ? '活跃' : customer.status === 'inactive' ? '非活跃' : '待处理'}
              </span>
            ) : column.key === 'revenue' ? (
              `¥${customer.revenue.toLocaleString()}`
            ) : column.key === 'createdAt' ? (
              new Date(customer.createdAt).toLocaleDateString('zh-CN')
            ) : (
              customer[column.key] || '-'
            )}
          </div>
        ))}
        
        <div style={{ width: '40px', position: 'relative' }}>
          <button
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: `${tokens.spacing.xs}px`,
              color: tokens.color.text.secondary
            }}
            onClick={(e) => {
              e.stopPropagation();
              setOpenMenuId(openMenuId === customer.id ? null : customer.id);
            }}
          >
            <MoreVertical size={16} />
          </button>
          
          {openMenuId === customer.id && (
            <div style={kebabMenuStyles}>
              <div
                style={menuItemStyles}
                onClick={(e) => {
                  e.stopPropagation();
                  onAction?.('view', customer);
                  setOpenMenuId(null);
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = tokens.color.background.secondary;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <Eye size={14} />
                查看
              </div>
              <div
                style={menuItemStyles}
                onClick={(e) => {
                  e.stopPropagation();
                  onAction?.('edit', customer);
                  setOpenMenuId(null);
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = tokens.color.background.secondary;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <Edit size={14} />
                编辑
              </div>
              <div
                style={{
                  ...menuItemStyles,
                  color: tokens.color.danger[600],
                  borderTop: `1px solid ${tokens.color.border.default}`
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  onAction?.('delete', customer);
                  setOpenMenuId(null);
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = tokens.color.danger[50];
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <Trash2 size={14} />
                删除
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // 列折叠控制栏
  const collapsibleBar: React.CSSProperties = {
    padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
    background: tokens.color.background.tertiary,
    borderBottom: `1px solid ${tokens.color.border.default}`,
    display: 'flex',
    gap: `${tokens.spacing.sm}px`,
    fontSize: `${tokens.typography.fontSize.xs}px`
  };

  const collapsibleBtnStyles: React.CSSProperties = {
    padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px`,
    background: tokens.color.background.default,
    border: `1px solid ${tokens.color.border.default}`,
    borderRadius: `${tokens.borderRadius.sm}px`,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: `${tokens.spacing.xs}px`,
    fontSize: `${tokens.typography.fontSize.xs}px`,
    transition: 'all 0.2s'
  };

  if (loading) {
    return (
      <div style={tableStyles}>
        <div style={{ padding: `${tokens.spacing.xl}px`, textAlign: 'center' }}>
          加载中...
        </div>
      </div>
    );
  }

  return (
    <div style={tableStyles}>
      {/* 列折叠控制 */}
      <div style={collapsibleBar}>
        <span style={{ marginRight: `${tokens.spacing.sm}px`, color: tokens.color.text.secondary }}>显示列：</span>
        {columns.filter(col => col.collapsible).map(col => (
          <button
            key={col.key}
            style={{
              ...collapsibleBtnStyles,
              ...(collapsedColumns.has(col.key) ? {
                background: tokens.color.gray[100],
                color: tokens.color.text.secondary
              } : {})
            }}
            onClick={() => toggleColumn(col.key)}
          >
            {col.title}
            {collapsedColumns.has(col.key) ? <ChevronDown size={12} /> : <ChevronUp size={12} />}
          </button>
        ))}
      </div>

      {/* 表头 */}
      <div style={headerStyles}>
        {visibleColumns.map(column => (
          <div
            key={column.key}
            style={{
              ...cellStyles,
              width: column.width || 'auto',
              flex: column.width ? 'none' : 1,
              cursor: column.sortable ? 'pointer' : 'default'
            }}
            onClick={() => column.sortable && handleSort(column.key)}
          >
            {column.title}
            {column.sortable && sortConfig?.key === column.key && (
              <span style={{ marginLeft: `${tokens.spacing.xs}px` }}>
                {sortConfig.direction === 'asc' ? '↑' : '↓'}
              </span>
            )}
          </div>
        ))}
        <div style={{ width: '40px' }}>操作</div>
      </div>

      {/* 虚拟化表格主体 */}
      <List
        height={Math.min(600, sortedData.length * ROW_HEIGHT)}
        itemCount={sortedData.length}
        itemSize={ROW_HEIGHT}
        width="100%"
      >
        {Row}
      </List>
    </div>
  );
};

// 如需使用 @tanstack/react-virtual 替换：
// 1. 安装: npm install @tanstack/react-virtual
// 2. 导入: import { useVirtualizer } from '@tanstack/react-virtual'
// 3. 替换 List 组件为:
/*
const parentRef = useRef<HTMLDivElement>(null);
const virtualizer = useVirtualizer({
  count: sortedData.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => ROW_HEIGHT,
  overscan: 5
});

// 渲染部分改为:
<div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
  <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
    {virtualizer.getVirtualItems().map(virtualItem => (
      <div
        key={virtualItem.key}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: `${virtualItem.size}px`,
          transform: `translateY(${virtualItem.start}px)`
        }}
      >
        {Row({ index: virtualItem.index, style: {} })}
      </div>
    ))}
  </div>
</div>
*/
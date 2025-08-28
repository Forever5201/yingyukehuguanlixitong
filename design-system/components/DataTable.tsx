import React, { useState, useCallback } from 'react';
import type { FC, ReactNode } from 'react';
import { FixedSizeList as List } from 'react-window';

export interface Column<T> {
  key: string;
  header: string;
  accessor: (row: T) => ReactNode;
  width?: number;
  sortable?: boolean;
  resizable?: boolean;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  pagination?: {
    currentPage: number;
    totalPages: number;
    pageSize: number;
    onPageChange: (page: number) => void;
  };
  virtualized?: boolean;
  rowHeight?: number;
  maxHeight?: number;
  onRowClick?: (row: T) => void;
  rowKey: (row: T) => string;
}

export function DataTable<T>({
  columns,
  data,
  pagination,
  virtualized = false,
  rowHeight = 48,
  maxHeight = 600,
  onRowClick,
  rowKey,
}: DataTableProps<T>) {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const handleSort = useCallback((key: string) => {
    setSortConfig((current) => {
      if (current?.key === key) {
        return {
          key,
          direction: current.direction === 'asc' ? 'desc' : 'asc',
        };
      }
      return { key, direction: 'asc' };
    });
  }, []);

  const sortedData = React.useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const column = columns.find((col) => col.key === sortConfig.key);
      if (!column) return 0;

      const aValue = column.accessor(a);
      const bValue = column.accessor(b);

      if (aValue === bValue) return 0;
      
      const comparison = aValue < bValue ? -1 : 1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });
  }, [data, sortConfig, columns]);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const row = sortedData[index];
    return (
      <tr
        style={style}
        className="data-table__row"
        onClick={() => onRowClick?.(row)}
        tabIndex={0}
        role="row"
      >
        {columns.map((column) => (
          <td key={column.key} className="data-table__cell">
            {column.accessor(row)}
          </td>
        ))}
      </tr>
    );
  };

  return (
    <div className="data-table">
      <div className="data-table__container">
        <table className="data-table__table">
          <thead className="data-table__header">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`data-table__header-cell ${
                    column.sortable ? 'data-table__header-cell--sortable' : ''
                  }`}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <span className="data-table__header-content">
                    {column.header}
                    {column.sortable && sortConfig?.key === column.key && (
                      <span className="data-table__sort-icon" aria-label={`Sorted ${sortConfig.direction}`}>
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          {virtualized ? (
            <tbody>
              <tr>
                <td colSpan={columns.length} style={{ padding: 0 }}>
                  <List
                    height={maxHeight}
                    itemCount={sortedData.length}
                    itemSize={rowHeight}
                    width="100%"
                  >
                    {Row}
                  </List>
                </td>
              </tr>
            </tbody>
          ) : (
            <tbody className="data-table__body">
              {sortedData.map((row, index) => (
                <tr
                  key={rowKey(row)}
                  className="data-table__row"
                  onClick={() => onRowClick?.(row)}
                  tabIndex={0}
                  role="row"
                >
                  {columns.map((column) => (
                    <td key={column.key} className="data-table__cell">
                      {column.accessor(row)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          )}
        </table>
      </div>
      {pagination && (
        <div className="data-table__pagination">
          <button
            className="data-table__pagination-btn"
            onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
            disabled={pagination.currentPage === 1}
            aria-label="Previous page"
          >
            ←
          </button>
          <span className="data-table__pagination-info">
            第 {pagination.currentPage} 页，共 {pagination.totalPages} 页
          </span>
          <button
            className="data-table__pagination-btn"
            onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
            disabled={pagination.currentPage === pagination.totalPages}
            aria-label="Next page"
          >
            →
          </button>
        </div>
      )}
    </div>
  );
}

// Storybook Story
export default {
  title: 'Components/DataTable',
  component: DataTable,
};

interface CustomerData {
  id: number;
  name: string;
  phone: string;
  status: 'active' | 'inactive' | 'pending';
  revenue: number;
  createdAt: string;
}

const mockData: CustomerData[] = Array.from({ length: 100 }, (_, i) => ({
  id: i + 1,
  name: `客户 ${i + 1}`,
  phone: `138${String(10000000 + i).padStart(8, '0')}`,
  status: ['active', 'inactive', 'pending'][i % 3] as CustomerData['status'],
  revenue: Math.floor(Math.random() * 100000),
  createdAt: new Date(Date.now() - Math.random() * 10000000000).toISOString(),
}));

const columns: Column<CustomerData>[] = [
  {
    key: 'id',
    header: 'ID',
    accessor: (row) => row.id,
    width: 80,
    sortable: true,
  },
  {
    key: 'name',
    header: '客户姓名',
    accessor: (row) => row.name,
    sortable: true,
  },
  {
    key: 'phone',
    header: '联系电话',
    accessor: (row) => row.phone,
  },
  {
    key: 'status',
    header: '状态',
    accessor: (row) => (
      <span className={`status-badge status-badge--${row.status}`}>
        {row.status === 'active' ? '活跃' : row.status === 'inactive' ? '非活跃' : '待处理'}
      </span>
    ),
    sortable: true,
  },
  {
    key: 'revenue',
    header: '收入',
    accessor: (row) => `¥${row.revenue.toLocaleString()}`,
    sortable: true,
  },
  {
    key: 'createdAt',
    header: '创建时间',
    accessor: (row) => new Date(row.createdAt).toLocaleDateString(),
    sortable: true,
  },
];

export const Default = () => (
  <DataTable
    columns={columns}
    data={mockData.slice(0, 10)}
    rowKey={(row) => String(row.id)}
  />
);

export const WithPagination = () => {
  const [currentPage, setCurrentPage] = React.useState(1);
  const pageSize = 10;
  const totalPages = Math.ceil(mockData.length / pageSize);
  
  const paginatedData = mockData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <DataTable
      columns={columns}
      data={paginatedData}
      pagination={{
        currentPage,
        totalPages,
        pageSize,
        onPageChange: setCurrentPage,
      }}
      rowKey={(row) => String(row.id)}
    />
  );
};

export const Virtualized = () => (
  <DataTable
    columns={columns}
    data={mockData}
    virtualized
    maxHeight={400}
    rowHeight={48}
    rowKey={(row) => String(row.id)}
  />
);

export const WithRowClick = () => (
  <DataTable
    columns={columns}
    data={mockData.slice(0, 10)}
    onRowClick={(row) => alert(`Clicked: ${row.name}`)}
    rowKey={(row) => String(row.id)}
  />
);

// CSS for the component
export const dataTableStyles = `
.data-table {
  background: var(--color-background);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.data-table__container {
  overflow-x: auto;
}

.data-table__table {
  width: 100%;
  border-collapse: collapse;
}

.data-table__header {
  background: var(--color-table-header-bg);
  border-bottom: 1px solid var(--color-table-border);
}

.data-table__header-cell {
  padding: var(--spacing-md);
  text-align: left;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.data-table__header-cell--sortable {
  cursor: pointer;
  user-select: none;
}

.data-table__header-cell--sortable:hover {
  background: var(--color-background-tertiary);
}

.data-table__header-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.data-table__sort-icon {
  font-size: var(--font-size-xs);
  color: var(--color-primary);
}

.data-table__body {
  background: var(--color-background);
}

.data-table__row {
  border-bottom: 1px solid var(--color-table-border);
  transition: background var(--duration-fast) var(--easing-ease);
}

.data-table__row:hover {
  background: var(--color-table-row-hover);
}

.data-table__row[tabindex]:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.data-table__cell {
  padding: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.data-table__pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-table-border);
}

.data-table__pagination-btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-ease);
}

.data-table__pagination-btn:hover:not(:disabled) {
  background: var(--color-background-secondary);
  border-color: var(--color-primary);
}

.data-table__pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.data-table__pagination-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Status badge styles */
.status-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.status-badge--active {
  background: rgba(82, 196, 26, 0.1);
  color: var(--color-success);
}

.status-badge--inactive {
  background: rgba(108, 117, 125, 0.1);
  color: var(--color-muted);
}

.status-badge--pending {
  background: rgba(255, 193, 7, 0.1);
  color: var(--color-warning);
}
`;
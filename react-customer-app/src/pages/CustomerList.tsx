// /src/pages/CustomerList.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Plus, Search } from 'lucide-react';
import { CustomerTable, Customer } from '../components/CustomerTable';
import { api } from '../api/mockData';
import tokens from '../design/tokens.json';

export const CustomerList: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [total, setTotal] = useState(0);

  // 从 URL 参数获取筛选条件
  const statusFilter = searchParams.get('status') || '';
  const sortBy = searchParams.get('sort') || '';

  useEffect(() => {
    loadCustomers();
  }, [statusFilter, sortBy]);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const result = await api.getCustomers({
        status: statusFilter || undefined,
        search: searchTerm
      });
      
      let data = result.data;
      
      // 前端排序（实际项目应在后端实现）
      if (sortBy === 'revenue') {
        data = [...data].sort((a, b) => b.revenue - a.revenue);
      }
      
      setCustomers(data);
      setTotal(result.total);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadCustomers();
  };

  const handleAction = (action: string, customer: Customer) => {
    switch (action) {
      case 'view':
        navigate(`/customers/${customer.id}`);
        break;
      case 'edit':
        navigate(`/customers/${customer.id}/edit`);
        break;
      case 'delete':
        if (window.confirm(`确定要删除客户 ${customer.name} 吗？`)) {
          api.deleteCustomer(customer.id).then(() => {
            loadCustomers();
          });
        }
        break;
    }
  };

  const containerStyles: React.CSSProperties = {
    padding: `${tokens.spacing.lg}px`,
    background: tokens.color.background.secondary,
    minHeight: '100vh'
  };

  const headerStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: `${tokens.spacing.xl}px`
  };

  const titleSectionStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: `${tokens.spacing.md}px`
  };

  const backButtonStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: `${tokens.spacing.xs}px`,
    padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
    background: 'none',
    border: `1px solid ${tokens.color.border.default}`,
    borderRadius: `${tokens.borderRadius.base}px`,
    cursor: 'pointer',
    fontSize: `${tokens.typography.fontSize.sm}px`,
    color: tokens.color.text.secondary,
    transition: 'all 0.2s'
  };

  const titleStyles: React.CSSProperties = {
    fontSize: `${tokens.typography.fontSize['2xl']}px`,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.color.text.primary
  };

  const badgeStyles: React.CSSProperties = {
    padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px`,
    background: tokens.color.primary[100],
    color: tokens.color.primary[700],
    borderRadius: `${tokens.borderRadius.full}px`,
    fontSize: `${tokens.typography.fontSize.sm}px`,
    fontWeight: tokens.typography.fontWeight.medium
  };

  const searchFormStyles: React.CSSProperties = {
    display: 'flex',
    gap: `${tokens.spacing.md}px`,
    marginBottom: `${tokens.spacing.lg}px`
  };

  const searchInputStyles: React.CSSProperties = {
    flex: 1,
    padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
    paddingLeft: `${tokens.spacing.xl}px`,
    border: `1px solid ${tokens.color.border.default}`,
    borderRadius: `${tokens.borderRadius.base}px`,
    fontSize: `${tokens.typography.fontSize.base}px`,
    transition: 'all 0.2s'
  };

  const searchButtonStyles: React.CSSProperties = {
    padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
    background: tokens.color.primary[500],
    color: tokens.color.text.inverse,
    border: 'none',
    borderRadius: `${tokens.borderRadius.base}px`,
    fontSize: `${tokens.typography.fontSize.base}px`,
    fontWeight: tokens.typography.fontWeight.medium,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: `${tokens.spacing.xs}px`,
    transition: 'all 0.2s'
  };

  const addButtonStyles: React.CSSProperties = {
    ...searchButtonStyles,
    background: tokens.color.success[500]
  };

  const filterBarStyles: React.CSSProperties = {
    display: 'flex',
    gap: `${tokens.spacing.sm}px`,
    marginBottom: `${tokens.spacing.md}px`,
    fontSize: `${tokens.typography.fontSize.sm}px`
  };

  const filterChipStyles: React.CSSProperties = {
    padding: `${tokens.spacing.xs}px ${tokens.spacing.md}px`,
    background: tokens.color.warning[50],
    color: tokens.color.warning[700],
    borderRadius: `${tokens.borderRadius.full}px`,
    border: `1px solid ${tokens.color.warning[200]}`,
    display: 'flex',
    alignItems: 'center',
    gap: `${tokens.spacing.xs}px`
  };

  return (
    <div style={containerStyles}>
      <header style={headerStyles}>
        <div style={titleSectionStyles}>
          <button
            style={backButtonStyles}
            onClick={() => navigate('/')}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = tokens.color.primary[500];
              e.currentTarget.style.color = tokens.color.primary[500];
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = tokens.color.border.default;
              e.currentTarget.style.color = tokens.color.text.secondary;
            }}
          >
            <ArrowLeft size={16} />
            返回
          </button>
          <h1 style={titleStyles}>客户列表</h1>
          <span style={badgeStyles}>{total} 位客户</span>
        </div>
        
        <button
          style={addButtonStyles}
          onClick={() => navigate('/customers/new')}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = tokens.color.success[600];
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = tokens.color.success[500];
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          <Plus size={16} />
          新增客户
        </button>
      </header>

      {/* 搜索栏 */}
      <form style={searchFormStyles} onSubmit={handleSearch}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search 
            size={16} 
            style={{
              position: 'absolute',
              left: `${tokens.spacing.md}px`,
              top: '50%',
              transform: 'translateY(-50%)',
              color: tokens.color.text.secondary
            }}
          />
          <input
            type="text"
            placeholder="搜索客户姓名、电话或邮箱..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={searchInputStyles}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = tokens.color.border.focus;
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = tokens.color.border.default;
            }}
          />
        </div>
        <button
          type="submit"
          style={searchButtonStyles}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = tokens.color.primary[600];
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = tokens.color.primary[500];
          }}
        >
          <Search size={16} />
          搜索
        </button>
      </form>

      {/* 当前筛选条件 */}
      {(statusFilter || sortBy) && (
        <div style={filterBarStyles}>
          <span style={{ color: tokens.color.text.secondary }}>当前筛选：</span>
          {statusFilter && (
            <span style={filterChipStyles}>
              状态: {statusFilter === 'active' ? '活跃' : statusFilter}
              <button
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer',
                  padding: 0,
                  marginLeft: `${tokens.spacing.xs}px`
                }}
                onClick={() => navigate('/customers')}
              >
                ×
              </button>
            </span>
          )}
          {sortBy && (
            <span style={filterChipStyles}>
              排序: {sortBy === 'revenue' ? '收入' : sortBy}
              <button
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer',
                  padding: 0,
                  marginLeft: `${tokens.spacing.xs}px`
                }}
                onClick={() => navigate('/customers')}
              >
                ×
              </button>
            </span>
          )}
        </div>
      )}

      {/* 客户表格 */}
      <CustomerTable
        data={customers}
        loading={loading}
        onRowClick={(customer) => navigate(`/customers/${customer.id}`)}
        onAction={handleAction}
      />
    </div>
  );
};
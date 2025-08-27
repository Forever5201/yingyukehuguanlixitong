import React, { useState, useEffect } from 'react';
import type { FC, ChangeEvent } from 'react';

export interface FilterOption {
  value: string;
  label: string;
}

export interface FilterField {
  id: string;
  label: string;
  type: 'select' | 'text' | 'date' | 'daterange' | 'checkbox';
  options?: FilterOption[];
  placeholder?: string;
}

export interface FilterValues {
  [key: string]: any;
}

export interface FilterPanelProps {
  fields: FilterField[];
  values: FilterValues;
  onChange: (values: FilterValues) => void;
  onApply?: () => void;
  onReset?: () => void;
  variant?: 'inline' | 'sidebar';
  className?: string;
}

export const FilterPanel: FC<FilterPanelProps> = ({
  fields,
  values,
  onChange,
  onApply,
  onReset,
  variant = 'inline',
  className = '',
}) => {
  const [localValues, setLocalValues] = useState<FilterValues>(values);

  useEffect(() => {
    setLocalValues(values);
  }, [values]);

  const handleFieldChange = (fieldId: string, value: any) => {
    const newValues = { ...localValues, [fieldId]: value };
    setLocalValues(newValues);
    if (!onApply) {
      onChange(newValues);
    }
  };

  const handleApply = () => {
    onChange(localValues);
    onApply?.();
  };

  const handleReset = () => {
    const resetValues = fields.reduce((acc, field) => {
      acc[field.id] = field.type === 'checkbox' ? false : '';
      return acc;
    }, {} as FilterValues);
    setLocalValues(resetValues);
    onChange(resetValues);
    onReset?.();
  };

  const renderField = (field: FilterField) => {
    const value = localValues[field.id] ?? '';

    switch (field.type) {
      case 'select':
        return (
          <select
            className="filter-panel__select"
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            aria-label={field.label}
          >
            <option value="">{field.placeholder || `选择${field.label}`}</option>
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'text':
        return (
          <input
            type="text"
            className="filter-panel__input"
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            placeholder={field.placeholder || `输入${field.label}`}
            aria-label={field.label}
          />
        );

      case 'date':
        return (
          <input
            type="date"
            className="filter-panel__input"
            value={value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            aria-label={field.label}
          />
        );

      case 'daterange':
        return (
          <div className="filter-panel__daterange">
            <input
              type="date"
              className="filter-panel__input"
              value={value.start || ''}
              onChange={(e) =>
                handleFieldChange(field.id, { ...value, start: e.target.value })
              }
              aria-label={`${field.label} 开始日期`}
            />
            <span className="filter-panel__daterange-separator">至</span>
            <input
              type="date"
              className="filter-panel__input"
              value={value.end || ''}
              onChange={(e) =>
                handleFieldChange(field.id, { ...value, end: e.target.value })
              }
              aria-label={`${field.label} 结束日期`}
            />
          </div>
        );

      case 'checkbox':
        return (
          <label className="filter-panel__checkbox">
            <input
              type="checkbox"
              checked={!!value}
              onChange={(e) => handleFieldChange(field.id, e.target.checked)}
              aria-label={field.label}
            />
            <span className="filter-panel__checkbox-label">{field.placeholder || field.label}</span>
          </label>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`filter-panel filter-panel--${variant} ${className}`}>
      <div className="filter-panel__header">
        <h3 className="filter-panel__title">筛选条件</h3>
        {variant === 'sidebar' && (
          <button className="filter-panel__close" aria-label="关闭筛选面板">
            ×
          </button>
        )}
      </div>
      <div className="filter-panel__content">
        {fields.map((field) => (
          <div key={field.id} className="filter-panel__field">
            {field.type !== 'checkbox' && (
              <label className="filter-panel__label">{field.label}</label>
            )}
            {renderField(field)}
          </div>
        ))}
      </div>
      <div className="filter-panel__actions">
        <button
          className="filter-panel__btn filter-panel__btn--secondary"
          onClick={handleReset}
        >
          重置
        </button>
        {onApply && (
          <button
            className="filter-panel__btn filter-panel__btn--primary"
            onClick={handleApply}
          >
            应用筛选
          </button>
        )}
      </div>
    </div>
  );
};

// Storybook Story
export default {
  title: 'Components/FilterPanel',
  component: FilterPanel,
};

const mockFields: FilterField[] = [
  {
    id: 'status',
    label: '客户状态',
    type: 'select',
    options: [
      { value: 'active', label: '活跃' },
      { value: 'inactive', label: '非活跃' },
      { value: 'pending', label: '待处理' },
    ],
  },
  {
    id: 'search',
    label: '搜索',
    type: 'text',
    placeholder: '输入客户姓名或电话',
  },
  {
    id: 'dateRange',
    label: '日期范围',
    type: 'daterange',
  },
  {
    id: 'source',
    label: '客户来源',
    type: 'select',
    options: [
      { value: 'taobao', label: '淘宝' },
      { value: 'wechat', label: '微信' },
      { value: 'offline', label: '线下' },
      { value: 'other', label: '其他' },
    ],
  },
  {
    id: 'hasRevenue',
    label: '收入状态',
    type: 'checkbox',
    placeholder: '仅显示有收入的客户',
  },
];

export const Inline = () => {
  const [filterValues, setFilterValues] = useState<FilterValues>({});

  return (
    <FilterPanel
      fields={mockFields}
      values={filterValues}
      onChange={setFilterValues}
      variant="inline"
    />
  );
};

export const Sidebar = () => {
  const [filterValues, setFilterValues] = useState<FilterValues>({});

  return (
    <div style={{ width: '320px', height: '600px', position: 'relative' }}>
      <FilterPanel
        fields={mockFields}
        values={filterValues}
        onChange={setFilterValues}
        onApply={() => console.log('Applied:', filterValues)}
        variant="sidebar"
      />
    </div>
  );
};

export const WithInitialValues = () => {
  const [filterValues, setFilterValues] = useState<FilterValues>({
    status: 'active',
    search: '张',
    dateRange: { start: '2024-01-01', end: '2024-01-31' },
    hasRevenue: true,
  });

  return (
    <FilterPanel
      fields={mockFields}
      values={filterValues}
      onChange={setFilterValues}
      onReset={() => console.log('Reset clicked')}
    />
  );
};

// CSS for the component
export const filterPanelStyles = `
.filter-panel {
  background: var(--color-filter-bg);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-card);
}

.filter-panel--inline {
  padding: var(--spacing-md);
}

.filter-panel--sidebar {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 0;
  box-shadow: var(--shadow-xl);
}

.filter-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.filter-panel__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin: 0;
}

.filter-panel__close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-2xl);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-ease);
}

.filter-panel__close:hover {
  background: var(--color-background-secondary);
  color: var(--color-text);
}

.filter-panel__content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

.filter-panel--inline .filter-panel__content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;
}

.filter-panel__field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.filter-panel__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.filter-panel__input,
.filter-panel__select {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-background);
  color: var(--color-text);
  font-size: var(--font-size-sm);
  transition: all var(--duration-fast) var(--easing-ease);
}

.filter-panel__input:focus,
.filter-panel__select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.filter-panel__daterange {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.filter-panel__daterange-separator {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.filter-panel__checkbox {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
}

.filter-panel__checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.filter-panel__checkbox-label {
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.filter-panel__actions {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg) var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.filter-panel--inline .filter-panel__actions {
  justify-content: flex-end;
  border-top: none;
  padding: var(--spacing-md) 0 0;
}

.filter-panel__btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-ease);
}

.filter-panel__btn--primary {
  background: var(--color-primary);
  color: white;
}

.filter-panel__btn--primary:hover {
  background: var(--color-primary-600);
}

.filter-panel__btn--secondary {
  background: var(--color-background-secondary);
  color: var(--color-text);
}

.filter-panel__btn--secondary:hover {
  background: var(--color-background-tertiary);
}

.filter-panel__btn:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .filter-panel--inline .filter-panel__content {
    grid-template-columns: 1fr;
  }
  
  .filter-panel__daterange {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-panel__daterange-separator {
    align-self: center;
  }
}
`;
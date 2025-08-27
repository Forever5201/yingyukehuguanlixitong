import React, { useState, useRef, useEffect } from 'react';
import type { FC } from 'react';

export interface MenuAction {
  id: string;
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  variant?: 'default' | 'danger';
  disabled?: boolean;
}

export interface KebabMenuProps {
  actions: MenuAction[];
  className?: string;
  position?: 'left' | 'right';
  ariaLabel?: string;
}

export const KebabMenu: FC<KebabMenuProps> = ({
  actions,
  className = '',
  position = 'right',
  ariaLabel = '更多操作',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  const handleActionClick = (action: MenuAction) => {
    if (!action.disabled) {
      action.onClick();
      setIsOpen(false);
    }
  };

  return (
    <div className={`kebab-menu ${className}`}>
      <button
        ref={buttonRef}
        className="kebab-menu__trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={ariaLabel}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <circle cx="10" cy="4" r="2" />
          <circle cx="10" cy="10" r="2" />
          <circle cx="10" cy="16" r="2" />
        </svg>
      </button>
      {isOpen && (
        <div
          ref={menuRef}
          className={`kebab-menu__dropdown kebab-menu__dropdown--${position}`}
          role="menu"
        >
          {actions.map((action) => (
            <button
              key={action.id}
              className={`kebab-menu__item kebab-menu__item--${action.variant || 'default'} ${
                action.disabled ? 'kebab-menu__item--disabled' : ''
              }`}
              onClick={() => handleActionClick(action)}
              disabled={action.disabled}
              role="menuitem"
            >
              {action.icon && (
                <span className="kebab-menu__icon" aria-hidden="true">
                  {action.icon}
                </span>
              )}
              <span className="kebab-menu__label">{action.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// Storybook Story
export default {
  title: 'Components/KebabMenu',
  component: KebabMenu,
};

const EditIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
    <path d="M11.7 2.3a1 1 0 0 1 1.4 0l.6.6a1 1 0 0 1 0 1.4L5 13H2v-3L10.7 2.3zM3 12h1.6l7-7L10 3.4l-7 7V12z" />
  </svg>
);

const DeleteIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
  </svg>
);

const ExportIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
    <path d="M8.5 1.5A1.5 1.5 0 1 0 10 3v5h-1V3a.5.5 0 0 0-1 0v5H7V3a.5.5 0 0 0-1 0v5H5V3a1.5 1.5 0 1 0-1.5-1.5v11A1.5 1.5 0 0 0 5 14h6a1.5 1.5 0 0 0 1.5-1.5v-11a1.5 1.5 0 0 0-1.5-1.5v1A.5.5 0 0 0 10.5 2h-2a.5.5 0 0 0-.5-.5z"/>
  </svg>
);

const mockActions: MenuAction[] = [
  {
    id: 'edit',
    label: '编辑',
    icon: <EditIcon />,
    onClick: () => console.log('Edit clicked'),
  },
  {
    id: 'export',
    label: '导出',
    icon: <ExportIcon />,
    onClick: () => console.log('Export clicked'),
  },
  {
    id: 'delete',
    label: '删除',
    icon: <DeleteIcon />,
    onClick: () => console.log('Delete clicked'),
    variant: 'danger',
  },
];

export const Default = () => <KebabMenu actions={mockActions} />;

export const LeftPosition = () => <KebabMenu actions={mockActions} position="left" />;

export const WithDisabledActions = () => (
  <KebabMenu
    actions={[
      ...mockActions.slice(0, 2),
      {
        id: 'archive',
        label: '归档（不可用）',
        onClick: () => {},
        disabled: true,
      },
      mockActions[2],
    ]}
  />
);

export const MinimalActions = () => (
  <KebabMenu
    actions={[
      {
        id: 'view',
        label: '查看详情',
        onClick: () => console.log('View clicked'),
      },
      {
        id: 'download',
        label: '下载',
        onClick: () => console.log('Download clicked'),
      },
    ]}
  />
);

// CSS for the component
export const kebabMenuStyles = `
.kebab-menu {
  position: relative;
  display: inline-block;
}

.kebab-menu__trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-ease);
}

.kebab-menu__trigger:hover {
  background: var(--color-background-secondary);
  color: var(--color-text);
}

.kebab-menu__trigger:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.kebab-menu__dropdown {
  position: absolute;
  top: 100%;
  margin-top: var(--spacing-xs);
  min-width: 180px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-dropdown);
  z-index: var(--z-dropdown);
  padding: var(--spacing-xs);
  animation: kebab-menu-slide-down var(--duration-fast) var(--easing-ease-out);
}

.kebab-menu__dropdown--left {
  left: 0;
}

.kebab-menu__dropdown--right {
  right: 0;
}

@keyframes kebab-menu-slide-down {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.kebab-menu__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text);
  font-size: var(--font-size-sm);
  text-align: left;
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-ease);
}

.kebab-menu__item:hover:not(.kebab-menu__item--disabled) {
  background: var(--color-background-secondary);
}

.kebab-menu__item:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.kebab-menu__item--danger {
  color: var(--color-danger);
}

.kebab-menu__item--danger:hover:not(.kebab-menu__item--disabled) {
  background: rgba(220, 53, 69, 0.1);
}

.kebab-menu__item--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.kebab-menu__icon {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

.kebab-menu__label {
  flex: 1;
}
`;
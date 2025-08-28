/**
 * 现代化通知系统
 * 提供优雅的消息提示功能
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // 创建通知容器
        if (!document.getElementById('notification-container')) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                pointer-events: none;
            `;
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('notification-container');
        }
    }

    /**
     * 显示通知
     * @param {string} message - 消息内容
     * @param {string} type - 类型: success, error, warning, info
     * @param {number} duration - 持续时间（毫秒）
     */
    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        const id = 'notification-' + Date.now();
        notification.id = id;
        notification.className = `notification ${type} animate__animated animate__slideInRight`;
        notification.style.pointerEvents = 'auto';
        
        const icon = this.getIcon(type);
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${icon}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="NotificationManager.close('${id}')">
                <i class="fas fa-times"></i>
            </button>
            <div class="notification-progress">
                <div class="notification-progress-bar" style="animation-duration: ${duration}ms;"></div>
            </div>
        `;
        
        this.container.appendChild(notification);
        
        // 自动关闭
        setTimeout(() => {
            this.close(id);
        }, duration);
    }

    /**
     * 关闭通知
     * @param {string} id - 通知ID
     */
    close(id) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.classList.remove('animate__slideInRight');
            notification.classList.add('animate__slideOutRight');
            
            setTimeout(() => {
                notification.remove();
            }, 500);
        }
    }

    /**
     * 获取图标
     * @param {string} type - 通知类型
     * @returns {string} 图标类名
     */
    getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * 快捷方法
     */
    success(message, duration) {
        this.show(message, 'success', duration);
    }

    error(message, duration) {
        this.show(message, 'error', duration);
    }

    warning(message, duration) {
        this.show(message, 'warning', duration);
    }

    info(message, duration) {
        this.show(message, 'info', duration);
    }
}

// 创建全局实例
const NotificationManager = new NotificationSystem();

// 添加样式
const style = document.createElement('style');
style.textContent = `
    .notification {
        display: flex;
        align-items: center;
        min-width: 300px;
        max-width: 500px;
        margin-bottom: 10px;
        padding: 16px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        position: relative;
        overflow: hidden;
    }

    .notification-icon {
        flex-shrink: 0;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
    }

    .notification.success .notification-icon {
        background: #d1fae5;
        color: #065f46;
    }

    .notification.error .notification-icon {
        background: #fee2e2;
        color: #991b1b;
    }

    .notification.warning .notification-icon {
        background: #fed7aa;
        color: #92400e;
    }

    .notification.info .notification-icon {
        background: #dbeafe;
        color: #1e3a8a;
    }

    .notification-content {
        flex: 1;
    }

    .notification-message {
        font-size: 14px;
        font-weight: 500;
        color: #1e293b;
    }

    .notification-close {
        position: absolute;
        top: 8px;
        right: 8px;
        background: none;
        border: none;
        cursor: pointer;
        color: #999;
        font-size: 16px;
        padding: 4px;
        transition: color 0.2s;
    }

    .notification-close:hover {
        color: #333;
    }

    .notification-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(0, 0, 0, 0.1);
    }

    .notification-progress-bar {
        height: 100%;
        background: #667eea;
        animation: progress linear forwards;
    }

    .notification.success .notification-progress-bar {
        background: #10b981;
    }

    .notification.error .notification-progress-bar {
        background: #ef4444;
    }

    .notification.warning .notification-progress-bar {
        background: #f59e0b;
    }

    @keyframes progress {
        from {
            width: 100%;
        }
        to {
            width: 0%;
        }
    }
`;
document.head.appendChild(style);

// 替换原有的 alert
window.showSuccess = (message) => NotificationManager.success(message);
window.showError = (message) => NotificationManager.error(message);
window.showWarning = (message) => NotificationManager.warning(message);
window.showInfo = (message) => NotificationManager.info(message);
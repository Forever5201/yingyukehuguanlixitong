/**
 * 统一的 API 客户端
 * 提供标准化的 API 调用方法，包含错误处理、加载状态管理等
 */

const ApiClient = {
    // 基础配置
    baseURL: '/api',
    defaultHeaders: {
        'Content-Type': 'application/json',
    },

    /**
     * 发送 HTTP 请求的核心方法
     */
    async request(url, options = {}) {
        const fullURL = url.startsWith('http') ? url : `${this.baseURL}${url}`;
        
        const config = {
            ...options,
            headers: {
                ...this.defaultHeaders,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(fullURL, config);
            
            // 处理响应
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    /**
     * GET 请求
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullURL = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullURL, {
            method: 'GET',
        });
    },

    /**
     * POST 请求
     */
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * PUT 请求
     */
    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    /**
     * DELETE 请求
     */
    async delete(url) {
        return this.request(url, {
            method: 'DELETE',
        });
    },

    /**
     * PATCH 请求
     */
    async patch(url, data = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }
};

/**
 * 加载状态管理器
 */
const LoadingManager = {
    show(elementId = 'loading') {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'block';
        }
    },

    hide(elementId = 'loading') {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    },

    /**
     * 带加载状态的异步操作包装器
     */
    async withLoading(asyncFn, elementId = 'loading') {
        try {
            this.show(elementId);
            return await asyncFn();
        } finally {
            this.hide(elementId);
        }
    }
};

/**
 * 通知管理器
 */
const NotificationManager = {
    show(message, type = 'info', duration = 3000) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // 自动隐藏
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, duration);
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'error');
    },

    warning(message) {
        this.show(message, 'warning');
    },

    info(message) {
        this.show(message, 'info');
    }
};

/**
 * 表单验证工具
 */
const FormValidator = {
    rules: {
        required: (value) => value !== '' && value !== null && value !== undefined,
        email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        phone: (value) => /^[a-zA-Z0-9_\u4e00-\u9fa5-]{3,50}$/.test(value),  // 支持手机号或微信号等各种联系方式
        number: (value) => !isNaN(value) && isFinite(value),
        minLength: (min) => (value) => value.length >= min,
        maxLength: (max) => (value) => value.length <= max,
        min: (min) => (value) => Number(value) >= min,
        max: (max) => (value) => Number(value) <= max,
    },

    validate(formData, rules) {
        const errors = {};
        
        for (const [field, fieldRules] of Object.entries(rules)) {
            const value = formData[field];
            
            for (const rule of fieldRules) {
                if (typeof rule === 'function') {
                    if (!rule(value)) {
                        errors[field] = '验证失败';
                        break;
                    }
                } else if (typeof rule === 'object') {
                    const { validator, message } = rule;
                    if (!validator(value)) {
                        errors[field] = message;
                        break;
                    }
                }
            }
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    }
};

// 导出到全局
window.ApiClient = ApiClient;
window.LoadingManager = LoadingManager;
window.NotificationManager = NotificationManager;
window.FormValidator = FormValidator;
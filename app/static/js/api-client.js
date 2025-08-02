/**
 * 统一的API客户端
 * 
 * 实现正规软件开发规范中的前端架构原则：
 * 1. 统一的错误处理
 * 2. 一致的请求格式
 * 3. 标准化的响应处理
 * 4. 可复用的HTTP客户端
 */

class ApiClient {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    /**
     * 统一的HTTP请求方法
     * @param {string} url - 请求URL
     * @param {Object} options - 请求选项
     * @returns {Promise<Object>} 响应数据
     */
    async request(url, options = {}) {
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(`${this.baseUrl}${url}`, config);
            const data = await response.json();

            if (!response.ok) {
                throw new ApiError(data.message || '请求失败', response.status, data);
            }

            return data;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError('网络请求失败', 0, { originalError: error.message });
        }
    }

    /**
     * GET请求
     * @param {string} url - 请求URL
     * @param {Object} params - 查询参数
     * @returns {Promise<Object>} 响应数据
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullUrl, {
            method: 'GET'
        });
    }

    /**
     * POST请求
     * @param {string} url - 请求URL
     * @param {Object} data - 请求体数据
     * @returns {Promise<Object>} 响应数据
     */
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT请求
     * @param {string} url - 请求URL
     * @param {Object} data - 请求体数据
     * @returns {Promise<Object>} 响应数据
     */
    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE请求
     * @param {string} url - 请求URL
     * @returns {Promise<Object>} 响应数据
     */
    async delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
}

/**
 * API错误类
 */
class ApiError extends Error {
    constructor(message, status, details = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;
    }
}

/**
 * 课程API服务
 */
class CourseApiService {
    constructor() {
        this.client = new ApiClient();
    }

    /**
     * 获取课程列表
     * @param {Object} filters - 过滤条件
     * @returns {Promise<Object>} 课程数据
     */
    async getCourses(filters = {}) {
        try {
            const response = await this.client.get('/courses', filters);
            return response.data;
        } catch (error) {
            console.error('获取课程列表失败:', error);
            throw error;
        }
    }



    /**
     * 获取状态映射
     * @returns {Promise<Object>} 状态映射
     */
    async getStatusMapping() {
        try {
            const response = await this.client.get('/courses/status-mapping');
            return response.data;
        } catch (error) {
            console.error('获取状态映射失败:', error);
            throw error;
        }
    }
}

/**
 * 统一的错误处理器
 */
class ErrorHandler {
    /**
     * 显示错误消息
     * @param {Error|ApiError} error - 错误对象
     * @param {string} defaultMessage - 默认错误消息
     */
    static showError(error, defaultMessage = '操作失败') {
        let message = defaultMessage;
        
        if (error instanceof ApiError) {
            message = error.message;
            
            // 根据状态码显示不同的错误信息
            switch (error.status) {
                case 400:
                    message = `请求参数错误: ${error.message}`;
                    break;
                case 401:
                    message = '未授权访问，请重新登录';
                    break;
                case 403:
                    message = '权限不足';
                    break;
                case 404:
                    message = '请求的资源不存在';
                    break;
                case 500:
                    message = '服务器内部错误，请稍后重试';
                    break;
            }
        } else if (error.message) {
            message = error.message;
        }

        // 显示错误消息（可以根据UI框架调整）
        if (typeof showToast === 'function') {
            showToast(message, 'error');
        } else if (typeof alert === 'function') {
            alert(message);
        } else {
            console.error(message);
        }
    }

    /**
     * 显示成功消息
     * @param {string} message - 成功消息
     */
    static showSuccess(message) {
        if (typeof showToast === 'function') {
            showToast(message, 'success');
        } else {
            console.log(message);
        }
    }
}

/**
 * 加载状态管理器
 */
class LoadingManager {
    constructor() {
        this.loadingStates = new Map();
    }

    /**
     * 设置加载状态
     * @param {string} key - 加载状态键
     * @param {boolean} isLoading - 是否加载中
     */
    setLoading(key, isLoading) {
        this.loadingStates.set(key, isLoading);
        this.updateUI(key, isLoading);
    }

    /**
     * 获取加载状态
     * @param {string} key - 加载状态键
     * @returns {boolean} 是否加载中
     */
    isLoading(key) {
        return this.loadingStates.get(key) || false;
    }

    /**
     * 更新UI加载状态
     * @param {string} key - 加载状态键
     * @param {boolean} isLoading - 是否加载中
     */
    updateUI(key, isLoading) {
        // 查找对应的按钮或元素
        const button = document.querySelector(`[data-loading-key="${key}"]`);
        if (button) {
            button.disabled = isLoading;
            
            if (isLoading) {
                button.classList.add('loading');
                const originalText = button.textContent;
                button.dataset.originalText = originalText;
                button.textContent = '加载中...';
            } else {
                button.classList.remove('loading');
                if (button.dataset.originalText) {
                    button.textContent = button.dataset.originalText;
                }
            }
        }

        // 查找对应的加载指示器
        const loader = document.querySelector(`[data-loader-key="${key}"]`);
        if (loader) {
            loader.style.display = isLoading ? 'block' : 'none';
        }
    }
}

// 创建全局实例
window.courseApiService = new CourseApiService();
window.errorHandler = ErrorHandler;
window.loadingManager = new LoadingManager();

// 导出类（如果使用模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ApiClient,
        ApiError,
        CourseApiService,
        ErrorHandler,
        LoadingManager
    };
}
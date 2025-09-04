// 客户管理系统的JavaScript功能
// 性能优化和缓存管理
class PerformanceOptimizer {
    constructor() {
        this.cache = new Map();
        this.requestQueue = [];
        this.isProcessing = false;
    }

    // 缓存请求结果
    async cachedFetch(url, options = {}) {
        const cacheKey = `${url}_${JSON.stringify(options)}`;
        
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < 300000) { // 5分钟缓存
                return cached.data;
            }
            this.cache.delete(cacheKey);
        }

        // 防抖处理
        return this.debounceFetch(url, options, cacheKey);
    }

    // 防抖请求
    async debounceFetch(url, options, cacheKey) {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ url, options, cacheKey, resolve, reject });
            
            if (!this.isProcessing) {
                this.isProcessing = true;
                setTimeout(() => this.processQueue(), 50);
            }
        });
    }

    async processQueue() {
        while (this.requestQueue.length > 0) {
            const { url, options, cacheKey, resolve, reject } = this.requestQueue.shift();
            
            try {
                const response = await fetch(url, options);
                const data = await response.json();
                
                this.cache.set(cacheKey, {
                    data: data,
                    timestamp: Date.now()
                });
                
                resolve(data);
            } catch (error) {
                reject(error);
            }
        }
        
        this.isProcessing = false;
    }

    // 优化事件处理
    optimizeEventListeners() {
        // 防抖搜索
        let searchTimeout;
        
        // 延迟执行，确保DOM完全加载
        setTimeout(() => {
            const searchInputs = document.querySelectorAll('input[type="text"]');
            
            if (searchInputs && searchInputs.length > 0) {
                searchInputs.forEach(input => {
                    try {
                        if (input && input.placeholder && input.placeholder.includes('搜索')) {
                            input.addEventListener('input', (e) => {
                                clearTimeout(searchTimeout);
                                searchTimeout = setTimeout(() => {
                                    this.performSearch(e.target);
                                }, 300);
                            });
                        }
                    } catch (error) {
                        console.warn('无法为输入元素添加事件监听器:', error);
                    }
                });
            }
        }, 100);
    }

    performSearch(input) {
        const searchTerm = input.value.toLowerCase();
        const table = input.closest('.table-container')?.querySelector('table');
        
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    // 优化滚动性能
    optimizeScroll() {
        let ticking = false;
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    ticking = false;
                });
                ticking = true;
            }
        });
    }
}

// 初始化性能优化
const optimizer = new PerformanceOptimizer();

document.addEventListener('DOMContentLoaded', () => {
    optimizer.optimizeEventListeners();
    optimizer.optimizeScroll();
});
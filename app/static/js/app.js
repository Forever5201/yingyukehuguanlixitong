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
        const searchInputs = document.querySelectorAll('input[type="text"]');
        
        searchInputs.forEach(input => {
            if (input.placeholder && input.placeholder.includes('搜索')) {
                input.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        this.performSearch(e.target);
                    }, 300);
                });
            }
        });
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

// 全局错误处理
window.addEventListener('error', (e) => {
    console.error('JavaScript错误:', e.error);
});

// 网络状态监控
window.addEventListener('online', () => {
    console.log('网络已连接');
});

window.addEventListener('offline', () => {
    console.log('网络已断开');
});

console.log('客户管理系统已加载');
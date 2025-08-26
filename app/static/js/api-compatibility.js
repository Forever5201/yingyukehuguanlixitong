/**
 * API兼容层 - 支持新旧API的平滑切换
 * 
 * 功能：
 * 1. 提供统一的接口，内部决定使用新旧API
 * 2. 支持功能开关控制
 * 3. 自动处理响应格式差异
 * 4. 提供降级机制
 */

class ApiCompatibility {
    constructor() {
        // 从localStorage读取配置，支持按功能切换
        this.config = {
            useNewTrialApi: localStorage.getItem('useNewTrialApi') === 'true',
            useNewFormalApi: localStorage.getItem('useNewFormalApi') === 'true',
            useNewCustomerApi: localStorage.getItem('useNewCustomerApi') === 'true',
            // 全局开关
            useNewApiGlobal: localStorage.getItem('useNewApiGlobal') === 'true'
        };
        
        // API版本
        this.oldApiBase = '/api';
        this.newApiBase = '/api/v1';
    }
    
    /**
     * 获取是否使用新API
     */
    shouldUseNewApi(feature) {
        return this.config.useNewApiGlobal || this.config[`useNew${feature}Api`];
    }
    
    /**
     * 设置功能开关
     */
    setFeatureFlag(feature, enabled) {
        const key = `useNew${feature}Api`;
        this.config[key] = enabled;
        localStorage.setItem(key, enabled.toString());
    }
    
    /**
     * 获取试听课列表
     */
    async getTrialCourses(params = {}) {
        const useNewApi = this.shouldUseNewApi('Trial');
        
        try {
            if (useNewApi) {
                // 使用新API
                const queryString = new URLSearchParams(params).toString();
                const response = await fetch(`${this.newApiBase}/courses/trial?${queryString}`);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || '请求失败');
                }
                
                // 新API返回格式已经标准化
                return data.data;
            } else {
                // 使用旧API
                const response = await fetch(`${this.oldApiBase}/trial-courses`);
                const data = await response.json();
                
                // 转换旧API响应格式
                return {
                    courses: data,
                    statistics: this._calculateStatistics(data)
                };
            }
        } catch (error) {
            console.error('获取试听课列表失败:', error);
            
            // 如果新API失败，尝试降级到旧API
            if (useNewApi) {
                console.warn('新API失败，尝试使用旧API');
                this.config.useNewTrialApi = false;
                return this.getTrialCourses(params);
            }
            
            throw error;
        }
    }
    
    /**
     * 创建试听课
     */
    async createTrialCourse(courseData) {
        const useNewApi = this.shouldUseNewApi('Trial');
        
        try {
            if (useNewApi) {
                // 使用新API
                const response = await fetch(`${this.newApiBase}/courses/trial`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(courseData)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || '创建失败');
                }
                
                return data;
            } else {
                // 使用旧API（通过表单提交）
                // 这里需要特殊处理，因为旧API使用表单而不是JSON
                const formData = new FormData();
                Object.keys(courseData).forEach(key => {
                    if (courseData[key] !== null && courseData[key] !== undefined) {
                        formData.append(key, courseData[key]);
                    }
                });
                
                const response = await fetch(`${this.oldApiBase}/trial-courses`, {
                    method: 'POST',
                    body: formData
                });
                
                // 旧API返回的是HTML，需要检查是否成功
                if (response.redirected) {
                    return {
                        success: true,
                        data: {
                            message: '试听课创建成功'
                        }
                    };
                } else {
                    throw new Error('创建失败');
                }
            }
        } catch (error) {
            console.error('创建试听课失败:', error);
            
            // 降级处理
            if (useNewApi) {
                console.warn('新API失败，尝试使用旧API');
                this.config.useNewTrialApi = false;
                return this.createTrialCourse(courseData);
            }
            
            throw error;
        }
    }
    
    /**
     * 试听课转正课
     */
    async convertTrialToFormal(trialId, formalCourseData) {
        const useNewApi = this.shouldUseNewApi('Trial');
        
        try {
            if (useNewApi) {
                // 使用新API
                const response = await fetch(`${this.newApiBase}/courses/trial/${trialId}/convert`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formalCourseData)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || '转化失败');
                }
                
                return data;
            } else {
                // 使用旧的表单提交方式
                // 需要构造表单并提交到convert-trial页面
                window.location.href = `/convert-trial/${trialId}`;
                return null;
            }
        } catch (error) {
            console.error('试听课转正失败:', error);
            throw error;
        }
    }
    
    /**
     * 获取正式课列表
     */
    async getFormalCourses(params = {}) {
        const useNewApi = this.shouldUseNewApi('Formal');
        
        try {
            if (useNewApi) {
                // 使用新API
                const queryString = new URLSearchParams({...params, type: 'formal'}).toString();
                const response = await fetch(`${this.newApiBase}/courses?${queryString}`);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || '请求失败');
                }
                
                return data.data;
            } else {
                // 使用旧API
                const response = await fetch(`${this.oldApiBase}/formal-courses`);
                return await response.json();
            }
        } catch (error) {
            console.error('获取正式课列表失败:', error);
            
            // 降级处理
            if (useNewApi) {
                console.warn('新API失败，尝试使用旧API');
                this.config.useNewFormalApi = false;
                return this.getFormalCourses(params);
            }
            
            throw error;
        }
    }
    
    /**
     * 计算统计信息（用于旧API响应）
     */
    _calculateStatistics(courses) {
        if (!Array.isArray(courses)) return {};
        
        const stats = {
            total_count: courses.length,
            total_revenue: 0,
            total_cost: 0,
            total_profit: 0,
            status_distribution: {}
        };
        
        courses.forEach(course => {
            const revenue = parseFloat(course.trial_price || course.price || 0);
            const cost = parseFloat(course.cost || 0);
            
            stats.total_revenue += revenue;
            stats.total_cost += cost;
            stats.total_profit += (revenue - cost);
            
            const status = course.trial_status || 'unknown';
            stats.status_distribution[status] = (stats.status_distribution[status] || 0) + 1;
        });
        
        return stats;
    }
    
    /**
     * 显示API状态（用于调试）
     */
    showApiStatus() {
        console.log('API兼容层配置:', this.config);
        console.log('试听课API:', this.shouldUseNewApi('Trial') ? '新版' : '旧版');
        console.log('正式课API:', this.shouldUseNewApi('Formal') ? '新版' : '旧版');
        console.log('客户API:', this.shouldUseNewApi('Customer') ? '新版' : '旧版');
    }
}

// 创建全局实例
window.apiCompatibility = new ApiCompatibility();

// 提供便捷的全局函数
window.enableNewApi = function(feature) {
    if (feature) {
        window.apiCompatibility.setFeatureFlag(feature, true);
        console.log(`已启用${feature}的新API`);
    } else {
        localStorage.setItem('useNewApiGlobal', 'true');
        console.log('已启用所有新API');
    }
};

window.disableNewApi = function(feature) {
    if (feature) {
        window.apiCompatibility.setFeatureFlag(feature, false);
        console.log(`已禁用${feature}的新API`);
    } else {
        localStorage.setItem('useNewApiGlobal', 'false');
        console.log('已禁用所有新API');
    }
};

// 在控制台显示使用说明
console.log('API兼容层已加载。使用 enableNewApi() 或 disableNewApi() 来切换API版本。');
console.log('示例: enableNewApi("Trial") 启用试听课新API');
console.log('示例: enableNewApi() 启用所有新API');
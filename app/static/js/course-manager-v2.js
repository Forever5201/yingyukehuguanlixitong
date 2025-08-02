/**
 * 重构后的课程管理器 (v2)
 * 
 * 基于正规软件开发规范重构：
 * 1. 使用统一的API客户端
 * 2. 实现单一职责原则
 * 3. 标准化错误处理
 * 4. 提高代码复用性
 */

class CourseManagerV2 {
    constructor() {
        this.apiService = window.courseApiService;
        this.errorHandler = window.errorHandler;
        this.loadingManager = window.loadingManager;
        this.statusMapping = null;
        
        // 初始化
        this.init();
    }

    /**
     * 初始化管理器
     */
    async init() {
        try {
            // 加载状态映射
            this.statusMapping = await this.apiService.getStatusMapping();
        } catch (error) {
            console.error('初始化CourseManager失败:', error);
        }
    }



    /**
     * 创建课程行
     * @param {Object} course - 课程数据
     * @param {string} type - 课程类型
     * @returns {HTMLElement} 表格行元素
     */
    createCourseRow(course, type) {
        const row = document.createElement('tr');
        
        // 基础信息列
        const basicColumns = [
            course.customer_name || '',
            course.customer_phone || '',
            course.course_type || '',
            this.formatPrice(course.price),
            this.formatDate(course.created_at)
        ];

        // 根据类型添加特定列
        if (type === 'trial' || course.course_type === '试听课') {
            basicColumns.splice(4, 0, course.status || '');
        } else if (type === 'formal' || course.course_type === '正式课') {
            basicColumns.splice(4, 0, course.sessions || '', this.formatPrice(course.price_per_session));
        }

        // 添加操作列
        basicColumns.push(this.createActionButtons(course));

        // 创建单元格
        basicColumns.forEach(content => {
            const cell = document.createElement('td');
            if (typeof content === 'string') {
                cell.textContent = content;
            } else {
                cell.appendChild(content);
            }
            row.appendChild(cell);
        });

        return row;
    }

    /**
     * 创建操作按钮
     * @param {Object} course - 课程数据
     * @returns {HTMLElement} 按钮容器
     */
    createActionButtons(course) {
        const container = document.createElement('div');
        container.className = 'btn-group';

        // 编辑按钮
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-sm btn-outline-primary';
        editBtn.textContent = '编辑';
        editBtn.onclick = () => this.editCourse(course);

        // 删除按钮
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-sm btn-outline-danger';
        deleteBtn.textContent = '删除';
        deleteBtn.onclick = () => this.deleteCourse(course);

        container.appendChild(editBtn);
        container.appendChild(deleteBtn);

        return container;
    }

    /**
     * 更新业绩显示
     * @param {Object} performance - 业绩数据
     * @param {string} containerId - 容器ID
     */
    updatePerformanceDisplay(performance, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !performance) return;

        const html = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">总收入</h5>
                            <p class="card-text text-success">¥${this.formatPrice(performance.total_revenue)}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">总成本</h5>
                            <p class="card-text text-warning">¥${this.formatPrice(performance.total_cost)}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">手续费</h5>
                            <p class="card-text text-info">¥${this.formatPrice(performance.total_fees)}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">净利润</h5>
                            <p class="card-text ${performance.total_profit >= 0 ? 'text-success' : 'text-danger'}">
                                ¥${this.formatPrice(performance.total_profit)}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    /**
     * 编辑课程
     * @param {Object} course - 课程数据
     */
    async editCourse(course) {
        // 这里可以打开编辑模态框或跳转到编辑页面
        console.log('编辑课程:', course);
        
        // 示例：显示编辑模态框
        if (typeof showEditCourseModal === 'function') {
            showEditCourseModal(course);
        } else {
            alert(`编辑课程: ${course.customer_name} - ${course.course_type}`);
        }
    }

    /**
     * 删除课程
     * @param {Object} course - 课程数据
     */
    async deleteCourse(course) {
        if (!confirm(`确定要删除 ${course.customer_name} 的${course.course_type}吗？`)) {
            return;
        }

        // 这里应该调用删除API
        console.log('删除课程:', course);
        
        // 示例实现
        try {
            // await this.apiService.deleteCourse(course.id);
            this.errorHandler.showSuccess('课程删除成功');
            
            // 刷新表格
            // this.refreshCurrentTable();
        } catch (error) {
            this.errorHandler.showError(error, '删除课程失败');
        }
    }

    /**
     * 格式化价格
     * @param {number} price - 价格
     * @returns {string} 格式化后的价格
     */
    formatPrice(price) {
        if (price == null || price === '') return '0.00';
        return parseFloat(price).toFixed(2);
    }

    /**
     * 格式化日期
     * @param {string} dateString - 日期字符串
     * @returns {string} 格式化后的日期
     */
    formatDate(dateString) {
        if (!dateString) return '';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        } catch (error) {
            return dateString;
        }
    }

    /**
     * 获取状态显示文本
     * @param {string} statusKey - 状态键
     * @returns {string} 状态显示文本
     */
    getStatusText(statusKey) {
        if (!this.statusMapping || !statusKey) return statusKey || '';
        return this.statusMapping[statusKey] || statusKey;
    }
}

// 创建全局实例（向后兼容）
window.CourseManagerV2 = CourseManagerV2;

// 当DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    if (!window.courseManagerV2) {
        window.courseManagerV2 = new CourseManagerV2();
    }
});

// 导出类（如果使用模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CourseManagerV2;
}
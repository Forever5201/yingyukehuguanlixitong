/**
 * 课程管理模块
 * 封装所有课程相关的业务逻辑
 */

const CourseModule = {
    /**
     * 获取试听课列表
     */
    async getTrialCourses(filters = {}) {
        try {
            const response = await ApiClient.get('/trial-courses', filters);
            return response.data || [];
        } catch (error) {
            NotificationManager.error('获取试听课列表失败');
            throw error;
        }
    },

    /**
     * 获取正课列表
     */
    async getFormalCourses(filters = {}) {
        try {
            const response = await ApiClient.get('/formal-courses', filters);
            return response.data || [];
        } catch (error) {
            NotificationManager.error('获取正课列表失败');
            throw error;
        }
    },

    /**
     * 创建试听课
     */
    async createTrialCourse(courseData) {
        // 验证数据
        const rules = {
            customer_id: [
                { validator: FormValidator.rules.required, message: '请选择客户' }
            ],
            trial_price: [
                { validator: FormValidator.rules.required, message: '请输入试听价格' },
                { validator: FormValidator.rules.min(0), message: '价格不能为负数' }
            ],
            source: [
                { validator: FormValidator.rules.required, message: '请选择渠道来源' }
            ]
        };

        const validation = FormValidator.validate(courseData, rules);
        if (!validation.isValid) {
            const firstError = Object.values(validation.errors)[0];
            NotificationManager.error(firstError);
            return null;
        }

        try {
            const response = await LoadingManager.withLoading(
                () => ApiClient.post('/trial-courses', courseData)
            );
            
            if (response.success) {
                NotificationManager.success('试听课创建成功');
                return response.data;
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            NotificationManager.error(error.message || '创建试听课失败');
            throw error;
        }
    },

    /**
     * 更新试听课状态
     */
    async updateTrialStatus(courseId, status) {
        try {
            const response = await ApiClient.put(`/trial-courses/${courseId}/status`, { status });
            
            if (response.success) {
                NotificationManager.success('状态更新成功');
                return response.data;
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            NotificationManager.error(error.message || '更新状态失败');
            throw error;
        }
    },

    /**
     * 试听转正课
     */
    async convertToFormal(trialId, formalData) {
        // 验证数据
        const rules = {
            course_type: [
                { validator: FormValidator.rules.required, message: '请选择课程类型' }
            ],
            sessions: [
                { validator: FormValidator.rules.required, message: '请输入购买节数' },
                { validator: FormValidator.rules.min(1), message: '购买节数至少为1' }
            ],
            price: [
                { validator: FormValidator.rules.required, message: '请输入单节价格' },
                { validator: FormValidator.rules.min(0), message: '价格不能为负数' }
            ]
        };

        const validation = FormValidator.validate(formalData, rules);
        if (!validation.isValid) {
            const firstError = Object.values(validation.errors)[0];
            NotificationManager.error(firstError);
            return null;
        }

        try {
            const response = await LoadingManager.withLoading(
                () => ApiClient.post(`/trial-courses/${trialId}/convert`, formalData)
            );
            
            if (response.success) {
                NotificationManager.success('转正课成功');
                return response.data;
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            NotificationManager.error(error.message || '转正课失败');
            throw error;
        }
    },

    /**
     * 申请退费
     */
    async applyRefund(courseId, refundData) {
        // 验证数据
        const rules = {
            refund_sessions: [
                { validator: FormValidator.rules.required, message: '请输入退费节数' },
                { validator: FormValidator.rules.min(1), message: '退费节数至少为1' }
            ],
            refund_reason: [
                { validator: FormValidator.rules.required, message: '请输入退费原因' }
            ]
        };

        const validation = FormValidator.validate(refundData, rules);
        if (!validation.isValid) {
            const firstError = Object.values(validation.errors)[0];
            NotificationManager.error(firstError);
            return null;
        }

        try {
            const response = await LoadingManager.withLoading(
                () => ApiClient.post(`/courses/${courseId}/refund`, refundData)
            );
            
            if (response.success) {
                NotificationManager.success('退费申请成功');
                return response.data;
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            NotificationManager.error(error.message || '退费申请失败');
            throw error;
        }
    },

    /**
     * 获取退费信息
     */
    async getRefundInfo(courseId) {
        try {
            const response = await ApiClient.get(`/courses/${courseId}/refund-info`);
            
            if (response.success) {
                return response;
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            NotificationManager.error('获取退费信息失败');
            throw error;
        }
    },

    /**
     * 导出课程数据
     */
    async exportCourses(type = 'trial') {
        try {
            const url = type === 'trial' ? '/export/trial-courses' : '/export/formal-courses';
            
            // 创建下载链接
            const link = document.createElement('a');
            link.href = `/api${url}`;
            link.download = `${type}_courses_${new Date().toISOString().split('T')[0]}.xlsx`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            NotificationManager.success('导出成功');
        } catch (error) {
            NotificationManager.error('导出失败');
            throw error;
        }
    }
};

// 辅助函数
const CourseUIHelper = {
    /**
     * 格式化课程状态
     */
    formatStatus(status) {
        const statusMap = {
            'registered': '已报名',
            'scheduled': '已排课',
            'completed': '已完成',
            'converted': '已转正课',
            'cancelled': '已取消'
        };
        return statusMap[status] || status;
    },

    /**
     * 格式化金额
     */
    formatCurrency(amount) {
        return `¥${Number(amount).toFixed(2)}`;
    },

    /**
     * 格式化日期
     */
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    },

    /**
     * 渲染课程表格
     */
    renderCourseTable(courses, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (courses.length === 0) {
            container.innerHTML = '<p class="no-data">暂无数据</p>';
            return;
        }

        const table = document.createElement('table');
        table.className = 'course-table';

        // 表头
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>客户姓名</th>
                <th>课程类型</th>
                <th>状态</th>
                <th>金额</th>
                <th>创建时间</th>
                <th>操作</th>
            </tr>
        `;
        table.appendChild(thead);

        // 表体
        const tbody = document.createElement('tbody');
        courses.forEach(course => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${course.customer_name}</td>
                <td>${course.course_type || '试听课'}</td>
                <td>${this.formatStatus(course.trial_status || course.status)}</td>
                <td>${this.formatCurrency(course.price * (course.sessions || 1))}</td>
                <td>${this.formatDate(course.created_at)}</td>
                <td>
                    <button class="btn-action" onclick="viewCourseDetails(${course.id})">查看</button>
                    ${course.is_trial && course.trial_status === 'completed' ? 
                        `<button class="btn-action btn-primary" onclick="convertToFormal(${course.id})">转正课</button>` : ''}
                </td>
            `;
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        container.innerHTML = '';
        container.appendChild(table);
    }
};

// 导出到全局
window.CourseModule = CourseModule;
window.CourseUIHelper = CourseUIHelper;
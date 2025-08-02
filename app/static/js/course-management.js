/**
 * 课程管理公共JavaScript模块
 * 统一管理试听课和正课的编辑、删除等功能
 */

class CourseManager {
    /**
     * 编辑试听课
     * @param {number} courseId - 课程ID
     * @param {Object} courseData - 课程数据
     */
    static editTrialCourse(courseId, courseData) {
        console.log('CourseManager.editTrialCourse 被调用');
        console.log('课程ID:', courseId);
        console.log('课程数据:', courseData);
        
        // 填充试听课编辑表单数据
        const courseIdField = document.getElementById('edit_trial_course_id');
        const nameField = document.getElementById('edit_trial_customer_name');
        const phoneField = document.getElementById('edit_trial_customer_phone');
        const genderField = document.getElementById('edit_trial_customer_gender');
        const gradeField = document.getElementById('edit_trial_customer_grade');
        const regionField = document.getElementById('edit_trial_customer_region');
        const priceField = document.getElementById('edit_trial_price');
        const sourceField = document.getElementById('edit_trial_source');
        const tutoringField = document.getElementById('edit_trial_has_tutoring_experience');
        
        console.log('表单字段检查:');
        console.log('courseIdField:', courseIdField);
        console.log('nameField:', nameField);
        console.log('phoneField:', phoneField);
        console.log('genderField:', genderField);
        console.log('gradeField:', gradeField);
        console.log('regionField:', regionField);
        console.log('priceField:', priceField);
        console.log('sourceField:', sourceField);
        console.log('tutoringField:', tutoringField);
        
        if (courseIdField) courseIdField.value = courseId;
        if (nameField) nameField.value = courseData.customer_name || '';
        if (phoneField) phoneField.value = courseData.customer_phone || '';
        if (genderField) genderField.value = courseData.customer_gender || '';
        if (gradeField) gradeField.value = courseData.customer_grade || '';
        if (regionField) regionField.value = courseData.customer_region || '';
        if (priceField) priceField.value = courseData.trial_price || courseData.price || '';
        if (sourceField) sourceField.value = courseData.source || '';
        if (tutoringField) tutoringField.value = courseData.has_tutoring_experience || '';
        
        console.log('表单填充完成，检查填充结果:');
        console.log('姓名:', nameField ? nameField.value : 'field not found');
        console.log('电话:', phoneField ? phoneField.value : 'field not found');
        console.log('性别:', genderField ? genderField.value : 'field not found');
        console.log('年级:', gradeField ? gradeField.value : 'field not found');
        console.log('地区:', regionField ? regionField.value : 'field not found');
        console.log('价格:', priceField ? priceField.value : 'field not found');
        console.log('来源:', sourceField ? sourceField.value : 'field not found');
        console.log('辅导经验:', tutoringField ? tutoringField.value : 'field not found');
        
        // 显示试听课编辑模态框
        const modal = document.getElementById('editTrialModal');
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            console.log('模态框已显示');
        } else {
            console.error('找不到editTrialModal模态框');
        }
    }

    /**
     * 编辑正课
     * @param {number} courseId - 课程ID
     * @param {Object} courseData - 课程数据
     */
    static editFormalCourse(courseId, courseData) {
        // 填充正课编辑表单数据
        document.getElementById('edit_formal_course_id').value = courseId;
        document.getElementById('edit_formal_customer_name').value = courseData.customer_name || '';
        document.getElementById('edit_formal_customer_phone').value = courseData.customer_phone || '';
        document.getElementById('edit_formal_customer_gender').value = courseData.customer_gender || '';
        document.getElementById('edit_formal_customer_grade').value = courseData.customer_grade || '';
        document.getElementById('edit_formal_customer_region').value = courseData.customer_region || '';
        document.getElementById('edit_formal_course_type').value = courseData.course_type || '';
        document.getElementById('edit_formal_sessions').value = courseData.sessions || courseData.purchased_sessions || '';
        document.getElementById('edit_formal_gift_sessions').value = courseData.gift_sessions || courseData.gifted_sessions || 0;
        document.getElementById('edit_formal_price').value = courseData.price_per_session || courseData.price || '';
        document.getElementById('edit_formal_payment_channel').value = courseData.payment_channel || '';
        document.getElementById('edit_formal_cost').value = courseData.cost || '';
        document.getElementById('edit_formal_other_cost').value = courseData.other_cost || 0;
        document.getElementById('edit_formal_source').value = courseData.source || '';
        
        // 显示正课编辑模态框
        const modal = document.getElementById('editFormalModal');
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * 提交试听课表单
     * @param {HTMLFormElement} form - 表单元素
     * @param {Function} successCallback - 成功回调函数
     * @param {Function} onError - 错误回调函数
     */
    static submitTrialForm(form, successCallback = null, onError) {
        const courseId = document.getElementById('edit_trial_course_id').value;
        const formData = new FormData(form);
        
        fetch(`/api/trial-courses/${courseId}`, {
            method: 'PUT',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('试听课信息更新成功！');
                if (successCallback && typeof successCallback === 'function') {
                    successCallback(data);
                } else {
                    CourseManager.closeTrialModal();
                    location.reload();
                }
            } else {
                if (onError) onError(data);
                else alert(data.message || '更新失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (onError) onError(error);
            else alert('更新失败');
        });
    }

    /**
     * 提交正课表单
     * @param {HTMLFormElement} form - 表单元素
     * @param {Function} successCallback - 成功回调函数
     */
    static submitFormalForm(form, successCallback = null) {
        const formData = new FormData(form);
        const courseId = formData.get('course_id');
        
        fetch(`/api/formal_courses/${courseId}`, {
            method: 'PUT',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('正课信息更新成功');
                if (successCallback && typeof successCallback === 'function') {
                    successCallback(data);
                } else {
                    window.location.reload();
                }
            } else {
                alert('更新失败：' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('更新失败，请重试');
        });
    }

    /**
     * 删除试听课
     * @param {number} courseId - 课程ID
     * @param {string} userType - 用户类型
     * @param {Function} onSuccess - 成功回调函数
     * @param {Function} onError - 错误回调函数
     */
    static deleteTrialCourse(courseId, userType = '试听课用户', onSuccess, onError) {
        const confirmMessage = userType === '体验课用户' ? 
            '确定要删除这条体验课用户记录吗？' : 
            '确定要删除这条试听课记录吗？';
        
        if (confirm(confirmMessage)) {
            fetch(`/api/trial-courses/${courseId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (onSuccess) onSuccess(data);
                    else {
                        alert('删除成功！');
                        location.reload();
                    }
                } else {
                    if (onError) onError(data);
                    else alert(data.message || '删除失败');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (onError) onError(error);
                else alert('删除失败');
            });
        }
    }

    /**
     * 删除正课
     * @param {number} courseId - 课程ID
     * @param {Function} onSuccess - 成功回调函数
     * @param {Function} onError - 错误回调函数
     */
    static deleteFormalCourse(courseId, onSuccess, onError) {
        if (confirm('确定要删除这条正课记录吗？')) {
            fetch(`/api/formal-courses/${courseId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (onSuccess) onSuccess(data);
                    else {
                        alert('删除成功！');
                        location.reload();
                    }
                } else {
                    if (onError) onError(data);
                    else alert(data.message || '删除失败');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (onError) onError(error);
                else alert('删除失败');
            });
        }
    }

    /**
     * 试听课转正课
     * @param {number} courseId - 试听课ID
     */
    static convertTrialToCourse(courseId) {
        if (confirm('确定要将此试听课转为正课吗？')) {
            window.location.href = `/convert-trial/${courseId}`;
        }
    }

    /**
     * 关闭试听课编辑模态框
     */
    static closeTrialModal() {
        const modal = document.getElementById('editTrialModal');
        const form = document.getElementById('editTrialForm');
        
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
        if (form) {
            form.reset();
        }
    }

    /**
     * 关闭正课编辑模态框
     */
    static closeFormalModal() {
        const modal = document.getElementById('editFormalModal');
        const form = document.getElementById('editFormalForm');
        
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
        if (form) {
            form.reset();
        }
    }

    /**
     * 设置成功回调函数
     * @param {Function} trialCallback - 试听课成功回调
     * @param {Function} formalCallback - 正课成功回调
     */
    static setSuccessCallbacks(trialCallback = null, formalCallback = null) {
        CourseManager.trialSuccessCallback = trialCallback;
        CourseManager.formalSuccessCallback = formalCallback;
    }

    /**
     * 初始化模态框事件监听器
     */
    static initModalEvents() {
        // 试听课编辑模态框事件
        const editTrialModal = document.getElementById('editTrialModal');
        if (editTrialModal) {
            const closeBtn = editTrialModal.querySelector('.close-edit');
            const cancelBtn = document.getElementById('editTrialCancelBtn') || document.getElementById('editCancelBtn');
            const form = document.getElementById('editTrialForm');

            if (closeBtn) closeBtn.addEventListener('click', CourseManager.closeTrialModal);
            if (cancelBtn) cancelBtn.addEventListener('click', CourseManager.closeTrialModal);

            // 点击模态框外部关闭
            window.addEventListener('click', function(event) {
                if (event.target === editTrialModal) {
                    CourseManager.closeTrialModal();
                }
            });

            // 表单提交事件
            if (form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    CourseManager.submitTrialForm(form, CourseManager.trialSuccessCallback);
                });
            }
        }

        // 正课编辑模态框事件
        const editFormalModal = document.getElementById('editFormalModal');
        if (editFormalModal) {
            const closeBtn = editFormalModal.querySelector('.close');
            const cancelBtn = document.getElementById('editFormalCancelBtn');
            const form = document.getElementById('editFormalForm');

            if (closeBtn) closeBtn.addEventListener('click', CourseManager.closeFormalModal);
            if (cancelBtn) cancelBtn.addEventListener('click', CourseManager.closeFormalModal);

            // 点击模态框外部关闭
            window.addEventListener('click', function(event) {
                if (event.target === editFormalModal) {
                    CourseManager.closeFormalModal();
                }
            });

            // 表单提交事件
            if (form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    CourseManager.submitFormalForm(form, CourseManager.formalSuccessCallback);
                });
            }
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    CourseManager.initModalEvents();
});

// 全局函数，保持向后兼容
// editTrialCourse 函数已移至各页面内部实现

function editFormalCourseGlobal(courseId, courseData) {
    CourseManager.editFormalCourse(courseId, courseData);
}

function deleteTrialCourse(courseId, userType) {
    CourseManager.deleteTrialCourse(courseId, userType);
}

function deleteFormalCourse(courseId) {
    CourseManager.deleteFormalCourse(courseId);
}

function convertTrialToCourse(courseId) {
    CourseManager.convertTrialToCourse(courseId);
}
/**
 * 全局模态框修复脚本
 * 解决跨页面的按钮无响应问题
 * 统一处理模态框显示、JavaScript函数作用域和DOM加载时机问题
 */

(function() {
    'use strict';
    
    // 全局命名空间
    window.GlobalModalManager = window.GlobalModalManager || {};
    
    // 调试开关
    const DEBUG = true;
    
    function log(message, data = null) {
        if (DEBUG) {
            console.log(`🔧 [GlobalModalManager] ${message}`, data ? data : '');
        }
    }
    
    // 确保DOM就绪的工具函数
    function ensureDOMReady(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    }
    
    // 安全的元素获取函数
    function safeGetElement(id) {
        const element = document.getElementById(id);
        if (!element) {
            log(`⚠️ 元素未找到: ${id}`);
        }
        return element;
    }
    
    // 尝试一组ID并设置值（避免对每个尝试都打警告，仅在全部失败时提示一次）
    function setValueByIds(idList, value) {
        for (const id of idList) {
            const el = document.getElementById(id); // 这里不使用 safeGetElement，避免多次告警
            if (el) {
                if (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA') {
                    el.value = (value !== null && value !== undefined) ? value : '';
                } else {
                    el.textContent = (value !== null && value !== undefined) ? value : '';
                }
                return true;
            }
        }
        log(`⚠️ 目标元素未找到: ${idList.join(' | ')}`);
        return false;
    }
    
    // 安全的模态框显示函数
    function safeShowModal(modalId, setupCallback = null) {
        log(`🎯 准备显示模态框: ${modalId}`);
        
        const modal = safeGetElement(modalId);
        if (!modal) {
            log(`❌ 模态框不存在: ${modalId}`);
            return false;
        }
        
        // 执行设置回调
        if (setupCallback && typeof setupCallback === 'function') {
            try {
                setupCallback();
                log(`✅ 模态框设置回调执行成功`);
            } catch (error) {
                log(`❌ 模态框设置回调执行失败: ${error.message}`);
                return false;
            }
        }
        
        // 多重显示方式确保兼容性
        modal.classList.remove('modal-hidden', 'hidden');
        modal.classList.add('modal-show', 'show');
        modal.style.display = 'flex';
        modal.style.visibility = 'visible';
        modal.style.opacity = '1';
        modal.style.pointerEvents = 'auto';
        modal.style.zIndex = '9999';
        
        // 防止背景滚动
        document.body.style.overflow = 'hidden';
        
        log(`✅ 模态框已显示: ${modalId}`);
        return true;
    }
    
    // 安全的模态框隐藏函数
    function safeHideModal(modalId) {
        log(`🔒 准备隐藏模态框: ${modalId}`);
        
        const modal = safeGetElement(modalId);
        if (!modal) {
            return false;
        }
        
        modal.classList.remove('modal-show', 'show');
        modal.classList.add('modal-hidden', 'hidden');
        modal.style.display = 'none';
        modal.style.visibility = 'hidden';
        modal.style.opacity = '0';
        modal.style.pointerEvents = 'none';
        
        // 恢复背景滚动
        document.body.style.overflow = '';
        
        log(`✅ 模态框已隐藏: ${modalId}`);
        return true;
    }
    
    // 通用的API调用函数
    function apiCall(url, options = {}) {
        log(`🌐 API调用: ${url}`);
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        return fetch(url, { ...defaultOptions, ...options })
            .then(response => {
                log(`📡 API响应状态: ${response.status}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                log(`📦 API响应数据:`, data);
                return data;
            })
            .catch(error => {
                log(`❌ API调用失败: ${error.message}`);
                throw error;
            });
    }
    
    // ========================================
    // 1. 刷单管理模态框修复
    // ========================================
    window.GlobalModalManager.showAddModal = function() {
        log(`🚀 全局showAddModal被调用`);
        
        ensureDOMReady(() => {
            const modal = safeGetElement('orderModal');
            if (!modal) {
                log(`❌ 找不到orderModal元素`);
                return;
            }
            
            const setupModal = () => {
                // 重置表单
                const form = safeGetElement('orderForm');
                if (form) form.reset();
                
                const modalTitle = safeGetElement('modalTitle');
                if (modalTitle) modalTitle.textContent = '添加刷单记录';
                
                const orderId = safeGetElement('orderId');
                if (orderId) orderId.value = '';
                
                const orderTime = safeGetElement('order_time');
                if (orderTime) orderTime.value = new Date().toISOString().slice(0, 16);
            };
            
            safeShowModal('orderModal', setupModal);
        });
    };
    
    window.GlobalModalManager.closeModal = function() {
        log(`🔒 全局closeModal被调用`);
        safeHideModal('orderModal');
    };
    
    // ========================================
    // 2. 正课管理退费模态框修复
    // ========================================
    window.GlobalModalManager.showRefundModal = function(courseId) {
        log(`🚀 全局showRefundModal被调用，课程ID: ${courseId}`);
        
        if (!courseId) {
            alert('课程ID无效');
            return;
        }
        
        // 保护：若页面存在试听退款表单元素，判定为试听上下文，禁止调用正课退费接口
        try {
            const trialRefundForm = document.getElementById('refundForm');
            const trialRefundModal = document.getElementById('refundModal');
            if (trialRefundForm || trialRefundModal) {
                log('⚠️ 检测到试听页上下文，已阻止调用正课退费模态');
                alert('当前为试听课程，请直接在本页提交试听退费。');
                return;
            }
        } catch (e) { /* 忽略检测错误，按原逻辑继续 */ }

        ensureDOMReady(() => {
            // 获取课程信息并显示退费模态框
            apiCall(`/api/formal-courses/${courseId}`)
                .then(courseData => {
                    if (!courseData.success) {
                        throw new Error(courseData.message || '获取课程信息失败');
                    }
                    
                    return apiCall(`/api/courses/${courseId}/refund-info`)
                        .then(refundData => {
                            if (!refundData.success) {
                                throw new Error(refundData.message || '获取退费信息失败');
                            }
                            
                            const setupRefundModal = () => {
                                // 填充课程信息
                                const elements = {
                                    'refund_course_id': courseId,
                                    'refund_customer_name': courseData.customer_name || '未知',
                                    'refund_course_type': courseData.course_type || '未知',
                                    'refund_purchased_sessions': courseData.sessions || 0,
                                    'refund_refunded_sessions': refundData.refund_summary.total_refunded_sessions || 0,
                                    'refund_refundable_sessions': refundData.refund_summary.refundable_sessions || 0,
                                    'refund_unit_price': `¥${(refundData.refund_summary.unit_price || 0).toFixed(2)}`
                                };
                                
                                for (const [id, value] of Object.entries(elements)) {
                                    const element = safeGetElement(id);
                                    if (element) {
                                        if (element.tagName === 'INPUT') {
                                            element.value = value;
                                        } else {
                                            element.textContent = value;
                                        }
                                    }
                                }
                                
                                // 设置最大可退费节数
                                const refundSessions = safeGetElement('refund_sessions');
                                if (refundSessions) {
                                    refundSessions.max = refundData.refund_summary.refundable_sessions || 0;
                                }
                                
                                // 保存退费数据到全局变量
                                window.currentRefundCourse = {
                                    ...courseData,
                                    ...refundData.refund_summary,
                                    refund_history: refundData.refund_history || []
                                };
                            };
                            
                            safeShowModal('refundModal', setupRefundModal);
                        });
                })
                .catch(error => {
                    log(`❌ 退费模态框显示失败: ${error.message}`);
                    alert(`获取信息失败：${error.message}`);
                });
        });
    };
    
    window.GlobalModalManager.closeRefundModal = function() {
        log(`🔒 全局closeRefundModal被调用`);
        
        safeHideModal('refundModal');
        
        // 重置表单
        const form = safeGetElement('refundForm');
        if (form) form.reset();
        
        // 隐藏退费历史
        const historySection = safeGetElement('refundHistorySection');
        if (historySection) historySection.style.display = 'none';
        
        // 清除全局变量
        window.currentRefundCourse = null;
    };
    
    // ========================================
    // 3. 客户详情模态框修复（委托到本地实现的加载逻辑）
    // ========================================
    window.GlobalModalManager.showCustomerDetail = function(customerId, courseId = null, courseType = null) {
        log(`🚀 全局showCustomerDetail被调用`, { customerId, courseId, courseType });
        
        if (!customerId && !courseId) {
            alert('参数无效');
            return;
        }
        
        ensureDOMReady(() => {
            const setupCustomerModal = () => {
                // 复用本地实现的展示结构：重置并隐藏所有区块
                const form = safeGetElement('customerDetailForm');
                if (form) form.reset();
                
                const trialSec = document.getElementById('trialCourseSection');
                const formalSec = document.getElementById('formalCourseSection');
                const profitSec = document.getElementById('profitPreviewSection');
                const refundSec = document.getElementById('refundSection');
                const refundInfoSec = document.getElementById('refundInfoSection');
                const renewalInfoSec = document.getElementById('renewalInfoSection');
                if (trialSec) trialSec.style.display = 'none';
                if (formalSec) formalSec.style.display = 'none';
                if (profitSec) profitSec.style.display = 'none';
                if (refundSec) refundSec.style.display = 'none';
                if (refundInfoSec) refundInfoSec.style.display = 'none';
                if (renewalInfoSec) renewalInfoSec.style.display = 'none';
                
                // 调用本地的数据加载函数，保持原有字段与区块逻辑
                try {
                    if (courseType === 'trial' && courseId && typeof window.loadTrialCourseDetail === 'function') {
                        window.loadTrialCourseDetail(courseId);
                    } else if (courseType === 'formal' && courseId && typeof window.loadFormalCourseDetail === 'function') {
                        window.loadFormalCourseDetail(courseId);
                    } else if (customerId && typeof window.loadCustomerDetail === 'function') {
                        window.loadCustomerDetail(customerId);
                    } else {
                        log('⚠️ 找不到本地加载函数或参数无效');
                    }
                } catch (e) {
                    log(`❌ 本地加载函数执行失败: ${e.message}`);
                    alert('加载详情失败，请重试');
                }
            };
            
            safeShowModal('customerDetailModal', setupCustomerModal);
        });
    };
    
    // 填充客户数据的辅助函数
    function fillCustomerData(customer) {
        // 兼容 components/customer_detail_modal.html 中的实际ID
        // 基础隐藏字段
        setValueByIds(['detail_customer_id'], customer.id);

        // 基本信息
        setValueByIds(['detail_name', 'detail_customer_name'], customer.name);
        setValueByIds(['detail_phone', 'detail_customer_phone'], customer.phone);
        // wechat/age 在当前详情模态中不存在，避免无谓告警
        setValueByIds(['detail_gender', 'detail_customer_gender'], customer.gender);
        setValueByIds(['detail_grade', 'detail_customer_grade'], customer.grade);
        setValueByIds(['detail_region', 'detail_customer_region', 'detail_customer_location'], customer.region ?? customer.location);
        setValueByIds(['detail_source', 'detail_customer_source'], customer.source);
        setValueByIds(['detail_tutoring_exp', 'detail_customer_tutoring_exp'], customer.has_tutoring_experience);
        // 备注字段若未来存在，可加入 ['detail_remark','detail_customer_remark']
    }
    
    // 填充课程数据的辅助函数  
    function fillCourseData(course, courseType) {
        if (courseType === 'trial') {
            setValueByIds(['detail_course_id'], course.id);
            setValueByIds(['detail_trial_price'], course.trial_price);
            setValueByIds(['detail_trial_status'], course.trial_status);
            setValueByIds(['detail_trial_cost'], course.custom_trial_cost);
        } else if (courseType === 'formal') {
            // 兼容 customer_detail_modal.html 中的正课字段ID
            setValueByIds(['detail_course_id'], course.id);
            setValueByIds(['detail_course_type'], course.course_type);
            setValueByIds(['detail_sessions', 'detail_formal_sessions'], course.sessions);
            setValueByIds(['detail_gift_sessions'], course.gift_sessions);
            setValueByIds(['detail_price', 'detail_formal_price'], course.price);
            setValueByIds(['detail_payment_channel'], course.payment_channel);
            setValueByIds(['detail_other_cost', 'detail_formal_other_cost'], course.other_cost);
            // 自定义成本或单节成本
            const courseCost = course.custom_course_cost ?? course.course_cost;
            setValueByIds(['detail_course_cost', 'detail_formal_course_cost'], courseCost);
        }
    }
    
    // ========================================
    // 4. 试听课编辑模态框修复
    // ========================================
    window.GlobalModalManager.editTrialCourse = function(courseId) {
        log(`🚀 全局editTrialCourse被调用，课程ID: ${courseId}`);
        
        if (!courseId) {
            alert('课程ID无效');
            return;
        }
        
        ensureDOMReady(() => {
            apiCall(`/api/trial-courses/${courseId}`)
                .then(data => {
                    if (!data.success) {
                        throw new Error(data.message || '获取课程信息失败');
                    }
                    
                    const setupTrialEditModal = () => {
                        const course = data.course;
                        const customer = data.customer || {};
                        
                        // 填充试听课编辑表单（使用多ID兼容映射，优先匹配现有模板ID）
                        setValueByIds(['edit_trial_course_id'], course.id);
                        setValueByIds(['edit_trial_customer_name'], customer.name);
                        setValueByIds(['edit_trial_customer_phone'], customer.phone);
                        setValueByIds(['edit_trial_customer_gender'], customer.gender);
                        setValueByIds(['edit_trial_customer_grade'], customer.grade);
                        setValueByIds(['edit_trial_customer_region', 'edit_trial_customer_location'], customer.region ?? customer.location);
                        setValueByIds(['edit_trial_has_tutoring_experience'], customer.has_tutoring_experience);
                        setValueByIds(['edit_trial_price'], course.trial_price);
                        setValueByIds(['edit_trial_source'], course.source ?? customer.source);
                        // 下列字段在当前模板中可能不存在，故不强制设置以减少告警：
                        // edit_trial_status, edit_trial_cost, edit_trial_employee_id, edit_trial_remark, edit_trial_customer_wechat, edit_trial_customer_age
                    };
                    
                    safeShowModal('editTrialModal', setupTrialEditModal);
                })
                .catch(error => {
                    log(`❌ 试听课编辑模态框显示失败: ${error.message}`);
                    alert(`获取课程信息失败：${error.message}`);
                });
        });
    };
    
    // ========================================
    // 5. 全局函数替换和兼容性处理
    // ========================================
    
    // 在DOM加载完成后替换全局函数
    ensureDOMReady(() => {
        log(`🔄 开始替换全局函数...`);
        
        // 替换常见的模态框函数
        if (typeof window.showAddModal === 'undefined') {
            window.showAddModal = window.GlobalModalManager.showAddModal;
            log(`✅ 已设置全局showAddModal函数`);
        }
        
        if (typeof window.closeModal === 'undefined') {
            window.closeModal = window.GlobalModalManager.closeModal;
            log(`✅ 已设置全局closeModal函数`);
        }
        
        if (typeof window.showRefundModal === 'undefined') {
            window.showRefundModal = window.GlobalModalManager.showRefundModal;
            log(`✅ 已设置全局showRefundModal函数`);
        }
        
        if (typeof window.closeRefundModal === 'undefined') {
            window.closeRefundModal = window.GlobalModalManager.closeRefundModal;
            log(`✅ 已设置全局closeRefundModal函数`);
        }
        
        if (typeof window.showCustomerDetail === 'undefined') {
            window.showCustomerDetail = window.GlobalModalManager.showCustomerDetail;
            log(`✅ 已设置全局showCustomerDetail函数`);
        }
        
        if (typeof window.editTrialCourse === 'undefined') {
            window.editTrialCourse = window.GlobalModalManager.editTrialCourse;
            log(`✅ 已设置全局editTrialCourse函数`);
        }
        
        // 刷单订单详情查看：始终包一层全局委托，兼容本地函数与兜底显示
        (function(){
            const originalShowOrderDetail = (typeof window.showOrderDetail === 'function') ? window.showOrderDetail : null;
            window.showOrderDetail = function(orderId){
                log(`🛒 全局委托 showOrderDetail`, { orderId });
                // 如果有本地实现，先调用本地（完成数据填充）
                if (originalShowOrderDetail) {
                    try {
                        originalShowOrderDetail(orderId);
                    } catch (e) {
                        log(`⚠️ 本地showOrderDetail执行异常: ${e.message}`);
                    }
                    // 无论本地执行是否成功，都强制确保模态显示
                    ensureDOMReady(() => {
                        safeShowModal('taobaoOrderDetailModal');
                    });
                    return;
                }
                // 无本地实现时，走兜底：请求、填充、显示
                ensureDOMReady(() => {
                    const modalId = 'taobaoOrderDetailModal';
                    apiCall(`/api/taobao-orders/${orderId}`)
                        .then(data => {
                            if (!data.success) {
                                throw new Error(data.message || '获取订单信息失败');
                            }
                            const order = data.order || {};
                            setValueByIds(['order_detail_id'], order.id);
                            setValueByIds(['order_detail_name'], order.name);
                            setValueByIds(['order_detail_level'], order.level);
                            setValueByIds(['order_detail_amount'], order.amount);
                            setValueByIds(['order_detail_commission'], order.commission);
                            setValueByIds(['order_detail_taobao_fee'], order.taobao_fee || 0);
                            setValueByIds(['order_detail_evaluated'], order.evaluated ? '1' : '0');
                            setValueByIds(['order_detail_settled'], order.settled ? '1' : '0');
                            if (order.order_time) {
                                const t = new Date(order.order_time);
                                setValueByIds(['order_detail_order_time'], t.toISOString().slice(0, 16));
                            }
                            const settlementInfo = document.getElementById('settlementInfo');
                            if (settlementInfo) {
                                settlementInfo.style.display = order.settled ? 'flex' : 'none';
                            }
                            if (order.settled && order.settled_at) {
                                const st = new Date(order.settled_at);
                                setValueByIds(['order_detail_settled_at'], st.toISOString().slice(0, 16));
                            }
                            if (typeof window.updateOrderCostPreview === 'function') {
                                window.updateOrderCostPreview();
                            }
                        })
                        .catch(err => {
                            alert(`获取订单信息失败：${err.message}`);
                        })
                        .finally(() => {
                            safeShowModal(modalId);
                        });
                });
            };
            log(`✅ 已设置全局showOrderDetail函数（包装本地并兜底显示）`);
        })();
        
        log(`🎉 全局模态框管理器初始化完成！`);
    });
    
    // ========================================
    // 6. 错误监控和恢复机制
    // ========================================
    
    // 监听未捕获的错误
    window.addEventListener('error', function(event) {
        log(`💥 捕获到错误: ${event.error.message}`, event.error);
    });
    
    // 提供手动修复按钮的功能
    window.GlobalModalManager.forceShowModal = function(modalId) {
        log(`🔧 强制显示模态框: ${modalId}`);
        
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.cssText = `
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                background-color: rgba(0, 0, 0, 0.5) !important;
                z-index: 9999 !important;
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                visibility: visible !important;
                opacity: 1 !important;
            `;
            
            document.body.style.overflow = 'hidden';
            log(`✅ 模态框已强制显示: ${modalId}`);
            return true;
        }
        
        log(`❌ 强制显示失败，模态框不存在: ${modalId}`);
        return false;
    };
    
    log(`🚀 全局模态框修复脚本加载完成！`);
    
})();
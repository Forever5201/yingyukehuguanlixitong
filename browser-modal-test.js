
// ========================================
// 浏览器端模态框功能测试脚本
// 请在各个页面的Console中执行此脚本
// ========================================

console.log('🧪 开始浏览器端模态框功能测试...');

// 测试全局修复脚本是否加载
if (typeof GlobalModalManager !== 'undefined') {
    console.log('✅ GlobalModalManager已加载');
    
    // 测试各个函数是否存在
    const functions = [
        'showAddModal',
        'closeModal', 
        'showRefundModal',
        'closeRefundModal',
        'showCustomerDetail',
        'editTrialCourse',
        'forceShowModal'
    ];
    
    console.log('\n📋 函数可用性检查:');
    functions.forEach(funcName => {
        const exists = typeof GlobalModalManager[funcName] === 'function';
        const globalExists = typeof window[funcName] === 'function';
        console.log(`  ${exists ? '✅' : '❌'} GlobalModalManager.${funcName} - ${exists ? '可用' : '不可用'}`);
        console.log(`  ${globalExists ? '✅' : '❌'} window.${funcName} - ${globalExists ? '可用' : '不可用'}`);
    });
    
    console.log('\n🎯 测试命令:');
    console.log('在刷单管理页面执行:');
    console.log('  GlobalModalManager.showAddModal()');
    console.log('  或 showAddModal()');
    console.log('');
    console.log('在正课管理页面执行:'); 
    console.log('  GlobalModalManager.showRefundModal(1)  // 使用实际的课程ID');
    console.log('  GlobalModalManager.showCustomerDetail(1, 1, "formal")');
    console.log('');
    console.log('在试听课管理页面执行:');
    console.log('  GlobalModalManager.editTrialCourse(1)  // 使用实际的课程ID');
    console.log('  GlobalModalManager.showCustomerDetail(1, 1, "trial")');
    console.log('');
    console.log('强制显示任意模态框:');
    console.log('  GlobalModalManager.forceShowModal("orderModal")');
    console.log('  GlobalModalManager.forceShowModal("refundModal")');
    console.log('  GlobalModalManager.forceShowModal("customerDetailModal")');
    
} else {
    console.error('❌ GlobalModalManager未加载！请检查global-modal-fix.js文件是否正确引入。');
}

console.log('\n✅ 浏览器端测试脚本执行完成！');

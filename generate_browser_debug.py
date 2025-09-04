#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行时调试工具：生成JavaScript代码用于在浏览器Console中直接调试模态框
"""

def generate_browser_debug_script():
    """生成浏览器调试脚本"""
    
    debug_script = """
// ========================================
// 刷单管理模态框运行时调试工具
// 请将以下代码复制到浏览器Console中执行
// ========================================

console.log('🔧 开始模态框调试...');

// 1. 检查模态框元素是否存在
const modal = document.getElementById('orderModal');
if (!modal) {
    console.error('❌ 严重问题：找不到orderModal元素！');
} else {
    console.log('✅ 找到orderModal元素');
    console.log('📊 模态框当前状态:', {
        display: getComputedStyle(modal).display,
        visibility: getComputedStyle(modal).visibility,
        opacity: getComputedStyle(modal).opacity,
        zIndex: getComputedStyle(modal).zIndex,
        position: getComputedStyle(modal).position,
        classList: Array.from(modal.classList),
        inlineStyle: modal.style.cssText
    });
}

// 2. 检查CSS样式定义
function checkCSSRules() {
    console.log('\\n🎨 检查CSS样式定义...');
    
    // 查找所有样式表
    let hiddenRuleFound = false;
    let showRuleFound = false;
    
    for (let i = 0; i < document.styleSheets.length; i++) {
        try {
            const styleSheet = document.styleSheets[i];
            const rules = styleSheet.cssRules || styleSheet.rules;
            
            for (let j = 0; j < rules.length; j++) {
                const rule = rules[j];
                if (rule.selectorText === '.modal-hidden') {
                    hiddenRuleFound = true;
                    console.log('✅ 找到modal-hidden规则:', rule.cssText);
                }
                if (rule.selectorText === '.modal-show') {
                    showRuleFound = true;
                    console.log('✅ 找到modal-show规则:', rule.cssText);
                }
            }
        } catch (e) {
            // 跨域样式表会抛出异常，忽略
        }
    }
    
    if (!hiddenRuleFound) {
        console.warn('⚠️ 未找到modal-hidden CSS规则');
    }
    if (!showRuleFound) {
        console.warn('⚠️ 未找到modal-show CSS规则');
    }
}

checkCSSRules();

// 3. 测试手动显示模态框
function testManualShow() {
    console.log('\\n🧪 测试手动显示模态框...');
    
    if (!modal) {
        console.error('❌ 无法测试：模态框元素不存在');
        return;
    }
    
    // 方法1：直接设置样式
    console.log('方法1: 直接设置display=flex');
    modal.style.display = 'flex';
    
    setTimeout(() => {
        const currentDisplay = getComputedStyle(modal).display;
        console.log('结果1:', currentDisplay === 'flex' ? '✅ 成功' : '❌ 失败', '当前display:', currentDisplay);
        
        // 方法2：移除隐藏类
        console.log('\\n方法2: 移除modal-hidden类');
        modal.classList.remove('modal-hidden');
        
        setTimeout(() => {
            const currentDisplay2 = getComputedStyle(modal).display;
            console.log('结果2:', currentDisplay2 !== 'none' ? '✅ 成功' : '❌ 失败', '当前display:', currentDisplay2);
            
            // 方法3：添加显示类
            console.log('\\n方法3: 添加modal-show类');
            modal.classList.add('modal-show');
            
            setTimeout(() => {
                const currentDisplay3 = getComputedStyle(modal).display;
                console.log('结果3:', currentDisplay3 === 'flex' ? '✅ 成功' : '❌ 失败', '当前display:', currentDisplay3);
                
                // 如果模态框现在可见，说明CSS没问题
                if (currentDisplay3 === 'flex') {
                    console.log('\\n🎉 模态框可以正常显示！问题可能在JavaScript函数执行时机。');
                    
                    // 隐藏模态框以便后续测试
                    modal.classList.remove('modal-show');
                    modal.classList.add('modal-hidden');
                    modal.style.display = 'none';
                } else {
                    console.log('\\n❌ 模态框无法显示，存在CSS问题。');
                }
            }, 100);
        }, 100);
    }, 100);
}

testManualShow();

// 4. 测试showAddModal函数
function testShowAddModal() {
    console.log('\\n🔧 测试showAddModal函数...');
    
    if (typeof showAddModal === 'function') {
        console.log('✅ showAddModal函数存在');
        
        // 添加调试包装
        const originalShowAddModal = showAddModal;
        window.showAddModal = function() {
            console.log('🚀 调用showAddModal函数...');
            
            try {
                const result = originalShowAddModal.apply(this, arguments);
                
                // 检查执行后的状态
                setTimeout(() => {
                    const modal = document.getElementById('orderModal');
                    if (modal) {
                        const computedStyle = getComputedStyle(modal);
                        console.log('📊 函数执行后模态框状态:', {
                            display: computedStyle.display,
                            visibility: computedStyle.visibility,
                            opacity: computedStyle.opacity,
                            classList: Array.from(modal.classList)
                        });
                        
                        if (computedStyle.display === 'flex') {
                            console.log('✅ showAddModal函数工作正常！');
                        } else {
                            console.log('❌ showAddModal函数执行后模态框仍未显示');
                            console.log('💡 建议检查CSS样式优先级或JavaScript执行时机');
                        }
                    }
                }, 50);
                
                return result;
            } catch (error) {
                console.error('❌ showAddModal函数执行出错:', error);
            }
        };
        
        console.log('🎯 现在点击"添加刷单记录"按钮，或在Console中执行 showAddModal() 进行测试');
    } else {
        console.error('❌ showAddModal函数不存在！');
    }
}

// 延迟执行以确保DOM加载完成
setTimeout(testShowAddModal, 500);

// 5. 提供修复建议
setTimeout(() => {
    console.log('\\n💡 修复建议:');
    console.log('1. 如果手动显示测试成功，但showAddModal失败，检查JavaScript函数实现');
    console.log('2. 如果手动显示测试失败，检查CSS样式定义和优先级');
    console.log('3. 确保没有其他CSS规则覆盖了模态框样式');
    console.log('4. 检查是否有JavaScript错误阻止了函数执行');
    console.log('\\n🔧 快速修复命令:');
    console.log('document.getElementById("orderModal").style.display = "flex"; // 强制显示');
    console.log('document.getElementById("orderModal").style.display = "none"; // 强制隐藏');
}, 2000);

console.log('\\n✅ 调试工具加载完成！请查看上方的测试结果。');
"""
    
    return debug_script

def main():
    """主函数"""
    print("🔧 生成浏览器运行时调试工具")
    print("=" * 50)
    
    script = generate_browser_debug_script()
    
    # 保存到文件
    with open('f:/3454353/browser_debug_modal.js', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("✅ 调试脚本已生成")
    print("📁 文件位置: f:/3454353/browser_debug_modal.js")
    print()
    print("📋 使用方法:")
    print("1. 在浏览器中打开刷单管理页面")
    print("2. 按F12打开开发者工具")
    print("3. 切换到Console标签")
    print("4. 复制以下脚本内容到Console中执行:")
    print()
    print("-" * 40)
    print(script)
    print("-" * 40)
    print()
    print("💡 这个脚本将帮助您:")
    print("- 检查模态框元素是否存在")
    print("- 验证CSS样式定义")
    print("- 测试手动显示模态框")
    print("- 调试showAddModal函数")
    print("- 提供具体的修复建议")

if __name__ == "__main__":
    main()
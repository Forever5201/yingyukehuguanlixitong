#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试听课删除后重新添加bug的具体修复方案
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """创建routes.py的备份"""
    routes_file = "f:/3454353/app/routes.py"
    backup_file = f"f:/3454353/app/routes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(routes_file):
        shutil.copy2(routes_file, backup_file)
        print(f"已创建备份文件: {backup_file}")
        return backup_file
    else:
        print("routes.py文件不存在")
        return None

def generate_fixed_code():
    """生成修复后的代码片段"""
    print("\n=== 修复方案代码 ===")
    
    print("\n1. 修复试听课添加API (routes.py 第380-450行):")
    print("""
# 在试听课添加API中的修复代码
@app.route('/api/trial_courses', methods=['POST'])
def add_trial_course():
    try:
        data = request.get_json()
        
        # 获取客户信息
        customer_id = data.get('customer_id')
        if not customer_id:
            # 创建新客户的逻辑...
            pass
        
        # 修复点1: 在重复检查前刷新数据库会话
        db.session.expire_all()  # 清除会话缓存
        
        # 修复点2: 更严格的重复检查
        existing_trial = db.session.query(Course).filter_by(
            customer_id=customer_id, 
            is_trial=True
        ).first()
        
        if existing_trial:
            # 修复点3: 提供更详细的错误信息
            customer = Customer.query.get(customer_id)
            error_msg = f"学员 {customer.name}({customer.phone}) 已有试听课记录(ID:{existing_trial.id})，无法重复添加！"
            app.logger.warning(f"试听课重复添加尝试: {error_msg}")
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # 创建新的试听课记录...
        trial = Course(
            name=data.get('name', '试听课'),
            customer_id=customer_id,
            is_trial=True,
            trial_price=float(data.get('trial_price', 0)),
            source=data.get('source', ''),
            cost=float(data.get('cost', 0))
        )
        
        db.session.add(trial)
        db.session.commit()
        
        app.logger.info(f"试听课添加成功: 客户ID={customer_id}, 试听课ID={trial.id}")
        return jsonify({'success': True, 'message': '试听课添加成功'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"试听课添加失败: {str(e)}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500
""")
    
    print("\n2. 修复试听课删除API (routes.py 第670-680行):")
    print("""
@app.route('/api/trial_courses/<int:course_id>', methods=['DELETE'])
def delete_trial_course(course_id):
    try:
        trial = Course.query.get_or_404(course_id)
        
        # 修复点1: 验证是否为试听课
        if not trial.is_trial:
            return jsonify({'success': False, 'message': '只能删除试听课记录'}), 400
        
        # 修复点2: 记录删除操作日志
        customer = Customer.query.get(trial.customer_id)
        app.logger.info(f"删除试听课: ID={course_id}, 客户={customer.name}({customer.phone})")
        
        db.session.delete(trial)
        
        # 修复点3: 确保事务提交
        db.session.commit()
        
        # 修复点4: 验证删除结果
        check_deleted = Course.query.get(course_id)
        if check_deleted:
            app.logger.error(f"试听课删除失败: ID={course_id} 仍然存在")
            return jsonify({'success': False, 'message': '删除失败，请重试'}), 500
        
        app.logger.info(f"试听课删除成功: ID={course_id}")
        return jsonify({'success': True, 'message': '删除成功'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"试听课删除失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500
""")

def generate_frontend_fixes():
    """生成前端修复代码"""
    print("\n3. 前端JavaScript修复 (templates中的相关文件):")
    print("""
// 修复删除操作的JavaScript代码
function deleteTrialCourse(courseId, customerName) {
    if (!confirm(`确定要删除 ${customerName} 的试听课记录吗？`)) {
        return;
    }
    
    // 修复点1: 添加loading状态
    const deleteBtn = event.target;
    deleteBtn.disabled = true;
    deleteBtn.textContent = '删除中...';
    
    fetch(`/api/trial_courses/${courseId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('删除成功');
            // 修复点2: 强制刷新页面数据
            location.reload();
        } else {
            alert(`删除失败: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('删除请求失败:', error);
        alert('删除请求失败，请检查网络连接');
    })
    .finally(() => {
        // 恢复按钮状态
        deleteBtn.disabled = false;
        deleteBtn.textContent = '删除';
    });
}

// 修复添加操作的JavaScript代码
function addTrialCourse(formData) {
    // 修复点3: 添加loading状态
    const submitBtn = document.querySelector('#submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = '添加中...';
    
    fetch('/api/trial_courses', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('添加成功');
            // 修复点4: 清空表单并刷新数据
            document.querySelector('#trial-form').reset();
            location.reload();
        } else {
            // 修复点5: 显示详细错误信息
            alert(`添加失败: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('添加请求失败:', error);
        alert('添加请求失败，请检查网络连接');
    })
    .finally(() => {
        // 恢复按钮状态
        submitBtn.disabled = false;
        submitBtn.textContent = '添加试听课';
    });
}
""")

def generate_database_migration():
    """生成数据库优化方案"""
    print("\n4. 数据库优化方案:")
    print("""
-- 添加数据库唯一约束（可选）
-- 这将在数据库层面防止重复记录
CREATE UNIQUE INDEX idx_customer_trial_unique 
ON course(customer_id) 
WHERE is_trial = 1;

-- 或者在SQLAlchemy模型中添加约束
class Course(db.Model):
    # ... 其他字段 ...
    
    __table_args__ = (
        db.Index('idx_customer_trial_unique', 'customer_id', 
                unique=True, 
                postgresql_where=db.text('is_trial = true')),
    )
""")

def main():
    """主函数"""
    print("=== 试听课删除后重新添加bug修复方案 ===")
    
    # 创建备份
    backup_file = create_backup()
    
    # 生成修复代码
    generate_fixed_code()
    generate_frontend_fixes()
    generate_database_migration()
    
    print("\n=== 修复步骤总结 ===")
    print("1. 已创建routes.py备份文件")
    print("2. 后端修复要点:")
    print("   - 在重复检查前刷新数据库会话")
    print("   - 添加详细的错误日志和信息")
    print("   - 在删除后验证操作结果")
    print("3. 前端修复要点:")
    print("   - 添加操作loading状态")
    print("   - 操作完成后强制刷新页面")
    print("   - 提供更好的用户反馈")
    print("4. 数据库优化:")
    print("   - 可选择添加唯一约束防止重复")
    
    print("\n=== 实施建议 ===")
    print("1. 先在测试环境实施修复")
    print("2. 测试各种场景（正常添加、删除、重新添加）")
    print("3. 确认修复效果后部署到生产环境")
    print("4. 监控日志确保问题解决")

if __name__ == '__main__':
    main()
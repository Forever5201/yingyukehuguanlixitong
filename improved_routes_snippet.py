"""
改进后的路由代码片段
修复了测试中发现的各种问题
"""

from flask import jsonify, request
from app.models import db, Config, Course, Employee, CommissionConfig
from datetime import datetime
import logging

# 配置日志
logger = logging.getLogger(__name__)

# ============ 利润分配相关改进 ============

@app.route('/api/profit-config', methods=['POST'])
def save_profit_config_improved():
    """保存利润分配配置（改进版）"""
    try:
        # 开始事务
        for key in request.form:
            # 输入验证
            if key.endswith('_shareholder_a'):
                try:
                    value = float(request.form[key])
                except ValueError:
                    return jsonify({'success': False, 'message': f'{key}必须是数字'})
                
                # 范围验证
                if value < 0 or value > 100:
                    return jsonify({'success': False, 'message': f'{key}必须在0-100之间'})
                
                # 自动计算B的比例
                b_key = key.replace('_a', '_b')
                b_value = 100 - value
                
                # 保存配置
                save_or_update_config(key, str(value))
                save_or_update_config(b_key, str(b_value))
                
                # 记录日志
                logger.info(f'利润分配配置更新: {key}={value}, {b_key}={b_value}')
        
        db.session.commit()
        return jsonify({'success': True, 'message': '配置保存成功'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'保存利润配置失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)})


def save_or_update_config(key, value):
    """保存或更新配置项"""
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Config(key=key, value=value)
        db.session.add(config)


@app.route('/api/profit-report')
def get_profit_report_improved():
    """获取利润分配报表（改进版）"""
    try:
        period = request.args.get('period', 'month')
        
        # 获取日期范围
        start_date, end_date = get_date_range(period, request.args)
        
        # 验证日期
        if start_date > end_date:
            return jsonify({
                'success': True,  # 不报错，返回空数据
                'new_courses': [],
                'renewal_courses': [],
                'summary': {
                    'total_revenue': 0,
                    'total_cost': 0,
                    'total_profit': 0,
                    'shareholder_a_total': 0,
                    'shareholder_b_total': 0
                },
                'distribution': {
                    'new_course_profit': 0,
                    'renewal_profit': 0,
                    'new_course_shareholder_a': 0,
                    'new_course_shareholder_b': 0,
                    'renewal_shareholder_a': 0,
                    'renewal_shareholder_b': 0
                },
                'config': get_profit_config()
            })
        
        # 获取配置（带缓存）
        profit_config = get_profit_config_cached()
        
        # 查询课程数据
        new_courses = Course.query.filter(
            Course.is_trial == False,
            Course.is_renewal == False,
            Course.created_at >= start_date,
            Course.created_at <= end_date
        ).all()
        
        renewal_courses = Course.query.filter(
            Course.is_trial == False,
            Course.is_renewal == True,
            Course.created_at >= start_date,
            Course.created_at <= end_date
        ).all()
        
        # 计算利润分配
        new_course_data, new_course_profit_total = calculate_courses_profit(
            new_courses, 
            profit_config['new_course_shareholder_a'],
            profit_config['new_course_shareholder_b']
        )
        
        renewal_data, renewal_profit_total = calculate_courses_profit(
            renewal_courses,
            profit_config['renewal_shareholder_a'],
            profit_config['renewal_shareholder_b']
        )
        
        # 汇总数据
        result = build_profit_report_result(
            new_course_data, renewal_data,
            new_course_profit_total, renewal_profit_total,
            profit_config
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'生成利润报表失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)})


def calculate_courses_profit(courses, shareholder_a_ratio, shareholder_b_ratio):
    """计算课程利润和分配"""
    course_data = []
    profit_total = 0
    
    for course in courses:
        # 安全的收入计算
        revenue = (course.sessions or 0) * (course.price or 0)
        
        # 处理折扣
        if course.meta:
            try:
                import json
                meta_data = json.loads(course.meta)
                discount = meta_data.get('discount_amount', 0)
                revenue -= discount
            except:
                pass
        
        # 安全的费用计算
        fee = 0
        if course.payment_channel == '淘宝':
            fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else 0.006
            fee = revenue * fee_rate
        
        # 安全的成本计算（处理None值）
        cost = (course.cost or 0) + fee
        profit = revenue - cost
        profit_total += profit
        
        # 分配计算
        shareholder_a = profit * shareholder_a_ratio / 100
        shareholder_b = profit * shareholder_b_ratio / 100
        
        course_data.append({
            'customer_name': course.customer.name if course.customer else '未知客户',
            'course_type': course.course_type or '未分类',
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
            'shareholder_a': shareholder_a,
            'shareholder_b': shareholder_b,
            'date': course.created_at.strftime('%Y-%m-%d') if course.created_at else '未知'
        })
    
    return course_data, profit_total


# ============ 员工业绩相关改进 ============

@app.route('/api/employees/<int:employee_id>/performance')
def get_employee_performance_improved(employee_id):
    """获取员工业绩详情（改进版）"""
    try:
        # 使用联表查询优化性能
        employee = Employee.query.get_or_404(employee_id)
        
        # 一次性获取所有相关数据
        courses = db.session.query(Course).join(Customer).filter(
            Course.assigned_employee_id == employee_id
        ).all()
        
        # 分离试听课和正课
        trial_courses = [c for c in courses if c.is_trial]
        formal_courses = [c for c in courses if not c.is_trial]
        
        # 计算统计数据
        stats = calculate_employee_stats(trial_courses, formal_courses)
        
        # 获取或创建提成配置
        config = get_or_create_commission_config(employee_id)
        
        # 计算提成
        commission_data = calculate_employee_commission(
            trial_courses, formal_courses, config
        )
        
        # 构建返回数据
        result = {
            'success': True,
            'employee_name': employee.name,
            'stats': stats,
            'trial_courses': format_trial_courses(trial_courses),
            'formal_courses': format_formal_courses(formal_courses),
            'commission': commission_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'获取员工业绩失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/employees/<int:employee_id>/commission-config', methods=['POST'])
def save_commission_config_improved(employee_id):
    """保存员工提成配置（改进版）"""
    try:
        # 验证员工存在
        employee = Employee.query.get_or_404(employee_id)
        
        data = request.get_json()
        
        # 输入验证
        errors = validate_commission_config(data)
        if errors:
            return jsonify({'success': False, 'errors': errors})
        
        # 使用事务保存配置
        config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if not config:
            config = CommissionConfig(employee_id=employee_id)
            db.session.add(config)
        
        # 更新配置
        for field in ['commission_type', 'trial_rate', 'new_course_rate', 'renewal_rate', 'base_salary']:
            if field in data:
                setattr(config, field, data[field])
        
        db.session.commit()
        
        # 记录日志
        logger.info(f'员工{employee.name}的提成配置已更新')
        
        return jsonify({
            'success': True,
            'message': '配置保存成功',
            'config': {
                'commission_type': config.commission_type,
                'trial_rate': config.trial_rate,
                'new_course_rate': config.new_course_rate,
                'renewal_rate': config.renewal_rate,
                'base_salary': config.base_salary
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'保存提成配置失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)})


def validate_commission_config(data):
    """验证提成配置数据"""
    errors = []
    
    # 验证提成类型
    if 'commission_type' in data:
        if data['commission_type'] not in ['profit', 'sales']:
            errors.append('提成类型必须是profit或sales')
    
    # 验证比例范围
    rate_fields = ['trial_rate', 'new_course_rate', 'renewal_rate']
    for field in rate_fields:
        if field in data:
            try:
                rate = float(data[field])
                if rate < 0 or rate > 100:
                    errors.append(f'{field}必须在0-100之间')
            except ValueError:
                errors.append(f'{field}必须是数字')
    
    # 验证底薪
    if 'base_salary' in data:
        try:
            salary = float(data['base_salary'])
            if salary < 0:
                errors.append('底薪不能为负数')
        except ValueError:
            errors.append('底薪必须是数字')
    
    return errors


def calculate_employee_commission(trial_courses, formal_courses, config):
    """计算员工提成（改进版）"""
    trial_commission = 0
    new_course_commission = 0
    renewal_commission = 0
    
    # 试听课提成（只计算转化的）
    for course in trial_courses:
        if course.trial_status == 'converted' and course.trial_price:
            trial_commission += (course.trial_price or 0) * (config.trial_rate / 100)
    
    # 正课提成
    for course in formal_courses:
        revenue = (course.sessions or 0) * (course.price or 0)
        
        # 根据提成类型计算基数
        if config.commission_type == 'profit':
            # 计算利润
            fee = 0
            if course.payment_channel == '淘宝' and course.snapshot_fee_rate:
                fee = revenue * (course.snapshot_fee_rate or 0.006)
            
            profit = revenue - (course.cost or 0) - fee
            base_amount = profit
        else:  # sales
            base_amount = revenue
        
        # 根据课程类型计算提成
        if course.is_renewal:
            renewal_commission += base_amount * (config.renewal_rate / 100)
        else:
            new_course_commission += base_amount * (config.new_course_rate / 100)
    
    # 汇总
    total_commission = trial_commission + new_course_commission + renewal_commission
    total_salary = (config.base_salary or 0) + total_commission
    
    return {
        'trial_commission': round(trial_commission, 2),
        'new_course_commission': round(new_course_commission, 2),
        'renewal_commission': round(renewal_commission, 2),
        'total_commission': round(total_commission, 2),
        'base_salary': config.base_salary or 0,
        'total_salary': round(total_salary, 2)
    }


# ============ 辅助函数 ============

def get_date_range(period, args):
    """获取日期范围"""
    now = datetime.now()
    
    if period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period == 'quarter':
        quarter = (now.month - 1) // 3
        start_date = datetime(now.year, quarter * 3 + 1, 1)
        end_date = now
    elif period == 'year':
        start_date = datetime(now.year, 1, 1)
        end_date = now
    else:  # custom
        try:
            start_date = datetime.strptime(args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(args.get('end_date'), '%Y-%m-%d')
        except:
            # 返回当月作为默认值
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
    
    return start_date, end_date


def get_profit_config_cached():
    """获取利润分配配置（带缓存）"""
    # 这里可以添加Redis缓存逻辑
    return get_profit_config()


def get_profit_config():
    """获取利润分配配置"""
    profit_config = {
        'new_course_shareholder_a': 50,
        'new_course_shareholder_b': 50,
        'renewal_shareholder_a': 40,
        'renewal_shareholder_b': 60
    }
    
    configs = Config.query.filter(Config.key.in_(profit_config.keys())).all()
    for config in configs:
        try:
            profit_config[config.key] = float(config.value)
        except ValueError:
            logger.warning(f'配置值无效: {config.key}={config.value}')
    
    return profit_config


def get_or_create_commission_config(employee_id):
    """获取或创建提成配置"""
    config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
    if not config:
        config = CommissionConfig(
            employee_id=employee_id,
            commission_type='profit',
            trial_rate=0,
            new_course_rate=0,
            renewal_rate=0,
            base_salary=0
        )
        # 不立即保存到数据库，只在内存中使用
    return config
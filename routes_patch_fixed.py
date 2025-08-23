"""
路由补丁文件（修复版）
用于修复现有路由的问题，确保测试能够通过
"""

import json
from datetime import datetime, timedelta
from flask import jsonify, request, current_app as app
from app.models import db, Config, Course, Employee, CommissionConfig

# ========== 辅助函数 ==========

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
    elif period == 'custom':
        try:
            start_date = datetime.strptime(args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(args.get('end_date'), '%Y-%m-%d')
        except:
            start_date = now.replace(day=1)
            end_date = now
    else:
        start_date = now.replace(day=1)
        end_date = now
    
    return start_date, end_date

def safe_float(value, default=0):
    """安全转换为浮点数"""
    try:
        return float(value) if value is not None else default
    except:
        return default

def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value) if value is not None else default
    except:
        return default

# ========== 修复利润报表路由 ==========

def get_profit_report_fixed():
    """获取利润分配报表（修复版）"""
    try:
        period = request.args.get('period', 'month')
        
        # 获取日期范围
        start_date, end_date = get_date_range(period, request.args)
        
        # 如果开始日期大于结束日期，返回空数据
        if start_date > end_date:
            return jsonify({
                'success': True,
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
                'config': {
                    'new_course_shareholder_a': 50,
                    'new_course_shareholder_b': 50,
                    'renewal_shareholder_a': 40,
                    'renewal_shareholder_b': 60
                }
            })
        
        # 获取利润分配配置
        profit_config = {
            'new_course_shareholder_a': 50,
            'new_course_shareholder_b': 50,
            'renewal_shareholder_a': 40,
            'renewal_shareholder_b': 60
        }
        
        configs = Config.query.filter(Config.key.in_(profit_config.keys())).all()
        for config in configs:
            profit_config[config.key] = safe_float(config.value, profit_config[config.key])
        
        # 获取正课数据（非续课）
        new_courses = Course.query.filter(
            Course.is_trial == False,
            Course.is_renewal == False,
            Course.created_at >= start_date,
            Course.created_at <= end_date
        ).all()
        
        # 获取续课数据
        renewal_courses = Course.query.filter(
            Course.is_trial == False,
            Course.is_renewal == True,
            Course.created_at >= start_date,
            Course.created_at <= end_date
        ).all()
        
        # 计算正课数据
        new_course_data = []
        new_course_profit_total = 0
        
        for course in new_courses:
            sessions = safe_int(course.sessions, 0)
            price = safe_float(course.price, 0)
            cost = safe_float(course.cost, 0)
            
            revenue = sessions * price
            fee = 0
            
            if course.payment_channel == '淘宝':
                fee_rate = safe_float(course.snapshot_fee_rate, 0.006)
                fee = revenue * fee_rate
            
            total_cost = cost + fee
            profit = revenue - total_cost
            new_course_profit_total += profit
            
            shareholder_a = profit * profit_config['new_course_shareholder_a'] / 100
            shareholder_b = profit * profit_config['new_course_shareholder_b'] / 100
            
            new_course_data.append({
                'customer_name': course.customer.name if course.customer else '',
                'course_type': course.course_type or '',
                'revenue': revenue,
                'cost': total_cost,
                'profit': profit,
                'shareholder_a': shareholder_a,
                'shareholder_b': shareholder_b,
                'date': course.created_at.strftime('%Y-%m-%d')
            })
        
        # 计算续课数据
        renewal_data = []
        renewal_profit_total = 0
        
        for course in renewal_courses:
            sessions = safe_int(course.sessions, 0)
            price = safe_float(course.price, 0)
            cost = safe_float(course.cost, 0)
            
            revenue = sessions * price
            
            # 检查是否有优惠
            discount = 0
            if course.meta:
                try:
                    meta_data = json.loads(course.meta)
                    discount = safe_float(meta_data.get('discount_amount', 0), 0)
                except:
                    pass
            
            revenue -= discount
            
            fee = 0
            if course.payment_channel == '淘宝':
                fee_rate = safe_float(course.snapshot_fee_rate, 0.006)
                fee = revenue * fee_rate
            
            total_cost = cost + fee
            profit = revenue - total_cost
            renewal_profit_total += profit
            
            shareholder_a = profit * profit_config['renewal_shareholder_a'] / 100
            shareholder_b = profit * profit_config['renewal_shareholder_b'] / 100
            
            renewal_data.append({
                'customer_name': course.customer.name if course.customer else '',
                'course_type': course.course_type or '',
                'revenue': revenue,
                'cost': total_cost,
                'profit': profit,
                'shareholder_a': shareholder_a,
                'shareholder_b': shareholder_b,
                'date': course.created_at.strftime('%Y-%m-%d')
            })
        
        # 计算汇总数据
        total_revenue = sum(c['revenue'] for c in new_course_data + renewal_data)
        total_cost = sum(c['cost'] for c in new_course_data + renewal_data)
        total_profit = new_course_profit_total + renewal_profit_total
        
        new_course_shareholder_a = new_course_profit_total * profit_config['new_course_shareholder_a'] / 100
        new_course_shareholder_b = new_course_profit_total * profit_config['new_course_shareholder_b'] / 100
        renewal_shareholder_a = renewal_profit_total * profit_config['renewal_shareholder_a'] / 100
        renewal_shareholder_b = renewal_profit_total * profit_config['renewal_shareholder_b'] / 100
        
        result = {
            'success': True,
            'config': profit_config,
            'new_courses': new_course_data,
            'renewal_courses': renewal_data,
            'summary': {
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'shareholder_a_total': new_course_shareholder_a + renewal_shareholder_a,
                'shareholder_b_total': new_course_shareholder_b + renewal_shareholder_b
            },
            'distribution': {
                'new_course_profit': new_course_profit_total,
                'new_course_shareholder_a': new_course_shareholder_a,
                'new_course_shareholder_b': new_course_shareholder_b,
                'renewal_profit': renewal_profit_total,
                'renewal_shareholder_a': renewal_shareholder_a,
                'renewal_shareholder_b': renewal_shareholder_b
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ========== 修复利润配置路由 ==========

def save_profit_config_fixed():
    """保存利润分配配置（修复版）"""
    try:
        # 获取并验证参数
        new_course_a = safe_float(request.form.get('new_course_shareholder_a', 50), 50)
        renewal_a = safe_float(request.form.get('renewal_shareholder_a', 40), 40)
        
        # 确保比例在合理范围内
        if new_course_a < 0:
            new_course_a = 0
        elif new_course_a > 100:
            new_course_a = 100
            
        if renewal_a < 0:
            renewal_a = 0
        elif renewal_a > 100:
            renewal_a = 100
        
        # 计算B的比例
        new_course_b = 100 - new_course_a
        renewal_b = 100 - renewal_a
        
        # 保存配置
        configs = {
            'new_course_shareholder_a': str(new_course_a),
            'new_course_shareholder_b': str(new_course_b),
            'renewal_shareholder_a': str(renewal_a),
            'renewal_shareholder_b': str(renewal_b)
        }
        
        for key, value in configs.items():
            config = Config.query.filter_by(key=key).first()
            if config:
                config.value = value
            else:
                config = Config(key=key, value=value)
                db.session.add(config)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '配置保存成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ========== 修复员工业绩路由 ==========

def get_employee_performance_fixed(employee_id):
    """获取员工业绩数据（修复版）"""
    try:
        # 查询员工
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': '员工不存在'}), 404
        
        # 获取员工的所有课程
        courses = Course.query.filter_by(assigned_employee_id=employee_id).all()
        
        # 统计数据
        trial_courses = [c for c in courses if c.is_trial]
        converted_trials = [c for c in trial_courses if c.trial_status == 'converted']
        formal_courses = [c for c in courses if not c.is_trial and not c.is_renewal]
        renewal_courses = [c for c in courses if c.is_renewal]
        
        # 计算统计信息
        trial_count = len(trial_courses)
        converted_count = len(converted_trials)
        conversion_rate = (converted_count / trial_count * 100) if trial_count > 0 else 0
        
        # 计算总收入
        total_revenue = 0
        for course in formal_courses + renewal_courses:
            sessions = safe_int(course.sessions, 0)
            price = safe_float(course.price, 0)
            total_revenue += sessions * price
        
        # 获取提成配置
        commission_config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if not commission_config:
            commission_config = CommissionConfig(
                employee_id=employee_id,
                commission_type='profit',
                trial_rate=10,
                new_course_rate=10,
                renewal_rate=15,
                base_salary=0
            )
            db.session.add(commission_config)
            db.session.commit()
        
        # 计算提成
        trial_commission = 0
        for trial in converted_trials:
            trial_price = safe_float(trial.trial_price, 0)
            trial_commission += trial_price * commission_config.trial_rate / 100
        
        new_course_commission = 0
        for course in formal_courses:
            sessions = safe_int(course.sessions, 0)
            price = safe_float(course.price, 0)
            cost = safe_float(course.cost, 0)
            
            revenue = sessions * price
            
            # 计算手续费
            fee = 0
            if course.payment_channel == '淘宝':
                fee_rate = safe_float(course.snapshot_fee_rate, 0.006)
                fee = revenue * fee_rate
            
            if commission_config.commission_type == 'profit':
                profit = revenue - cost - fee
                new_course_commission += profit * commission_config.new_course_rate / 100
            else:
                new_course_commission += revenue * commission_config.new_course_rate / 100
        
        renewal_commission = 0
        for course in renewal_courses:
            sessions = safe_int(course.sessions, 0)
            price = safe_float(course.price, 0)
            cost = safe_float(course.cost, 0)
            
            revenue = sessions * price
            
            # 计算手续费
            fee = 0
            if course.payment_channel == '淘宝':
                fee_rate = safe_float(course.snapshot_fee_rate, 0.006)
                fee = revenue * fee_rate
            
            if commission_config.commission_type == 'profit':
                profit = revenue - cost - fee
                renewal_commission += profit * commission_config.renewal_rate / 100
            else:
                renewal_commission += revenue * commission_config.renewal_rate / 100
        
        # 总提成和薪资
        total_commission = trial_commission + new_course_commission + renewal_commission
        total_salary = commission_config.base_salary + total_commission
        
        # 返回结果
        result = {
            'success': True,
            'employee_name': employee.name,
            'stats': {
                'trial_count': trial_count,
                'converted_count': converted_count,
                'conversion_rate': round(conversion_rate, 2),
                'total_revenue': total_revenue
            },
            'commission': {
                'trial_commission': round(trial_commission, 2),
                'new_course_commission': round(new_course_commission, 2),
                'renewal_commission': round(renewal_commission, 2),
                'total_commission': round(total_commission, 2),
                'base_salary': commission_config.base_salary,
                'total_salary': round(total_salary, 2)
            },
            'commission_config': {
                'commission_type': commission_config.commission_type,
                'trial_rate': commission_config.trial_rate,
                'new_course_rate': commission_config.new_course_rate,
                'renewal_rate': commission_config.renewal_rate,
                'base_salary': commission_config.base_salary
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ========== 修复提成配置路由 ==========

def save_commission_config_fixed(employee_id):
    """保存员工提成配置（修复版）"""
    try:
        # 查询员工
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': '员工不存在'}), 404
        
        # 获取参数
        data = request.get_json() if request.is_json else request.form
        
        commission_type = data.get('commission_type', 'profit')
        trial_rate = safe_float(data.get('trial_rate', 10), 10)
        new_course_rate = safe_float(data.get('new_course_rate', 10), 10)
        renewal_rate = safe_float(data.get('renewal_rate', 15), 15)
        base_salary = safe_float(data.get('base_salary', 0), 0)
        
        # 验证比率
        for rate in [trial_rate, new_course_rate, renewal_rate]:
            if rate < 0 or rate > 100:
                return jsonify({'success': False, 'message': '提成比例必须在0-100之间'})
        
        if base_salary < 0:
            return jsonify({'success': False, 'message': '底薪不能为负数'})
        
        # 更新或创建配置
        config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if config:
            config.commission_type = commission_type
            config.trial_rate = trial_rate
            config.new_course_rate = new_course_rate
            config.renewal_rate = renewal_rate
            config.base_salary = base_salary
        else:
            config = CommissionConfig(
                employee_id=employee_id,
                commission_type=commission_type,
                trial_rate=trial_rate,
                new_course_rate=new_course_rate,
                renewal_rate=renewal_rate,
                base_salary=base_salary
            )
            db.session.add(config)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '配置保存成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("路由补丁已加载")
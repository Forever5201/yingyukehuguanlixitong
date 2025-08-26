from flask import render_template, request, redirect, url_for, jsonify, flash, make_response, send_from_directory, current_app, Blueprint, session
from .models import db, Customer, Config, TaobaoOrder, Course, Employee, CommissionConfig, CourseRefund
from datetime import datetime, timedelta
import csv
from io import StringIO, BytesIO
import pandas as pd
import os
import json

# 导入服务层
from .services import RefundService, ProfitService, PerformanceService, TransactionService

# 创建主蓝图
main_bp = Blueprint('main', __name__)

# ========== 安全转换函数 ==========
def safe_float(value, default=0):
    """安全转换为浮点数"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


@main_bp.route('/test-js')
def test_js():
    """JavaScript测试页面"""
    return render_template('test_js.html')

@main_bp.route('/static/vendor/fontawesome/all.min.css')
def serve_fa_css():
    """本地提供 FontAwesome all.min.css，避免外部CDN超时导致样式缺失"""
    try:
        css_dir = os.path.join(current_app.root_path, 'static', 'vendor', 'fontawesome')
        css_path = os.path.join(css_dir, 'all.min.css')
        os.makedirs(css_dir, exist_ok=True)
        if not os.path.exists(css_path):
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write("/* fallback for fontawesome if CDN not available */\n")
        return send_from_directory(css_dir, 'all.min.css', mimetype='text/css')
    except Exception:
        return make_response("/* fallback */", 200, {"Content-Type": "text/css"})

@main_bp.route('/api/test')
def test_api():
    """简单的测试API"""
    return jsonify({'status': 'ok', 'message': '服务器正常工作'})

@main_bp.route('/api/test-excel')
def test_excel_export():
    """测试Excel导出功能"""
    try:
        # 创建简单的测试数据
        data = [
            {'订单ID': 1, '客户姓名': '测试客户1', '金额': 100},
            {'订单ID': 2, '客户姓名': '测试客户2', '金额': 200}
        ]
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='测试数据', index=False)
        
        output.seek(0)
        
        # 创建响应
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename="test.xlsx"'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/')
def home():
    # 批量获取配置值
    configs = {c.key: float(c.value) for c in Config.query.filter(Config.key.in_([
        'trial_cost', 'course_cost', 'taobao_fee_rate'
    ])).all()}
    
    trial_cost_value = configs.get('trial_cost', 0)
    course_cost_value = configs.get('course_cost', 0)
    taobao_fee_rate_value = configs.get('taobao_fee_rate', 0)
    
    # 获取统计数据（单次查询）
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    
    # 分别查询客户和订单统计，避免笛卡尔积
    from sqlalchemy import case
    
    # 客户统计
    customer_stats = db.session.query(
        db.func.count(Customer.id).label('total_customers'),
        db.func.sum(case((Customer.created_at >= current_month_start, 1), else_=0)).label('new_customers')
    ).first()
    
    # 订单统计
    order_stats = db.session.query(
        db.func.count(TaobaoOrder.id).label('total_orders'),
        db.func.coalesce(db.func.sum(TaobaoOrder.amount), 0).label('total_order_amount')
    ).first()
    
    # 获取最近客户（使用索引）
    recent_customers = Customer.query.with_entities(
        Customer.name, Customer.phone, Customer.grade, Customer.region, Customer.created_at
    ).order_by(Customer.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_customers=customer_stats.total_customers or 0,
                         new_customers=customer_stats.new_customers or 0,
                         trial_cost=trial_cost_value,
                         course_cost=course_cost_value,
                         taobao_fee_rate=taobao_fee_rate_value,
                         total_orders=order_stats.total_orders or 0,
                         total_order_amount=order_stats.total_order_amount or 0,
                         recent_customers=recent_customers)

@main_bp.route('/customers', methods=['GET', 'POST'])
def manage_customers():
    if request.method == 'POST':
        name = request.form['name'].strip()
        gender = request.form['gender']
        grade = request.form['grade']
        region = request.form['region']
        phone = request.form['phone'].strip()
        source = request.form['source']
        
        # 验证必填字段
        if not name or not phone:
            flash('请填写客户姓名和联系电话！', 'error')
            return redirect(url_for('main.manage_customers'))
        
        # 检查手机号是否已存在
        existing_customer = Customer.query.filter_by(phone=phone).first()
        if existing_customer:
            flash(f'手机号 {phone} 已存在，客户：{existing_customer.name}', 'error')
            return redirect(url_for('main.manage_customers'))
        
        new_customer = Customer(
            name=name, 
            gender=gender if gender else None, 
            grade=grade if grade else None, 
            region=region if region else None, 
            phone=phone, 
            source=source if source else None
        )
        db.session.add(new_customer)
        db.session.commit()
        flash(f'客户 {name} 添加成功！', 'success')
        return redirect(url_for('main.manage_customers'))

    # 使用分页和选择性字段查询
    customers = Customer.query.with_entities(
        Customer.id, Customer.name, Customer.gender, 
        Customer.grade, Customer.region, Customer.phone, 
        Customer.source, Customer.created_at
    ).order_by(Customer.created_at.desc()).all()
    return render_template('customers.html', customers=customers)

@main_bp.route('/employee-performance')
def employee_performance():
    """员工业绩管理页面"""
    employees = Employee.query.all()
    
    # 计算每个员工的基础统计数据
    for employee in employees:
        # 试听课统计
        trial_courses = Course.query.filter_by(
            assigned_employee_id=employee.id, 
            is_trial=True
        ).all()
        
        # 转化统计
        converted_count = sum(1 for c in trial_courses if c.converted_to_course)
        conversion_rate = (converted_count / len(trial_courses) * 100) if trial_courses else 0
        
        # 本月业绩（正课）- 只计算试听课和正课都分配给该员工的记录
        from datetime import datetime, timedelta
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_courses = []
        for trial_course in trial_courses:
            if trial_course.converted_to_course:
                # 查找对应的正课
                formal_course = Course.query.get(trial_course.converted_to_course)
                if (formal_course and 
                    formal_course.assigned_employee_id == employee.id and
                    formal_course.created_at >= start_of_month):
                    monthly_courses.append(formal_course)
        
        monthly_revenue = sum(c.sessions * c.price for c in monthly_courses)
        
        employee.stats = {
            'trial_count': len(trial_courses),
            'conversion_rate': conversion_rate,
            'monthly_revenue': monthly_revenue
        }
    
    return render_template('employee_performance.html', employees=employees)

@main_bp.route('/api/employees/<int:employee_id>/performance')
def get_employee_performance(employee_id):
    """获取员工业绩详情 - 优化版，使用PerformanceService"""
    try:
        # 获取查询参数
        period = request.args.get('period', 'all')
        
        # 根据期间计算日期范围
        from datetime import datetime
        now = datetime.now()
        start_date = None
        end_date = None
        
        if period == 'current_month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
            end_date = now
        elif period == 'last_month':
            start_date = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = now.replace(day=1) - timedelta(days=1)
        
        # 使用服务层获取业绩数据
        performance = PerformanceService.calculate_employee_performance(
            employee_id, start_date, end_date
        )
        
        # 格式化返回数据以兼容现有前端
        result = {
            'success': True,
            'employee_name': performance['employee']['name'],
            'stats': {
                'trial_count': performance['trial_courses']['count'],
                'converted_count': performance['trial_courses']['converted'],
                'conversion_rate': performance['trial_courses']['conversion_rate'],
                'total_revenue': performance['total_revenue']
            },
            'commission': performance['commission']
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': '获取业绩数据失败'}), 500

def calculate_course_profit(course):
    """计算课程利润"""
    sessions = safe_int(course.sessions, 0)
    price = safe_float(course.price, 0)
    revenue = sessions * price
    fee = 0
    if course.payment_channel == '淘宝':
        fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else 0.006
        fee = revenue * fee_rate
    return revenue - course.cost - fee

def calculate_course_profit_with_refund(course, include_refund=True):
    """统一的课程利润计算函数（考虑退费）"""
    # 原始计算
    sessions = safe_int(course.sessions, 0)
    price = safe_float(course.price, 0)
    revenue = sessions * price
    
    # 计算手续费（基于原始收入）
    fee = 0
    if course.payment_channel == '淘宝':
        fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else 0.006
        fee = revenue * fee_rate
    
    # 原始成本
    cost = safe_float(course.cost, 0)
    
    if include_refund and not course.is_trial:  # 只对正课计算退费
        # 获取退费记录
        refunds = CourseRefund.query.filter_by(
            course_id=course.id,
            status='completed'
        ).all()
        
        if refunds:
            total_refunded_sessions = sum(r.refund_sessions for r in refunds)
            total_refunded_amount = sum(r.refund_amount for r in refunds)
            
            # 实际收入 = 原始收入 - 退费金额
            actual_revenue = revenue - total_refunded_amount
            
            # 成本按比例调整
            actual_sessions = sessions - total_refunded_sessions
            if sessions > 0:
                # 分离固定成本和变动成本
                other_cost = safe_float(course.other_cost, 0)  # 固定成本
                course_cost = cost - other_cost  # 变动成本
                
                # 变动成本按比例，固定成本不变
                actual_cost = (course_cost * actual_sessions / sessions) + other_cost
            else:
                actual_cost = cost  # 全部退费时保留成本
            
            # 利润 = 实际收入 - 实际成本 - 手续费（手续费不退）
            profit = actual_revenue - actual_cost - fee
            
            return {
                'revenue': actual_revenue,
                'cost': actual_cost + fee,  # 为了兼容现有逻辑，成本包含手续费
                'profit': profit,
                'has_refund': True,
                'refund_info': {
                    'sessions': total_refunded_sessions,
                    'amount': total_refunded_amount
                }
            }
        else:
            # 没有退费，返回原始数据
            return {
                'revenue': revenue,
                'cost': cost + fee,
                'profit': revenue - cost - fee,
                'has_refund': False
            }
    else:
        # 不考虑退费的原始计算
        return {
            'revenue': revenue,
            'cost': cost + fee,
            'profit': revenue - cost - fee,
            'has_refund': False
        }

@main_bp.route('/api/employees/<int:employee_id>/commission-config', methods=['GET'])
def get_commission_config(employee_id):
    """获取员工提成配置"""
    try:
        config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if config:
            return jsonify({
                'success': True,
                'config': {
                    'commission_type': config.commission_type,
                    'trial_rate': config.trial_rate,
                    'new_course_rate': config.new_course_rate,
                    'renewal_rate': config.renewal_rate,
                    'base_salary': config.base_salary
                }
            })
        else:
            return jsonify({
                'success': True,
                'config': None
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/employees/<int:employee_id>/commission-config', methods=['POST'])
def save_commission_config(employee_id):
    """保存员工提成配置"""
    try:
        # 检查员工是否存在
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': '员工不存在'}), 404
        
        # 获取或创建配置
        config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if not config:
            config = CommissionConfig(employee_id=employee_id)
            db.session.add(config)
        
        # 更新配置
        config.commission_type = request.form.get('commission_type', 'profit')
        config.trial_rate = 0  # 试听课不参与提成
        config.new_course_rate = float(request.form.get('new_course_rate', 0))
        config.renewal_rate = float(request.form.get('renewal_rate', 0))
        config.base_salary = float(request.form.get('base_salary', 0))
        
        db.session.commit()
        return jsonify({'success': True, 'message': '配置保存成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/profit-distribution')
def profit_distribution():
    """股东利润分配页面"""
    # 获取利润分配配置
    profit_config = {
        'new_course_shareholder_a': 50,
        'new_course_shareholder_b': 50,
        'renewal_shareholder_a': 40,
        'renewal_shareholder_b': 60
    }
    
    # 从Config表获取配置
    configs = Config.query.filter(Config.key.in_([
        'new_course_shareholder_a',
        'new_course_shareholder_b', 
        'renewal_shareholder_a',
        'renewal_shareholder_b'
    ])).all()
    
    for config in configs:
        profit_config[config.key] = float(config.value)
    
    return render_template('profit_distribution.html', profit_config=profit_config)

@main_bp.route('/api/profit-config', methods=['POST'])
def save_profit_config():
    """保存利润分配配置"""
    try:
        # 验证比例是否正确
        new_course_a = float(request.form.get('new_course_shareholder_a', 50))
        new_course_b = 100 - new_course_a
        renewal_a = float(request.form.get('renewal_shareholder_a', 40))
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

@main_bp.route('/api/profit-report')
def get_profit_report():
    """获取利润分配报表 - 优化版，使用ProfitService"""
    try:
        period = request.args.get('period', 'month')
        
        # 确定时间范围
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
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        
        # 使用服务层生成利润报表
        report = ProfitService.generate_profit_report(start_date, end_date)
        
        # 获取利润分配配置（用于兼容现有前端）
        profit_config = {
            'new_course_shareholder_a': report['shareholder_distribution']['new_course']['ratio_a'],
            'new_course_shareholder_b': report['shareholder_distribution']['new_course']['ratio_b'],
            'renewal_shareholder_a': report['shareholder_distribution']['renewal']['ratio_a'],
            'renewal_shareholder_b': report['shareholder_distribution']['renewal']['ratio_b']
        }
        
        # 格式化结果以兼容现有前端
        result = {
            'success': True,
            'config': profit_config,
            'summary': report['summary'],
            'distribution': {
                'new_course_profit': report['profit_by_type']['new_course'],
                'new_course_shareholder_a': report['shareholder_distribution']['new_course']['shareholder_a'],
                'new_course_shareholder_b': report['shareholder_distribution']['new_course']['shareholder_b'],
                'renewal_profit': report['profit_by_type']['renewal'],
                'renewal_shareholder_a': report['shareholder_distribution']['renewal']['shareholder_a'],
                'renewal_shareholder_b': report['shareholder_distribution']['renewal']['shareholder_b']
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/config', methods=['GET', 'POST'])
def manage_config():
    if request.method == 'POST':
        config_type = request.form.get('config_type', 'basic')
        
        if config_type == 'profit_distribution':
            # 处理股东利润分配配置
            configs_to_save = {
                'shareholder_a_name': request.form.get('shareholder_a_name', '股东A'),
                'shareholder_b_name': request.form.get('shareholder_b_name', '股东B'),
                'new_course_shareholder_a': request.form.get('new_course_shareholder_a', '50'),
                'new_course_shareholder_b': str(100 - float(request.form.get('new_course_shareholder_a', '50'))),
                'renewal_shareholder_a': request.form.get('renewal_shareholder_a', '40'),
                'renewal_shareholder_b': str(100 - float(request.form.get('renewal_shareholder_a', '40')))
            }
            
            for key, value in configs_to_save.items():
                config = Config.query.filter_by(key=key).first()
                if config:
                    config.value = value
                else:
                    config = Config(key=key, value=value)
                    db.session.add(config)
            
            db.session.commit()
            flash('股东配置已更新', 'success')
        else:
            # 处理基础配置
            for key in ['trial_cost', 'course_cost', 'taobao_fee_rate', 'shuadan_products']:
                config_item = Config.query.filter_by(key=key).first()
                if not config_item:
                    config_item = Config(key=key)
                    db.session.add(config_item)
                config_item.value = request.form[key]
            db.session.commit()
            flash('基础配置已更新', 'success')
            
        return redirect(url_for('main.manage_config'))

    # 获取所有配置
    config_keys = [
        'trial_cost', 'course_cost', 'taobao_fee_rate', 'shuadan_products',
        'shareholder_a_name', 'shareholder_b_name',
        'new_course_shareholder_a', 'new_course_shareholder_b',
        'renewal_shareholder_a', 'renewal_shareholder_b'
    ]
    
    configs = Config.query.filter(Config.key.in_(config_keys)).all()
    config_dict = {c.key: c.value for c in configs}
    
    # 设置默认值
    config = {
        'trial_cost': config_dict.get('trial_cost', '0'),
        'course_cost': config_dict.get('course_cost', '0'),
        'taobao_fee_rate': config_dict.get('taobao_fee_rate', '0'),
        'shareholder_a_name': config_dict.get('shareholder_a_name', '股东A'),
        'shareholder_b_name': config_dict.get('shareholder_b_name', '股东B'),
        'new_course_shareholder_a': config_dict.get('new_course_shareholder_a', '50'),
        'new_course_shareholder_b': config_dict.get('new_course_shareholder_b', '50'),
        'renewal_shareholder_a': config_dict.get('renewal_shareholder_a', '40'),
        'renewal_shareholder_b': config_dict.get('renewal_shareholder_b', '60'),
        # 刷单商品列表（JSON 或逗号分隔）
        'shuadan_products': config_dict.get('shuadan_products', '')
    }
    
    return render_template('config.html', config=config)

@main_bp.route('/taobao-orders', methods=['GET', 'POST'])
def manage_taobao_orders():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        name = request.form['customer_name']
        level = request.form['level']
        product_name = request.form.get('product_name')
        amount = float(request.form['amount'])
        commission = float(request.form.get('commission', 0))
        evaluated = bool(request.form.get('evaluated'))
        
        # 自动计算淘宝手续费
        taobao_fee_rate_config = Config.query.filter_by(key='taobao_fee_rate').first()
        taobao_fee_rate = float(taobao_fee_rate_config.value) if taobao_fee_rate_config else 0.6
        taobao_fee = amount * (taobao_fee_rate / 100)
        
        # 处理时间格式
        order_time_str = request.form['order_time']
        if order_time_str:
            order_time = datetime.fromisoformat(order_time_str.replace('T', ' '))
        else:
            order_time = datetime.now()
        
        if order_id:  # 编辑现有记录
            order = TaobaoOrder.query.get(order_id)
            if order:
                order.name = name
                order.level = level
                order.product_name = product_name
                order.amount = amount
                order.commission = commission
                # 重新计算手续费
                order.taobao_fee = taobao_fee
                order.evaluated = evaluated
                order.order_time = order_time
        else:  # 添加新记录
            new_order = TaobaoOrder(
                name=name,
                level=level,
                product_name=product_name,
                amount=amount,
                commission=commission,
                taobao_fee=taobao_fee,
                evaluated=evaluated,
                order_time=order_time
            )
            db.session.add(new_order)
        
        db.session.commit()
        return redirect(url_for('main.manage_taobao_orders'))
    
    # 计算统计数据
    from sqlalchemy import case
    stats = db.session.query(
        db.func.count(TaobaoOrder.id).label('total_count'),
        db.func.coalesce(db.func.sum(TaobaoOrder.amount), 0).label('total_amount'),
        db.func.coalesce(db.func.sum(TaobaoOrder.commission), 0).label('total_commission'),
        db.func.coalesce(db.func.sum(TaobaoOrder.taobao_fee), 0).label('total_taobao_fee'),
        db.func.coalesce(db.func.sum(case((TaobaoOrder.settled == False, TaobaoOrder.amount), else_=0)), 0).label('pending_amount'),
        db.func.coalesce(db.func.sum(case((TaobaoOrder.settled == False, TaobaoOrder.commission), else_=0)), 0).label('pending_commission'),
        db.func.coalesce(db.func.sum(case((TaobaoOrder.settled == False, TaobaoOrder.taobao_fee), else_=0)), 0).label('pending_taobao_fee'),
        db.func.coalesce(db.func.sum(case((TaobaoOrder.settled == True, TaobaoOrder.amount), else_=0)), 0).label('settled_amount'),
        db.func.coalesce(db.func.sum(case((TaobaoOrder.settled == True, TaobaoOrder.commission), else_=0)), 0).label('settled_commission'),
        db.func.coalesce(db.func.sum(case((TaobaoOrder.settled == True, TaobaoOrder.taobao_fee), else_=0)), 0).label('settled_taobao_fee')
    ).first()
    
    # 计算总本金（刷单金额加上佣金）
    total_principal = (stats.total_amount or 0) + (stats.total_commission or 0)
    pending_principal = (stats.pending_amount or 0) + (stats.pending_commission or 0)
    settled_principal = (stats.settled_amount or 0) + (stats.settled_commission or 0)
    
    # 读取刷单商品配置（系统配置中 key=shuadan_products，value为JSON数组或逗号分隔字符串）
    import json
    products_cfg = Config.query.filter_by(key='shuadan_products').first()
    product_list = []
    if products_cfg and products_cfg.value:
        try:
            product_list = json.loads(products_cfg.value)
        except Exception:
            product_list = [s.strip() for s in products_cfg.value.split(',') if s.strip()]

    # 使用分页和选择性字段查询
    orders = TaobaoOrder.query.with_entities(
        TaobaoOrder.id, TaobaoOrder.name, TaobaoOrder.level, TaobaoOrder.product_name,
        TaobaoOrder.amount, TaobaoOrder.commission, TaobaoOrder.taobao_fee,
        TaobaoOrder.evaluated, TaobaoOrder.order_time, TaobaoOrder.settled, 
        TaobaoOrder.settled_at, TaobaoOrder.created_at
    ).order_by(TaobaoOrder.order_time.desc()).all()
    
    return render_template('taobao_orders.html', 
                         orders=orders,
                         products=product_list,
                         stats={
                             'total_count': stats.total_count or 0,
                             'total_amount': stats.total_amount or 0,
                             'total_commission': stats.total_commission or 0,
                             'total_taobao_fee': stats.total_taobao_fee or 0,
                             'total_principal': total_principal,
                             'pending_amount': stats.pending_amount or 0,
                             'pending_commission': stats.pending_commission or 0,
                             'pending_taobao_fee': stats.pending_taobao_fee or 0,
                             'pending_principal': pending_principal,
                             'settled_amount': stats.settled_amount or 0,
                             'settled_commission': stats.settled_commission or 0,
                             'settled_taobao_fee': stats.settled_taobao_fee or 0,
                             'settled_principal': settled_principal
                         })

@main_bp.route('/api/taobao-orders/<int:order_id>', methods=['GET'])
def get_taobao_order(order_id):
    """获取单个淘宝订单详情"""
    try:
        order = TaobaoOrder.query.get_or_404(order_id)
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'name': order.name,
                'level': order.level,
                'product_name': order.product_name,
                'amount': order.amount,
                'commission': order.commission,
                'taobao_fee': order.taobao_fee,
                'evaluated': order.evaluated,
                'order_time': order.order_time.isoformat() if order.order_time else None,
                'settled': order.settled,
                'settled_at': order.settled_at.isoformat() if order.settled_at else None,
                'created_at': order.created_at.isoformat() if order.created_at else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/taobao-orders/<int:order_id>', methods=['PUT'])
def update_taobao_order(order_id):
    """更新淘宝订单字段"""
    order = TaobaoOrder.query.get_or_404(order_id)
    data = request.json
    
    field = data.get('field')
    value = data.get('value')
    
    if field == 'settled':
        order.settled = bool(value)
        if order.settled:
            order.settled_at = datetime.now()
        else:
            order.settled_at = None
    elif field == 'level':
        order.level = value
    elif field == 'amount':
        order.amount = float(value)
        # 当修改刷单金额时，自动重新计算淘宝手续费
        taobao_fee_rate_config = Config.query.filter_by(key='taobao_fee_rate').first()
        taobao_fee_rate = float(taobao_fee_rate_config.value) if taobao_fee_rate_config else 0.6
        order.taobao_fee = order.amount * taobao_fee_rate / 100
    elif field == 'commission':
        order.commission = float(value)
    elif field == 'taobao_fee':
        order.taobao_fee = float(value)
    elif field == 'evaluated':
        order.evaluated = bool(value)
    elif field == 'order_time':
        order.order_time = datetime.fromisoformat(value.replace('T', ' ')) if value else None
    else:
        return jsonify({'success': False, 'message': '不支持的字段'})
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '更新成功',
        'order': {
            'id': order.id,
            'name': order.name,
            'level': order.level,
            'amount': order.amount,
            'commission': order.commission,
            'taobao_fee': order.taobao_fee,
            'evaluated': order.evaluated,
            'order_time': order.order_time.isoformat() if order.order_time else None,
            'settled': order.settled,
            'settled_at': order.settled_at.isoformat() if order.settled_at else None
        }
    })

@main_bp.route('/api/taobao-orders/<int:order_id>', methods=['DELETE'])
def delete_taobao_order(order_id):
    """删除淘宝订单"""
    order = TaobaoOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True, 'message': '订单删除成功'})

@main_bp.route('/api/export/taobao-orders')
def export_taobao_orders():
    """导出刷单数据为Excel"""
    try:
        current_app.logger.info("开始导出刷单数据")
        
        # 查询所有订单数据，与UI界面保持一致
        try:
            orders = TaobaoOrder.query.order_by(TaobaoOrder.order_time.desc()).all()
            current_app.logger.info(f"成功查询到 {len(orders)} 条订单")
        except Exception as query_error:
            current_app.logger.error(f"订单查询失败: {str(query_error)}")
            return jsonify({'error': f'订单查询失败: {str(query_error)}'}), 500
        
        if not orders:
            current_app.logger.info("没有找到订单数据")
            return jsonify({'error': '没有找到订单数据'}), 404
        
        # 准备完整的数据，与UI界面显示的字段保持一致
        data = []
        for i, order in enumerate(orders):
            try:
                data.append({
                    '序号': i + 1,
                    '订单ID': order.id,
                    '客户姓名': order.name or '',
                    '等级': order.level or '',
                    '刷单金额': order.amount or 0,
                    '佣金': order.commission or 0,
                    '淘宝手续费': order.taobao_fee or 0,
                    '本金': (order.amount or 0) + (order.commission or 0),
                    '是否已评价': '是' if order.evaluated else '否',
                    '订单时间': order.order_time.strftime('%Y-%m-%d %H:%M:%S') if order.order_time else '',
                    '结算状态': '已结算' if order.settled else '未结算',
                    '结算时间': order.settled_at.strftime('%Y-%m-%d %H:%M:%S') if order.settled_at else '',
                    '创建时间': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else ''
                })
            except Exception as data_error:
                current_app.logger.error(f"处理第{i+1}条订单数据时出错: {str(data_error)}")
                continue
        
        current_app.logger.info(f"准备了 {len(data)} 条数据")
        
        if not data:
            return jsonify({'error': '没有有效的数据可导出'}), 404
        
        # 创建DataFrame
        try:
            df = pd.DataFrame(data)
            current_app.logger.info("创建DataFrame成功")
        except Exception as df_error:
            current_app.logger.error(f"创建DataFrame失败: {str(df_error)}")
            return jsonify({'error': f'创建DataFrame失败: {str(df_error)}'}), 500
        
        # 创建Excel文件
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='刷单数据', index=False)
            
            output.seek(0)
            current_app.logger.info("Excel文件创建成功")
        except Exception as excel_error:
            current_app.logger.error(f"创建Excel文件失败: {str(excel_error)}")
            return jsonify({'error': f'创建Excel文件失败: {str(excel_error)}'}), 500
        
        # 生成文件名（使用英文避免编码问题）
        filename = f"taobao_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # 创建响应
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        current_app.logger.info("导出完成")
        return response
        
    except Exception as e:
        current_app.logger.error(f"导出刷单数据时出错: {str(e)}")
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@main_bp.route('/api/export/trial-courses')
def export_trial_courses():
    """导出试听课数据为Excel（使用现有模型字段）"""
    try:
        courses = Course.query.filter_by(is_trial=True).order_by(Course.created_at.desc()).all()

        data = []
        for course in courses:
            customer = db.session.get(Customer, course.customer_id)
            data.append({
                '课程ID': course.id,
                '客户姓名': customer.name if customer else '',
                '客户电话': customer.phone if customer else '',
                '课程类型': '试听课',
                '试听售价': course.trial_price or 0,
                '渠道来源': course.source or '',
                '状态': course.trial_status or '',
                '基础成本': course.cost or 0,
                '退款金额': course.refund_amount or 0,
                '退款手续费': course.refund_fee or 0,
                '退款渠道': course.refund_channel or '',
                '创建时间': course.created_at.strftime('%Y-%m-%d %H:%M:%S') if course.created_at else ''
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='试听课数据', index=False)

        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f"attachment; filename=trial_courses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return response
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@main_bp.route('/api/export/formal-courses')
def export_formal_courses():
    """导出正课数据为Excel（使用现有模型字段）"""
    try:
        courses = Course.query.filter_by(is_trial=False).order_by(Course.created_at.desc()).all()

        data = []
        for course in courses:
            customer = db.session.get(Customer, course.customer_id)
            price = float(course.price or 0)
            base_cost = float(course.cost or 0)
            other_cost = float(course.other_cost or 0)
            profit = price - base_cost - other_cost
            data.append({
                '课程ID': course.id,
                '客户姓名': customer.name if customer else '',
                '客户电话': customer.phone if customer else '',
                '课程类型': course.course_type or '',
                '购买节数': course.sessions or 0,
                '赠课节数': course.gift_sessions or 0,
                '课程售价': price,
                '课程成本': base_cost,
                '其他成本': other_cost,
                '利润': profit,
                '支付渠道': course.payment_channel or '',
                '来源': course.source or '',
                '创建时间': course.created_at.strftime('%Y-%m-%d %H:%M:%S') if course.created_at else ''
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='正课数据', index=False)

        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f"attachment; filename=formal_courses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return response
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500







@main_bp.route('/api/taobao-orders/settle', methods=['POST'])
def settle_orders():
    """批量结算淘宝订单"""
    order_ids = request.json.get('order_ids', [])
    if not order_ids:
        return jsonify({'success': False, 'message': '请选择要结算的订单'})
    
    # 更新订单结算状态
    orders = TaobaoOrder.query.filter(TaobaoOrder.id.in_(order_ids)).all()
    total_amount = 0
    total_commission = 0
    
    for order in orders:
        if not order.settled:  # 只结算未结算的订单
            order.settled = True
            order.settled_at = datetime.now()
            total_amount += order.amount or 0
            total_commission += order.commission or 0
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'成功结算 {len(orders)} 条订单',
        'total_amount': total_amount,
        'total_commission': total_commission
    })

@main_bp.route('/api/taobao-orders/<int:order_id>/quick-edit', methods=['PUT'])
def quick_edit_order(order_id):
    """快捷编辑订单字段"""
    order = TaobaoOrder.query.get_or_404(order_id)
    data = request.json
    
    # 更新允许快捷编辑的字段
    if 'level' in data:
        order.level = data['level']
    if 'amount' in data:
        order.amount = float(data['amount'])
        # 当刷单金额更新时，自动重新计算淘宝手续费
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        taobao_fee_rate = float(taobao_fee_config.value) if taobao_fee_config else 0.6
        order.taobao_fee = order.amount * taobao_fee_rate / 100
    if 'commission' in data:
        order.commission = float(data['commission'])
    if 'taobao_fee' in data:
        order.taobao_fee = float(data['taobao_fee'])
    if 'evaluated' in data:
        order.evaluated = bool(data['evaluated'])
    if 'order_time' in data:
        order.order_time = datetime.fromisoformat(data['order_time'].replace('T', ' '))
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '更新成功',
        'order': {
            'id': order.id,
            'level': order.level,
            'amount': order.amount,
            'commission': order.commission,
            'taobao_fee': order.taobao_fee,
            'evaluated': order.evaluated,
            'order_time': order.order_time.isoformat() if order.order_time else None
        }
    })

@main_bp.route('/api/config/<config_key>')
def get_config(config_key):
    """获取系统配置参数"""
    config_item = Config.query.filter_by(key=config_key).first()
    if config_item:
        return jsonify({
            'key': config_item.key,
            'value': config_item.value
        })
    else:
        # 返回默认值
        default_values = {
            'trial_cost': '0',
            'course_cost': '0',
            'taobao_fee_rate': '0.6'  # 默认0.6%手续费率
        }
        return jsonify({
            'key': config_key,
            'value': default_values.get(config_key, '0')
        })

# 试听课管理路由
@main_bp.route('/trial-courses', methods=['GET', 'POST'])
def manage_trial_courses():
    """试听课管理页面"""
    if request.method == 'POST':
        # 获取表单数据
        customer_id = request.form.get('customer_id')
        trial_price = float(request.form['trial_price'])
        source = request.form['source']
        
        # 如果没有选择现有客户，则创建新客户
        if not customer_id:
            # 创建新客户
            new_customer_name = request.form['new_customer_name'].strip()
            new_customer_phone = request.form['new_customer_phone'].strip()
            new_customer_gender = request.form.get('new_customer_gender', '').strip()
            new_customer_grade = request.form.get('new_customer_grade', '').strip()
            new_customer_region = request.form.get('new_customer_region', '').strip()
            
            # 验证必填字段（只验证联系电话）
            if not new_customer_phone:
                flash('请填写联系电话！', 'error')
                return redirect(url_for('main.manage_trial_courses'))
            
            # 如果姓名为空，使用手机号作为临时姓名
            if not new_customer_name:
                new_customer_name = f"学员{new_customer_phone[-4:]}"  # 使用手机号后4位作为临时姓名
            
            # 检查手机号是否已存在
            existing_customer = Customer.query.filter_by(phone=new_customer_phone).first()
            if existing_customer:
                flash(f'手机号 {new_customer_phone} 已存在，学员：{existing_customer.name}', 'error')
                return redirect(url_for('main.manage_trial_courses'))
            
            # 创建新客户
            new_customer = Customer(
                name=new_customer_name,
                phone=new_customer_phone,
                gender=new_customer_gender if new_customer_gender else None,
                grade=new_customer_grade if new_customer_grade else None,
                region=new_customer_region if new_customer_region else None
            )
            
            db.session.add(new_customer)
            db.session.flush()  # 获取新客户的ID
            customer_id = new_customer.id
        
        # 检查该客户是否已有未删除的试听课记录
        existing_trial = Course.query.filter_by(customer_id=customer_id, is_trial=True).first()
        if existing_trial:
            customer = Customer.query.get(customer_id)
            flash(f'学员 {customer.name} 已有试听课记录，无法重复添加！', 'error')
            db.session.rollback()  # 回滚事务，避免新客户被创建
            return redirect(url_for('main.manage_trial_courses'))
        
        # 获取试听课成本配置
        trial_cost_config = Config.query.filter_by(key='trial_cost').first()
        base_trial_cost = float(trial_cost_config.value) if trial_cost_config else 0
        
        # 统一规则：试听课成本仅为基础成本，不包含任何渠道手续费
        total_trial_cost = base_trial_cost
        
        # 获取分配的员工ID
        assigned_employee_id = request.form.get('assigned_employee_id')
        if assigned_employee_id and assigned_employee_id.strip():
            assigned_employee_id = int(assigned_employee_id)
        else:
            assigned_employee_id = None
        
        # 创建试听课记录
        new_trial = Course(
            name='试听课',
            customer_id=customer_id,
            is_trial=True,
            trial_price=trial_price,
            source=source,
            cost=total_trial_cost,
            trial_status='registered',
            assigned_employee_id=assigned_employee_id
        )
        
        db.session.add(new_trial)
        db.session.commit()
        
        # 检查是否是编辑请求
        course_id = request.form.get('course_id')
        if course_id:
            # 编辑现有试听课
            try:
                course = Course.query.get(course_id)
                if not course or not course.is_trial:
                    return jsonify({'success': False, 'message': '试听课不存在'})
                
                # 更新课程信息
                course.trial_price = trial_price
                course.source = source
                
                # 更新客户信息
                customer = Customer.query.get(course.customer_id)
                if customer:
                    customer.name = request.form.get('customer_name', customer.name)
                    customer.phone = request.form.get('customer_phone', customer.phone)
                    customer.gender = request.form.get('customer_gender', customer.gender)
                    customer.grade = request.form.get('customer_grade', customer.grade)
                    customer.region = request.form.get('customer_region', customer.region)
                    customer.has_tutoring_experience = request.form.get('has_tutoring_experience', customer.has_tutoring_experience)
                
                db.session.commit()
                return jsonify({'success': True, 'message': '更新成功'})
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})
        else:
            # 新增试听课
            if not request.form.get('customer_id'):
                flash(f'新学员 {new_customer_name} 和试听课记录添加成功！', 'success')
            else:
                flash('试听课记录添加成功！', 'success')
            
            return redirect(url_for('main.manage_trial_courses'))
    
    embedded = request.args.get('embedded', 'false').lower() == 'true'
    debug_mode = request.args.get('debug', '0') in ('1', 'true', 'True')
    
    # 构建试听课查询
    query = db.session.query(Course, Customer).join(
        Customer, Course.customer_id == Customer.id
    ).filter(Course.is_trial == True)
        
    trial_courses = query.order_by(Course.created_at.desc()).all()
    
    # 获取客户列表用于下拉选择
    customers = Customer.query.order_by(Customer.name).all()
    
    # 获取多渠道手续费率配置（默认0）
    fee_keys = ['taobao_fee_rate', 'xiaohongshu_fee_rate', 'douyin_fee_rate', 'referral_fee_rate']
    fee_configs = {c.key: c.value for c in Config.query.filter(Config.key.in_(fee_keys)).all()}
    taobao_fee_rate = float(fee_configs.get('taobao_fee_rate', 0)) / 100
    xhs_fee_rate = float(fee_configs.get('xiaohongshu_fee_rate', 0)) / 100
    douyin_fee_rate = float(fee_configs.get('douyin_fee_rate', 0)) / 100
    referral_fee_rate = float(fee_configs.get('referral_fee_rate', 0)) / 100

    def calc_channel_fee_rate(source_name: str) -> float:
        if source_name == '淘宝':
            return taobao_fee_rate
        if source_name == '小红书':
            return xhs_fee_rate
        if source_name == '抖音':
            return douyin_fee_rate
        if source_name == '转介绍':
            return referral_fee_rate
        return 0.0
    
    # 按状态分组统计试听课（使用与页面相同的数据集，确保前后端一致）
    # 注意：页面表格数据 trial_courses 来源于 Course INNER JOIN Customer 的结果，
    # 若存在"孤儿"试听课（缺失客户记录），页面不会显示该条，但此前统计会包含，导致不一致。
    # 这里改为直接使用同一数据源中的 Course 对象集合，保证一致性。
    trial_courses_list = [course for (course, _) in trial_courses]
    
    # 初始化各状态统计
    status_stats = {
        'registered': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0, 'profit': 0},
        'not_registered': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0, 'profit': 0},
        'refunded': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0, 'profit': 0},
        'converted': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0, 'profit': 0},
        'no_action': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0, 'profit': 0}
    }
    # 调试用明细
    calc_rows = []
    
    # 计算各状态的统计数据
    for course in trial_courses_list:
        # 默认状态为空时按"已报名试听课"处理，避免被错误排除
        status = course.trial_status or 'registered'

        # 未报名：完全不参与统计（不计数、不计收入/成本/费用/利润）
        if status == 'not_registered':
            # 调试记录
            if debug_mode:
                calc_rows.append({
                    'id': course.id,
                    'status': status,
                    'source': course.source or '',
                    'trial_price': float(course.trial_price or 0),
                    'included': False,
                    'revenue': 0.0,
                    'cost': float(course.cost or 0),
                    'fees': 0.0,
                })
            continue

        # 每个状态都需要按来源计算渠道费率
        channel_rate = calc_channel_fee_rate(course.source or '')

        # 按状态计算
        if status == 'registered':
            revenue = course.trial_price or 0
            cost = course.cost or 0  # 使用成本
            fees = (revenue * channel_rate) if revenue else 0
            profit = revenue - cost  # 修改为不扣除手续费
        elif status == 'refunded':
            # 退费（MIGRATION_GUIDE）：收入=0；成本=基础成本C；不再从利润中扣除手续费
            revenue = 0
            cost = course.cost or 0  # 使用成本
            refund_channel = (course.refund_channel or '').strip()
            if refund_channel == '淘宝':
                fees = 0.0
            else:
                # 以退款渠道计算费率；若未配置该渠道费率则回退到淘宝费率
                channel_r = calc_channel_fee_rate(refund_channel)
                if not channel_r:
                    channel_r = taobao_fee_rate or 0.0
                base_amount = float(course.trial_price or 0)
                # 若数据库已记录退款手续费且>0，则以记录值为准（人工覆盖）；否则按费率估算
                recorded_fee = float(course.refund_fee or 0)
                fees = recorded_fee if recorded_fee > 0 else base_amount * channel_r
            profit = -cost
        elif status == 'converted':
            # 独立核算：与已报名一致
            revenue = course.trial_price or 0
            cost = course.cost or 0  # 使用成本
            fees = (revenue * channel_rate) if revenue else 0
            profit = revenue - cost  # 修改为不扣除手续费
        elif status == 'no_action':
            # 视为已支付并完成试听：与已报名一致
            revenue = course.trial_price or 0
            cost = course.cost or 0  # 使用成本
            fees = (revenue * channel_rate) if revenue else 0
            profit = revenue - cost  # 修改为不扣除手续费
        else:
            # 未知状态保护
            revenue = 0
            cost = 0
            fees = 0
            profit = 0

        # 只有参与统计的状态才累计
        status_stats[status]['count'] += 1
        
        # 累加到对应状态
        status_stats[status]['revenue'] += revenue
        status_stats[status]['cost'] += cost
        status_stats[status]['fees'] += fees
        status_stats[status]['profit'] += profit

        # 记录调试明细
        if debug_mode:
            calc_rows.append({
                'id': course.id,
                'status': status,
                'source': course.source or '',
                'trial_price': float(course.trial_price or 0),
                'included': True,
                'revenue': float(revenue or 0),
                'cost': float(cost or 0),
                'fees': float(fees or 0),
            })
    
    # 计算总统计
    total_stats = {
        # 仅统计纳入口径的状态：已报名、转正、无操作、退费；未报名不计入
        'total_trials': (
            status_stats['registered']['count']
            + status_stats['converted']['count']
            + status_stats['no_action']['count']
            + status_stats['refunded']['count']
        ),
        'total_revenue': sum(s['revenue'] for s in status_stats.values()),
        # 修改：总成本 = 基础成本合计（不重复计算手续费）
        'total_cost': sum(s['cost'] for s in status_stats.values()),
        # 修改：单独计算总手续费
        'total_fees': sum(s['fees'] for s in status_stats.values()),
        # 直接计算总利润 = 总收入 - 总成本
        'total_profit': sum(s['revenue'] for s in status_stats.values()) - sum(s['cost'] for s in status_stats.values())
    }
    
    # 获取员工列表
    employees = Employee.query.order_by(Employee.name).all()
    
    return render_template('trial_courses.html', 
                         trial_courses=trial_courses,
                         customers=customers,
                         taobao_fee_rate=taobao_fee_rate,
                         stats=total_stats,
                         status_stats=status_stats,
                         calc_rows=calc_rows if debug_mode else None,
                         embedded=embedded,
                         employees=employees)

@main_bp.route('/api/formal-courses/stats', methods=['GET'])
def api_formal_courses_stats():
    """正课统计API"""
    try:
        # 获取所有正课
        courses = Course.query.filter_by(is_trial=False).all()
        
        # 获取淘宝手续费率配置（用于旧数据）
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        default_fee_rate = safe_float(taobao_fee_config.value, 0.6) / 100 if taobao_fee_config else 0.006
        
        # 获取正课成本配置
        course_cost_config = Config.query.filter_by(key='course_cost').first()
        course_cost_per_session = safe_float(course_cost_config.value, 0) if course_cost_config else 0
        
        # 计算统计数据
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        total_fees = 0
        rows = []
        
        for course in courses:
            # 使用新的利润计算函数（包含退费）
            profit_info = calculate_course_profit_with_refund(course)
            
            revenue = profit_info['revenue']
            cost = profit_info['cost']
            profit = profit_info['profit']
            
            # 计算手续费（用于显示）
            fee = 0
            if course.payment_channel == '淘宝':
                fee_rate = course.snapshot_fee_rate if getattr(course, 'snapshot_fee_rate', None) else default_fee_rate
                fee = safe_int(course.sessions, 0) * safe_float(course.price, 0) * fee_rate  # 基于原始金额计算
            
            # 课程成本（用于显示）
            # 课时成本（不含其他成本、手续费）用于显示
            other_cost_val = safe_float(course.other_cost, 0)
            # 利用统一计算结果反推课时成本，避免因退费查询遗漏造成口径不一致
            adjusted_course_cost = max(0, safe_float(cost, 0) - safe_float(fee, 0) - other_cost_val)
            # 计入收入节数（购买节数 − 已完成退费节数）
            refunds_completed = CourseRefund.query.filter_by(course_id=course.id, status='completed').all()
            refunded_sessions = sum(safe_int(r.refund_sessions, 0) for r in refunds_completed)
            counted_sessions = max(0, safe_int(course.sessions, 0) - refunded_sessions)
            # other_cost 单独返回；总成本 cost 已含手续费
            course_cost = adjusted_course_cost + other_cost_val
            
            # 累加统计
            total_revenue += revenue
            total_cost += cost
            total_profit += profit
            total_fees += fee
            
            # 构建行数据
            rows.append({
                'id': course.id,
                'customer_id': course.customer.id if getattr(course, 'customer', None) else None,
                'customer_name': course.customer.name if getattr(course, 'customer', None) else '-',
                'course_type': course.course_type,
                'sessions': safe_int(course.sessions, 0),
                'gift_sessions': safe_int(course.gift_sessions, 0),
                'price': safe_float(course.price, 0),
                'payment_channel': course.payment_channel,
                'fee': fee,
                'course_cost': course_cost,
                'adjusted_course_cost': adjusted_course_cost,
                'other_cost': other_cost_val,
                'revenue': revenue,
                'profit': profit,
                'counted_sessions': counted_sessions,
                'has_refund': profit_info['has_refund'],
                'refund_amount': profit_info.get('refund_info', {}).get('amount', 0),
                'created_at': course.created_at.isoformat() if course.created_at else None,
            })
        
        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'total_fees': total_fees,
            'rows': rows,
        }
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/trial-courses/stats', methods=['GET'])
def api_trial_courses_stats():
    """试听统计API"""
    try:
        # 获取所有试听
        courses = Course.query.filter_by(is_trial=True).all()
        
        # 获取淘宝手续费率配置（用于旧数据）
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        default_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006
        
        # 计算统计数据
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        total_fees = 0
        rows = []
        
        for course in courses:
            # 试听课收入应以 trial_price 为准，不按节数乘以正课单价
            price = safe_float(getattr(course, 'trial_price', None), 0)
            revenue = price
            
            # 计算手续费
            fee = 0
            if course.payment_channel == '淘宝' or getattr(course, 'source', None) == '淘宝':
                # 优先使用快照费率，否则使用默认费率
                fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else default_fee_rate
                fee = revenue * fee_rate
            
            # 计算成本（course.cost已包含课时成本和其他成本）
            cost = safe_float(course.cost, 0)
            cost = cost + fee  # 总成本包含手续费
            
            # 计算利润
            profit = revenue - cost
            
            # 累加统计
            total_revenue += revenue
            total_cost += cost
            total_profit += profit
            total_fees += fee
            
            # 构建行数据
            rows.append({
                'id': course.id,
                'customer_name': course.customer.name,
                'course_type': course.course_type,
                'sessions': safe_int(getattr(course, 'sessions', 0), 0),
                'gift_sessions': safe_int(getattr(course, 'gift_sessions', 0), 0),
                'price': price,
                'payment_channel': course.payment_channel or getattr(course, 'source', None),
                'fee': fee,
                'course_cost': course.cost,
                'revenue': revenue,
                'profit': profit,
            })
        
        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'total_fees': total_fees,
            'rows': rows,
        }
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/customers', methods=['GET'])
def api_customers():
    """客户列表API"""
    try:
        customers = Customer.query.order_by(Customer.name).all()
        return [{'id': c.id, 'name': c.name} for c in customers]
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/employees', methods=['GET'])
def api_employees():
    """员工列表API - 包含提成配置信息"""
    try:
        employees = Employee.query.order_by(Employee.name).all()
        employee_list = []
        
        for employee in employees:
            # 获取提成配置
            config = CommissionConfig.query.filter_by(employee_id=employee.id).first()
            
            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'phone': getattr(employee, 'phone', None),
                'email': getattr(employee, 'email', None),
                'base_salary': config.base_salary if config else 0,
                'commission_type': config.commission_type if config else 'profit',
                'new_course_rate': config.new_course_rate if config else 0,
                'renewal_rate': config.renewal_rate if config else 0
            }
            employee_list.append(employee_data)
        
        return employee_list
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/employees', methods=['POST'])
def create_employee():
    """创建新员工API - 包含提成配置"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': '员工姓名不能为空'}), 400
        
        # 检查是否已存在
        existing = Employee.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': '该员工已存在'}), 400
        
        # 创建新员工
        employee = Employee(name=name)
        
        # 添加扩展字段（如果Employee模型支持）
        if hasattr(employee, 'phone'):
            employee.phone = data.get('phone', '').strip() or None
        if hasattr(employee, 'email'):
            employee.email = data.get('email', '').strip() or None
        
        db.session.add(employee)
        db.session.flush()  # 获取employee.id
        
        # 创建提成配置
        commission_config = CommissionConfig(
            employee_id=employee.id,
            commission_type=data.get('commission_type', 'profit'),
            trial_rate=0,  # 试听课不参与提成
            new_course_rate=float(data.get('new_course_rate', 0)),
            renewal_rate=float(data.get('renewal_rate', 0)),
            base_salary=float(data.get('base_salary', 0))
        )
        db.session.add(commission_config)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '员工添加成功',
            'employee': {
                'id': employee.id, 
                'name': employee.name,
                'phone': getattr(employee, 'phone', None),
                'email': getattr(employee, 'email', None),
                'base_salary': commission_config.base_salary,
                'commission_type': commission_config.commission_type,
                'new_course_rate': commission_config.new_course_rate,
                'renewal_rate': commission_config.renewal_rate
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/courses/<int:course_id>/refund-info', methods=['GET'])
def get_refund_info(course_id):
    """获取课程的可退费信息 - 优化版，使用RefundService"""
    try:
        course = Course.query.get(course_id)
        if not course or course.is_trial:
            return jsonify({'success': False, 'message': '课程不存在或不是正课'}), 404
        
        # 使用服务层计算退费信息
        refund_calc = RefundService.calculate_refund_amount(course_id, 0)
        
        # 获取退费历史
        refund_history = RefundService.get_refund_history(course_id)
        
        # 计算已退费手续费总额
        total_refunded_fees = sum(r.get('refund_fee', 0) for r in refund_history)
        
        return jsonify({
            'success': True,
            'refund_summary': {
                'total_refunded_sessions': refund_calc['total_refunded_sessions'],
                'total_refunded_amount': refund_calc['total_refunded_amount'],
                'total_refunded_fees': total_refunded_fees,
                'refundable_sessions': refund_calc['remaining_sessions'],
                'unit_price': refund_calc['unit_price']
            },
            'refund_history': refund_history
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/courses/<int:course_id>/refund', methods=['POST'])
def apply_course_refund(course_id):
    """申请正课退费 - 优化版，使用RefundService"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 准备退费数据
        refund_data = {
            'refund_sessions': int(data.get('refund_sessions', 0)),
            'refund_reason': data.get('refund_reason', ''),
            'refund_channel': data.get('refund_channel', '原路退回'),
            'refund_fee': float(data.get('refund_fee', 0)),
            'remark': data.get('remark', ''),
            'operator_name': session.get('user_name', 'System')
        }
        
        # 使用服务层处理退费（自带事务管理）
        success, message, refund = RefundService.process_refund(course_id, refund_data)
        
        if not success:
            return jsonify({'success': False, 'message': message}), 400
        
        # 计算剩余信息
        refund_calc = RefundService.calculate_refund_amount(course_id, 0)
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'refund_id': refund.id,
                'refund_amount': refund.refund_amount,
                'actual_refund': refund.refund_amount - refund.refund_fee,
                'remaining_sessions': refund_calc['remaining_sessions']
            }
        })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/courses/<int:course_id>/refund-history', methods=['GET'])
def get_refund_history(course_id):
    """获取课程退费历史 - 优化版，使用RefundService"""
    try:
        # 直接使用服务层获取格式化的历史记录
        refund_history = RefundService.get_refund_history(course_id)
        
        # 添加实际退费金额字段（为了兼容前端）
        for refund in refund_history:
            refund['actual_refund'] = refund['refund_amount'] - refund['refund_fee']
        
        return jsonify({
            'success': True,
            'refunds': refund_history
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/formal-courses', methods=['GET'])
def api_formal_courses():
    """正课列表API"""
    try:
        courses = Course.query.filter_by(is_trial=False).all()
        return [{'id': c.id, 'customer_name': c.customer.name, 'course_type': c.course_type, 'sessions': c.sessions, 'gift_sessions': c.gift_sessions, 'price': c.price, 'payment_channel': c.payment_channel} for c in courses]
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/trial-courses', methods=['GET'])
def api_trial_courses():
    """试听列表API"""
    try:
        courses = Course.query.filter_by(is_trial=True).all()
        return [{'id': c.id, 'customer_name': c.customer.name, 'course_type': c.course_type, 'sessions': c.sessions, 'gift_sessions': c.gift_sessions, 'price': c.price, 'payment_channel': c.payment_channel} for c in courses]
    except Exception as e:
        return {'error': str(e)}, 500





@main_bp.route('/api/formal-courses', methods=['POST'])
def create_formal_course():
    """创建正课API - 必须从试听课转化"""
    try:
        data = request.get_json()
        
        # 业务规范检查：必须从试听课转化
        trial_id = data.get('converted_from_trial')
        if not trial_id:
            return {'error': '正课必须从试听课转化而来，请提供converted_from_trial参数'}, 400
        
        # 验证试听课是否存在且属于该客户
        trial_course = Course.query.filter_by(
            id=trial_id,
            customer_id=data['customer_id'],
            is_trial=True
        ).first()
        
        if not trial_course:
            return {'error': '未找到对应的试听课记录，或试听课不属于该客户'}, 400
        
        # 检查试听课是否已转化
        if trial_course.converted_to_course:
            return {'error': '该试听课已经转化为正课'}, 400
        
        # 业务规范：正课必须分配给试听课的同一个员工
        assigned_employee_id = trial_course.assigned_employee_id
        if not assigned_employee_id:
            return {'error': '试听课未分配员工，无法创建正课。请先分配试听课给员工'}, 400
        
        # 创建正课记录
        course = Course(
            customer_id=data['customer_id'],
            course_type=data['course_type'],
            sessions=data['sessions'],
            gift_sessions=data['gift_sessions'],
            price=data['price'],
            payment_channel=data['payment_channel'],
            snapshot_fee_rate=data.get('snapshot_fee_rate'),
            custom_course_cost=data.get('custom_course_cost'),
            assigned_employee_id=assigned_employee_id,  # 必须与试听课分配给同一个员工
            converted_from_trial=trial_id,  # 记录转化关系
            is_trial=False
        )
        db.session.add(course)
        db.session.flush()  # 获取course.id
        
        # 更新试听课记录，标记已转化
        trial_course.converted_to_course = course.id
        trial_course.trial_status = 'converted'
        
        db.session.commit()
        return {'message': 'Course created successfully from trial course'}
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@main_bp.route('/api/trial-courses', methods=['POST'])
def create_trial_course():
    """创建试听API"""
    try:
        data = request.get_json()
        course = Course(
            customer_id=data['customer_id'],
            course_type=data['course_type'],
            sessions=data['sessions'],
            gift_sessions=data['gift_sessions'],
            price=data['price'],
            payment_channel=data['payment_channel'],
            snapshot_fee_rate=data.get('snapshot_fee_rate'),
            custom_course_cost=data.get('custom_course_cost'),
            assigned_employee_id=data.get('assigned_employee_id'),  # 添加员工分配
            is_trial=True
        )
        db.session.add(course)
        db.session.commit()
        return {'message': 'Course created successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/trial-courses/<int:course_id>', methods=['DELETE'])
def delete_trial_course(course_id):
    """删除试听API"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return {'error': 'Course not found'}, 404
        db.session.delete(course)
        db.session.commit()
        return {'message': 'Course deleted successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/customers/<int:customer_id>', methods=['GET'])
def api_customer(customer_id):
    """单个客户详情API"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'error': 'Customer not found'}, 404
        return {'id': customer.id, 'name': customer.name}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """更新客户API"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'error': 'Customer not found'}, 404
        data = request.get_json()
        customer.name = data.get('name', customer.name)
        db.session.commit()
        return {'message': 'Customer updated successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/customers', methods=['POST'])
def create_customer():
    """创建客户API"""
    try:
        data = request.get_json()
        customer = Customer(name=data['name'])
        db.session.add(customer)
        db.session.commit()
        return {'message': 'Customer created successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """删除客户API"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'error': 'Customer not found'}, 404
        db.session.delete(customer)
        db.session.commit()
        return {'message': 'Customer deleted successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/employees/<int:employee_id>', methods=['GET'])
def api_employee(employee_id):
    """单个员工详情API"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return {'error': 'Employee not found'}, 404
        return {'id': employee.id, 'name': employee.name}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """更新员工API - 包含提成配置"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': '员工不存在'}), 404
        
        data = request.get_json()
        
        # 更新员工基本信息
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'success': False, 'message': '员工姓名不能为空'}), 400
            
            # 检查姓名是否与其他员工重复
            existing = Employee.query.filter(Employee.name == name, Employee.id != employee_id).first()
            if existing:
                return jsonify({'success': False, 'message': '该员工姓名已存在'}), 400
            
            employee.name = name
        
        # 更新扩展字段（如果Employee模型支持）
        if hasattr(employee, 'phone') and 'phone' in data:
            employee.phone = data['phone'].strip() or None
        if hasattr(employee, 'email') and 'email' in data:
            employee.email = data['email'].strip() or None
        
        # 更新或创建提成配置
        commission_config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if not commission_config:
            commission_config = CommissionConfig(employee_id=employee_id)
            db.session.add(commission_config)
        
        # 更新提成配置
        if 'commission_type' in data:
            commission_config.commission_type = data['commission_type']
        if 'base_salary' in data:
            commission_config.base_salary = float(data['base_salary'])
        if 'new_course_rate' in data:
            commission_config.new_course_rate = float(data['new_course_rate'])
        if 'renewal_rate' in data:
            commission_config.renewal_rate = float(data['renewal_rate'])
        
        # 试听课不参与提成
        commission_config.trial_rate = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': '员工更新成功',
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'phone': getattr(employee, 'phone', None),
                'email': getattr(employee, 'email', None),
                'base_salary': commission_config.base_salary,
                'commission_type': commission_config.commission_type,
                'new_course_rate': commission_config.new_course_rate,
                'renewal_rate': commission_config.renewal_rate
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500



@main_bp.route('/api/config/<string:key>', methods=['GET'])
def api_config(key):
    """配置详情API"""
    try:
        config = Config.query.filter_by(key=key).first()
        if not config:
            return {'error': 'Config not found'}, 404
        return {'key': config.key, 'value': config.value}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/config/<string:key>', methods=['PUT'])
def update_config(key):
    """更新配置API"""
    try:
        config = Config.query.filter_by(key=key).first()
        if not config:
            return {'error': 'Config not found'}, 404
        data = request.get_json()
        config.value = data.get('value', config.value)
        db.session.commit()
        return {'message': 'Config updated successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/config', methods=['POST'])
def create_config():
    """创建配置API"""
    try:
        data = request.get_json()
        config = Config(key=data['key'], value=data['value'])
        db.session.add(config)
        db.session.commit()
        return {'message': 'Config created successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """删除员工API"""
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': '员工不存在'}), 404
        
        # 检查是否有关联的课程数据
        trial_courses = Course.query.filter_by(assigned_employee_id=employee_id, is_trial=True).count()
        formal_courses = Course.query.filter_by(assigned_employee_id=employee_id, is_trial=False).count()
        
        if trial_courses > 0 or formal_courses > 0:
            return jsonify({
                'success': False, 
                'message': f'无法删除员工，该员工还有 {trial_courses} 个试听课和 {formal_courses} 个正课记录'
            }), 400
        
        # 删除提成配置
        commission_config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if commission_config:
            db.session.delete(commission_config)
        
        # 删除员工
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '员工删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/config/<string:key>', methods=['DELETE'])
def delete_config(key):
    """删除配置API"""
    try:
        config = Config.query.filter_by(key=key).first()
        if not config:
            return {'error': 'Config not found'}, 404
        db.session.delete(config)
        db.session.commit()
        return {'message': 'Config deleted successfully'}
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/formal-courses/status-stats', methods=['GET'])
def api_formal_courses_status_stats():
    """正课状态统计API"""
    try:
        # 获取所有正课
        courses = Course.query.filter_by(is_trial=False).all()
        
        # 获取淘宝手续费率配置（用于旧数据）
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        default_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006
        
        # 获取正课成本配置
        course_cost_config = Config.query.filter_by(key='course_cost').first()
        course_cost_per_session = float(course_cost_config.value) if course_cost_config else 0
        
        # 计算统计数据
        status_stats = {
            'paid': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0},
            'unpaid': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0},
            'refunded': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0},
        }
        calc_rows = []
        
        for course in courses:
            # 计算收入
            sessions = safe_int(course.sessions, 0)
            price = safe_float(course.price, 0)
            revenue = sessions * price
            
            # 计算手续费
            fee = 0
            if course.payment_channel == '淘宝':
                # 优先使用快照费率，否则使用默认费率
                fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else default_fee_rate
                fee = revenue * fee_rate
            
            # 计算成本（使用基础成本和自定义成本）
            if course.custom_course_cost:
                # 使用自定义成本
                course_cost = course.custom_course_cost
            elif course.snapshot_course_cost:
                # 使用快照成本
                course_cost = (course.sessions + course.gift_sessions) * course.snapshot_course_cost + (course.other_cost or 0)
            else:
                # 使用配置的成本
                course_cost = (course.sessions + course.gift_sessions) * course_cost_per_session + (course.other_cost or 0)
            
            # 总成本包含手续费
            cost = course_cost + fee
            
            # 计算利润
            profit = revenue - course_cost  # 利润不包含手续费
            
            # 累加统计
            if course.status == 'paid':
                status_stats['paid']['count'] += 1
                status_stats['paid']['revenue'] += revenue
                status_stats['paid']['cost'] += cost
                status_stats['paid']['fees'] += fee
            elif course.status == 'unpaid':
                status_stats['unpaid']['count'] += 1
                status_stats['unpaid']['revenue'] += revenue
                status_stats['unpaid']['cost'] += cost
                status_stats['unpaid']['fees'] += fee
            elif course.status == 'refunded':
                status_stats['refunded']['count'] += 1
                status_stats['refunded']['revenue'] += revenue
                status_stats['refunded']['cost'] += cost
                status_stats['refunded']['fees'] += fee
            
            # 构建行数据
            calc_rows.append({
                'id': course.id,
                'customer_name': course.customer.name,
                'course_type': course.course_type,
                'sessions': course.sessions,
                'gift_sessions': course.gift_sessions,
                'price': course.price,
                'payment_channel': course.payment_channel,
                'fee': fee,
                'course_cost': course_cost,
                'revenue': revenue,
                'profit': profit,
            })
        
        return {
            'total_revenue': sum(s['revenue'] for s in status_stats.values()),
            'total_cost': sum(s['course_cost'] for s in status_stats.values()),
            'total_fees': sum(s['fee'] for s in status_stats.values()),
            'total_profit': sum(s['revenue'] for s in status_stats.values()) - sum(s['course_cost'] for s in status_stats.values())

        }
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/api/trial-courses/status-stats', methods=['GET'])
def api_trial_courses_status_stats():
    """试听状态统计API"""
    try:
        # 获取所有试听
        courses = Course.query.filter_by(is_trial=True).all()
        
        # 获取淘宝手续费率配置（用于旧数据）
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        default_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006
        
        # 计算统计数据
        status_stats = {
            'paid': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0},
            'unpaid': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0},
            'refunded': {'count': 0, 'revenue': 0, 'cost': 0, 'fees': 0},
        }
        calc_rows = []
        
        # 初始化统计变量
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        total_fees = 0
        
        for course in courses:
            # 计算收入（处理None值）
            sessions = course.sessions or 0
            price = course.price or 0
            revenue = sessions * price
            
            # 计算手续费
            fee = 0
            if course.payment_channel == '淘宝':
                # 优先使用快照费率，否则使用默认费率
                fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else default_fee_rate
                fee = revenue * fee_rate
            
            # 计算成本（course.cost已包含课时成本和其他成本）
            cost = (course.cost or 0) + fee  # 总成本包含手续费
            
            # 计算利润
            profit = revenue - cost
            
            # 累加统计
            if course.trial_status == 'registered':
                status_stats['paid']['count'] += 1
                status_stats['paid']['revenue'] += revenue
                status_stats['paid']['cost'] += cost
                status_stats['paid']['fees'] += fee
            elif course.trial_status == 'not_registered':
                status_stats['unpaid']['count'] += 1
                status_stats['unpaid']['revenue'] += revenue
                status_stats['unpaid']['cost'] += cost
                status_stats['unpaid']['fees'] += fee
            elif course.trial_status == 'refunded':
                status_stats['refunded']['count'] += 1
                status_stats['refunded']['revenue'] += revenue
                status_stats['refunded']['cost'] += cost
                status_stats['refunded']['fees'] += fee
            
            # 累加总体统计
            total_revenue += revenue
            total_cost += cost
            total_profit += profit
            total_fees += fee
            
            # 构建行数据
            calc_rows.append({
                'id': course.id,
                'customer_name': course.customer.name,
                'course_type': course.course_type,
                'sessions': course.sessions,
                'gift_sessions': course.gift_sessions,
                'price': course.price,
                'payment_channel': course.payment_channel,
                'revenue': revenue,
                'course_cost': course.cost,  # 原始成本（不含手续费）
                'other_cost': course.other_cost,
                'fee': fee,
                'total_cost': cost,  # 总成本（含手续费）
                'profit': profit,
                'created_at': course.created_at.strftime('%Y-%m-%d') if course.created_at else ''
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'total_courses': len(courses),
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'total_profit': round(total_profit, 2),
                'total_fees': round(total_fees, 2)
            },
            'rows': calc_rows
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/formal-courses', methods=['GET'])
def manage_formal_courses():
    """正课管理页面"""
    
    embedded = request.args.get('embedded', 'false').lower() == 'true'
    
    # 构建正课查询
    query = db.session.query(Course, Customer).join(
        Customer, Course.customer_id == Customer.id
    ).filter(Course.is_trial == False)
        
    formal_courses = query.order_by(Course.created_at.desc()).all()
    
    # 获取客户列表用于下拉选择
    customers = Customer.query.order_by(Customer.name).all()
    
    # 计算正课统计
    formal_stats_query = db.session.query(
        db.func.count(Course.id).label('total_courses'),
        db.func.coalesce(db.func.sum(Course.sessions), 0).label('total_sessions'),
        db.func.coalesce(db.func.sum(Course.gift_sessions), 0).label('total_gift_sessions')
    ).filter(Course.is_trial == False)
        
    formal_stats = formal_stats_query.first()
    
    # 计算实际总收入（考虑手续费）
    courses_query = Course.query.filter(Course.is_trial == False)
    courses = courses_query.all()
    total_revenue = 0
    total_fees = 0
    total_cost = 0
    
    # 获取淘宝手续费率配置
    taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
    taobao_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006  # 转换为小数
    
    # 获取正课成本配置
    course_cost_config = Config.query.filter_by(key='course_cost').first()
    course_cost_per_session = float(course_cost_config.value) if course_cost_config else 0
    
    for course in courses:
        # 计算基础收入：购买节数 × 单节售价
        sessions = safe_int(course.sessions, 0)
        price = safe_float(course.price, 0)
        revenue = sessions * price
        
        # 如果是淘宝支付，扣除手续费
        if course.payment_channel == '淘宝':
            fee_amount = revenue * taobao_fee_rate
            actual_revenue = revenue - fee_amount
            total_fees += fee_amount
        else:
            actual_revenue = revenue
            
        total_revenue += actual_revenue
        
        # 计算成本
        course_cost = course.cost if course.cost is not None else 0
        if course_cost == 0:
            # 如果cost字段为空，使用配置的成本计算
            course_cost = (course.sessions + course.gift_sessions) * course_cost_per_session + (course.other_cost or 0)
        total_cost += course_cost
    
    # 计算利润
    total_profit = total_revenue - total_cost
    
    return render_template('formal_courses.html', 
                         formal_courses=formal_courses,
                         customers=customers,
                         taobao_fee_rate=taobao_fee_rate,
                         stats={
                             'total_courses': formal_stats.total_courses or 0,
                             'total_revenue': total_revenue,
                             'total_cost': total_cost,
                             'total_profit': total_profit,
                             'total_sessions': formal_stats.total_sessions or 0,
                             'total_gift_sessions': formal_stats.total_gift_sessions or 0,
                             'total_fees': total_fees
                         },
                         embedded=embedded)

@main_bp.route('/renew-course/<int:course_id>', methods=['GET', 'POST'])
def renew_course(course_id):
    """续课功能"""
    course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
    
    if request.method == 'POST':
        # 创建续课记录
        course_type = request.form['course_type']
        sessions = int(request.form['sessions'])
        price = float(request.form['price'])  # 单节售价
        payment_channel = request.form['payment_channel']
        gift_sessions = int(request.form.get('gift_sessions', 0))
        other_cost = float(request.form.get('other_cost', 0))
        discount_amount = float(request.form.get('discount_amount', 0))
        renewal_reason = request.form.get('renewal_reason', '')
        assigned_employee_id = request.form.get('assigned_employee_id')
        
        # 获取正课成本配置
        course_cost_config = Config.query.filter_by(key='course_cost').first()
        course_cost_per_session = float(course_cost_config.value) if course_cost_config else 0
        
        # 获取淘宝手续费率配置
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        taobao_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006
        
        # 计算总成本（不包含手续费，手续费单独计算）
        total_cost = (sessions + gift_sessions) * course_cost_per_session + other_cost
        
        # 处理员工分配
        if assigned_employee_id and assigned_employee_id.strip():
            assigned_employee_id = int(assigned_employee_id)
        else:
            assigned_employee_id = course.assigned_employee_id  # 继承原课程的员工
        
        # 准备元数据
        import json
        meta_data = {
            'renewal_reason': renewal_reason,
            'discount_amount': discount_amount,
            'original_course_id': course_id,
            'course_cost_per_session': course_cost_per_session,
            'taobao_fee_rate': taobao_fee_rate * 100  # 存储为百分比
        }
        
        # 创建续课记录
        renewal_course = Course(
            name=course_type + '（续课）',
            customer_id=course.customer_id,
            is_trial=False,
            course_type=course_type,
            sessions=sessions,
            price=price,  # 存储单节售价
            cost=total_cost,
            gift_sessions=gift_sessions,
            other_cost=other_cost,
            payment_channel=payment_channel,
            is_renewal=True,  # 标记为续课
            renewal_from_course_id=course_id,  # 记录续课来源
            assigned_employee_id=assigned_employee_id,
            snapshot_course_cost=course_cost_per_session,  # 保存单节成本快照
            snapshot_fee_rate=taobao_fee_rate,  # 保存手续费率快照（小数）
            meta=json.dumps(meta_data, ensure_ascii=False)  # 保存续课信息
        )
        
        db.session.add(renewal_course)
        db.session.commit()
        
        flash(f'续课成功：{course_type}，共{sessions}节课', 'success')
        return redirect(url_for('main.manage_formal_courses'))
    
    # 获取员工列表
    employees = Employee.query.order_by(Employee.name).all()
    
    return render_template('renew_course.html', course=course, employees=employees)

@main_bp.route('/convert-trial/<int:trial_id>', methods=['GET', 'POST'])
def convert_trial_to_course(trial_id):
    """试听课转正课"""
    trial_course = Course.query.filter_by(id=trial_id, is_trial=True).first_or_404()
    
    if request.method == 'POST':
        # 创建正课记录
        course_type = request.form['course_type']
        sessions = int(request.form['sessions'])
        price = float(request.form['price'])  # 单节售价
        payment_channel = request.form['payment_channel']
        gift_sessions = int(request.form.get('gift_sessions', 0))
        other_cost = float(request.form.get('other_cost', 0))
        
        # 获取正课成本配置
        course_cost_config = Config.query.filter_by(key='course_cost').first()
        course_cost_per_session = float(course_cost_config.value) if course_cost_config else 0
        
        # 获取淘宝手续费率配置
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        taobao_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006
        
        # 计算总成本（不包含手续费，手续费单独计算）
        total_cost = (sessions + gift_sessions) * course_cost_per_session + other_cost
        
        # 准备表单数据快照
        import json
        form_data = {
            'course_type': course_type,
            'sessions': sessions,
            'price': price,
            'payment_channel': payment_channel,
            'gift_sessions': gift_sessions,
            'other_cost': other_cost,
            'course_cost_per_session': course_cost_per_session,
            'taobao_fee_rate': taobao_fee_rate * 100  # 存储为百分比
        }
        
        # 创建正课记录
        formal_course = Course(
            name=course_type,
            customer_id=trial_course.customer_id,
            is_trial=False,
            assigned_employee_id=trial_course.assigned_employee_id,  # 继承试听课的员工分配
            course_type=course_type,
            sessions=sessions,
            price=price,  # 存储单节售价
            cost=total_cost,
            gift_sessions=gift_sessions,
            other_cost=other_cost,
            payment_channel=payment_channel,
            converted_from_trial=trial_id,
            snapshot_course_cost=course_cost_per_session,  # 保存单节成本快照
            snapshot_fee_rate=taobao_fee_rate,  # 保存手续费率快照（小数）
            meta=json.dumps(form_data, ensure_ascii=False)  # 保存表单数据快照
        )
        
        db.session.add(formal_course)
        db.session.commit()
        
        # 更新试听课记录，标记已转化
        trial_course.converted_to_course = formal_course.id
        trial_course.trial_status = 'converted'  # 同步更新状态
        db.session.commit()
        
        flash(f'试听课已成功转化为正课：{course_type}', 'success')
        return redirect(url_for('main.manage_trial_courses'))
    
    return render_template('convert_trial.html', trial_course=trial_course)

@main_bp.route('/api/trial-courses/<int:course_id>', methods=['GET'])
def get_trial_course(course_id):
    """获取单个试听课的详细信息"""
    course = Course.query.filter_by(id=course_id, is_trial=True).first_or_404()
    
    try:
        course_data = {
            'id': course.id,
            'trial_price': course.trial_price,
            'price': course.trial_price,
            'source': course.source,
            'trial_status': course.trial_status,
            'refund_amount': course.refund_amount,
            'refund_fee': course.refund_fee,
            'refund_channel': course.refund_channel,
            'converted_to_course': course.converted_to_course,
            'custom_trial_cost': course.custom_trial_cost,
            'created_at': course.created_at.isoformat() if course.created_at else None
        }
        
        customer_data = {
            'id': course.customer.id,
            'name': course.customer.name,
            'phone': course.customer.phone,
            'gender': course.customer.gender,
            'grade': course.customer.grade,
            'region': course.customer.region,
            'has_tutoring_experience': course.customer.has_tutoring_experience
        }
        
        return jsonify({
            'success': True,
            'course': course_data,
            'customer': customer_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取课程信息失败：{str(e)}'})

@main_bp.route('/formal-courses/<int:course_id>/details', methods=['GET'])
def formal_course_details(course_id):
    """正课详情页面"""
    course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
    
    # 获取试听课信息（如果是转化而来）
    trial_course = None
    if course.converted_from_trial:
        trial_course = Course.query.get(course.converted_from_trial)
    
    # 解析meta信息
    import json
    meta_data = {}
    if course.meta:
        try:
            meta_data = json.loads(course.meta)
        except:
            pass
    
    # 计算展示信息（与列表页保持一致逻辑，考虑退费）
    sessions = safe_int(course.sessions, 0)
    price = safe_float(course.price, 0)
    original_revenue = sessions * price
    fee = 0
    fee_rate = 0
    if course.payment_channel == '淘宝':
        fee_rate = course.snapshot_fee_rate if getattr(course, 'snapshot_fee_rate', None) else 0.006
        fee = original_revenue * fee_rate
    
    profit_info = calculate_course_profit_with_refund(course)
    revenue = profit_info['revenue']
    total_cost = profit_info['cost']  # 已包含手续费
    profit = profit_info['profit']
    
    # 计算用于展示的课时成本（从实际成本中扣除手续费与其他成本后的课时部分）
    other_cost = safe_float(course.other_cost, 0)
    session_cost = max(0, total_cost - fee - other_cost)
    
    # 计入收入的节数（用于详情页显示）
    refunds_completed = CourseRefund.query.filter_by(course_id=course.id, status='completed').all()
    total_refunded_sessions = sum(safe_int(r.refund_sessions, 0) for r in refunds_completed)
    counted_sessions = max(0, sessions - total_refunded_sessions)
    
    # 课时成本
    course_cost_per_session = course.snapshot_course_cost if course.snapshot_course_cost else 0
    # 生效单节成本与来源：自定义 > 快照 > 配置
    effective_cost_per_session = None
    effective_cost_source = '配置'
    if getattr(course, 'custom_course_cost', None) is not None:
        effective_cost_per_session = safe_float(course.custom_course_cost, 0)
        effective_cost_source = '自定义'
    elif getattr(course, 'snapshot_course_cost', None) is not None:
        effective_cost_per_session = safe_float(course.snapshot_course_cost, 0)
        effective_cost_source = '快照'
    else:
        cfg = Config.query.filter_by(key='course_cost').first()
        effective_cost_per_session = safe_float(cfg.value, 0) if cfg else 0
        effective_cost_source = '配置'
    # 用于显示：按计入节数反推当期单节成本（避免标签与数值不一致）
    display_cost_per_session = (session_cost / counted_sessions) if counted_sessions > 0 else course_cost_per_session
    
    # 退费记录与统计
    refund_history = CourseRefund.query.filter_by(course_id=course.id).order_by(CourseRefund.refund_date.desc()).all()
    total_refunded_sessions = sum(safe_int(r.refund_sessions, 0) for r in refund_history if r.status == 'completed')
    total_refunded_amount = sum(safe_float(r.refund_amount, 0) for r in refund_history if r.status == 'completed')
    total_refunded_fees = sum(safe_float(r.refund_fee, 0) for r in refund_history if r.status == 'completed')
    refundable_sessions = 0
    try:
        refundable_sessions = calculate_refundable_sessions(course)
    except Exception:
        refundable_sessions = max(0, safe_int(course.sessions, 0) - total_refunded_sessions)
    
    return render_template('formal_course_details.html',
                         course=course,
                         trial_course=trial_course,
                         meta_data=meta_data,
                         calculations={
                             'revenue': revenue,
                             'session_cost': session_cost,
                             'other_cost': course.other_cost,
                             'fee': fee,
                             'total_cost': total_cost,
                             'profit': profit,
                             'course_cost_per_session': course_cost_per_session,
                             'fee_rate': round(fee_rate * 100, 2),
                             'counted_sessions': counted_sessions,
                             'display_cost_per_session': display_cost_per_session
                         },
                         effective_cost_per_session=effective_cost_per_session,
                         effective_cost_source=effective_cost_source,
                         refund_history=refund_history,
                         refund_summary={
                             'total_refunded_sessions': total_refunded_sessions,
                             'total_refunded_amount': total_refunded_amount,
                             'total_refunded_fees': total_refunded_fees,
                             'refundable_sessions': refundable_sessions,
                             'unit_price': safe_float(course.price, 0),
                             'max_refund_amount': refundable_sessions * safe_float(course.price, 0)
                         })

@main_bp.route('/api/formal-courses/<int:course_id>', methods=['GET'])
def get_formal_course(course_id):
    """获取单个正课信息"""
    try:
        course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
        
        course_data = {
            'success': True,
            'id': course.id,
            'customer_id': course.customer.id,
            'customer_name': course.customer.name,
            'customer_phone': course.customer.phone,
            'customer_gender': course.customer.gender,
            'customer_grade': course.customer.grade,
            'customer_region': course.customer.region,
            'customer_source': course.customer.source,
            'customer_has_tutoring_experience': course.customer.has_tutoring_experience,
            'course_type': course.course_type,
            'sessions': course.sessions,
            'gift_sessions': course.gift_sessions,
            'price': course.price,
            'payment_channel': course.payment_channel,
            'cost': course.cost,
            'other_cost': course.other_cost,
            'custom_course_cost': course.custom_course_cost,
            'source': '试听课转化' if course.converted_from_trial else '直接报名',
            'converted_from_trial': course.converted_from_trial,
            'created_at': course.created_at.isoformat() if course.created_at else None
        }
        
        return jsonify(course_data)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取课程信息失败：{str(e)}'})

@main_bp.route('/api/formal-courses/<int:course_id>/costs', methods=['PUT'])
def update_formal_course_costs(course_id):
    """更新正课成本与其他成本（部分更新）"""
    try:
        course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
        data = request.get_json(silent=True) or {}
        custom_course_cost = data.get('custom_course_cost', None)
        other_cost = data.get('other_cost', None)

        if custom_course_cost is not None:
            val = safe_float(custom_course_cost, None)
            if val is None or val < 0:
                return jsonify({'success': False, 'message': '正课成本必须为非负数字'}), 400
            course.custom_course_cost = val
        if other_cost is not None:
            val = safe_float(other_cost, None)
            if val is None or val < 0:
                return jsonify({'success': False, 'message': '其他成本必须为非负数字'}), 400
            course.other_cost = val

        db.session.commit()

        # 变更后返回最新统计
        profit_info = calculate_course_profit_with_refund(course)

        # 退费摘要
        refunds = CourseRefund.query.filter_by(course_id=course.id).order_by(CourseRefund.refund_date.desc()).all()
        total_refunded_sessions = sum(safe_int(r.refund_sessions, 0) for r in refunds if r.status == 'completed')
        total_refunded_amount = sum(safe_float(r.refund_amount, 0) for r in refunds if r.status == 'completed')
        refundable_sessions = calculate_refundable_sessions(course)

        return jsonify({
            'success': True,
            'course': {
                'id': course.id,
                'custom_course_cost': course.custom_course_cost,
                'other_cost': course.other_cost,
            },
            'calculations': profit_info,
            'refund_summary': {
                'total_refunded_sessions': total_refunded_sessions,
                'total_refunded_amount': total_refunded_amount,
                'refundable_sessions': refundable_sessions
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/api/formal-courses/<int:course_id>', methods=['DELETE'])
def delete_formal_course(course_id):
    """删除正课记录"""
    course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
    
    # 如果是从试听课转化而来，需要清除试听课的转化标记
    if course.converted_from_trial:
        trial_course = Course.query.get(course.converted_from_trial)
        if trial_course:
            trial_course.converted_to_course = None
    
    db.session.delete(course)
    db.session.commit()
    return jsonify({'success': True, 'message': '正课记录删除成功'})

@main_bp.route('/api/config/course_cost')
def get_course_cost_config():
    """获取正课成本配置"""
    try:
        config = Config.query.filter_by(key='course_cost').first()
        if config:
            return jsonify({'value': config.value})
        else:
            return jsonify({'value': '0'})
    except Exception as e:
        return jsonify({'value': '0'})

@main_bp.route('/api/trial-courses/<int:course_id>', methods=['PUT'])
def update_trial_course(course_id):
    """更新试听课记录"""
    course = Course.query.filter_by(id=course_id, is_trial=True).first_or_404()
    
    try:
        # 更新客户信息
        customer = course.customer
        customer.name = request.form.get('name', request.form.get('customer_name', customer.name)).strip()
        customer.phone = request.form.get('phone', request.form.get('customer_phone', customer.phone)).strip()
        customer.gender = request.form.get('gender', request.form.get('customer_gender')) or None
        customer.grade = request.form.get('grade', request.form.get('customer_grade')) or None
        customer.region = request.form.get('region', request.form.get('customer_region')) or None
        customer.source = request.form.get('source', customer.source) or None
        customer.has_tutoring_experience = request.form.get('has_tutoring_experience', customer.has_tutoring_experience) or None
        
        # 更新试听课信息
        course.trial_price = float(request.form.get('trial_price', course.trial_price))
        course.source = request.form.get('source', course.source)
        course.trial_status = request.form.get('trial_status', course.trial_status)
        
        # 更新自定义成本（如果提供）
        custom_trial_cost = request.form.get('trial_cost')
        if custom_trial_cost and custom_trial_cost.strip():
            course.custom_trial_cost = float(custom_trial_cost)
        
        # 更新退费信息（如果是退费状态）
        if course.trial_status == 'refunded':
            course.refund_amount = float(request.form.get('refund_amount', 0))
            course.refund_fee = float(request.form.get('refund_fee', 0))
            course.refund_channel = request.form.get('refund_channel')
        
        # 计算试听课成本
        # 统一规则：course.cost 仅存储"基础试听课成本"，不包含任何渠道手续费，防止与统计中的手续费重复计算
        if course.custom_trial_cost is not None:
            course.cost = course.custom_trial_cost
        else:
            base_trial_cost_config = Config.query.filter_by(key='trial_cost').first()
            base_trial_cost = float(base_trial_cost_config.value) if base_trial_cost_config else 0
            course.cost = base_trial_cost
        
        db.session.commit()
        return jsonify({'success': True, 'message': '试听课信息更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})

@main_bp.route('/api/formal-courses/<int:course_id>', methods=['PUT'])
def update_formal_course(course_id):
    """更新正课记录"""
    course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
    
    try:
        # 更新客户信息
        customer = course.customer
        customer.name = request.form.get('name', request.form.get('customer_name', customer.name)).strip()
        customer.phone = request.form.get('phone', request.form.get('customer_phone', customer.phone)).strip()
        customer.gender = request.form.get('gender', request.form.get('customer_gender')) or None
        customer.grade = request.form.get('grade', request.form.get('customer_grade')) or None
        customer.region = request.form.get('region', request.form.get('customer_region')) or None
        customer.source = request.form.get('source', customer.source) or None
        customer.has_tutoring_experience = request.form.get('has_tutoring_experience', customer.has_tutoring_experience) or None
        
        # 更新正课信息
        course.course_type = request.form.get('course_type', course.course_type)
        course.sessions = int(request.form.get('sessions', course.sessions))
        course.price = float(request.form.get('price', course.price))
        course.gift_sessions = int(request.form.get('gift_sessions', course.gift_sessions))
        course.other_cost = float(request.form.get('other_cost', course.other_cost))
        course.payment_channel = request.form.get('payment_channel', course.payment_channel)
        
        # 更新自定义成本（如果提供）
        custom_course_cost = request.form.get('course_cost_per_session')
        if custom_course_cost and custom_course_cost.strip():
            course.custom_course_cost = float(custom_course_cost)
            course.snapshot_course_cost = float(custom_course_cost)
        
        # 重新计算正课成本
        # 获取单节成本
        if course.custom_course_cost is not None:
            course_cost_per_session = course.custom_course_cost
        elif course.snapshot_course_cost:
            course_cost_per_session = course.snapshot_course_cost
        else:
            course_cost_config = Config.query.filter_by(key='course_cost').first()
            course_cost_per_session = float(course_cost_config.value) if course_cost_config else 0
        
        # 计算总成本
        total_cost = (course.sessions + course.gift_sessions) * course_cost_per_session + course.other_cost
        course.cost = total_cost
        
        db.session.commit()
        return jsonify({'success': True, 'message': '正课信息更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})

@main_bp.route('/api/trial-courses/<int:course_id>/assign', methods=['POST'])
def assign_trial_course(course_id):
    """分配试听课给员工"""
    course = Course.query.filter_by(id=course_id, is_trial=True).first_or_404()
    
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        
        # 如果employee_id为空字符串或None，则清除分配
        if employee_id == '' or employee_id is None:
            course.assigned_employee_id = None
        else:
            # 验证员工是否存在
            employee = Employee.query.get(employee_id)
            if not employee:
                return jsonify({'success': False, 'message': '员工不存在'}), 400
            course.assigned_employee_id = employee_id
        
        db.session.commit()
        return jsonify({'success': True, 'message': '分配成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'分配失败：{str(e)}'})

@main_bp.route('/api/trial-courses/<int:course_id>/status', methods=['PUT'])
def update_trial_status(course_id):
    """更新试听课状态"""
    course = Course.query.filter_by(id=course_id, is_trial=True).first_or_404()
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        # 验证状态值
        valid_statuses = ['registered', 'not_registered', 'refunded', 'converted', 'no_action']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': '无效的状态值'})
        
        # 更新状态
        course.trial_status = new_status
        
        # 如果是退费状态，更新退费相关信息（金额=试听售价；手续费=0；记录退款渠道）
        if new_status == 'refunded':
            refund_channel = (data.get('refund_channel') or '').strip()
            if not refund_channel:
                return jsonify({'success': False, 'message': '请选择退款渠道'}), 400
            # 接受前端传入的退费金额与手续费（若未提供，采用默认值）
            try:
                refund_amount = float(data.get('refund_amount')) if data.get('refund_amount') is not None else float(course.trial_price or 0)
                refund_fee = float(data.get('refund_fee')) if data.get('refund_fee') is not None else 0.0
            except (TypeError, ValueError):
                return jsonify({'success': False, 'message': '退费金额或手续费格式不正确'}), 400

            course.refund_channel = refund_channel
            course.refund_amount = refund_amount
            course.refund_fee = refund_fee
        else:
            # 非退费状态清空退费信息
            course.refund_amount = 0
            course.refund_fee = 0
            course.refund_channel = None
        
        # 如果状态改为已转化，需要检查是否有对应的正课记录
        if new_status == 'converted' and not course.converted_to_course:
            # 可以在这里添加逻辑来处理转化关系
            pass
        
        db.session.commit()
        return jsonify({'success': True, 'message': '试听课状态更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})



# 课程管理API

@main_bp.route('/api/trial-courses/revenue-debug', methods=['GET'])
def trial_courses_revenue_debug():
    """只读调试接口：输出试听课收入统计的逐条明细与汇总

    口径与 manage_trial_courses() 完全一致：
    - 纳入状态：registered / converted / no_action / refunded
    - 收入：
        * refunded -> 0
        * 其他三类 -> trial_price
    - 未报名 not_registered 完全不纳入

    返回 JSON：
    {
      success: true,
      total_revenue: float,
      included_ids: [int],
      rows: [
        {id, customer_name, status, trial_price, included, revenue}
      ]
    }
    """
    try:
        # 查询所有试听课（不受前端筛选影响）
        trial_courses_list = Course.query.filter(Course.is_trial == True).order_by(Course.created_at.asc()).all()

        rows = []
        total_revenue = 0.0
        included_ids = []

        for course in trial_courses_list:
            status = course.trial_status or 'registered'
            price = float(course.trial_price or 0.0)
            customer_name = course.customer.name if getattr(course, 'customer', None) else None

            included = status in ['registered', 'converted', 'no_action', 'refunded']
            revenue = 0.0
            if included:
                revenue = 0.0 if status == 'refunded' else price
                total_revenue += revenue
                included_ids.append(course.id)

            rows.append({
                'id': course.id,
                'customer_name': customer_name,
                'status': status,
                'trial_price': price,
                'included': included,
                'revenue': revenue
            })

        return jsonify({
            'success': True,
            'total_revenue': round(total_revenue, 2),
            'included_ids': included_ids,
            'rows': rows
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'调试接口执行失败：{str(e)}'}), 500

@main_bp.route('/test-export')
def test_export():
    """测试导出功能页面"""
    return render_template('test_export.html')

# ========== 退费相关API ==========

def calculate_refundable_sessions(course):
    """计算可退费节数"""
    # 获取已退费记录
    existing_refunds = CourseRefund.query.filter_by(
        course_id=course.id,
        status='completed'
    ).all()
    
    # 兼容空值，避免 None 导致求和错误
    total_refunded = sum(safe_int(r.refund_sessions, 0) for r in existing_refunds)
    
    # 可退费节数 = 购买节数 - 已退费节数
    # 注意：赠送节数不参与退费
    refundable = safe_int(course.sessions, 0) - total_refunded
    
    return max(0, refundable)

@main_bp.route('/api/courses/refunds/<int:refund_id>', methods=['PATCH'])
def edit_refund(refund_id):
    """编辑退费记录的节数与金额"""
    try:
        refund = CourseRefund.query.get_or_404(refund_id)
        course = Course.query.get_or_404(refund.course_id)

        data = request.get_json(silent=True) or {}
        new_sessions = data.get('refund_sessions', None)
        new_amount = data.get('refund_amount', None)
        new_reason = data.get('refund_reason', None)
        new_channel = data.get('refund_channel', None)
        new_fee = data.get('refund_fee', None)
        new_remark = data.get('remark', None)

        if all(v is None for v in [new_sessions, new_amount, new_reason, new_channel, new_fee, new_remark]):
            return jsonify({'success': False, 'message': '缺少可更新字段'}), 400

        # 计算可用上限：允许把本记录的原节数释放后再计算
        existing_refunds = CourseRefund.query.filter(
            CourseRefund.course_id == course.id,
            CourseRefund.status == 'completed',
            CourseRefund.id != refund.id
        ).all()
        other_refunded = sum(safe_int(r.refund_sessions, 0) for r in existing_refunds)
        max_sessions = max(0, safe_int(course.sessions, 0) - other_refunded)

        if new_sessions is not None:
            new_sessions_int = safe_int(new_sessions, -1)
            if new_sessions_int <= 0 or new_sessions_int > max_sessions:
                return jsonify({'success': False, 'message': f'退费节数无效，允许区间为 1..{max_sessions}'}), 409
            refund.refund_sessions = new_sessions_int
            # 若未提供金额，按单价计算
            if new_amount is None:
                refund.refund_amount = new_sessions_int * safe_float(course.price, 0)

        if new_amount is not None:
            amount = safe_float(new_amount, None)
            if amount is None or amount < 0:
                return jsonify({'success': False, 'message': '退费金额必须为非负数字'}), 400
            refund.refund_amount = amount

        if new_reason is not None:
            refund.refund_reason = new_reason

        if new_channel is not None:
            refund.refund_channel = new_channel

        if new_fee is not None:
            fee = safe_float(new_fee, None)
            if fee is None or fee < 0:
                return jsonify({'success': False, 'message': '手续费必须为非负数字'}), 400
            refund.refund_fee = fee

        if new_remark is not None:
            refund.remark = new_remark

        db.session.commit()

        # 返回最新统计
        profit_info = calculate_course_profit_with_refund(course)
        refund_history = CourseRefund.query.filter_by(course_id=course.id).order_by(CourseRefund.refund_date.desc()).all()
        total_refunded_sessions = sum(safe_int(r.refund_sessions, 0) for r in refund_history if r.status == 'completed')
        total_refunded_amount = sum(safe_float(r.refund_amount, 0) for r in refund_history if r.status == 'completed')
        total_refunded_fees = sum(safe_float(r.refund_fee, 0) for r in refund_history if r.status == 'completed')
        refundable_sessions = calculate_refundable_sessions(course)

        return jsonify({
            'success': True,
            'refund': {
                'id': refund.id,
                'refund_sessions': refund.refund_sessions,
                'refund_amount': refund.refund_amount,
                'refund_reason': refund.refund_reason,
                'refund_channel': refund.refund_channel,
                'refund_fee': refund.refund_fee,
                'remark': refund.remark
            },
            'calculations': profit_info,
            'refund_summary': {
                'total_refunded_sessions': total_refunded_sessions,
                'total_refunded_amount': total_refunded_amount,
                'total_refunded_fees': total_refunded_fees,
                'refundable_sessions': refundable_sessions
            },
            'refund_history': [
                {
                    'id': r.id,
                    'refund_sessions': r.refund_sessions,
                    'refund_amount': r.refund_amount,
                    'refund_reason': r.refund_reason,
                    'refund_channel': r.refund_channel,
                    'refund_fee': r.refund_fee,
                    'remark': r.remark,
                    'refund_date': (r.refund_date.strftime('%Y-%m-%d %H:%M:%S') if r.refund_date else None),
                    'status': r.status,
                    'operator_name': r.operator_name
                } for r in refund_history
            ]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
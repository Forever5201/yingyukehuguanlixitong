from flask import render_template, request, redirect, url_for, jsonify, flash
from flask import current_app as app
from .models import db, Customer, Config, TaobaoOrder, Course
from datetime import datetime

@app.route('/test-js')
def test_js():
    """JavaScript测试页面"""
    return render_template('test_js.html')

@app.route('/')
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
        Customer.name, Customer.created_at
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

@app.route('/customers', methods=['GET', 'POST'])
def manage_customers():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        grade = request.form['grade']
        region = request.form['region']
        phone = request.form['phone']
        source = request.form['source']
        
        new_customer = Customer(
            name=name, 
            gender=gender, 
            grade=grade, 
            region=region, 
            phone=phone, 
            source=source
        )
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('manage_customers'))

    # 使用分页和选择性字段查询
    customers = Customer.query.with_entities(
        Customer.id, Customer.name, Customer.gender, 
        Customer.grade, Customer.region, Customer.phone, 
        Customer.source, Customer.created_at
    ).order_by(Customer.created_at.desc()).all()
    return render_template('customers.html', customers=customers)

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    if request.method == 'POST':
        # 获取表单数据并更新或创建配置项
        for key in ['trial_cost', 'course_cost', 'taobao_fee_rate']:
            config_item = Config.query.filter_by(key=key).first()
            if not config_item:
                config_item = Config(key=key)
                db.session.add(config_item)
            config_item.value = request.form[key]
        db.session.commit()
        return redirect(url_for('manage_config'))

    # 查询现有配置，如果不存在则提供默认值
    trial_cost = Config.query.filter_by(key='trial_cost').first()
    course_cost = Config.query.filter_by(key='course_cost').first()
    taobao_fee_rate = Config.query.filter_by(key='taobao_fee_rate').first()
    
    config = {
        'trial_cost': trial_cost.value if trial_cost else '0',
        'course_cost': course_cost.value if course_cost else '0',
        'taobao_fee_rate': taobao_fee_rate.value if taobao_fee_rate else '0'
    }
    
    return render_template('config.html', config=config)

@app.route('/taobao-orders', methods=['GET', 'POST'])
def manage_taobao_orders():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        name = request.form['customer_name']
        level = request.form['level']
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
                order.amount = amount
                order.commission = commission
                order.taobao_fee = taobao_fee
                order.evaluated = evaluated
                order.order_time = order_time
        else:  # 添加新记录
            new_order = TaobaoOrder(
                name=name,
                level=level,
                amount=amount,
                commission=commission,
                taobao_fee=taobao_fee,
                evaluated=evaluated,
                order_time=order_time
            )
            db.session.add(new_order)
        
        db.session.commit()
        return redirect(url_for('manage_taobao_orders'))
    
    # 计算统计数据
    from sqlalchemy import case
    stats = db.session.query(
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
    
    # 使用分页和选择性字段查询
    orders = TaobaoOrder.query.with_entities(
        TaobaoOrder.id, TaobaoOrder.name, TaobaoOrder.level,
        TaobaoOrder.amount, TaobaoOrder.commission, TaobaoOrder.taobao_fee,
        TaobaoOrder.evaluated, TaobaoOrder.order_time, TaobaoOrder.settled, 
        TaobaoOrder.settled_at, TaobaoOrder.created_at
    ).order_by(TaobaoOrder.order_time.desc()).all()
    
    return render_template('taobao_orders.html', 
                         orders=orders,
                         stats={
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

@app.route('/api/taobao-orders/<int:order_id>', methods=['GET'])
def get_taobao_order(order_id):
    """获取单个淘宝订单详情"""
    order = TaobaoOrder.query.get_or_404(order_id)
    return jsonify({
        'success': True,
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
            'settled_at': order.settled_at.isoformat() if order.settled_at else None,
            'created_at': order.created_at.isoformat() if order.created_at else None
        }
    })

@app.route('/api/taobao-orders/<int:order_id>', methods=['PUT'])
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

@app.route('/api/taobao-orders/<int:order_id>', methods=['DELETE'])
def delete_taobao_order(order_id):
    """删除淘宝订单"""
    order = TaobaoOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True, 'message': '订单删除成功'})
@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer_api(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/api/taobao-orders/settle', methods=['POST'])
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

@app.route('/api/taobao-orders/<int:order_id>/quick-edit', methods=['PUT'])
def quick_edit_order(order_id):
    """快捷编辑订单字段"""
    order = TaobaoOrder.query.get_or_404(order_id)
    data = request.json
    
    # 更新允许快捷编辑的字段
    if 'level' in data:
        order.level = data['level']
    if 'amount' in data:
        order.amount = float(data['amount'])
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

@app.route('/api/config/<config_key>')
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
@app.route('/trial-courses', methods=['GET', 'POST'])
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
            
            # 验证必填字段
            if not new_customer_name or not new_customer_phone:
                flash('请填写学员姓名和联系电话！', 'error')
                return redirect(url_for('manage_trial_courses'))
            
            # 检查手机号是否已存在
            existing_customer = Customer.query.filter_by(phone=new_customer_phone).first()
            if existing_customer:
                flash(f'手机号 {new_customer_phone} 已存在，学员：{existing_customer.name}', 'error')
                return redirect(url_for('manage_trial_courses'))
            
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
        
        # 获取试听课成本配置
        trial_cost_config = Config.query.filter_by(key='trial_cost').first()
        base_trial_cost = float(trial_cost_config.value) if trial_cost_config else 0
        
        # 计算总成本（基础成本 + 手续费）
        total_trial_cost = base_trial_cost
        
        # 如果来源是淘宝，需要加上手续费
        if source == '淘宝':
            # 获取淘宝手续费率配置
            taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
            taobao_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006  # 转换为小数
            
            # 计算手续费：试听课售价 × 手续费率
            taobao_fee = trial_price * taobao_fee_rate
            total_trial_cost += taobao_fee
        
        # 创建试听课记录
        new_trial = Course(
            name='试听课',
            customer_id=customer_id,
            is_trial=True,
            trial_price=trial_price,
            source=source,
            cost=total_trial_cost
        )
        
        db.session.add(new_trial)
        db.session.commit()
        
        if not request.form.get('customer_id'):
            flash(f'新学员 {new_customer_name} 和试听课记录添加成功！', 'success')
        else:
            flash('试听课记录添加成功！', 'success')
        
        return redirect(url_for('manage_trial_courses'))
    
    # 获取试听课列表
    trial_courses = db.session.query(Course, Customer).join(
        Customer, Course.customer_id == Customer.id
    ).filter(Course.is_trial == True).order_by(Course.created_at.desc()).all()
    
    # 获取客户列表用于下拉选择
    customers = Customer.query.order_by(Customer.name).all()
    
    # 计算试听课统计
    trial_stats = db.session.query(
        db.func.count(Course.id).label('total_trials'),
        db.func.coalesce(db.func.sum(Course.trial_price), 0).label('total_revenue'),
        db.func.coalesce(db.func.sum(Course.cost), 0).label('total_cost')
    ).filter(Course.is_trial == True).first()
    
    # 计算手续费总额
    trial_courses_list = Course.query.filter(Course.is_trial == True).all()
    total_fees = 0
    
    # 获取淘宝手续费率配置
    taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
    taobao_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006  # 转换为小数
    
    for course in trial_courses_list:
        if course.source == '淘宝':
            fee_amount = course.trial_price * taobao_fee_rate
            total_fees += fee_amount
    
    # 计算利润
    total_profit = (trial_stats.total_revenue or 0) - (trial_stats.total_cost or 0)
    
    return render_template('trial_courses.html', 
                         trial_courses=trial_courses,
                         customers=customers,
                         taobao_fee_rate=taobao_fee_rate,
                         stats={
                             'total_trials': trial_stats.total_trials or 0,
                             'total_revenue': trial_stats.total_revenue or 0,
                             'total_cost': trial_stats.total_cost or 0,
                             'total_profit': total_profit,
                             'total_fees': total_fees
                         })

@app.route('/formal-courses', methods=['GET'])
def manage_formal_courses():
    """正课管理页面"""
    
    # 获取正课列表
    formal_courses = db.session.query(Course, Customer).join(
        Customer, Course.customer_id == Customer.id
    ).filter(Course.is_trial == False).order_by(Course.created_at.desc()).all()
    
    # 获取客户列表用于下拉选择
    customers = Customer.query.order_by(Customer.name).all()
    
    # 计算正课统计
    formal_stats = db.session.query(
        db.func.count(Course.id).label('total_courses'),
        db.func.coalesce(db.func.sum(Course.cost), 0).label('total_cost'),
        db.func.coalesce(db.func.sum(Course.sessions), 0).label('total_sessions'),
        db.func.coalesce(db.func.sum(Course.gift_sessions), 0).label('total_gift_sessions')
    ).filter(Course.is_trial == False).first()
    
    # 计算实际总收入（考虑手续费）
    courses = Course.query.filter(Course.is_trial == False).all()
    total_revenue = 0
    total_fees = 0
    
    # 获取淘宝手续费率配置
    taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
    taobao_fee_rate = float(taobao_fee_config.value) if taobao_fee_config else 0.006  # 默认0.6%
    
    for course in courses:
        # 计算基础收入：购买节数 × 单节售价
        base_revenue = course.sessions * course.price
        
        # 如果是淘宝支付，扣除手续费
        if course.payment_channel == '淘宝':
            fee_amount = base_revenue * taobao_fee_rate
            actual_revenue = base_revenue - fee_amount
            total_fees += fee_amount
        else:
            actual_revenue = base_revenue
            
        total_revenue += actual_revenue
    
    # 计算利润
    total_profit = total_revenue - (formal_stats.total_cost or 0)
    
    return render_template('formal_courses.html', 
                         formal_courses=formal_courses,
                         customers=customers,
                         stats={
                             'total_courses': formal_stats.total_courses or 0,
                             'total_revenue': total_revenue,
                             'total_cost': formal_stats.total_cost or 0,
                             'total_profit': total_profit,
                             'total_sessions': formal_stats.total_sessions or 0,
                             'total_gift_sessions': formal_stats.total_gift_sessions or 0,
                             'total_fees': total_fees
                         })

@app.route('/convert-trial/<int:trial_id>', methods=['GET', 'POST'])
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
        
        # 计算总成本
        total_cost = (sessions + gift_sessions) * course_cost_per_session + other_cost
        
        # 创建正课记录
        formal_course = Course(
            name=course_type,
            customer_id=trial_course.customer_id,
            is_trial=False,
            course_type=course_type,
            sessions=sessions,
            price=price,  # 存储单节售价
            cost=total_cost,
            gift_sessions=gift_sessions,
            other_cost=other_cost,
            payment_channel=payment_channel,
            converted_from_trial=trial_id
        )
        
        db.session.add(formal_course)
        db.session.commit()
        
        # 更新试听课记录，标记已转化
        trial_course.converted_to_course = formal_course.id
        db.session.commit()
        
        flash(f'试听课已成功转化为正课：{course_type}', 'success')
        return redirect(url_for('manage_trial_courses'))
    
    return render_template('convert_trial.html', trial_course=trial_course)

@app.route('/api/trial-courses/<int:course_id>', methods=['DELETE'])
def delete_trial_course(course_id):
    """删除试听课记录"""
    course = Course.query.filter_by(id=course_id, is_trial=True).first_or_404()
    
    # 检查是否已转化为正课
    if course.converted_to_course:
        return jsonify({'success': False, 'message': '该试听课已转化为正课，无法删除'})
    
    db.session.delete(course)
    db.session.commit()
    return jsonify({'success': True, 'message': '试听课记录删除成功'})

@app.route('/api/formal-courses/<int:course_id>', methods=['DELETE'])
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

@app.route('/api/config/course_cost')
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

@app.route('/api/trial-courses/<int:course_id>', methods=['PUT'])
def update_trial_course(course_id):
    """更新试听课记录"""
    course = Course.query.filter_by(id=course_id, is_trial=True).first_or_404()
    
    try:
        # 更新客户信息
        customer = course.customer
        customer.name = request.form['customer_name'].strip()
        customer.phone = request.form['customer_phone'].strip()
        customer.gender = request.form.get('customer_gender') or None
        customer.grade = request.form.get('customer_grade') or None
        customer.region = request.form.get('customer_region') or None
        
        # 更新试听课信息
        course.trial_price = float(request.form['trial_price'])
        course.source = request.form['source']
        
        # 重新计算成本
        trial_cost_config = Config.query.filter_by(key='trial_cost').first()
        base_trial_cost = float(trial_cost_config.value) if trial_cost_config else 0
        
        # 如果来源是淘宝，需要加上手续费
        if course.source == '淘宝':
            taobao_fee_rate_config = Config.query.filter_by(key='taobao_fee_rate').first()
            taobao_fee_rate = float(taobao_fee_rate_config.value) if taobao_fee_rate_config else 0.006
            taobao_fee = course.trial_price * taobao_fee_rate
            total_trial_cost = base_trial_cost + taobao_fee
        else:
            total_trial_cost = base_trial_cost
            
        course.cost = total_trial_cost
        
        db.session.commit()
        return jsonify({'success': True, 'message': '试听课信息更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})

@app.route('/api/formal-courses/<int:course_id>', methods=['PUT'])
def update_formal_course(course_id):
    """更新正课记录"""
    course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
    
    try:
        # 更新客户信息
        customer = course.customer
        customer.name = request.form['customer_name'].strip()
        customer.phone = request.form['customer_phone'].strip()
        customer.gender = request.form.get('customer_gender') or None
        customer.grade = request.form.get('customer_grade') or None
        customer.region = request.form.get('customer_region') or None
        
        # 更新正课信息
        course.course_type = request.form['course_type']
        course.name = request.form['course_type']  # 保持name字段同步
        course.sessions = int(request.form['sessions'])
        course.gift_sessions = int(request.form.get('gift_sessions', 0))
        course.price = float(request.form['price'])
        course.payment_channel = request.form['payment_channel']
        course.other_cost = float(request.form.get('other_cost', 0))
        
        # 重新计算成本
        course_cost_config = Config.query.filter_by(key='course_cost').first()
        course_cost_per_session = float(course_cost_config.value) if course_cost_config else 0
        
        # 计算总成本（购买节数 + 赠课节数）* 单节成本 + 其他成本
        total_cost = (course.sessions + course.gift_sessions) * course_cost_per_session + course.other_cost
        course.cost = total_cost
        
        # 更新来源信息
        source = request.form.get('source')
        if source == '试听课转化':
            # 如果改为试听课转化但之前不是，需要处理转化关系
            if not course.converted_from_trial:
                # 这里可以根据需要添加逻辑来关联试听课
                pass
        else:
            # 如果改为直接报名，清除转化关系
            if course.converted_from_trial:
                trial_course = Course.query.get(course.converted_from_trial)
                if trial_course:
                    trial_course.converted_to_course = None
                course.converted_from_trial = None
        
        db.session.commit()
        return jsonify({'success': True, 'message': '正课信息更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'})
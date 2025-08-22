from flask import render_template, request, redirect, url_for, jsonify, flash, make_response, send_from_directory
from flask import current_app as app
from .models import db, Customer, Config, TaobaoOrder, Course
from datetime import datetime
import csv
from io import StringIO, BytesIO
import pandas as pd

@app.route('/test-js')
def test_js():
    """JavaScript测试页面"""
    return render_template('test_js.html')

@app.route('/api/test')
def test_api():
    """简单的测试API"""
    return jsonify({'status': 'ok', 'message': '服务器正常工作'})

@app.route('/api/test-excel')
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

@app.route('/customers', methods=['GET', 'POST'])
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
            return redirect(url_for('manage_customers'))
        
        # 检查手机号是否已存在
        existing_customer = Customer.query.filter_by(phone=phone).first()
        if existing_customer:
            flash(f'手机号 {phone} 已存在，客户：{existing_customer.name}', 'error')
            return redirect(url_for('manage_customers'))
        
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
                # 重新计算手续费
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

@app.route('/api/taobao-orders/<int:order_id>', methods=['GET'])
def get_taobao_order(order_id):
    """获取单个淘宝订单详情"""
    order = TaobaoOrder.query.get_or_404(order_id)
    return jsonify({
        'id': order.id,
        'customer_name': order.name,  # 修正字段名匹配前端期望
        'level': order.level,
        'amount': order.amount,
        'commission': order.commission,
        'taobao_fee': order.taobao_fee,
        'evaluated': order.evaluated,
        'order_time': order.order_time.isoformat() if order.order_time else None,
        'settled': order.settled,
        'settled_at': order.settled_at.isoformat() if order.settled_at else None,
        'created_at': order.created_at.isoformat() if order.created_at else None
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

@app.route('/api/taobao-orders/<int:order_id>', methods=['DELETE'])
def delete_taobao_order(order_id):
    """删除淘宝订单"""
    order = TaobaoOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True, 'message': '订单删除成功'})

@app.route('/api/export/taobao-orders')
def export_taobao_orders():
    """导出刷单数据为Excel"""
    try:
        app.logger.info("开始导出刷单数据")
        
        # 查询所有订单数据，与UI界面保持一致
        try:
            orders = TaobaoOrder.query.order_by(TaobaoOrder.order_time.desc()).all()
            app.logger.info(f"成功查询到 {len(orders)} 条订单")
        except Exception as query_error:
            app.logger.error(f"订单查询失败: {str(query_error)}")
            return jsonify({'error': f'订单查询失败: {str(query_error)}'}), 500
        
        if not orders:
            app.logger.info("没有找到订单数据")
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
                app.logger.error(f"处理第{i+1}条订单数据时出错: {str(data_error)}")
                continue
        
        app.logger.info(f"准备了 {len(data)} 条数据")
        
        if not data:
            return jsonify({'error': '没有有效的数据可导出'}), 404
        
        # 创建DataFrame
        try:
            df = pd.DataFrame(data)
            app.logger.info("创建DataFrame成功")
        except Exception as df_error:
            app.logger.error(f"创建DataFrame失败: {str(df_error)}")
            return jsonify({'error': f'创建DataFrame失败: {str(df_error)}'}), 500
        
        # 创建Excel文件
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='刷单数据', index=False)
            
            output.seek(0)
            app.logger.info("Excel文件创建成功")
        except Exception as excel_error:
            app.logger.error(f"创建Excel文件失败: {str(excel_error)}")
            return jsonify({'error': f'创建Excel文件失败: {str(excel_error)}'}), 500
        
        # 生成文件名（使用英文避免编码问题）
        filename = f"taobao_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # 创建响应
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        app.logger.info("导出完成")
        return response
        
    except Exception as e:
        app.logger.error(f"导出刷单数据时出错: {str(e)}")
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@app.route('/api/export/trial-courses')
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

@app.route('/api/export/formal-courses')
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

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer_api(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # 记录删除信息用于日志
        customer_name = customer.name
        customer_phone = customer.phone
        
        # 查找并删除关联的课程记录
        related_courses = Course.query.filter_by(customer_id=customer_id).all()
        course_count = len(related_courses)
        
        # 删除关联的课程记录
        for course in related_courses:
            db.session.delete(course)
        
        # 删除客户记录
        db.session.delete(customer)
        db.session.commit()
        
        # 记录删除日志
        app.logger.info(f"客户删除成功: {customer_name}({customer_phone}), 同时删除了 {course_count} 条关联课程记录")
        
        return jsonify({
            'success': True, 
            'message': f'删除成功，同时清理了 {course_count} 条关联记录'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"客户删除失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

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
            
            # 验证必填字段（只验证联系电话）
            if not new_customer_phone:
                flash('请填写联系电话！', 'error')
                return redirect(url_for('manage_trial_courses'))
            
            # 如果姓名为空，使用手机号作为临时姓名
            if not new_customer_name:
                new_customer_name = f"学员{new_customer_phone[-4:]}"  # 使用手机号后4位作为临时姓名
            
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
        
        # 检查该客户是否已有未删除的试听课记录
        existing_trial = Course.query.filter_by(customer_id=customer_id, is_trial=True).first()
        if existing_trial:
            customer = Customer.query.get(customer_id)
            flash(f'学员 {customer.name} 已有试听课记录，无法重复添加！', 'error')
            db.session.rollback()  # 回滚事务，避免新客户被创建
            return redirect(url_for('manage_trial_courses'))
        
        # 获取试听课成本配置
        trial_cost_config = Config.query.filter_by(key='trial_cost').first()
        base_trial_cost = float(trial_cost_config.value) if trial_cost_config else 0
        
        # 统一规则：试听课成本仅为基础成本，不包含任何渠道手续费
        total_trial_cost = base_trial_cost
        
        # 创建试听课记录
        new_trial = Course(
            name='试听课',
            customer_id=customer_id,
            is_trial=True,
            trial_price=trial_price,
            source=source,
            cost=total_trial_cost,
            trial_status='registered'
        )
        
        db.session.add(new_trial)
        db.session.commit()
        
        if not request.form.get('customer_id'):
            flash(f'新学员 {new_customer_name} 和试听课记录添加成功！', 'success')
        else:
            flash('试听课记录添加成功！', 'success')
        
        return redirect(url_for('manage_trial_courses'))
    
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
    # 若存在“孤儿”试听课（缺失客户记录），页面不会显示该条，但此前统计会包含，导致不一致。
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
        # 默认状态为空时按“已报名试听课”处理，避免被错误排除
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
            cost = course.cost or 0
            fees = (revenue * channel_rate) if revenue else 0
            profit = revenue - cost  # 修改为不扣除手续费
        elif status == 'refunded':
            # 退费（MIGRATION_GUIDE）：收入=0；成本=基础成本C；不再从利润中扣除手续费
            revenue = 0
            cost = course.cost or 0
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
            cost = course.cost or 0
            fees = (revenue * channel_rate) if revenue else 0
            profit = revenue - cost  # 修改为不扣除手续费
        elif status == 'no_action':
            # 视为已支付并完成试听：与已报名一致
            revenue = course.trial_price or 0
            cost = course.cost or 0
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
    
    return render_template('trial_courses.html', 
                         trial_courses=trial_courses,
                         customers=customers,
                         taobao_fee_rate=taobao_fee_rate,
                         stats=total_stats,
                         status_stats=status_stats,
                         calc_rows=calc_rows if debug_mode else None,
                         embedded=embedded)

@app.route('/formal-courses', methods=['GET'])
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
        db.func.coalesce(db.func.sum(Course.cost), 0).label('total_cost'),
        db.func.coalesce(db.func.sum(Course.sessions), 0).label('total_sessions'),
        db.func.coalesce(db.func.sum(Course.gift_sessions), 0).label('total_gift_sessions')
    ).filter(Course.is_trial == False)
        
    formal_stats = formal_stats_query.first()
    
    # 计算实际总收入（考虑手续费）
    courses_query = Course.query.filter(Course.is_trial == False)
    courses = courses_query.all()
    total_revenue = 0
    total_fees = 0
    
    # 获取淘宝手续费率配置
    taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
    taobao_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006  # 转换为小数
    
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
                         taobao_fee_rate=taobao_fee_rate,
                         stats={
                             'total_courses': formal_stats.total_courses or 0,
                             'total_revenue': total_revenue,
                             'total_cost': formal_stats.total_cost or 0,
                             'total_profit': total_profit,
                             'total_sessions': formal_stats.total_sessions or 0,
                             'total_gift_sessions': formal_stats.total_gift_sessions or 0,
                             'total_fees': total_fees
                         },
                         embedded=embedded)

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
        trial_course.trial_status = 'converted'  # 同步更新状态
        db.session.commit()
        
        flash(f'试听课已成功转化为正课：{course_type}', 'success')
        return redirect(url_for('manage_trial_courses'))
    
    return render_template('convert_trial.html', trial_course=trial_course)

@app.route('/api/trial-courses/<int:course_id>', methods=['GET'])
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
            'converted_to_course': course.converted_to_course,
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

@app.route('/api/formal-courses/<int:course_id>', methods=['GET'])
def get_formal_course(course_id):
    """获取单个正课信息"""
    try:
        course = Course.query.filter_by(id=course_id, is_trial=False).first_or_404()
        
        course_data = {
            'id': course.id,
            'customer_name': course.customer.name,
            'customer_phone': course.customer.phone,
            'customer_gender': course.customer.gender,
            'customer_grade': course.customer.grade,
            'customer_region': course.customer.region,
            'course_type': course.course_type,
            'sessions': course.sessions,
            'gift_sessions': course.gift_sessions,
            'price': course.price,
            'payment_channel': course.payment_channel,
            'cost': course.cost,
            'other_cost': course.other_cost,
            'source': '试听课转化' if course.converted_from_trial else '直接报名',
            'converted_from_trial': course.converted_from_trial,
            'created_at': course.created_at.isoformat() if course.created_at else None
        }
        
        return jsonify({
            'success': True,
            'course': course_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取课程信息失败：{str(e)}'})

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
        
        # 计算试听课成本
        # 统一规则：course.cost 仅存储“基础试听课成本”，不包含任何渠道手续费，防止与统计中的手续费重复计算
        base_trial_cost_config = Config.query.filter_by(key='trial_cost').first()
        base_trial_cost = float(base_trial_cost_config.value) if base_trial_cost_config else 0
        course.cost = base_trial_cost
        
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

@app.route('/api/trial-courses/<int:course_id>/status', methods=['PUT'])
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

@app.route('/api/trial-courses/revenue-debug', methods=['GET'])
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

@app.route('/test-export')
def test_export():
    """测试导出功能页面"""
    return render_template('test_export.html')
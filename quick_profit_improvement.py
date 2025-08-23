"""
快速改进利润分配计算逻辑
直接可以集成到现有系统中
"""

def calculate_profit_distribution(courses, year, month):
    """
    计算月度利润分配
    
    参数:
        courses: 当月课程列表
        year: 年份
        month: 月份
    
    返回:
        包含详细分配信息的字典
    """
    # 初始化统计数据
    result = {
        'year': year,
        'month': month,
        'details': [],  # 明细
        'summary': {
            'total_revenue': 0,
            'total_cost': 0,
            'total_profit': 0,
            'shareholder_a_total': 0,
            'shareholder_b_total': 0
        },
        'breakdown': {
            'shareholder_direct': {
                'new_course': {'profit': 0, 'a_amount': 0, 'b_amount': 0},
                'renewal': {'profit': 0, 'a_amount': 0, 'b_amount': 0}
            },
            'employee': {
                'profit': 0,
                'a_amount': 0,
                'b_amount': 0
            }
        }
    }
    
    # 分配规则
    RULES = {
        'shareholder_new': {'a': 0.5, 'b': 0.5},     # 股东新课 50/50
        'shareholder_renewal': {'a': 0.4, 'b': 0.6}, # 股东续课 40/60
        'employee': {'a': 0.5, 'b': 0.5}             # 员工业务 50/50
    }
    
    # 处理每个课程
    for course in courses:
        # 计算收入
        revenue = course.sessions * course.price
        
        # 计算成本
        base_cost = course.cost
        payment_fee = 0
        if course.payment_channel == '淘宝':
            fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else 0.006
            payment_fee = revenue * fee_rate
        
        total_cost = base_cost + payment_fee
        
        # 判断归属类型（当前阶段默认都是股东）
        attribution_type = 'employee' if course.assigned_employee_id else 'shareholder'
        
        # 如果是员工业务，需要计算员工成本
        employee_cost = 0
        if attribution_type == 'employee':
            # 这里简化处理，实际应该根据员工配置计算
            # employee_cost = 计算员工底薪分摊 + 计算员工提成
            employee_cost = revenue * 0.1  # 假设员工成本占收入的10%
            total_cost += employee_cost
        
        # 计算利润
        profit = revenue - total_cost
        
        # 确定分配规则
        if attribution_type == 'employee':
            rule = RULES['employee']
            shareholder_a_amount = profit * rule['a']
            shareholder_b_amount = profit * rule['b']
            
            # 更新员工业务统计
            result['breakdown']['employee']['profit'] += profit
            result['breakdown']['employee']['a_amount'] += shareholder_a_amount
            result['breakdown']['employee']['b_amount'] += shareholder_b_amount
        else:
            # 股东直接业务
            if course.is_renewal:
                rule = RULES['shareholder_renewal']
                shareholder_a_amount = profit * rule['a']
                shareholder_b_amount = profit * rule['b']
                
                # 更新续课统计
                result['breakdown']['shareholder_direct']['renewal']['profit'] += profit
                result['breakdown']['shareholder_direct']['renewal']['a_amount'] += shareholder_a_amount
                result['breakdown']['shareholder_direct']['renewal']['b_amount'] += shareholder_b_amount
            else:
                rule = RULES['shareholder_new']
                shareholder_a_amount = profit * rule['a']
                shareholder_b_amount = profit * rule['b']
                
                # 更新新课统计
                result['breakdown']['shareholder_direct']['new_course']['profit'] += profit
                result['breakdown']['shareholder_direct']['new_course']['a_amount'] += shareholder_a_amount
                result['breakdown']['shareholder_direct']['new_course']['b_amount'] += shareholder_b_amount
        
        # 保存明细
        detail = {
            'course_id': course.id,
            'customer_name': course.customer.name,
            'course_type': course.course_type,
            'is_renewal': course.is_renewal,
            'attribution_type': attribution_type,
            'revenue': revenue,
            'cost': total_cost,
            'profit': profit,
            'shareholder_a_ratio': rule['a'] * 100,
            'shareholder_b_ratio': rule['b'] * 100,
            'shareholder_a_amount': shareholder_a_amount,
            'shareholder_b_amount': shareholder_b_amount
        }
        result['details'].append(detail)
        
        # 更新汇总
        result['summary']['total_revenue'] += revenue
        result['summary']['total_cost'] += total_cost
        result['summary']['total_profit'] += profit
        result['summary']['shareholder_a_total'] += shareholder_a_amount
        result['summary']['shareholder_b_total'] += shareholder_b_amount
    
    return result


def generate_profit_report_html(distribution_data):
    """生成利润分配报表HTML"""
    html = f"""
    <div class="profit-report">
        <h2>{distribution_data['year']}年{distribution_data['month']}月 利润分配报表</h2>
        
        <div class="summary-section">
            <h3>汇总数据</h3>
            <table class="summary-table">
                <tr>
                    <td>总收入</td>
                    <td>¥{distribution_data['summary']['total_revenue']:,.2f}</td>
                </tr>
                <tr>
                    <td>总成本</td>
                    <td>¥{distribution_data['summary']['total_cost']:,.2f}</td>
                </tr>
                <tr>
                    <td>总利润</td>
                    <td>¥{distribution_data['summary']['total_profit']:,.2f}</td>
                </tr>
            </table>
        </div>
        
        <div class="distribution-section">
            <h3>利润分配</h3>
            
            <h4>股东直接业务</h4>
            <table class="distribution-table">
                <tr>
                    <th>类型</th>
                    <th>利润</th>
                    <th>股东A</th>
                    <th>股东B</th>
                </tr>
                <tr>
                    <td>新课 (50%/50%)</td>
                    <td>¥{distribution_data['breakdown']['shareholder_direct']['new_course']['profit']:,.2f}</td>
                    <td>¥{distribution_data['breakdown']['shareholder_direct']['new_course']['a_amount']:,.2f}</td>
                    <td>¥{distribution_data['breakdown']['shareholder_direct']['new_course']['b_amount']:,.2f}</td>
                </tr>
                <tr>
                    <td>续课 (40%/60%)</td>
                    <td>¥{distribution_data['breakdown']['shareholder_direct']['renewal']['profit']:,.2f}</td>
                    <td>¥{distribution_data['breakdown']['shareholder_direct']['renewal']['a_amount']:,.2f}</td>
                    <td>¥{distribution_data['breakdown']['shareholder_direct']['renewal']['b_amount']:,.2f}</td>
                </tr>
            </table>
            
            <h4>员工负责业务</h4>
            <table class="distribution-table">
                <tr>
                    <td>所有 (50%/50%)</td>
                    <td>¥{distribution_data['breakdown']['employee']['profit']:,.2f}</td>
                    <td>¥{distribution_data['breakdown']['employee']['a_amount']:,.2f}</td>
                    <td>¥{distribution_data['breakdown']['employee']['b_amount']:,.2f}</td>
                </tr>
            </table>
            
            <h4>最终分配</h4>
            <table class="final-distribution">
                <tr>
                    <th>股东</th>
                    <th>分配金额</th>
                </tr>
                <tr>
                    <td>股东A</td>
                    <td>¥{distribution_data['summary']['shareholder_a_total']:,.2f}</td>
                </tr>
                <tr>
                    <td>股东B</td>
                    <td>¥{distribution_data['summary']['shareholder_b_total']:,.2f}</td>
                </tr>
            </table>
        </div>
    </div>
    """
    return html


# 在routes.py中添加的新API端点示例
def improved_profit_report():
    """改进的利润报表API"""
    try:
        # 获取参数
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
        
        # 获取当月正课（非试听课）
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        courses = Course.query.filter(
            Course.is_trial == False,
            Course.created_at >= start_date,
            Course.created_at <= end_date
        ).all()
        
        # 计算分配
        distribution = calculate_profit_distribution(courses, year, month)
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': distribution
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


# 使用示例
if __name__ == '__main__':
    # 模拟数据测试
    class MockCourse:
        def __init__(self, id, customer_name, sessions, price, cost, is_renewal, assigned_employee_id=None):
            self.id = id
            self.customer = type('obj', (object,), {'name': customer_name})
            self.sessions = sessions
            self.price = price
            self.cost = cost
            self.is_renewal = is_renewal
            self.assigned_employee_id = assigned_employee_id
            self.payment_channel = '淘宝'
            self.snapshot_fee_rate = 0.006
            self.course_type = '语法课'
    
    # 测试数据
    test_courses = [
        MockCourse(1, '张三', 10, 100, 300, False),      # 股东新课
        MockCourse(2, '李四', 20, 100, 600, True),       # 股东续课
        MockCourse(3, '王五', 15, 100, 450, False, 1),   # 员工新课
    ]
    
    # 计算分配
    result = calculate_profit_distribution(test_courses, 2024, 11)
    
    # 打印结果
    print("利润分配计算结果：")
    print(f"总收入: ¥{result['summary']['total_revenue']:,.2f}")
    print(f"总成本: ¥{result['summary']['total_cost']:,.2f}")
    print(f"总利润: ¥{result['summary']['total_profit']:,.2f}")
    print(f"股东A: ¥{result['summary']['shareholder_a_total']:,.2f}")
    print(f"股东B: ¥{result['summary']['shareholder_b_total']:,.2f}")
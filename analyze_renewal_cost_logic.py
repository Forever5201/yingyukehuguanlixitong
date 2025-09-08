#!/usr/bin/env python3
"""
分析续课成本逻辑的脚本
"""

import sqlite3
import json
from datetime import datetime

def analyze_renewal_cost_logic():
    """分析续课成本逻辑"""
    print("🔍 开始分析续课成本逻辑...")
    print("=" * 60)
    
    # 连接数据库
    try:
        conn = sqlite3.connect('instance/database.sqlite')
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return
    
    print()
    
    # 1. 检查课程ID 18的详细信息
    print("1. 检查课程ID 18的详细信息...")
    cursor.execute("""
        SELECT id, customer_id, course_type, sessions, price, payment_channel, 
               other_cost, custom_course_cost, snapshot_course_cost, 
               snapshot_fee_rate, is_renewal, renewal_from_course_id,
               created_at, meta
        FROM course 
        WHERE id = 18
    """)
    
    course_18 = cursor.fetchone()
    if course_18:
        print("✅ 找到课程ID 18:")
        print(f"   - 课程类型: {course_18[2]}")
        print(f"   - 节数: {course_18[3]} 节")
        print(f"   - 价格: ¥{course_18[4]:.2f}")
        print(f"   - 支付渠道: {course_18[5]}")
        print(f"   - 其他成本: ¥{course_18[6]:.2f}")
        print(f"   - 自定义成本: ¥{course_18[7] if course_18[7] else '未设置'}")
        print(f"   - 快照成本: ¥{course_18[8] if course_18[8] else '未设置'}")
        print(f"   - 快照手续费率: {course_18[9] if course_18[9] else '未设置'}")
        print(f"   - 是否续课: {'是' if course_18[10] else '否'}")
        print(f"   - 续课来源: {course_18[11] if course_18[11] else '无'}")
        print(f"   - 创建时间: {course_18[12]}")
        
        if course_18[13]:  # meta信息
            try:
                meta = json.loads(course_18[13])
                print(f"   - Meta信息: {meta}")
            except:
                print(f"   - Meta信息: 解析失败")
    else:
        print("❌ 未找到课程ID 18")
        return
    
    print()
    
    # 2. 检查续课来源课程
    if course_18[11]:  # 如果有续课来源
        print("2. 检查续课来源课程...")
        cursor.execute("""
            SELECT id, course_type, sessions, price, payment_channel, 
                   other_cost, custom_course_cost, snapshot_course_cost, 
                   snapshot_fee_rate, created_at
            FROM course 
            WHERE id = ?
        """, (course_18[11],))
        
        source_course = cursor.fetchone()
        if source_course:
            print("✅ 找到续课来源课程:")
            print(f"   - 课程ID: {source_course[0]}")
            print(f"   - 课程类型: {source_course[1]}")
            print(f"   - 节数: {source_course[2]} 节")
            print(f"   - 价格: ¥{source_course[3]:.2f}")
            print(f"   - 支付渠道: {source_course[4]}")
            print(f"   - 其他成本: ¥{source_course[5]:.2f}")
            print(f"   - 自定义成本: ¥{source_course[6] if source_course[6] else '未设置'}")
            print(f"   - 快照成本: ¥{source_course[7] if source_course[7] else '未设置'}")
            print(f"   - 快照手续费率: {source_course[8] if source_course[8] else '未设置'}")
            print(f"   - 创建时间: {source_course[9]}")
        else:
            print("❌ 未找到续课来源课程")
    
    print()
    
    # 3. 检查所有续课记录
    print("3. 检查所有续课记录...")
    cursor.execute("""
        SELECT id, course_type, sessions, price, payment_channel, 
               other_cost, custom_course_cost, snapshot_course_cost, 
               snapshot_fee_rate, renewal_from_course_id, created_at, meta
        FROM course 
        WHERE is_renewal = 1
        ORDER BY created_at DESC
    """)
    
    renewal_courses = cursor.fetchall()
    print(f"✅ 找到 {len(renewal_courses)} 条续课记录:")
    
    for i, renewal in enumerate(renewal_courses, 1):
        print(f"\n   续课记录 {i}:")
        print(f"   - 课程ID: {renewal[0]}")
        print(f"   - 课程类型: {renewal[1]}")
        print(f"   - 节数: {renewal[2]} 节")
        print(f"   - 价格: ¥{renewal[3]:.2f}")
        print(f"   - 支付渠道: {renewal[4]}")
        print(f"   - 其他成本: ¥{renewal[5]:.2f}")
        print(f"   - 自定义成本: ¥{renewal[6] if renewal[6] else '未设置'}")
        print(f"   - 快照成本: ¥{renewal[7] if renewal[7] else '未设置'}")
        print(f"   - 快照手续费率: {renewal[8] if renewal[8] else '未设置'}")
        print(f"   - 续课来源: {renewal[9]}")
        print(f"   - 创建时间: {renewal[10]}")
        
        if renewal[11]:  # meta信息
            try:
                meta = json.loads(renewal[11])
                print(f"   - Meta信息: {meta}")
            except:
                print(f"   - Meta信息: 解析失败")
    
    print()
    
    # 4. 检查成本配置
    print("4. 检查成本配置...")
    cursor.execute("SELECT key, value FROM config WHERE key LIKE '%cost%'")
    cost_configs = cursor.fetchall()
    
    if cost_configs:
        print("✅ 找到成本相关配置:")
        for config in cost_configs:
            print(f"   - {config[0]}: {config[1]}")
    else:
        print("❌ 未找到成本相关配置")
    
    print()
    
    # 5. 分析成本计算逻辑
    print("5. 分析成本计算逻辑...")
    
    # 检查课程ID 18的续课记录
    cursor.execute("""
        SELECT id, course_type, sessions, price, payment_channel, 
               other_cost, custom_course_cost, snapshot_course_cost, 
               snapshot_fee_rate, meta
        FROM course 
        WHERE renewal_from_course_id = 18 AND is_renewal = 1
    """)
    
    course_18_renewals = cursor.fetchall()
    print(f"✅ 课程ID 18的续课记录: {len(course_18_renewals)} 条")
    
    for i, renewal in enumerate(course_18_renewals, 1):
        print(f"\n   续课记录 {i} 的成本分析:")
        print(f"   - 课程ID: {renewal[0]}")
        print(f"   - 课程类型: {renewal[1]}")
        print(f"   - 节数: {renewal[2]} 节")
        print(f"   - 价格: ¥{renewal[3]:.2f}")
        print(f"   - 支付渠道: {renewal[4]}")
        print(f"   - 其他成本: ¥{renewal[5]:.2f}")
        
        # 成本计算逻辑
        custom_cost = renewal[6]
        snapshot_cost = renewal[7]
        fee_rate = renewal[8] or 0.006
        
        print(f"   - 自定义成本: ¥{custom_cost if custom_cost else '未设置'}")
        print(f"   - 快照成本: ¥{snapshot_cost if snapshot_cost else '未设置'}")
        print(f"   - 手续费率: {fee_rate:.3f}")
        
        # 计算单节成本
        effective_cost = None
        cost_source = "未设置"
        if custom_cost is not None:
            effective_cost = custom_cost
            cost_source = "自定义"
        elif snapshot_cost is not None:
            effective_cost = snapshot_cost
            cost_source = "快照"
        else:
            # 从配置获取
            cursor.execute("SELECT value FROM config WHERE key = 'course_cost'")
            config_cost = cursor.fetchone()
            if config_cost:
                effective_cost = float(config_cost[0])
                cost_source = "配置"
        
        print(f"   - 生效单节成本: ¥{effective_cost if effective_cost else '未设置'} ({cost_source})")
        
        # 计算总成本
        if effective_cost:
            sessions = renewal[2]
            price = renewal[3]
            other_cost = renewal[5] or 0
            
            # 课时成本
            session_cost = sessions * effective_cost
            
            # 手续费
            fee = 0
            if renewal[4] == '淘宝':
                fee = sessions * price * fee_rate
            
            # 总成本
            total_cost = session_cost + other_cost + fee
            
            print(f"   - 课时成本: ¥{session_cost:.2f}")
            print(f"   - 手续费: ¥{fee:.2f}")
            print(f"   - 总成本: ¥{total_cost:.2f}")
            
            # 利润计算
            revenue = sessions * price
            profit = revenue - total_cost
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            
            print(f"   - 收入: ¥{revenue:.2f}")
            print(f"   - 利润: ¥{profit:.2f}")
            print(f"   - 利润率: {profit_margin:.1f}%")
        else:
            print("   - 无法计算成本（缺少单节成本信息）")
    
    print()
    
    # 6. 检查问题总结
    print("6. 问题总结...")
    
    issues = []
    
    # 检查续课记录是否缺少成本信息
    for renewal in course_18_renewals:
        if not renewal[6] and not renewal[7]:  # 没有自定义成本和快照成本
            issues.append(f"续课记录ID {renewal[0]} 缺少成本信息")
    
    # 检查配置是否完整
    cursor.execute("SELECT COUNT(*) FROM config WHERE key = 'course_cost'")
    config_count = cursor.fetchone()[0]
    if config_count == 0:
        issues.append("缺少默认课程成本配置")
    
    if issues:
        print("⚠️  发现以下问题:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ 未发现明显问题")
    
    print()
    
    # 7. 建议
    print("7. 改进建议...")
    print("   - 为续课记录设置单节成本（优先使用原课程的成本）")
    print("   - 确保续课时继承原课程的成本配置")
    print("   - 在续课表单中添加成本设置选项")
    print("   - 完善成本计算的默认值处理")
    
    # 关闭数据库连接
    conn.close()
    print("\n✅ 数据库连接已关闭")

if __name__ == "__main__":
    analyze_renewal_cost_logic()









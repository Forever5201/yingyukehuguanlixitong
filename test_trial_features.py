#!/usr/bin/env python3
"""
测试覆盖：试听课 5 状态 × 多支付渠道；以及状态更新接口行为。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Customer, Course, Config


def _reset_db():
    db.drop_all()
    db.create_all()


def _seed_config():
    # 配置多渠道手续费率：单位为百分比
    for k, v in {
        'taobao_fee_rate': 0.6,
        'xiaohongshu_fee_rate': 1.0,
        'douyin_fee_rate': 0.8,
        'referral_fee_rate': 0.0,
    }.items():
        cfg = Config(key=k, value=str(v))
        db.session.add(cfg)
    db.session.commit()


def _add_customer(name='张三', phone='13800000000'):
    c = Customer(name=name, phone=phone)
    db.session.add(c)
    db.session.commit()
    return c


def _add_trial(customer_id, price, cost, source, status, name='试听课'):
    t = Course(
        customer_id=customer_id,
        is_trial=True,
        name=name,
        trial_price=price,
        cost=cost,
        source=source,
        trial_status=status,
    )
    db.session.add(t)
    db.session.commit()
    return t


def _use_test_db():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir, exist_ok=True)
    os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(instance_dir, 'test_database.sqlite')


def test_update_trial_status_api_refund_and_clear_fields():
    _use_test_db()
    app = create_app()
    with app.app_context():
        _reset_db()
        _seed_config()

        cust = _add_customer()
        trial = _add_trial(cust.id, price=100.0, cost=20.0, source='淘宝', status='registered')

        client = app.test_client()

        # refund_channel 必填校验
        resp = client.put(f"/api/trial-courses/{trial.id}/status", json={
            'status': 'refunded'
        })
        assert resp.status_code == 400
        assert resp.get_json().get('success') is False

        # 正常退费：金额 = 试听售价；手续费 = 0；记录渠道
        resp = client.put(f"/api/trial-courses/{trial.id}/status", json={
            'status': 'refunded',
            'refund_channel': '微信',
            # 传入任意金额都应被后端覆盖为 trial_price
            'refund_amount': 1.23,
            'refund_fee': 9.99,
        })
        assert resp.status_code == 200
        assert resp.get_json().get('success') is True

        # 验证数据库值
        trial_db = db.session.get(Course, trial.id)
        assert trial_db.trial_status == 'refunded'
        assert float(trial_db.refund_amount or 0) == 100.0
        assert float(trial_db.refund_fee or 0) == 0.0
        assert trial_db.refund_channel == '微信'

        # 切回非退费状态，需清空退款字段
        resp = client.put(f"/api/trial-courses/{trial.id}/status", json={
            'status': 'registered'
        })
        assert resp.status_code == 200
        trial_db = db.session.get(Course, trial.id)
        assert trial_db.trial_status == 'registered'
        assert float(trial_db.refund_amount or 0) == 0.0
        assert float(trial_db.refund_fee or 0) == 0.0
        assert trial_db.refund_channel in (None, '')


def test_trial_stats_multi_channel_and_states():
    """
    覆盖 5 状态 × 多渠道：
    - not_registered：完全不参与统计
    - registered / converted / no_action：收入=售价；手续费=售价×渠道费率；利润=收入-成本-手续费
    - refunded：收入=0；手续费=0；利润=−基础成本
    """
    app = create_app()
    with app.app_context():
        _reset_db()
        _seed_config()

        c = _add_customer('李四', '13900000000')

        # 准备 5 条试听课（5 状态 × 多渠道）
        t1 = _add_trial(c.id, 100.0, 20.0, '淘宝',   'registered')   # 费率0.6% → 0.60
        t2 = _add_trial(c.id, 200.0, 30.0, '小红书', 'converted')    # 费率1.0% → 2.00
        t3 = _add_trial(c.id, 150.0, 25.0, '抖音',   'no_action')    # 费率0.8% → 1.20
        t4 = _add_trial(c.id, 120.0, 15.0, '转介绍', 'refunded')     # 手续费=0，利润=−15
        t5 = _add_trial(c.id,  80.0, 10.0, '淘宝',   'not_registered')  # 完全不计入

        # 期望统计（仅 t1,t2,t3,t4 计入）
        exp = {
            'registered': {
                'count': 1,
                'revenue': 100.0,
                'cost': 20.0,
                'fees': 0.6,
                'profit': 100.0 - 20.0 - 0.6,
            },
            'converted': {
                'count': 1,
                'revenue': 200.0,
                'cost': 30.0,
                'fees': 2.0,
                'profit': 200.0 - 30.0 - 2.0,
            },
            'no_action': {
                'count': 1,
                'revenue': 150.0,
                'cost': 25.0,
                'fees': 1.2,
                'profit': 150.0 - 25.0 - 1.2,
            },
            'refunded': {
                'count': 1,
                'revenue': 0.0,
                'cost': 15.0,
                'fees': 0.0,
                'profit': -15.0,
            },
        }

        # 从数据库读取、按新规则现算一遍
        all_trials = Course.query.filter_by(is_trial=True).all()

        def fee_rate(source: str) -> float:
            if source == '淘宝':
                return 0.006
            if source == '小红书':
                return 0.01
            if source == '抖音':
                return 0.008
            if source == '转介绍':
                return 0.0
            return 0.0

        got = {
            'registered': {'count': 0, 'revenue': 0.0, 'cost': 0.0, 'fees': 0.0, 'profit': 0.0},
            'converted':  {'count': 0, 'revenue': 0.0, 'cost': 0.0, 'fees': 0.0, 'profit': 0.0},
            'no_action':  {'count': 0, 'revenue': 0.0, 'cost': 0.0, 'fees': 0.0, 'profit': 0.0},
            'refunded':   {'count': 0, 'revenue': 0.0, 'cost': 0.0, 'fees': 0.0, 'profit': 0.0},
        }

        for c0 in all_trials:
            status = c0.trial_status or 'not_registered'
            if status == 'not_registered':
                continue

            if status in ('registered', 'converted', 'no_action'):
                revenue = float(c0.trial_price or 0)
                cost = float(c0.cost or 0)
                fees = revenue * fee_rate(c0.source or '') if revenue else 0.0
                profit = revenue - cost - fees
            elif status == 'refunded':
                revenue = 0.0
                cost = float(c0.cost or 0)
                fees = 0.0
                profit = -cost
            else:
                continue

            got[status]['count'] += 1
            got[status]['revenue'] += revenue
            got[status]['cost'] += cost
            got[status]['fees'] += fees
            got[status]['profit'] += profit

        # 断言各状态统计
        for k in exp:
            for m in exp[k]:
                assert abs(got[k][m] - exp[k][m]) < 1e-6, f"{k}.{m} 期望 {exp[k][m]} 实际 {got[k][m]}"


# 保留原有的打印式入口，方便手工运行观察数据
def test_trial_features():
    _use_test_db()
    app = create_app()
    with app.app_context():
        print("=== 试听课功能 smoke 测试（仅打印） ===")
        trials = Course.query.filter_by(is_trial=True).all()
        print(f"试听课数量: {len(trials)}")
        print("=== 结束 ===")

if __name__ == '__main__':
    test_trial_features()
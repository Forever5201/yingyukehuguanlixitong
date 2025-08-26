[1mdiff --git a/test_trial_add.py b/test_trial_add.py[m
[1mdeleted file mode 100644[m
[1mindex 3cfbb42..0000000[m
[1m--- a/test_trial_add.py[m
[1m+++ /dev/null[m
[36m@@ -1,55 +0,0 @@[m
[31m-#!/usr/bin/env python3[m
[31m-# -*- coding: utf-8 -*-[m
[31m-"""[m
[31m-测试试听课添加逻辑 - 测试用户反馈的具体场景[m
[31m-"""[m
[31m-[m
[31m-from app import create_app, db[m
[31m-from app.models import Course, Customer[m
[31m-[m
[31m-def test_existing_customer_trial():[m
[31m-    """测试为已存在客户添加试听课"""[m
[31m-    app = create_app()[m
[31m-    [m
[31m-    with app.app_context():[m
[31m-        print("=== 测试为已存在客户添加试听课 ===")[m
[31m-        [m
[31m-        # 测试用户反馈的手机号[m
[31m-        test_phone = "17844540733"[m
[31m-        [m
[31m-        # 1. 检查是否已有该手机号的客户[m
[31m-        existing_customer = Customer.query.filter_by(phone=test_phone).first()[m
[31m-        if existing_customer:[m
[31m-            print(f"发现已存在客户: {existing_customer.name}, 电话: {existing_customer.phone}")[m
[31m-            customer_id = existing_customer.id[m
[31m-            [m
[31m-            # 2. 检查该客户是否已有试听课记录[m
[31m-            existing_trial = Course.query.filter_by(customer_id=customer_id, is_trial=True).first()[m
[31m-            if existing_trial:[m
[31m-                print(f"发现已存在的试听课记录: ID={existing_trial.id}")[m
[31m-                print("这就是导致错误的原因！")[m
[31m-                print(f"试听课状态: {existing_trial.trial_status}")[m
[31m-                print(f"试听课创建时间: {existing_trial.created_at}")[m
[31m-            else:[m
[31m-                print("没有找到已存在的试听课记录，可以添加新的试听课")[m
[31m-        else:[m
[31m-            print("没有找到该手机号的客户")[m
[31m-[m
[31m-def test_all_customers_trials():[m
[31m-    """检查所有客户的试听课情况"""[m
[31m-    app = create_app()[m
[31m-    [m
[31m-    with app.app_context():[m
[31m-        print("\n=== 检查所有客户的试听课情况 ===")[m
[31m-        [m
[31m-        customers = Customer.query.all()[m
[31m-        for customer in customers:[m
[31m-            trials = Course.query.filter_by(customer_id=customer.id, is_trial=True).all()[m
[31m-            if trials:[m
[31m-                print(f"客户: {customer.name} ({customer.phone}) 有 {len(trials)} 个试听课记录:")[m
[31m-                for trial in trials:[m
[31m-                    print(f"  - ID: {trial.id}, 状态: {trial.trial_status}, 创建时间: {trial.created_at}")[m
[31m-[m
[31m-if __name__ == '__main__':[m
[31m-    test_existing_customer_trial()[m
[31m-    test_all_customers_trials()[m
\ No newline at end of file[m

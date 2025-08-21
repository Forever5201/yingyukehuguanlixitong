#!/usr/bin/env python3
"""
详细测试Excel导出功能
"""

import sys
import os
sys.path.append('.')

from app import create_app
import requests
import tempfile

def test_export_functionality():
    """测试导出功能的各个方面"""
    print("=== Excel导出功能详细测试 ===\n")
    
    app = create_app()
    
    # 测试1: 直接调用后端API
    print("1. 测试后端API直接调用...")
    with app.test_client() as client:
        try:
            response = client.get('/api/export/taobao-orders')
            print(f"   状态码: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   Content-Length: {response.headers.get('Content-Length')}")
            print(f"   Content-Disposition: {response.headers.get('Content-Disposition')}")
            
            if response.status_code == 200:
                # 保存文件到临时目录测试
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                    tmp_file.write(response.data)
                    tmp_file_path = tmp_file.name
                
                # 检查文件大小
                file_size = os.path.getsize(tmp_file_path)
                print(f"   生成的Excel文件大小: {file_size} bytes")
                
                # 尝试用pandas读取验证
                try:
                    import pandas as pd
                    df = pd.read_excel(tmp_file_path)
                    print(f"   Excel文件验证成功，包含 {len(df)} 行数据")
                    print(f"   列名: {list(df.columns)}")
                    if len(df) > 0:
                        print(f"   第一行数据: {df.iloc[0].to_dict()}")
                except Exception as e:
                    print(f"   Excel文件验证失败: {e}")
                
                # 清理临时文件
                os.unlink(tmp_file_path)
                print("   ✓ 后端API测试通过")
            else:
                print(f"   ✗ 后端API测试失败: {response.get_data(as_text=True)}")
                
        except Exception as e:
            print(f"   ✗ 后端API测试异常: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    
    # 测试2: 检查数据库中是否有数据
    print("2. 检查数据库中的刷单数据...")
    with app.app_context():
        from app.models import TaobaoOrder
        orders = TaobaoOrder.query.all()
        print(f"   数据库中共有 {len(orders)} 条刷单记录")
        
        if len(orders) > 0:
            order = orders[0]
            print(f"   示例记录: ID={order.id}, 姓名={order.name}, 金额={order.amount}")
        else:
            print("   ⚠️  数据库中没有刷单记录，这可能是导出为空的原因")
    
    print()
    
    # 测试3: 检查依赖库
    print("3. 检查必要的依赖库...")
    try:
        import pandas as pd
        print(f"   ✓ pandas版本: {pd.__version__}")
    except ImportError as e:
        print(f"   ✗ pandas未安装: {e}")
    
    try:
        import openpyxl
        print(f"   ✓ openpyxl版本: {openpyxl.__version__}")
    except ImportError as e:
        print(f"   ✗ openpyxl未安装: {e}")
    
    print()
    
    # 测试4: 模拟前端请求
    print("4. 模拟前端请求...")
    with app.test_client() as client:
        try:
            # 先访问刷单管理页面
            page_response = client.get('/taobao-orders')
            print(f"   刷单管理页面状态码: {page_response.status_code}")
            
            # 然后测试导出
            export_response = client.get('/api/export/taobao-orders')
            print(f"   导出请求状态码: {export_response.status_code}")
            
            if export_response.status_code == 200:
                print("   ✓ 前端请求模拟成功")
            else:
                print(f"   ✗ 前端请求模拟失败: {export_response.get_data(as_text=True)}")
                
        except Exception as e:
            print(f"   ✗ 前端请求模拟异常: {e}")
    
    print()
    
    # 测试5: 检查路由注册
    print("5. 检查路由注册...")
    with app.app_context():
        rules = list(app.url_map.iter_rules())
        export_routes = [rule for rule in rules if 'export' in rule.rule]
        print(f"   找到 {len(export_routes)} 个导出相关路由:")
        for route in export_routes:
            print(f"     - {route.rule} [{', '.join(route.methods)}]")
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_export_functionality()
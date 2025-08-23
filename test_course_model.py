#!/usr/bin/env python
"""
测试 Course 模型和数据库映射
"""
from app import create_app, db
from app.models import Course
from sqlalchemy import inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_course_model():
    """测试 Course 模型"""
    app = create_app()
    
    with app.app_context():
        logger.info("="*60)
        logger.info("测试 Course 模型")
        logger.info("="*60)
        
        # 1. 检查模型定义的属性
        logger.info("\n1. Course 模型定义的属性：")
        for attr in dir(Course):
            if not attr.startswith('_') and hasattr(Course, attr):
                attr_obj = getattr(Course, attr)
                if hasattr(attr_obj, 'type'):
                    logger.info(f"  - {attr}: {attr_obj.type}")
        
        # 2. 检查数据库表的实际列
        logger.info("\n2. 数据库表的实际列：")
        inspector = inspect(db.engine)
        columns = inspector.get_columns('course')
        for col in columns:
            logger.info(f"  - {col['name']}: {col['type']}")
        
        # 3. 测试创建一个 Course 实例
        logger.info("\n3. 测试创建 Course 实例：")
        try:
            test_course = Course(
                name="测试课程",
                customer_id=1,
                is_trial=True,
                cost=100.0
            )
            logger.info("✅ Course 实例创建成功，cost 属性可用")
            logger.info(f"   cost 值: {test_course.cost}")
        except Exception as e:
            logger.error(f"❌ 创建 Course 实例失败: {e}")
        
        # 4. 测试查询
        logger.info("\n4. 测试数据库查询：")
        try:
            courses = Course.query.limit(1).all()
            if courses:
                course = courses[0]
                logger.info(f"✅ 查询成功，获取到课程: {course.name}")
                try:
                    cost_value = course.cost
                    logger.info(f"   cost 值: {cost_value}")
                except AttributeError as e:
                    logger.error(f"❌ 访问 cost 属性失败: {e}")
            else:
                logger.info("   数据库中没有课程记录")
        except Exception as e:
            logger.error(f"❌ 查询失败: {e}")
        
        # 5. 直接执行 SQL 测试
        logger.info("\n5. 直接 SQL 查询测试：")
        try:
            from sqlalchemy import text
            result = db.session.execute(text("SELECT id, name, cost FROM course LIMIT 1"))
            row = result.fetchone()
            if row:
                logger.info(f"✅ SQL 查询成功: id={row[0]}, name={row[1]}, cost={row[2]}")
            else:
                logger.info("   没有数据")
        except Exception as e:
            logger.error(f"❌ SQL 查询失败: {e}")

if __name__ == "__main__":
    test_course_model()
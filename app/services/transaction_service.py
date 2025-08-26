"""
事务管理服务 - 为复杂业务操作提供事务支持

功能：
1. 统一的事务管理
2. 自动错误回滚
3. 事务日志记录
4. 嵌套事务支持
"""

from typing import Callable, Any, Optional, Dict
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from ..models import db
import logging

logger = logging.getLogger(__name__)


class TransactionService:
    """事务管理服务类"""
    
    @staticmethod
    def transactional(func: Callable) -> Callable:
        """
        事务装饰器 - 自动管理事务的提交和回滚
        
        使用方法:
            @TransactionService.transactional
            def my_business_method():
                # 业务逻辑
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 检查是否已经在事务中
                if db.session.get_transaction() is not None and db.session.get_transaction().is_active:
                    # 已在事务中，直接执行函数
                    result = func(*args, **kwargs)
                    return result
                else:
                    # 不在事务中，创建新事务
                    with db.session.begin():
                        result = func(*args, **kwargs)
                        return result
            except SQLAlchemyError as e:
                # 数据库错误，记录但不再次回滚（Flask-SQLAlchemy会自动处理）
                logger.error(f"事务执行失败 ({func.__name__}): {str(e)}")
                print(f"事务执行失败 ({func.__name__}): {str(e)}")
                raise
            except Exception as e:
                # 其他错误
                logger.error(f"业务逻辑执行失败 ({func.__name__}): {str(e)}")
                print(f"业务逻辑执行失败 ({func.__name__}): {str(e)}")
                if db.session.get_transaction() is not None and db.session.get_transaction().is_active:
                    db.session.rollback()
                raise
        
        return wrapper
    
    @classmethod
    def execute_in_transaction(cls, operations: list) -> Dict[str, Any]:
        """
        在单个事务中执行多个操作
        
        Args:
            operations: 操作列表，每个操作是一个字典:
                {
                    'func': 要执行的函数,
                    'args': 位置参数元组,
                    'kwargs': 关键字参数字典,
                    'name': 操作名称（用于日志）
                }
        
        Returns:
            执行结果字典，key为操作名称，value为执行结果
        """
        results = {}
        
        try:
            with db.session.begin():
                for operation in operations:
                    func = operation['func']
                    args = operation.get('args', ())
                    kwargs = operation.get('kwargs', {})
                    name = operation.get('name', func.__name__)
                    
                    logger.info(f"执行事务操作: {name}")
                    
                    try:
                        result = func(*args, **kwargs)
                        results[name] = result
                    except Exception as e:
                        logger.error(f"事务操作失败 ({name}): {str(e)}")
                        raise
                
                # 所有操作成功，事务自动提交
                logger.info(f"事务成功完成，共执行 {len(operations)} 个操作")
                return results
                
        except Exception as e:
            logger.error(f"事务执行失败，已回滚: {str(e)}")
            db.session.rollback()
            raise
    
    @classmethod
    def create_savepoint(cls, name: str) -> None:
        """
        创建一个保存点
        
        Args:
            name: 保存点名称
        """
        try:
            db.session.execute(f"SAVEPOINT {name}")
            logger.debug(f"创建保存点: {name}")
        except Exception as e:
            logger.error(f"创建保存点失败 ({name}): {str(e)}")
            raise
    
    @classmethod
    def rollback_to_savepoint(cls, name: str) -> None:
        """
        回滚到指定保存点
        
        Args:
            name: 保存点名称
        """
        try:
            db.session.execute(f"ROLLBACK TO SAVEPOINT {name}")
            logger.info(f"回滚到保存点: {name}")
        except Exception as e:
            logger.error(f"回滚到保存点失败 ({name}): {str(e)}")
            raise
    
    @classmethod
    def release_savepoint(cls, name: str) -> None:
        """
        释放保存点
        
        Args:
            name: 保存点名称
        """
        try:
            db.session.execute(f"RELEASE SAVEPOINT {name}")
            logger.debug(f"释放保存点: {name}")
        except Exception as e:
            logger.error(f"释放保存点失败 ({name}): {str(e)}")
            raise


class ComplexTransactionManager:
    """复杂事务管理器 - 用于处理涉及多个服务的复杂业务操作"""
    
    @classmethod
    @TransactionService.transactional
    def process_trial_to_formal_conversion(cls, trial_id: int, formal_course_data: Dict) -> Dict:
        """
        处理试听转正课的复杂事务
        
        包含步骤:
        1. 创建正课记录
        2. 更新试听课状态
        3. 计算并分配利润
        4. 更新员工业绩
        
        Args:
            trial_id: 试听课ID
            formal_course_data: 正课数据
            
        Returns:
            处理结果
        """
        from ..models import Course
        from .profit_service import ProfitService
        
        # 1. 获取试听课信息
        trial_course = Course.query.get(trial_id)
        if not trial_course or not trial_course.is_trial:
            raise ValueError("无效的试听课ID")
        
        # 2. 创建正课记录
        formal_course = Course(
            customer_id=trial_course.customer_id,
            is_trial=False,
            converted_from_trial=trial_id,
            assigned_employee_id=trial_course.assigned_employee_id,
            **formal_course_data
        )
        db.session.add(formal_course)
        db.session.flush()  # 获取ID
        
        # 3. 更新试听课状态
        trial_course.trial_status = 'converted'
        trial_course.converted_to_course = formal_course.id
        
        # 4. 计算利润（利润计算会在查询时动态进行，这里只是验证）
        profit_info = ProfitService.calculate_course_profit(formal_course)
        
        return {
            'trial_course_id': trial_id,
            'formal_course_id': formal_course.id,
            'profit_info': profit_info
        }
    
    @classmethod
    @TransactionService.transactional
    def process_course_renewal(cls, original_course_id: int, renewal_data: Dict) -> Dict:
        """
        处理课程续费的复杂事务
        
        Args:
            original_course_id: 原课程ID
            renewal_data: 续费数据
            
        Returns:
            处理结果
        """
        from ..models import Course
        
        # 1. 获取原课程信息
        original_course = Course.query.get(original_course_id)
        if not original_course or original_course.is_trial:
            raise ValueError("无效的课程ID")
        
        # 2. 创建续课记录
        renewal_course = Course(
            customer_id=original_course.customer_id,
            is_trial=False,
            is_renewal=True,
            renewal_from_course_id=original_course_id,
            assigned_employee_id=original_course.assigned_employee_id,
            **renewal_data
        )
        db.session.add(renewal_course)
        db.session.flush()
        
        return {
            'original_course_id': original_course_id,
            'renewal_course_id': renewal_course.id
        }
    
    @classmethod
    @TransactionService.transactional
    def batch_update_employee_commission(cls, employee_id: int, commission_data: Dict) -> bool:
        """
        批量更新员工提成配置
        
        Args:
            employee_id: 员工ID
            commission_data: 提成配置数据
            
        Returns:
            是否成功
        """
        from ..models import CommissionConfig, Employee
        
        # 验证员工存在
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError("员工不存在")
        
        # 查找或创建提成配置
        config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if not config:
            config = CommissionConfig(employee_id=employee_id)
            db.session.add(config)
        
        # 更新配置
        for key, value in commission_data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        db.session.flush()
        return True
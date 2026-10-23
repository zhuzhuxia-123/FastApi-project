from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.exception import (
    generic_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
)


def register_exception_handlers(app):
    """
    注册全局异常处理器
    """
    app.add_exception_handler(HTTPException, http_exception_handler)# 业务逻辑异常
    app.add_exception_handler(IntegrityError, integrity_error_handler)# 数据库约束异常
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)# 数据库操作异常
    app.add_exception_handler(Exception, generic_exception_handler)# 其他未捕获的异常

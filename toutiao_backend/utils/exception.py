from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette import status

DEBUG_MODE = True  # 设置为True以启用调试模式


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    error_message = str(exc.orig)  # 获取原始异常信息

    if "username_UNIQUE" in error_message or "Duplicate entry" in error_message:
        detail = "用户名已存在"
    elif "FOREIGN KEY" in error_message:
        detail = "外键约束错误"
    else:
        detail = "数据约束冲突，请检查输入数据"
    # 在开发模式下，可以返回详细的错误信息
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",
            "error_detail": error_message,
            "path": str(request.url),
        }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": 400, "message": detail, "data": error_data},
    )
from config.db_config import get_database
from crud import users
from fastapi import APIRouter, Depends, HTTPException, status
from models.users import User
from schemas.users import UserAuthResponse, UserInfoResponse, UserRequest, UserUpdateRequest
from sqlalchemy.ext.asyncio import AsyncSession
from utils import security
from utils import response
from utils.auth import get_current_user
from schemas.users import UserChangePasswordRequest

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register")
async def register_user(
    user_data: UserRequest, db: AsyncSession = Depends(get_database)
):
    existing_user = await users.get_user_by_username(db=db, username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )
    # 这里可以调用crud层的函数来处理用户注册逻辑
    new_user = await users.create_user(db=db, user_data=user_data)
    # 生成token逻辑
    new_token = await users.create_token(db=db, user_id=new_user.id)
    response_data = UserAuthResponse(
        token=new_token.token, userInfo=UserInfoResponse.model_validate(new_user)
    )
    return response.success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_database)):
    user = await users.authenticate_user(
        db=db, username=user_data.username, password=user_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )
    token = await users.create_token(db=db, user_id=user.id)
    response_data = UserAuthResponse(
        token=token.token, userInfo=UserInfoResponse.model_validate(user)
    )
    return response.success_response(message="登录成功", data=response_data)


# 查询用户信息，需要登录
@router.post("/info")
async def get_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
):
    return response.success_response(
        message="获取用户信息成功", data=UserInfoResponse.model_validate(current_user)
    )

# 修改用户信息：验证Token -> 更新（用户输入数据 put提交 -> 请求体参数 -> 定义pydantic模型） -> 返回成功响应
@router.put("update")
async def update_user_info(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
):
    updated_user = await users.update_user(
        user_data=user_data, username=current_user.username, db=db
    )
    return response.success_response(
        message="更新用户信息成功", data=UserInfoResponse.model_validate(updated_user)
    )

@router.put("/password")
async def update_password(
    password_data: UserChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
): 
    res_change_password = await users.update_password(
        db=db,
        current_user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    if not res_change_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码错误"
        )
    return response.success_response(
        message="密码更新成功"
        )
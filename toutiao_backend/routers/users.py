from config.db_config import get_database
from crud import users
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.users import UserAuthResponse, UserInfoResponse, UserRequest
from sqlalchemy.ext.asyncio import AsyncSession
from utils import response

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register")
async def register_user(
    user_data: UserRequest,
    db: AsyncSession = Depends(get_database),
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
    response_data = UserAuthResponse(token=new_token.token, userInfo=UserInfoResponse.model_validate(new_user))
    return response.success_response(message="注册成功", data=response_data)

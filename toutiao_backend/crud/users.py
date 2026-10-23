from datetime import datetime, timedelta
import uuid

from models.users import User, UserToken
from schemas.users import UserRequest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils import security


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    return user


async def create_user(db: AsyncSession, user_data: UserRequest):
    # 加密处理
    hashed_password = security.hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        password=hashed_password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  # 从数据库中刷新对象，获取最新的状态
    return new_user

async def create_token(db: AsyncSession,user_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)  # 设置过期时间为7天后
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        # 如果已经存在token，更新token和过期时间
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        # 如果不存在token，创建新的token记录
        new_token = UserToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return new_token

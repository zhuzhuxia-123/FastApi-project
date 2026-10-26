import uuid
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException

from models.users import User, UserToken
from schemas.users import UserChangePasswordRequest, UserRequest, UserUpdateRequest
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils import security
from fastapi import status



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


async def create_token(db: AsyncSession, user_id: int):
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
        new_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return new_token


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None
    return user


async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if not user_token or user_token.expires_at < datetime.now():
        return None
    query = await db.execute(select(User).where(User.id == user_token.user_id))
    user = query.scalar_one_or_none()
    return user

async def update_user(user_data: UserUpdateRequest, username: str, db: AsyncSession):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(query)
    await db.commit()
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    updated_user = await get_user_by_username(db=db, username=username)
    return updated_user

async def update_password(
    db: AsyncSession,
    current_user: User,
    old_password: str,
    new_password: str
):
    if not security.verify_password(old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")
    # 构建更新数据
    current_user.password = security.hash_password(new_password)
    query = update(User).where(User.username == current_user.username).values(password=current_user.password)
    await db.execute(query)
    await db.commit()
    await db.refresh(current_user)
    return True

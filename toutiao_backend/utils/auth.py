from config.db_config import get_database
from crud import users
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_database),
):
    # 从Authorization头中提取token,token = Bearer token
    token = authorization.split(" ")[1]
    user = await users.get_user_by_token(db=db, token=token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的token"
        )
    return user

from config.db_config import get_database
from crud import news
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 创建apirouter实例
# tags分组 标签
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_database)
):
    categories = await news.get_categories(db=db, skip=skip, limit=limit)
    return {"code": 200, "message": "获取新闻分类成功", "data": categories}

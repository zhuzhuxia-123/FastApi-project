from models.news import Category
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Category).offset(skip).limit(limit))
    categories = result.scalars().all()
    return categories

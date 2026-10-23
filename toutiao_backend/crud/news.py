from models.news import Category, News
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Category).offset(skip).limit(limit))
    categories = result.scalars().all()
    return categories


async def get_news_list(
    db: AsyncSession, category_id: int, skip: int = 1, limit: int = 10
):
    result = await db.execute(
        select(Category).where(Category.id == category_id).offset(skip).limit(limit)
    )
    news_list = result.scalars().all()
    return news_list


async def get_news_count(db: AsyncSession, category_id: int):
    result = await db.execute(
        select(func.count(News.id)).where(News.category_id == category_id)
    )
    return result.scalar_one()


async def get_news_detail(db: AsyncSession, news_id: int):
    result = await db.execute(select(News).where(News.id == news_id))
    news_detail = result.scalar_one_or_none()
    return news_detail


async def increment_news_views(db: AsyncSession, news_id: int) -> bool:
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0  # type: ignore # 返回是否成功更新


async def get_related_news(
    db: AsyncSession, category_id: int, news_id: int, limit: int = 5
):
    result = await db.execute(
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(News.publish_time.desc(), News.publish_time.desc())
        .limit(limit)
    )
    # 列表推导式，返回相关新闻列表
    return [
        {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "author": news_detail.author,
            "image": news_detail.image,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
        }
        for news_detail in result.scalars().all()
    ]  

from config.db_config import get_database
from crud import news
from fastapi import APIRouter, Depends, HTTPException, Query
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


# alias参数用于指定请求参数的别名，直接使用category_id不会生效
@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId", description="新闻分类id"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, alias="pageSize", description="每页数量"),
    db: AsyncSession = Depends(get_database),
):
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(
        db=db, category_id=category_id, skip=offset, limit=page_size
    )
    total = await news.get_news_count(db=db, category_id=category_id)
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": offset + len(news_list) < total,
        },
    }

@router.get("detail")
async def get_news_detail(
    news_id: int = Query(..., alias="newsId", description="新闻id"),
    db: AsyncSession = Depends(get_database),
):
    views_res = await news.increment_news_views(db=db, news_id=news_id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")
    news_detail = await news.get_news_detail(db=db, news_id=news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    related_news = await news.get_related_news(db=db, category_id=news_detail.category_id, news_id=news_id)
    return {"code": 200, "message": "获取新闻详情成功", "data": {
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "author": news_detail.author,
        "image": news_detail.image,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
    }}

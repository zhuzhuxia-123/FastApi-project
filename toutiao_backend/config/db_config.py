from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

Base_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8"
# 创建异步引擎
async_engine = create_async_engine(
    Base_URL,
    echo=True,
    pool_size=10,  # 允许活跃的连接数
    max_overflow=20,  # 额外的连接数
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session  # yield返回session,注意和return区别,返回数据库会话给路由处理函数
            await session.commit()  # 提交事务
        except Exception:
            await session.rollback()  # 有异常回滚
            raise
        finally:
            await session.close()  # 关闭会话

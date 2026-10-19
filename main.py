from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, Select, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()


# 请求体对参数的类型注解
class User(BaseModel):
    Username: str = Field(default="张三", min_length=2, max_length=10)
    PassWord: str = Field(min_length=3, max_length=20)


# 多个中间件的代码流程，客户端发请求 -》中间件2 -》中间件1 -》服务端 ，服务端响应 -》中间件1 -》中间件2 -》客户端
# 使用场景：所有接口都要执行的代码使用中间件，如权限，跨域
@app.middleware("http")
async def middleware1(request, call_next):
    print("中间件1:start")
    respones = await call_next(request)
    print("中间件1: end")
    return respones


@app.middleware("http")
async def middleware2(request, call_next):
    print("中间件2:start")
    respones = await call_next(request)
    print("中间件2: end")
    return respones


@app.get("/")
def home():
    return {"welcome to go Home"}


@app.get("/items/{item_id}")
async def get_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/items")
def create_item(user: User):
    return {"message": "创建成功", "User": user}


# get路径添加类型注解
@app.get("/book/{id}")
async def get_book(id: int = Path(..., gt=0, lt=101)):
    return {"id": id, "message": f"这是第{id}本书"}


# 需求 查询新闻 -> skip : 跳过的记录数 ，limit： 返回的记录数
# 查询类型 /news/news_list?skip = xx & limit = xx ,查询的类型注解为query
@app.get("/news/news_list")
async def get_news_list(
    skip: int = Query(0, description="跳过的记录数", lt=100), limit: int = 10
):
    return {"skip": skip, "limit": limit}


# 在装饰器中指定响应类
# 接口 -》 响应 HTML 代码
@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一级标题</h1>"


@app.get("/file")
async def get_file():
    file_path = "./files/cat.jpg"
    return FileResponse(file_path)


class News(BaseModel):
    id: int
    title: str
    content: str


@app.get("/news/{id}", response_model=News)
async def get_new_1(id: int):
    return {"id": id, "title": f"这是第{id}本书", "content": "西游记"}


@app.get("/news")
async def get_news_2(id: int):
    id_list = [1, 2, 3, 4, 5, 6]
    if id in id_list:
        return {"id": id}
    else:
        raise HTTPException(status_code=404, detail="新闻不存在")


# 使用依赖注入，重用重复的代码或者请求参数
async def common_paramters(
    skip: int = Query(default=0, le=10), limit: int = Query(default=10)
):
    return {"skip": skip, "limit": limit}


# 注入依赖项
@app.get("/news/news_list")
async def news_list(common: Annotated[dict, Depends(common_paramters)]):
    return common


Base_URL = "mysql+aiomysql://root:123456@localhost:3306/fastapi_project?charset=utf8"
# 创建异步引擎
async_engine = create_async_engine(
    Base_URL,
    echo=True,
    pool_size=10,  # 允许活跃的连接数
    max_overflow=20,  # 额外的连接数
)


# 定义模型类：基类 + 表对应的模型类
# 基类所有表共有的属性：创建时间、更新时间，书籍表：id、书名、作者、出版社
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), comment="创建时间"
    )
    updata_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )


# 继承base相当于Book是orm对象
class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍id")
    book_name: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[int] = mapped_column(Integer, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")


# 建表：定义函数建表 -》FastApi 启动的时候调用建表函数
async def create_tables():
    # 获取异步引擎：创建事务 - 建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Base模型类的元数据


@app.on_event("startup")
async def startup_event():
    await create_tables()


# 需求：查询功能的接口：查询图书 -》依赖注入：创建依赖项获取数据库会话
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  # 绑定数据库引擎
    class_=AsyncSession,  # 指定会话类
    expire_on_commit=False,  # 提交后会话不过期，不会重新查询数据库
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


@app.get("/book/books")
async def get_book_list(db: AsyncSession = Depends(get_database)):
    # 数据库查询功能
    result = await db.execute(select(Book))  # result是查询出来的orm结果
    books = result.scalars().all()  # 查询全部条数据
    # books = result.scalars().first() #查询一条数据
    # books = db.get(Book, 5) #按特定的下标数据
    return books


@app.get("/book/get_book/{book_id}")
async def get_book_by_id(book_id: int, db: AsyncSession = Depends(get_database)):
    result = await db.execute(Select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    return book


@app.get("/book")
async def search_book(db: AsyncSession = Depends(get_database)):
    # result = await db.execute(select(Book).where(Book.price >= 40))
    # result = await db.execute(select(Book).where(Book.author.like("余%") & Book.price >= 35))#模糊查询
    id_list = [1, 3, 5, 7]
    result = await db.execute(select(Book).where(Book.id.in_(id_list)))
    books = result.scalars().all()
    return books


# 聚合查询
@app.post("/book/count")
async def get_count(db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(func.max(Book.price)))
    num = result.scalar()  # 提取一个数值 -》 标量值
    return num


@app.get("/book/book_list")
async def get_book_l(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=3, ge=1, le=100),
    db: AsyncSession = Depends(get_database),
):
    skip = (page - 1) * page_size
    # offset跳过的记录数 ， limit 每页的数量
    stmt = select(Book).offset(skip).limit(page_size)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books


# 新增图书信息，用户输入 -》 参数 -》 请求体
# BookEntity      ORM实体（数据库）
# BookCreateInput  新增入参（前端传过来）
# BookUpdateInput  修改入参
# BookOutput       单条查询返回
# BookPageOutput   分页列表返回
class BookCreateSchema(BaseModel):
    id: int
    book_name: str
    author: str
    price: int
    publisher: str


class BookUpdateSchema(BaseModel):
    book_name: str
    author: str
    price: int
    publisher: str


@app.post("/book/add_book")
async def add_book(book: BookCreateSchema, db: AsyncSession = Depends(get_database)):
    # 创建orm对象 -> add -> commit
    book_obj = Book(**book.__dict__)
    db.add(book_obj)
    await db.commit()
    return book


# 修改图书信息
@app.put("/book/update_book/{book_id}")
async def update_book(
    book_id: int, data: BookUpdateSchema, db: AsyncSession = Depends(get_database)
):
    db_book = await db.get(Book, book_id)  # session跟踪这个对话的变化，已经创建orm对象
    if db_book is None:
        raise HTTPException(status_code=404, detail="查无此书")

    db_book.book_name = data.book_name
    db_book.author = data.author
    db_book.price = data.price
    db_book.publisher = data.publisher

    await db.commit()  # 提交的是这个session会话
    return db_book


# 删除图书
@app.delete("/book/delete_book/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_database)):
    # 先查再删 提交
    db_book = await db.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="书籍不存在")

    await db.delete(db_book)
    await db.commit()
    return db_book

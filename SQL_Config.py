from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
Base_URL = "mysql+aiomysql://root:123456@localhost:3306/FastApi_project?charset=utf8"
#创建异步引擎
async_engine = create_async_engine(
    Base_URL,
    echo= True,
    pool_size = 10,#允许活跃的连接数
    max_overflow = 20#额外的连接数
)

#定义模型类：基类 + 表对应的模型类
#基类所有表共有的属性：创建时间、更新时间，书籍表：id、书名、作者、出版社
class Base(DeclarativeBase):
    create_time: Mapped[datatime]




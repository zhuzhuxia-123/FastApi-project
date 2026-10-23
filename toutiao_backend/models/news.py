from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(  # type: ignore
        DateTime, default=datetime.now, comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(  # type: ignore
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class Category(Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="分类id"
    )
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="分类名称"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="排序字段"
    )

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name}, sort_order={self.sort_order})"


class News(Base):
    __tablename__ = "news"

    # 创建索引表：提升查询速度 -> 添加目录
    __table_args__ = (
        # 创建索引
        Index("fk_news_category_id", "category_id"),
        Index("idx_publish_time", "publish_time"),
    )
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="新闻id"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="新闻标题")
    description: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="新闻描述"
    )
    content: Mapped[str] = mapped_column(
        String(2000), nullable=False, comment="新闻内容"
    )
    image: Mapped[str] = mapped_column(
        String(200), nullable=True, comment="新闻图片URL"
    )
    author: Mapped[str] = mapped_column(String(100), nullable=False, comment="新闻作者")
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("news_category.id"), nullable=False, comment="新闻分类id"
    )
    views: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="浏览量"
    )
    publish_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="发布时间"
    )

    def __repr__(self) -> str:
        return f"News(id={self.id}, title={self.title}, description={self.description}, content={self.content}, image={self.image}, author={self.author}, views={self.views}, publish_time={self.publish_time})"

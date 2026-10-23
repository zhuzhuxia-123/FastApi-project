from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(  # type: ignore
        DateTime, default=datetime.now, comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(  # type: ignore
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        Index("username_UNIQUE" , "username"),
        Index("phone_UNIQUE" , "phone")
    )
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="用户id"
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="头像")
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="性别")
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="个人简介")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, comment="手机号")

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, nickname={self.nickname}, avatar={self.avatar}, gender={self.gender}, bio={self.bio}, phone={self.phone})"

class UserToken(Base):
    __tablename__ = "user_token"
    __table_args__ = (
        Index("token_UNIQUE" , "token"),
        Index("fk_user_token_user_idx", "user_id")
    )
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="用户令牌id"
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户id")
    token: Mapped[str] = mapped_column(String(200), nullable=False, comment="访问令牌")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")

    def __repr__(self) -> str:
        return f"UserToken(id={self.id}, user_id={self.user_id}, token={self.token}, expires_at={self.expires_at})"
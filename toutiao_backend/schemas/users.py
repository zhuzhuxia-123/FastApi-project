from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=10)
    password: str = Field(..., min_length=3, max_length=20)


class UserInfoBase(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="昵称")
    avatar: str | None = Field(None, max_length=200, description="头像")
    gender: str | None = Field(None, max_length=10, description="性别")
    bio: str | None = Field(None, max_length=500, description="个人简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True,  # 允许从对象属性创建模型实例
    )


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用别名进行数据填充
        from_attributes=True,  # 允许从对象属性创建模型实例
    )

#更新用户信息
class UserUpdateRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
    gender: str | None = None
    bio: str | None = None
    phone: str | None = None

class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword",description="旧密码")
    new_password: str = Field(..., min_length=3, alias="newPassword",description="新密码")


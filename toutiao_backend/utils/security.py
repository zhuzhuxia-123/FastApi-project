from passlib.context import CryptContext

# 创建密码上下文，指定使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密密码
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 验证密码
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

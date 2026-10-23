from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import news, users
from utils.exception_handlers import register_exception_handlers

app = FastAPI()
#注册全局异常处理器
register_exception_handlers(app)

# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源,开发阶段允许，部署后建议指定域名
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(news.router)
app.include_router(users.router)

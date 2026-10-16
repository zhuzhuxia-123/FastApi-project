from fastapi import FastAPI,Path,Query
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse

app = FastAPI()

#请求体对参数的类型注解
class User (BaseModel):
    Username : str = Field(default="张三",min_length=2,max_length=10)
    PassWord : str = Field(min_length=3 , max_length=20)

@app.get("/")
def home():
    return {"welcome to go Home"}

@app.get("/items/{item_id}")
async def get_item(item_id : int , q : str | None = None):
     return {"item_id": item_id, "q": q}

@app.post("/items")
def create_item(user : User):
    return {"message" : "创建成功" , "User" : user}

#get路径添加类型注解
@app.get("/book/{id}")
async def get_book(id : int = Path(... , gt = 0 , lt = 101)):
    return {"id": id , "message": f"这是第{id}本书"}

#需求 查询新闻 -> skip : 跳过的记录数 ，limit： 返回的记录数
#查询类型 /news/news_list?skip = xx & limit = xx ,查询的类型注解为query
@app.get("/news/news_list")
async def get_news_list(
    skip: int = Query(0,description="跳过的记录数" , lt= 100), 
    limit: int = 10
    ):
    return {"skip": skip , "limit": limit}

#在装饰器中指定响应类
# 接口 -》 响应 HTML 代码
@app.get("/html" , response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一级标题<h1>"

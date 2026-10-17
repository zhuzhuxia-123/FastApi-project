from fastapi import FastAPI,Path,Query,HTTPException,Depends
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse,FileResponse

app = FastAPI()

#请求体对参数的类型注解
class User (BaseModel):
    Username : str = Field(default="张三",min_length=2,max_length=10)
    PassWord : str = Field(min_length=3 , max_length=20)

#多个中间件的代码流程，客户端发请求 -》中间件2 -》中间件1 -》服务端 ，服务端响应 -》中间件1 -》中间件2 -》客户端
#使用场景：所有接口都要执行的代码使用中间件，如权限，跨域
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
    return "<h1>这是一级标题</h1>"

@app.get("/file")
async def get_file():
    file_path = "./files/cat.jpg"
    return FileResponse(file_path)

class News(BaseModel):
    id:int
    title:str
    content:str
@app.get("/news/{id}" , response_model= News)
async def get_news(id: int):
    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content": "西游记"
    }
@app.get("/news")
async def get_news(id:int):
    id_list = [1,2,3,4,5,6]
    if id in id_list:
        return {"id": id}
    else:
        raise HTTPException(status_code= 404,detail="新闻不存在")

#使用依赖注入，重用重复的代码或者请求参数
async def common_paramters(
        skip: int = Query(default= 0, le= 10),
        limit: int = Query(default= 10)
):
    return {"skip": skip, "limit": limit}

#注入依赖项
@app.get("/news/news_list")
async def news_list(common = Depends(common_paramters)):
    return common

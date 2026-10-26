import json
from typing import Any

import redis.asyncio as redis

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = "123456"
# 创建redis连接对象
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD,decode_responses=True)

#读取字符串
async def get_cache(key: str):
    """获取缓存"""
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None

#读取列表或者字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data) # 反序列化：将JSON字符串转换为Python对象
        else:
            return None
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None

async def set_cache(key: str, value: Any, expire: int = 60 * 60 * 24):
    """设置缓存"""
    try:
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value,ensure_ascii=False)#序列化: 将数据转换为JSON字符串
        await redis_client.set(key, value, expire)
    except Exception as e:
        print(f"设置缓存失败: {e}")

async def delete_cache(key: str):
    """删除缓存"""
    return await redis_client.delete(key)

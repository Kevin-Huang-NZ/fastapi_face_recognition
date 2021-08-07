# 人脸识别后台API原型
## 功能
1. 维护已知人脸信息
2. 分组查询、缓存人脸信息列表
3. 上传图片，识别是否有已知的人

## 代码说明

- api接口：使用[tiangolo/fastapi](https://github.com/tiangolo/fastapi)搭建open api
- 人脸识别：使用了[ageitgey/face_recognition](https://github.com/ageitgey/face_recognition)
- 缓存使用Redis，操作redis使用[aio-libs/aioredis-py](https://github.com/aio-libs/aioredis-py)


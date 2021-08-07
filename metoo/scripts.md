# alembic 命令
## 生成版本文件
    alembic revision --autogenerate -m "xxxxx"
## 将数据库升级到最新版本。
    alembic upgrade head
## 将数据库降级到最初版本。
    alembic downgrade base
## 将数据库升级到指定版本。
    alembic upgrade <version>
## 将数据库降级到指定版本。
    alembic downgrade <version>
## 相对升级，将数据库升级到当前版本后的两个版本。
    alembic upgrade +2
## 相对降级，将数据库降级到当前版本前的两个版本。
    alembic downgrade +2
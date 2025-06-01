from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from openai import OpenAI

app = FastAPI()

origins = [
    "http://localhost:8001",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据库连接配置
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='114514',
        db='db_test',
        cursorclass=pymysql.cursors.DictCursor
    )


# 查询 user_accounts 表
def get_user_accounts(search=None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_accounts"
            if search:
                sql += f" WHERE user_name LIKE '%{search}%'"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


#编写一个函数可以访问硅基流动的大模型api,使用OpenAI的模块
@app.get("/chat")
def chat_with_api(prompt):
    client = OpenAI(
        base_url='https://api.siliconflow.cn/v1',
        api_key='sk-diihbejqkjogqdvjipgbiiewmnwompshmnysafdztsooiabu'
    )
    # 发送带有流式输出的请求
    response = client.chat.completions.create(
        model="Qwen/Qwen3-32B",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content


@app.get("/user_info")
def read_user_account(username: str):
    data = str(read_user_accounts(username))
    data += "\n 根据上述数据生成100字以内的综合描述"
    print(data)
    return {"data": [chat_with_api(data)]}



@app.get("/user_accounts")
def read_user_accounts(search: str = None):
    users = get_user_accounts(search)
    return {"data": users}

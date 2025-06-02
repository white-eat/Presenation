import json
import traceback
import os
import pandas as pd
import plotly
import plotly.express as px
import pymysql
import requests  # 用于调用大模型API
import flask
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置一个安全密钥用于session加密

# 大模型API配置
API_KEY = "sk-diihbejqkjogqdvjipgbiiewmnwompshmnysafdztsooiabu"  # 硅基流动API密钥
MODEL_NAME = "Qwen/Qwen3-32B"  # 硅基流动模型名称
BASE_URL = "https://api.siliconflow.cn/v1"

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='114514',
        db='db_test',
        charset='utf8mb4',
        auth_plugin_map={'mysql_native_password': None},
        cursorclass=pymysql.cursors.DictCursor
    )

@app.before_request
def check_login():
    if request.endpoint in ['login', 'register', 'chat', 'chat_api']:
        return
    if 'user_tokens' not in session:
        return redirect('/login')
    if request.endpoint in ['insert'] and session['user_tokens'] != "ADMIN":
        return redirect('/403')

@app.route('/403')
def forbidden():
    return render_template('403.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users '
                           'WHERE username = %s AND '
                           'password = %s', (username, password))
            user = cursor.fetchone()
        if user is not None:
            session['user_tokens'] = user['tokens']
            # 检查用户是否为管理员
            if user['tokens'] == "ADMIN":
                session['user_role'] = "ADMIN"
            return redirect('/')
        else:
            return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html', 
                           username=request.args.get('username', ''),
                           password=request.args.get('password', ''))

@app.route('/logout')
def logout():
    session.pop('user_tokens', None)
    return redirect('/login')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('确认密码',
                                      validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO users (username, password, tokens) VALUES (%s, %s,"GUEST")',
                           (form.username.data, form.password.data))
            conn.commit()
        session['user_tokens'] = "GUEST"
        return redirect(url_for('login', username=form.username.data, password=form.password.data))
    return render_template('register.html', form=form)

@app.route('/')
@app.route('/list/<int:page_size>/<int:page_num>')
def index(page_size=10, page_num=1):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # 获取总记录数
        cursor.execute('SELECT COUNT(*) as total FROM db_test.user_accounts')
        total_records = cursor.fetchone()['total']

        # 计算总页数
        total_pages = (total_records + page_size - 1) // page_size

        # 获取当前页的数据
        cursor.execute(
            'SELECT * FROM db_test.user_accounts LIMIT %d OFFSET %d' % (int(page_size), page_size * (page_num - 1))
        )
        rows = cursor.fetchall()

    return render_template(
        'index.html',
        rows=rows,
        total_pages=total_pages,
        current_page=page_num,
        page_size=page_size
    )

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    # 检查用户是否为管理员
    if 'user_role' not in session or session['user_role'] != "ADMIN":
        return redirect('/403')
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO db_test.user_accounts (
                user_name, phone_number, id_card_number, account_type, opening_date,
                account_balance, loan_type, loan_amount, loan_date, loan_term,
                loan_channel, repayment_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['user_name'], data['phone_number'], data['id_card_number'],
                data['account_type'], data['opening_date'], float(data['account_balance']),
                data['loan_type'], float(data['loan_amount']), data['loan_date'],
                int(data['loan_term']), data['loan_channel'], data['repayment_status']
            ))
        conn.commit()
        return redirect('/list/10/1')

    return render_template('insert.html')

@app.route('/chart')
def chart():
    type = request.args.get('type')
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT loan_type, COUNT(*) as loan_type_count '
                       'FROM db_test.user_accounts '
                       'GROUP BY loan_type')
        rows = cursor.fetchall()
        labels = [row['loan_type'] for row in rows]
        values = [row['loan_type_count'] for row in rows]

    if type == 'line':
        fig = px.line(x=labels, y=values, color_discrete_sequence=['#636EFA'],
                      title='贷款类型分布统计', labels={'x': '贷款类型', 'y': '用户数量'})
    else:
        with conn.cursor() as cursor:
            cursor.execute('SELECT loan_amount, account_balance FROM user_accounts')
            data = cursor.fetchall()
        pandas_df = pd.DataFrame(data, columns=['loan_amount', 'account_balance'])
        fig = px.box(pandas_df, y=['loan_amount', 'account_balance'],
                     color_discrete_sequence=['#636EFA', '#EF553B'],
                     labels={'loan_amount': '贷款余额', 'account_balance': '账户余额',
                             'value': '金额', 'variable': '指标'})
        fig.update_traces(quartilemethod="exclusive")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('chart.html',
                           graphJSON=graphJSON
                           )

@app.route('/chat')
def chat():
    user_message = request.args.get('message', '')
    if not user_message:
        return render_template('chat.html')
    
    response = chat_with_large_model(user_message)
    return response

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return flask.jsonify({"error": "缺少消息内容"}), 400
    
    try:
        response = chat_with_large_model(user_message)
        return flask.jsonify({"reply": response})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

def get_user_info(user_name):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(f'SELECT * '
                       f'FROM db_test.user_accounts '
                       f'WHERE user_name LIKE "%{user_name}%" '
                       f'OR id_card_number LIKE "%{user_name}%" '
                       f'OR phone_number LIKE "%{user_name}%"')
        rows = cursor.fetchall()
    return str(rows)

def chat_with_large_model(message, history=None):
    if history is None:
        history = []
    
    if not message:
        return "请提供您的问题"
    
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        messages = []
        for user_msg, ai_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": ai_msg})
        
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": MODEL_NAME,
            "messages": messages,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_user_info",
                        "description": "获取用户贷款信息",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_name": {
                                    "type": "string",
                                    "description": "用户姓名"
                                }
                            },
                            "required": ["user_name"]
                        }
                    }
                }
            ]
        }

        response = requests.post(f"{BASE_URL}/chat/completions",
                                  json=data,
                                  headers=headers)
        response.raise_for_status()

        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            choice = response_json['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                model_response = choice['message']['content']
                
                if 'tool_calls' in choice['message']:
                    calls = choice['message']['tool_calls']
                    for call in calls:
                        if call['type'] == 'function' and call['function']['name'] == 'get_user_info':
                            json_args = json.loads(call['function']['arguments'])
                            user_info = get_user_info(json_args['user_name'])
                            model_response += f"\n用户信息: {user_info}"
                
                return model_response
            else:
                return "模型回复中缺少内容字段"
        else:
            return "无法从大模型获取有效回复"

    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return f"调用大模型时发生错误: {str(e)}"
    except (KeyError, IndexError, ValueError, json.JSONDecodeError) as e:
        return f"处理大模型响应时发生错误: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=1145)
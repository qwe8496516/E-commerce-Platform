from flask import Flask
from flask import render_template,redirect,url_for
from flask import request
import random
import psycopg2

app = Flask(__name__)

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/',methods=['POST'])
def home():
    if(request.method == 'POST'):
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        x = random.randint(111111111,999999999)
        start = chr(random.randint(ord('A'), ord('Z')))
        print
        x = str(x)
        x = start + x
        # data = "Insert into members values('{}','{}','{}','{}','{}','{}','{}');".format(x,request.form.get('name')   # 顯示要先改資料庫的東西
        #                                                                         ,request.form.get('my_phone'),request.form.get('email')
        #                                                                         ,request.form.get('sex'),request.form.get('address')
        #                                                                         ,request.form.get('password'))
        # cur = conn.cursor()
        # cur.execute(data)
    return render_template("login.html") + """<script>alert("註冊成功")</script>"""   
    


@app.route('/home', methods=['POST'])
def success():
    conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
    data = "SELECT m_phone,m_pass from members where m_phone = '{}' AND m_pass = '{}';".format(request.form.get('my_phone'),request.form.get('password'))
    cur = conn.cursor()
    cur.execute(data)
    rows = cur.fetchall()
    if(rows == []):
        return redirect('/')
    else:
        return render_template('home.html',username = request.form.get('my_phone')) + """<script>alert(" 登入成功 ")</script>"""
    


@app.route('/register')
def register():
    return render_template("register.html")

if __name__ == '__main__':
    app.run(host = '127.0.0.1',port = 5000,debug = True)
from flask import Flask, flash
from flask import render_template,redirect,url_for
from flask import request
import random
from os import urandom
import psycopg2


app = Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
app.config['SECRET_KEY']=urandom(24)

@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html")
    elif request.method=='POST':
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "SELECT m_phone,m_pass from members where m_phone = '{}' AND m_pass = '{}';".format(request.form.get('my_phone'),request.form.get('password'))
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        if(rows == []):
            # 失敗
            return render_template("login.html",error=True)
        else:
            # 成功
            flash('登入成功')
            return redirect('/home')


@app.route('/home/')
def success():
    return render_template('home.html')

@app.route('/home/seller/')
def shoppingcart():
    return render_template('seller.html')

@app.route('/home/customer/')
def customer():
    return render_template('customer.html')

@app.route('/home/cart/')
def cart():
    return render_template('cart.html')

@app.route('/home/customer/book/')
def book():
    return render_template('book.html')

@app.route('/home/customer/cd/')
def cd():
    return render_template('cd.html')



@app.route('/register/',methods=['GET','POST'])
def reg():
    if request.method=='GET':
        return render_template('register.html')
    elif request.method == 'POST':
        print(request.form.get('name'))
        print(request.form.get('phone'))
        print(request.form.get('email'))
        print(request.form.get('password'))
        print(request.form.get('address'))
        print(request.form.get('gender'))



        # conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        # x = random.randint(111111111,999999999)
        # start = chr(random.randint(ord('A'), ord('Z')))
        # print
        # x = str(x)
        # x = start + x
        # data = "Insert into members values('{}','{}','{}','{}','{}','{}','{}');".format(x,request.form.get('name')   # 顯示要先改資料庫的東西
        #                                                                         ,request.form.get('my_phone'),request.form.get('email')
        #                                                                         ,request.form.get('sex'),request.form.get('address')
        #                                                                         ,request.form.get('password'))
        # cur = conn.cursor()
        # cur.execute(data)
        return redirect('/')   

    





# @app.route('/register')
# def register():
#     return render_template("register.html")

if __name__ == '__main__':
    app.run(host = '127.0.0.1',port = 5000,debug = True)
import datetime
from flask import Flask, flash, session
from flask import render_template,redirect,url_for
from flask import request
import random
from os import urandom
import psycopg2


app = Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
app.config['SECRET_KEY']=urandom(24)


def generateId():
    id = random.randint(111111111,999999999)
    start = chr(random.randint(ord('A'), ord('Z')))
    id = str(id)
    id = start + id
    return id

def generateProductId():
    id = random.randint(11111,99999)
    start = ''
    for i in range(5):
        start = start + chr(random.randint(ord('A'), ord('Z')))
    id = str(id)
    id = start + id
    return id

def generateCartId(ch):
    start = ''
    if(ch == 'customer'):
        for i in range(3):
            start = start + chr(random.randint(ord('A'), ord('Z')))
        id = random.randint(1111111,9999999)
        id = str(id)
        id = start + id
    else:
        id = random.randint(1111111,9999999)
        id = str(id)
        for i in range(3):
            start = chr(random.randint(ord('A'), ord('Z'))) + start
        id = id + start
    return id


def generateOrderId():
    start = ''
    id = random.randint(111,999)
    id = str(id)
    for i in range(7):
        start = start + chr(random.randint(ord('A'), ord('Z')))
    id = start + id
    return id


@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html")
    elif request.method=='POST':
        if(request.form.get('my_phone') == 'username' and request.form.get('password') == 'username'):
            return redirect(url_for('.manage'))
        else:
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
                session['my_account'] = request.form.get('my_phone') # 保存手機(unique)資訊
                return redirect('/home/')


@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        phone =request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        checkpassword = request.form.get('password_vetify')
        address = request.form.get('address')
        gender = request.form.get('gender')
        if(gender == None):
            gender = ''
        if (password == checkpassword):
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            id = generateId()
            cart_id = generateCartId('customer')
            list_id = generateCartId('seller')
            data = "select m_id,list_id,cart_id from members,customer,seller where m_id = '{}' OR list_id = '{}' OR cart_id = '{}';".format(id,list_id,cart_id)
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
    
            while(rows != []): # 如果不是空值代表重複要重新輸入
                id = generateId()
                cart_id = generateCartId('customer')
                list_id = generateCartId('seller')
                data = "select m_id,list_id,cart_id from members,customer,seller where m_id = '{}' OR list_id = '{}' OR cart_id = '{}';".format(id,list_id,cart_id)
                cur = conn.cursor()
                cur.execute(data)   
                rows = cur.fetchall()
                if (rows == []):
                    break
            if(rows == []):
                # 可以註冊
                data = "Insert into members values('{}','{}','{}','{}','{}','{}','{}');Insert into seller values('{}','{}');Insert into customer values('{}','{}');".format(
                    id,name,phone,email,gender,address,password,id,list_id,id,cart_id)
                print(data)
                cur.execute(data)
                conn.commit()                                                     
            return redirect(url_for('.login'))
        #密碼不相同
        else:
            return render_template("register.html",error=True) 


@app.route('/manager/')
def manage():
    conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
    data = "select m_id,m_question from question Order by m_time;"
    cur = conn.cursor()
    cur.execute(data)
    rows = cur.fetchall()
    return render_template('feedback.html',info = rows)


# 首頁
@app.route('/home/')
def success():
    my_account = session.get('my_account',None) # 取得登入帳號
    conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
    data = "select m_id,m_name,list_id,cart_id,m_add from members,customer,seller where m_phone = '{}' AND m_id = s_id AND m_id = c_id".format(my_account)
    cur = conn.cursor()
    cur.execute(data)
    rows = cur.fetchall()
    session['account'] = rows
    return render_template('home.html',info = rows[0][1]) # 傳入顧客的名稱


@app.route('/home/personal/',methods=['POST','GET'])
def person():
    if(request.method == 'GET'):
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        Name = session.get('account',None)
        data = "select * from members where m_id = '{}'".format(Name[0][0])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('personal.html', info = rows)
    else:
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        person = session.get('account',None)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        Name = session.get('account',None)
        data = "Update members set m_name = '{}',m_phone = '{}',m_email = '{}',m_add = '{}' where m_id = '{}';".format(name,phone,email,address,person[0][0])
        cur = conn.cursor()
        cur.execute(data)
        conn.commit()
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        Name = session.get('account',None)
        data = "select * from members where m_id = '{}'".format(Name[0][0])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('personal.html', info = rows)

@app.route('/home/personal/order/',methods=['POST','GET'])
def order():
    if(request.method == 'GET'):
        # 抓取訂單編號
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        person = session.get('account',None)
        data = "select DISTINCT(o_id) from orders where c_id = '{}' order by o_id;".format(person[0][0])
        cur = conn.cursor()
        cur.execute(data)
        orderID = cur.fetchall()
        orderlen = len(orderID)
        # 抓取訂單的商品資訊
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select * from orders where c_id = '{}' AND o_time IN (select max(o_time) from orders);".format(person[0][0])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        sum = 0
        status = 0
        if(rows == []):
            return render_template('order.html',define = 0,person = person[0][1])
        else:
            for row in rows:
                sum += row[7]*row[8]
            row = rows[0][10]
            sum += 100
            if(row == '訂單未完成'):
                status = 1
            else:
                status = 0
            print(status)
            print(row)
            return render_template('order.html',rows = rows,status = status,sum = sum,define = 1)
    else:
        content = request.form.get('button')
        if(content == ' score'):
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select DISTINCT(o_id) from orders where c_id = '{}' order by o_id;".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            orderID = cur.fetchall()
            # 抓取訂單的商品資訊
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from orders where c_id = '{}' AND o_time IN (select max(o_time) from orders);".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            sum = 0
            status = 0
            if(rows == []):
                return render_template('order.html',define = 0,person = person[0][1])
            else:
                for row in rows:
                    sum += row[7]*row[8]
                row = rows[0][10]
                sum += 100
                if(row == '訂單未完成'):
                    status = 1
                else:
                    status = 0
                print(status)
                print(row)
                return render_template('order.html',rows = rows,status = status,sum = sum,define = 1)
        elif(content == 'over'):
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select * from orders where c_id = '{}' AND o_time IN (select max(o_time) from orders);".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            new = cur.fetchall()
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "Update orders set status = '完成訂單' where o_id = '{}'".format(new[0][0])
            cur = conn.cursor()
            cur.execute(data)
            conn.commit()
            # 抓取訂單的商品資訊
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from orders where c_id = '{}' AND o_time IN (select max(o_time) from orders);".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            sum = 0
            status = 0
            if(rows == []):
                return render_template('order.html',define = 0,person = person[0][1])
            else:
                for row in rows:
                    sum += row[7]*row[8]
                row = rows[0][10]
                sum += 100
                if(row == '訂單未完成'):
                    status = 1
                else:
                    status = 0
                print(status)
                print(row)
                return render_template('order.html',rows = rows,status = status,sum = sum,define = 1)
        elif(content == 'back'):
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select * from orders where c_id = '{}' AND o_time IN (select max(o_time) from orders);".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            new = cur.fetchall()
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "Update orders set status = '已退貨' where o_id = '{}'".format(new[0][0])
            cur = conn.cursor()
            cur.execute(data)
            conn.commit()
            # 抓取訂單的商品資訊
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from orders where c_id = '{}' AND o_time IN (select max(o_time) from orders);".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            sum = 0
            status = 0
            if(rows == []):
                return render_template('order.html',define = 0,person = person[0][1])
            else:
                for row in rows:
                    sum += row[7]*row[8]
                row = rows[0][10]
                sum += 100
                if(row == '訂單未完成'):
                    status = 1
                else:
                    status = 0
                print(status)
                print(row)
                return render_template('order.html',rows = rows,status = status,sum = sum,define = 1)
        else:
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select DISTINCT(o_id) from orders where c_id = '{}' order by o_id;".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            orderID = cur.fetchall()
            orderlen = len(orderID)
            # 抓取訂單的商品資訊
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from orders where c_id = '{}' AND o_time IN (select max(o_time) from orders);".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            sum = 0
            status = 0
            if(rows == []):
                return render_template('order.html',define = 0,person = person[0][1])
            else:
                for row in rows:
                    sum += row[7]*row[8]
                row = rows[0][10]
                sum += 100
                if(row == '訂單未完成'):
                    status = 1
                else:
                    status = 0
                print(status)
                print(row)
                return render_template('order.html',rows = rows,status = status,sum = sum,define = 1)


@app.route('/home/personal/change/',methods=['POST','GET'])
def change():
    if(request.method == 'GET'):
        person = session.get('account',None)
        return render_template('change.html',info = person)
    else:
        content = request.form.get('button')
        if(content == 'password'):
            person = session.get('account',None)
            return render_template('change.html',info = person)
        else:
            person = session.get('account',None)
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from members where m_id = '{}';".format(person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            info = rows[0][6]
            password = request.form.get('password')
            passwordcheck = request.form.get('passwordcheck')
            newpassword = request.form.get('newpassword')
            print(info,password,passwordcheck,newpassword)
            if(password == passwordcheck and password == info):
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "Update members set m_pass = '{}' where m_id = '{}';".format(newpassword,person[0][0])
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
                status = 0
                return render_template('change.html',error = status,info = person) + """<script>alert('密碼已更新')</script>"""
            else:
                status = 1
                return render_template('change.html',error = status,info = person)



        
        


@app.route('/home/question/',methods=['POST','GET'])
def question():
    if(request.method == 'GET'):
        Name = session.get('account',None)
        person = Name[0][1]
        return render_template('question.html',info = person)
    elif(request.method == 'POST'):
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        Name = session.get('account',None)
        time =  datetime.datetime.today()
        data = "Insert into question values('{}','{}','{}','{}');".format(Name[0][0],Name[0][1],request.form.get('question'),time)
        cur = conn.cursor()
        cur.execute(data)
        conn.commit()
        person = Name[0][1]
        return render_template('question.html',info = person) + """<script>alert('回報成功')</script>"""


@app.route('/home/seller/',methods=['POST','GET'])
def seller():
    if(request.method == 'GET'):
        account = session.get('account',None)
        print(account)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id Order by p_type".format(account[0][0])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('seller.html',productList = rows,info = account[0][1])
    else:
        content = request.form.get('keywords')
        if(content != None):
            account = session.get('account',None)
            print(account)
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND (p_name LIKE '%{}%' OR p_info LIKE '%{}%') Order by p_type".format(account[0][0],content,content)
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            return render_template('seller.html',productList = rows,info = account[0][1])
        else:
            content = request.form.get('button')
            if(content == None):
                account = session.get('account',None)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id Order by p_type".format(account[0][0])
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('seller.html',productList = rows,info = account[0][1])
            else:
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "Delete from product where p_id = '{}';".format(content)
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
                account = session.get('account',None)
                print(account)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id Order by p_type".format(account[0][0])
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('seller.html',productList = rows,info = account[0][1])


@app.route('/home/seller/sell_cd/',methods=['POST','GET'])
def sellcd():
    if(request.method == 'GET'):
        account = session.get('account',None)
        print(account)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND p_type = 'CD';".format(account[0][0])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('sell_cd.html',info = rows,name = account[0][1])
    else:
        content = request.form.get('keywords')
        if(content != None):
            account = session.get('account',None)
            print(account)
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND (p_name LIKE '%{}%' OR p_info LIKE '%{}%') AND p_type = 'CD';".format(account[0][0],content,content)
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            return render_template('sell_cd.html',info = rows,name = account[0][1])
        else:
            content = request.form.get('button')
            if(content == None):
                account = session.get('account',None)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND p_type = 'CD';".format(account[0][0])
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('sell_cd.html',info = rows,name = account[0][1])
            else:
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "Delete from product where p_id = '{}';".format(content)
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
                account = session.get('account',None)
                print(account)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND p_type = 'CD';".format(account[0][0])
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('sell_cd.html',info = rows,name = account[0][1])


@app.route('/home/seller/sell_book/',methods=['POST','GET'])
def sellbook():
    if(request.method == 'GET'):
        account = session.get('account',None)
        print(account)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND p_type = '書籍';".format(account[0][0])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('sell_book.html',info = rows,name = account[0][1])
    else:
        content = request.form.get('keywords')
        if(content != None):
            account = session.get('account',None)
            print(account)
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND (p_name LIKE '%{}%' OR p_info LIKE '%{}%') AND p_type = '書籍';".format(account[0][0],content,content)
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            return render_template('sell_book.html',info = rows,name = account[0][1])
        else:
            content = request.form.get('button')
            if(content == None):
                account = session.get('account',None)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND p_type = '書籍';".format(account[0][0])
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('sell_book.html',info = rows,name = account[0][1])
            else:
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "Delete from product where p_id = '{}';".format(content)
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
                account = session.get('account',None)
                print(account)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id AND p_type = '書籍';".format(account[0][0])
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('sell_book.html',info = rows,name = account[0][1])


@app.route('/home/seller/new_product/',methods = ['POST','GET'])
def addproduct():
    if(request.method == 'POST'):
        account = session.get('account',None)
        pname = request.form.get('pname')
        pprice = request.form.get('pprice')
        pnum = request.form.get('pnum')
        pinfo = request.form.get('pinfo')
        ptype = request.form.get('ptype')
        print(account)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        while(True):
            pid = generateProductId()
            data = "select p_id from product where p_id = '{}';".format(pid)
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            if(rows == []):
                break
        if(pprice.isdigit() and pnum.isdigit()):
            data = "Insert into product values('{}','{}','{}',{},{},{},'{}','{}')".format(pid,account[0][2],pname,pprice,pnum,5.0,pinfo,ptype)
            print(data)
            cur = conn.cursor()
            cur.execute(data)
            conn.commit()
            return redirect(url_for('.seller'))
        else:
            return render_template('new_product.html',error=True,name = account[0])
    else:
        account = session.get('account',None)
        return render_template('new_product.html',name = account[0][1])


@app.route('/home/customer/',methods=['POST','GET'])
def customer():
    if(request.method == 'GET'):
        person = session.get('account',None)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info from product,members,seller where product.list_id = seller.list_id AND seller.s_id = m_id;"
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('customer.html',relative = rows,person = person[0][0],name = person[0][1])
    elif(request.method == 'POST'):
        pid = request.form.get('button')
        purchaseNum = request.form.get(pid)
        if(pid == None and purchaseNum == None):
            keyword = request.form.get('keywords')
            if(keyword == ''):
                person = session.get('account',None)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where product.list_id = seller.list_id AND seller.s_id = m_id;"
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('customer.html',relative = rows,person = person[0][0],name = person[0][1])
            else:
                person = session.get('account',None)
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product where p_name LIKE '%{}%' OR p_info LIKE '%{}%';".format(keyword,keyword)
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('customer.html',relative = rows,person = person[0][0],name = person[0][1])
        else:
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where product.list_id = seller.list_id AND seller.s_id = m_id;"
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            person = session.get('account',None)
            print(person)
            p_id = request.form.get('button')
            purchaseNum = request.form.get(p_id)
            data = "select p_id,p_name,p_price,p_num from product where p_id = '{}';".format(p_id)
            cur = conn.cursor()
            cur.execute(data)
            pinfo = cur.fetchall()
            data = "select p_id,cart_id from shoppingcart where p_id = '{}' AND cart_id = '{}';".format(p_id,person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            info = cur.fetchall()
            print(pinfo)
            if(info == []):
                data = "Insert into shoppingcart values('{}','{}','{}',{},{},{});".format(p_id,person[0][3],pinfo[0][1],pinfo[0][2],pinfo[0][3],purchaseNum)
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
                return render_template('customer.html',relative = rows,person = person[0][0],name = person[0][1]) + """<script>alert('已將商品加入購物車')</script>"""
            else:
                return render_template('customer.html',relative = rows,person = person[0][0],name = person[0][1]) + """<script>alert('商品重複加入購物車請至購物車內調整購買數量')</script>"""


@app.route('/home/customer/book/',methods=['POST','GET'])
def book():
    if(request.method == 'GET'):
        person = session.get('account',None)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = '書籍' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('book.html',info = rows,name = person[0][1])
    elif(request.method == 'POST'):
        person = session.get('account',None)
        pid = request.form.get('button')
        purchaseNum = request.form.get(pid)
        if(pid == None and purchaseNum == None):
            keyword = request.form.get('keywords')
            if(keyword == ''):
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = '書籍' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('book.html',info = rows,name = person[0][1])
            else:
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product where (p_name LIKE '%{}%' OR p_info LIKE '%{}%') AND p_type = '書籍';".format(keyword,keyword)
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                print(rows)
                if(rows == []):
                    return render_template('book.html',info = rows,name = person[0][1])
                else:
                    return render_template('book.html',info = rows,name = person[0][1])
        else:
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = '書籍' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            person = session.get('account',None)
            p_id = request.form.get('button')
            purchaseNum = request.form.get(p_id)
            data = "select p_id,p_name,p_price,p_num from product where p_id = '{}';".format(p_id)
            cur = conn.cursor()
            cur.execute(data)
            pinfo = cur.fetchall()
            data = "select p_id,cart_id from shoppingcart where p_id = '{}' AND cart_id = '{}';".format(p_id,person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            info = cur.fetchall()
            print(pinfo)
            if(info == []):
                data = "Insert into shoppingcart values('{}','{}','{}',{},{},{});".format(p_id,person[0][3],pinfo[0][1],pinfo[0][2],pinfo[0][3],purchaseNum)
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
                return render_template('book.html',info = rows,name = person[0][1]) + """<script>alert('已將商品加入購物車')</script>"""
            else:
                return render_template('book.html',info = rows,name = person[0][1]) + """<script>alert('商品重複加入購物車請至購物車內調整購買數量')</script>"""
    

@app.route('/home/customer/cd/',methods=['POST','GET'])
def cd():
    if(request.method == 'GET'):
        person = session.get('account',None)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = 'CD' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('cd.html',info = rows,name = person[0][1])
    elif(request.method == 'POST'):
        person = session.get('account',None)
        pid = request.form.get('button')
        purchaseNum = request.form.get(pid)
        if(pid == None and purchaseNum == None):
            keyword = request.form.get('keywords')
            if(keyword == ''):
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = 'CD' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()
                return render_template('cd.html',info = rows,name = person[0][1])
            else:
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from product where (p_name LIKE '%{}%' OR p_info LIKE '%{}%') AND p_type = 'CD';".format(keyword,keyword)
                cur = conn.cursor()
                cur.execute(data)
                rows = cur.fetchall()   
                if(rows == []):
                    return render_template('cd.html',info = rows,name = person[0][1])
                else:
                    return render_template('cd.html',info = rows,name = person[0][1])
        else:
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = 'CD' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            person = session.get('account',None)
            print(person)
            p_id = request.form.get('button')
            purchaseNum = request.form.get(p_id)
            data = "select p_id,p_name,p_price,p_num from product where p_id = '{}';".format(p_id)
            cur = conn.cursor()
            cur.execute(data)
            pinfo = cur.fetchall()
            data = "select p_id,cart_id from shoppingcart where p_id = '{}' AND cart_id = '{}';".format(p_id,person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            info = cur.fetchall()
            print(pinfo)
            if(info == []):
                data = "Insert into shoppingcart values('{}','{}','{}',{},{});".format(p_id,person[0][3],pinfo[0][1],pinfo[0][2],pinfo[0][3],purchaseNum)
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
                return render_template('cd.html',info = rows,name = person[0][1]) + """<script>alert('已將商品加入購物車')</script>"""
            else:
                return render_template('cd.html',info = rows,name = person[0][1]) + """<script>alert('商品重複加入購物車請至購物車內調整購買數量')</script>"""


@app.route('/home/cart/',methods=['GET','POST'])
def cart():
    if(request.method == 'GET'):
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        person = session.get('account',None)
        data = "select * from shoppingcart where cart_id = '{}';".format(person[0][3])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        name = person[0][1]
        if(rows == []):
            sum = 0
            return render_template('cart.html',info = rows,all = sum, person = name)
        else:
            sum = 0
            for row in rows:
                sum += row[3]*row[5]
            name = person[0][1]
            return render_template('cart.html',info = rows,all = sum, person = name)
    elif(request.method == 'POST'):
        define = request.form.get('button') # 決定要做哪一個button
        # print(define)
        if(define == 'update'): #更新
            person = session.get('account',None)
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select * from shoppingcart where cart_id = '{}';".format(person[0][3])
            print(data)
            cur = conn.cursor()
            cur.execute(data)
            p_ids = cur.fetchall()
            print(p_ids)
            for p_id in p_ids:
                updateNum = request.form.get(p_id[0])
                # print(p_id[0])
                # print(updateNum)
                data = "Update shoppingcart set cart_num = '{}' where p_id = '{}';".format(updateNum,p_id[0])
                print(data)
                cur = conn.cursor()
                cur.execute(data)
                conn.commit()
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select * from shoppingcart where cart_id = '{}';".format(person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            name = person[0][1]
            rows = cur.fetchall()
            sum = 0
            for row in rows:
                sum += row[3]*row[5]
            return render_template('cart.html',info = rows,all = sum, person = name)
        elif(define == 'submit'):
            return redirect(url_for('.address'))
        else: # 刪除商品
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "delete from shoppingcart where p_id = '{}';".format(define)
            cur = conn.cursor()
            cur.execute(data)
            conn.commit()
            name = person[0][1]
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select * from shoppingcart where cart_id = '{}';".format(person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            sum = 0
            for row in rows:
                sum += row[3]*row[5]
            
            return render_template('cart.html',info = rows,all = sum, person = name)


@app.route('/home/cart/address/',methods=['GET','POST'])
def address():
    if(request.method == 'GET'):
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        person = session.get('account',None)
        address = person[0][4]
        data = "select * from shoppingcart where cart_id = '{}';".format(person[0][3])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        sum = 0
        for row in rows:
            sum += row[3]*row[5]
        sum += 100
        return render_template('address.html',info = rows,all = sum,add = address,name = person[0][1])
    else:
        content = request.form.get('button')
        if(content == 'submit'):
            # 將購物車裡的商品都撈出來
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select * from shoppingcart where cart_id = '{}' order by p_id;".format(person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            products = cur.fetchall()
            #計算商品總額
            sum = 0
            for product in products:
                sum += product[3]*product[5]
            sum += 100
            # 獲取所有賣家的名稱跟 ID
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "select m_id,m_name,p_id from members,seller,product where m_id = s_id AND seller.list_id = product.list_id AND p_id IN (select p_id from shoppingcart where cart_id = '{}') order by p_id;".format(person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            sellerinfos = cur.fetchall()
            # 生成隨機訂單ID
            orderID = ''
            while(True):
                orderID = generateOrderId()
                conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                data = "select * from generate where o_id = '{}';".format(orderID)
                cur = conn.cursor()
                cur.execute(data)
                orderconfirm = cur.fetchall()
                if(orderconfirm == []):
                    break
            # 將訂單資訊放入 generate 中
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "Insert into generate values('{}','{}','{}')".format(orderID,person[0][3],person[0][4])
            print(data)
            cur = conn.cursor()
            cur.execute(data)
            conn.commit()
            # 生成訂單
            print(orderID,sellerinfos[0][0],sellerinfos[0][1],person[0][0],person[0][1],products[0][0],products[0][2],products[0][3],products[0][5],person[0][4])
            time = datetime.datetime.today()
            for product in products:
                for sellerinfo in sellerinfos:
                    if(sellerinfo[2] == product[0]):
                        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
                        data = "Insert into orders values('{}','{}','{}','{}','{}','{}','{}',{},{},'{}','{}','{}');".format(orderID,sellerinfo[0],sellerinfo[1],person[0][0],person[0][1],product[0],product[2],product[3],product[5],person[0][4],'訂單未完成',time)
                        print(data)
                        cur = conn.cursor()
                        cur.execute(data)
                        conn.commit()
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            data = "Delete from shoppingcart where cart_id = '{}';".format(person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            conn.commit()
            return redirect(url_for('.success'))
        else:
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            address = request.form.get('address')
            print(address)
            data = "Update members set m_add ='{}' where m_id = '{}';".format(address,person[0][0])
            cur = conn.cursor()
            cur.execute(data)
            conn.commit()
            conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
            person = session.get('account',None)
            data = "select * from shoppingcart where cart_id = '{}';".format(person[0][3])
            cur = conn.cursor()
            cur.execute(data)
            rows = cur.fetchall()
            sum = 0
            for row in rows:
                sum += row[3]*row[5]
            sum += 100
            return render_template('address.html',info = rows,all = sum,add = address,name = person[0][1])

if __name__ == '__main__':
    app.run(host = '127.0.0.1',port = 5000,debug = True)
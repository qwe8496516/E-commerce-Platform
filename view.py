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
            start = start + chr(random.randint(ord('A'), ord('Z')))
        id = id + start
    return id



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
            session['my_account'] = request.form.get('my_phone') # 保存手機(unique)資訊
            return redirect('/home/')

# 首頁
@app.route('/home/')
def success():
    my_account = session.get('my_account',None) # 取得登入帳號
    conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
    data = "select m_id,m_name,list_id,cart_id from members,customer,seller where m_phone = '{}' AND m_id = s_id AND m_id = c_id".format(my_account)
    cur = conn.cursor()
    cur.execute(data)
    rows = cur.fetchall()
    session['account'] = rows
    row = rows[0][1]
    # print(rows)
    # print(row)
    return render_template('home.html',username = row) # 傳入顧客的名稱

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
        return render_template('seller.html',productList = rows)
    else:
        account = session.get('account',None)
        print(account)
        conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
        data = "select * from product,seller where s_id = '{}' AND seller.list_id = product.list_id Order by p_type".format(account[0][0])
        cur = conn.cursor()
        cur.execute(data)
        rows = cur.fetchall()
        return render_template('seller.html',productList = rows)



@app.route('/home/customer/')
def customer():
    return render_template('customer.html')

@app.route('/home/cart/')
def cart():
    return render_template('cart.html')

@app.route('/home/customer/book/')
def book():
    conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
    data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = '書籍' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
    cur = conn.cursor()
    cur.execute(data)
    rows = cur.fetchall()
    return render_template('book.html',info = rows)

@app.route('/home/customer/cd/')
def cd():
    conn = psycopg2.connect(database="Database_Topic", user="postgres", password="123456789", host="127.0.0.1", port="5432")
    data = "select p_id,product.list_id,m_name,p_name,p_price,p_num,p_star,p_info,p_type from product,members,seller where p_type = 'CD' AND product.list_id = seller.list_id AND seller.s_id = m_id;"
    cur = conn.cursor()
    cur.execute(data)
    rows = cur.fetchall()
    return render_template('cd.html',info = rows)



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
            return redirect(url_for('.seller'))
        #密碼不相同
        else:
            return render_template("register.html",error=True) 

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
            return render_template('new_product.html',error=True)
    else:
        return render_template('new_product.html')



if __name__ == '__main__':
    app.run(host = '127.0.0.1',port = 5000,debug = True)
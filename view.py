from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html")



# @app.route('/login',methods = ['post'])
# def result():
#     if(request.method == 'POST'):
#         user = request.values['user']
#         return render_template('result.html',name = user)

if __name__ == '__main__':
    debug = True
    app.run(host = '127.0.0.1',port = 5000)

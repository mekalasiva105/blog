from flask import Flask,render_template,request,url_for,redirect,flash,session
import mysql.connector
from cmail import sendmail
from otp import genotp
app=Flask(__name__)
app.config['SECRET_KEY'] = "my super key that no one is supposed to know"
mydb = mysql.connector.connect(host='localhost',user='root',password='system',db='blog')
with mysql.connector.connect(host='localhost',user='root',password='system',db='blog'):
    cursor = mydb.cursor(buffered=True)
    cursor.execute('create table if not exists registration(username varchar(50) primary key,mobile varchar(50),email varchar(50),address varchar(50),password varchar(20))')
mycursor = mydb.cursor()
@app.route('/regform',methods=['GET','POST'])
def reg():
    if request.method=='POST':
        username=request.form.get('name')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        address=request.form.get('address')
        password=request.form.get('password')
        otp=genotp()
        sendmail(to=email,subject="thanks for registration",body=f'otp is :{otp}')
        return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)
    return render_template('registration.html')
@app.route('/otp/<username>/<mobile>/<email>/<address>/<password>/<otp>',methods=['GET','POST'])
def otp(username,mobile,email,address,password,otp):
    if request.method=='POST':
        uotp = request.form['uotp']
        if otp==uotp:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('insert into registration values(%s,%s,%s,%s,%s)',[username,mobile,email,address,password])
            mydb.commit()
            cursor.close()
            return redirect(url_for('log'))
    return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)    
@app.route('/login',methods=['GET','POST'])
def log():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select count(*) from registration where username=%s && password=%s',[username,password])
        data = cursor.fetchone()[0]
        if data == 1:
            session['username']=username
            if not session.get(session['username']):
                session[session['username']]={}
            return redirect(url_for('home'))
        else:
            return 'Invalid Username and Password'
    return render_template('login.html')
@app.route('/logout',methods=['GET','POST'])
def logout():
    return redirect(url_for('log'))
@app.route('/')
def home():
    return render_template('homepage.html')
@app.route('/addpost',methods=['GET','POST'])
def add_post():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor = mydb.cursor(buffered=True)
        cursor.execute('insert into posts(title,content,slug) values(%s,%s,%s)',(title,content,slug))
        mydb.commit()
        cursor.close()
    return render_template('add_post.html')
@app.route('/view_posts')
def view_post():
    with mydb.cursor() as cursor:
        cursor.execute('SELECT * FROM posts')
        posts = cursor.fetchall()
    return render_template('view_posts.html',posts=posts)
@app.route('/delete_post/<int:id>',methods=['POST'])
def delete_post(id):
    cursor = mydb.cursor(buffered=True)
    cursor.execute('select * from posts where id=%s',(id,))
    post = cursor.fetchone()
    cursor.execute('DELETE from posts where id=%s',(id,))
    mydb.commit()
    cursor.close()
    return redirect(url_for('view_post'))
@app.route('/update_post/<int:id>',methods=['GET','POST'])
def update_post(id):
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor = mydb.cursor(buffered=True)
        cursor.execute('UPDATE posts SET title=%s,content=%s,slug=%s WHERE id=%s',(title,content,slug,id))
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_post'))
    else:
        cursor = mydb.cursor(buffered=True)
        cursor.execute('select * from posts where id = %s',(id,))
        post = cursor.fetchone()
        cursor.close()
        return render_template('update.html',post=post)
#admin page
@app.route('/admin')
def admin():
    return render_template('admin.html') 
app.run(debug=True,use_reloader=True)
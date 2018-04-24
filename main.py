from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__) 
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'A3s5g7jdgw'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref= 'owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Blog(db.Model): 

    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')     


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username_error = ''
        password_error = ''

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if user and user.password != password:
            password_error = 'Your password is incorrect'
            return render_template('login.html', username = username, password_error = password_error)
        else:
            username_error = 'Username does not exist'
            return render_template('login.html', username = username, username_error = username_error)
    
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ""
        password_error = ""
        verify_error = ""

        if username == "":
            username_error = "You must enter a username."
            username = ""

        if len(username) < 3:
            username_error = "Please enter a valid username"
            username = ""
            verify = ""

        for char in username:
            if char == " ":
                username_error = "Please enter a valid username."
                username = ""    

        if password == "":
            password_error = "You must enter a password."
            password = ""

        if len(password) < 3:
            password_error = "Please enter a valid password"
            password = ""

        if len(verify) < 3:
            verify_error = "Please enter a valid password"
            verify = ""

        if verify == "":
            verify_error = "Please enter matching passwords"
            verify = ""

        if password != verify:
            verify_error = "Please enter matching passwords"
            verify = ""
            password = ""

        for char in password:
            if char == " ":
                password_error = "Please enter a valid password"
                password = ""  

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                username_error = "That username already exists."
                username = ""
                return render_template('signup.html', username_error=username_error)
            
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost?username={0}'.format(username))

        else:
            return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/signup')
        else:
            return redirect('signup')

    return render_template('signup.html')

    

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.filter_by().order_by(Blog.id.desc()).all()   
    blogid = request.args.get('id')
    if request.method == 'GET':
        if blogid:
            blog = Blog.query.get(blogid)
            return render_template('singlepost.html',title="Post",blog=blog)
    
        else:    
        
            if request.args.get('user'):
                author = request.args.get('user')
                author_filter = User.query.filter_by(username=author).first() 
                owner_id = author_filter.id
                blogs = Blog.query.filter_by(owner_id=owner_id).all()
                return render_template('author.html', blogs=blogs)
     
    return render_template('blog.html',title="Blogz", blogs=blogs)

def input_error(input):
    if input == "":
        return  True


@app.route('/blog?id={{blog.id}}', methods=['POST', 'GET']) 
def singlepost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

    return render_template('singlepost.html',title_error=title,body_error=body)


@app.route('/newpost', methods=['POST', 'GET'])  
def newpost():

    title_error = ""
    body_error = ""

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        newblog = Blog(title, body, owner)  
        

        if input_error(title):
            title_error = "Title Required"
        
        if input_error(body):
            body_error = 'Body Required'

        if not input_error(title) and not input_error(body):
            db.session.add(newblog)
            db.session.commit()
            singlepost = "/blog?id=" + str(newblog.id)
            return redirect(singlepost)
          

    return render_template('newpost.html', title="Add a New Post", 
                             title_error=title_error, 
                             body_error=body_error)


@app.route('/')
def blog():
    list_of_owners = User.query.all()
    return render_template('index.html', owners=list_of_owners)


if __name__ == '__main__': 
    app.run()
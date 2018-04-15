from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__) 
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'A3s5g7jdgw'

#creates blog table in database
class Blog(db.Model): 

    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogid = request.args.get('id')
    if blogid:
        blog = Blog.query.get(blogid)
        return render_template('singlepost.html',title="Post",blog=blog)

  
    blogs = Blog.query.filter_by().order_by(Blog.id.desc()).all()    
    return render_template('blog.html',title="Build-a-blog", blogs=blogs)

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
        newblog = Blog(title, body)  

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
def reroute():
    return redirect('/blog')


if __name__ == '__main__': 
    app.run()
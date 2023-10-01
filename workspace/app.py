from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from models import User, Post
from forms import LoginForm, PostForm
from auth import get_google_provider_cfg, get_token, get_user_info
from database import db
from client import client

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'kissatkoiria123'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
app.config['USE_MOCK_OAUTH'] = os.environ.get('USE_MOCK_OAUTH') or False
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    # Check if the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Redirect logged-in users to the home page
    
    if form.validate_on_submit():
        if app.config['USE_MOCK_OAUTH']:
            user = User.query.filter_by(email='mockuser@gmail.com').first()
            if not user:
                user = User(email='mockuser@gmail.com', name='Mock User', profile_pic='default.jpg')
                db.session.add(user)
                db.session.commit()
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            google_provider_cfg = get_google_provider_cfg()
            authorization_endpoint = google_provider_cfg["authorization_endpoint"]
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=request.base_url + "/callback",
                scope=["openid", "email", "profile"],
            )
            return redirect(request_uri)
    
    # Render the login template with the form and conditional links
    return render_template('login.html', form=form, show_logout_link=False)  # Pass show_logout_link as False

@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    get_token(token_endpoint, code)
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo = get_user_info(userinfo_endpoint)
    user = User.query.filter_by(email=userinfo["email"]).first()
    if not user:
        user = User(email=userinfo["email"], name=userinfo["name"], profile_pic=userinfo["picture"])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)

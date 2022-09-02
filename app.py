import os
from flask import Flask, render_template, request, redirect, jsonify, flash
from flask.helpers import url_for
from flask_wtf.csrf import CSRFProtect
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
import models
from models import db
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('app_secret')
csrf = CSRFProtect(app)

env = os.environ.get("ENV")
if env == 'prod':
    prodURI = os.getenv('DATABASE_URL')
    prodURI = prodURI.replace("postgres://", "postgresql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = prodURI

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///friendflix.sqlite"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) 



with app.app_context():
    db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))




@app.route("/")
def landing():
    return redirect(url_for('login'))

@app.route("/home")
def hello_world():
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    friends = user.follow
    users = db.session.query(models.User).all()
    followers = []
    for person in users:
        if current_user in person.follow:
            followers.append(person)
    return render_template('index.html', d=friends, following = followers, s=current_user.shows, favs = current_user.favorite, watchLater = current_user.watch_later)


@app.route("/edit", methods=["POST"])
def edit():
    file= request.form.get("file", False)
    banner= request.form.get("banner", False)
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    if file:
        user.profile_pic = file
        user.thumbnail = file
    if banner:
        user.banner = banner
    if file or banner:
        db.session.commit()
    return redirect(url_for('hello_world'))

@app.route("/friend<int:friend_id>", methods=["GET"])
def hello_friend(friend_id):
    user =  db.session.query(models.User).filter_by(id = friend_id).first()
    friends = user.follow
    users = db.session.query(models.User).all()
    followers = []
    for person in users:
        if user in person.follow:
            followers.append(person)
    return render_template('friend.html', d=friends, following = followers, s=user.shows, favs = user.favorite, watchLater = user.watch_later, friend=user)

@app.route("/search/user", methods=["POST"])
def search_user():
    name = request.form.get("username", False)
    user =  db.session.query(models.User).filter_by(user_name = name).first()
    if not user:
        return redirect(url_for('hello_world'))
    return redirect(url_for('hello_friend', friend_id = user.id))


@app.route("/add_friend<int:friend_id>", methods=["GET"])
def add_friend(friend_id):
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    friend =  db.session.query(models.User).filter_by(id = friend_id).first()
    user.follow.append(friend)
    db.session.commit()
    return redirect(url_for('hello_friend', friend_id = friend.id))

@app.route("/unfollow<int:friend_id>", methods=["GET"])
def unfollow(friend_id):
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    friend =  db.session.query(models.User).filter_by(id = friend_id).first()
    user.follow.remove(friend)
    db.session.commit()
    return redirect(url_for('hello_friend', friend_id = friend.id))


@app.route("/remove/<int:movie_id>/<type>", methods=["GET"])
def remove(movie_id, type):
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    movie =  db.session.query(models.Entertainment).filter_by(id = movie_id).first()
    if type == 'current':
        user.shows.remove(movie)
        db.session.commit()
    elif type == 'favs':
        user.favorite.remove(movie)
        db.session.commit()
    elif type == 'later':
        user.watch_later.remove(movie)
        db.session.commit()
    return redirect(url_for('hello_world'))

@app.route("/single/<int:movie_id>")
def form(movie_id):
    show_one = db.session.query(models.Entertainment).get(movie_id)
    return render_template('singleMovie.html' , show=show_one)

@app.route('/signUp')
def sign_up():
    return render_template('signup.html')

@app.route("/sign-up", methods=["POST"])
def receive_data():
    name = request.form["username"]
    password = request.form.get('password')
    if name == '' or password == '':
        flash('Please enter both a username and password')
        return render_template('signup.html')

    user_exist = db.session.query(models.User).filter_by(user_name = name).first()
    if user_exist:
        flash('That username is already taken. Try Again.')
        return render_template('signup.html')

    hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
    user = models.User(
        user_name=name,
        password = hash_and_salted_password, 
        profile_pic= 'https://icon-library.com/images/default-profile-icon/default-profile-icon-24.jpg',
        banner = 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80',
        thumbnail = 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80'
        )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('hello_world'))



@app.route('/Login', methods=["POST"])
def login_form():
    user_name = request.form["username"]
    password = request.form["password"]
    user = db.session.query(models.User).filter_by(user_name = user_name).first()
    if user and password != '':
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('hello_world'))
        else:
            flash('Invalid username or password.  Try Again')
    else:
        flash('Invalid username or password.  Try Again')
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/search", methods=["POST"])
def search():

    title = request.form["title"].title()
    show_looking_for = db.session.query(models.Entertainment).filter_by(title = title).first()

    if(show_looking_for == None):
        movie_res  = requests.get(url=f'{os.environ.get("movie_api")}/?apikey={os.environ.get("api_key")}&t={title}')
        movie_data = movie_res.json()

        if movie_data['Response'] == 'False':
            return redirect(url_for('hello_world'))
        else:
            show_looking_for = models.Entertainment(
                title = movie_data['Title'],
                year = movie_data['Year'],
                released = movie_data['Released'],
                runtime = movie_data['Runtime'],
                genre = movie_data['Genre'],
                plot = movie_data['Plot'],
                poster = movie_data['Poster'],
                imdbRating = movie_data['imdbRating'],
                type = movie_data['Type'],
                rated = movie_data['Rated'],
                director = movie_data['Director'],
                awards = movie_data['Awards'],
                actors = movie_data['Actors'],
            )
            db.session.add(show_looking_for)
            db.session.commit()
    
    return render_template('singleMovie.html' , show=show_looking_for)

@app.route('/watching/<int:movie_id>', methods=['POST'])
def watching(movie_id):
    arr = request.form.getlist('current')
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    show_looking_for = db.session.query(models.Entertainment).filter_by(id = movie_id).first()
    if 'watchList' in arr:
        user.shows.append(show_looking_for)
    if 'fav' in arr:
            user.favorite.append(show_looking_for)
    if 'rec' in arr:
            user.watch_later.append(show_looking_for)
    db.session.commit()
    return redirect(url_for('hello_world'))

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)
    app.run(debug=False, host="0.0.0.0", port=port)
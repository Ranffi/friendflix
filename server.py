from flask import Flask, render_template, request, redirect, jsonify, flash
from flask.helpers import url_for
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
import models
import config 

app = Flask(__name__)
app.config['SECRET_KEY'] = config.app_secret
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///friendflix.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))




def seed():
    movies = ['westworld', 'breaking bad', 'altered carbon', 'vikings', 'narcos',]
    banners = [
        'https://images.unsplash.com/photo-1560972550-aba3456b5564?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80',
        'https://images.unsplash.com/photo-1528360983277-13d401cdc186?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80',
        'https://images.unsplash.com/photo-1636277073302-eee456f208a1?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2369&q=80',
        'https://images.unsplash.com/photo-1494633114655-819eb91fde40?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80',
        'https://images.unsplash.com/photo-1439792675105-701e6a4ab6f0?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2373&q=80',
        'https://images.unsplash.com/photo-1542977466-bbacf83cb0b4?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2376&q=80',
        'https://images.unsplash.com/photo-1523712999610-f77fbcfc3843?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80',
        'https://images.unsplash.com/photo-1627716129571-05179673b885?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80'

    ]

    for i in movies:
        movie_res  = requests.get(url=f'{config.movie_api}/?apikey={config.api_key}&t={i}')
        movie_data = movie_res.json()

        show = models.Entertainment(
            title = movie_data['Title'],
            year = movie_data['Year'],
            released = movie_data['Released'],
            runtime = movie_data['Runtime'],
            rated = movie_data['Rated'],
            director = movie_data['Director'],
            awards = movie_data['Awards'],
            actors = movie_data['Actors'],
            genre = movie_data['Genre'],
            plot = movie_data['Plot'],
            poster = movie_data['Poster'],
            imdbRating = movie_data['imdbRating'],
            type = movie_data['Type']
        )
        db.session.add(show)
    user_res = requests.get(url='https://randomuser.me/api/?results=8')
    user_data = user_res.json()
    i = 0
    for person in user_data['results']:
        user = models.User(
            user_name = person['login']['username'],
            thumbnail = person['picture']['thumbnail'],
            banner = banners[i],
            profile_pic = person['picture']['large'],
            password = person['login']['password']
        )
        db.session.add(user)
        i += 1
    db.session.commit()
        

@app.route("/")
def hello_world():
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    friends = user.follow
    users = db.session.query(models.User).all()
    return render_template('index.html', d=friends, s=current_user.shows, favs = current_user.favorite, watchLater = current_user.watch_later)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    file= request.form.get("file", False)
    banner= request.form.get("banner", False)
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    if file:
        user.profile_pic = file
    if banner:
        user.banner = banner
    if file or banner:
        db.session.commit()
    return redirect(url_for('hello_world'))

@app.route("/friend<int:friend_id>", methods=["GET", "POST"])
def hello_friend(friend_id):
    name = request.form.get("username", False)
    user =  db.session.query(models.User).filter_by(id = friend_id).first()
    friends = user.follow
    users = db.session.query(models.User).all()
    return render_template('friend.html', d=current_user.follow, s=user.shows, favs = user.favorite, watchLater = user.watch_later, friend=user)

@app.route("/search/user", methods=["GET", "POST"])
def search_user():
    name = request.form.get("username", False)
    user =  db.session.query(models.User).filter_by(user_name = name).first()
    if not user:
        return redirect(url_for('hello_world'))
    return redirect(url_for('hello_friend', friend_id = user.id))


@app.route("/add_friend<int:friend_id>", methods=["GET", "POST"])
def add_friend(friend_id):
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    friend =  db.session.query(models.User).filter_by(id = friend_id).first()
    user.follow.append(friend)
    db.session.commit()
    return redirect(url_for('hello_friend', friend_id = friend.id))

@app.route("/unfollow<int:friend_id>", methods=["GET", "POST"])
def unfollow(friend_id):
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    friend =  db.session.query(models.User).filter_by(id = friend_id).first()
    user.follow.remove(friend)
    db.session.commit()
    return redirect(url_for('hello_friend', friend_id = friend.id))


@app.route("/remove/<int:movie_id>/<type>", methods=["GET", "POST"])
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
    showOne = db.session.query(models.Entertainment).get(movie_id)
    return render_template('singleMovie.html' , show=showOne)

@app.route('/signUp')
def signUp():
    return render_template('signup.html')

@app.route("/sign-up", methods=["POST"])
def receive_data():
    name = request.form["username"]
    user = models.User(
        user_name=name, 
        profile_pic= 'https://icon-library.com/images/default-profile-icon/default-profile-icon-24.jpg',
        banner = 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80',
        thumbnail = 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2370&q=80'
        )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('hello_world'))



@app.route('/Login', methods=["GET", "POST"])
def Login():
    userName = request.form["username"]
    password = request.form["password"]
    user = db.session.query(models.User).filter_by(user_name = userName).first()
    if user:
        login_user(user)
        return redirect(url_for('hello_world'))
    return render_template('login.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template('login.html')

@app.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/search", methods=["POST"])
def search():

    title = request.form["title"]
    showLookingFor = db.session.query(models.Entertainment).filter_by(title = title).first()

    if(showLookingFor == None):
        movie_res  = requests.get(url=f'{config.movie_api}/?apikey={config.api_key}&t={title}')
        movie_data = movie_res.json()

        if movie_data['Response'] == 'False':
            return redirect(url_for('hello_world'))
        else:
            showLookingFor = models.Entertainment(
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
            db.session.add(showLookingFor)
            db.session.commit()
    
    return render_template('singleMovie.html' , show=showLookingFor)

@app.route('/watching/<int:movie_id>', methods=['POST'])
def watching(movie_id):
    arr = request.form.getlist('current')
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    showLookingFor = db.session.query(models.Entertainment).filter_by(id = movie_id).first()
    if 'watchList' in arr:
        user.shows.append(showLookingFor)
    if 'fav' in arr:
            user.favorite.append(showLookingFor)
    if 'rec' in arr:
            user.watch_later.append(showLookingFor)
    db.session.commit()
    return redirect(url_for('hello_world'))

if __name__ == '__main__':
    # seed()
    app.run(debug=True)
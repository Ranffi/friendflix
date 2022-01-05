from flask import Flask, render_template, request, redirect, jsonify
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
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))




def seed():
    movies = ['westworld', 'breaking bad', 'altered carbon', 'vikings', 'narcos']
    for i in movies:
        movie_res  = requests.get(url=f'{config.movie_api}/?apikey={config.api_key}&t={i}')
        movie_data = movie_res.json()

        show = models.Entertainment(
            title = movie_data['Title'],
            year = movie_data['Year'],
            released = movie_data['Released'],
            runtime = movie_data['Runtime'],
            genre = movie_data['Genre'],
            plot = movie_data['Plot'],
            poster = movie_data['Poster'],
            imdbRating = movie_data['imdbRating'],
            type = movie_data['Type']
        )
        db.session.add(show)
    user_res = requests.get(url='https://randomuser.me/api/?results=8')
    user_data = user_res.json()
    
    for person in user_data['results']:
        user = models.User(
            user_name = person['login']['username'],
            picture = person['picture']['thumbnail'],
            profile_pic = person['picture']['large'],
            password = person['login']['password']
        )
        db.session.add(user)

    db.session.commit()
        

@app.route("/all")
def get_all_cafes():
    # bob =db.session.query(models.User).filter_by(user_name = 'purplebear816').first()
    # show  = db.session.query(models.Entertainment).filter_by(title = 'Vikings').first()
    # show.shows.append(bob)
    # db.session.add(show)
    # db.session.commit()
    users = db.session.query(models.User).all()
    vikings = db.session.query(models.Entertainment).filter_by(title = 'Vikings').first()
    for user in users:
        user.shows.append(vikings)
    db.session.commit()
    return 'yup'

@app.route("/")
def hello_world():
    user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
    friends = user.follow
    users = db.session.query(models.User).all()
    print(friends)
    return render_template('index.html', d=friends, s=current_user.shows)

@app.route("/friend<int:friend_id>", methods=["GET", "POST"])
def hello_friend(friend_id):
    name = request.form.get("username", False)
    user =  db.session.query(models.User).filter_by(id = friend_id).first()
    friends = user.follow
    users = db.session.query(models.User).all()
    print(user)
    return render_template('friend.html', d=current_user.follow, s=user.shows, friend=user)

@app.route("/search/user", methods=["GET", "POST"])
def search_user():
    name = request.form.get("username", False)
    user =  db.session.query(models.User).filter_by(user_name = name).first()
    print(user)
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
    print(user.shows)
    if type == 'current':
        user.shows.remove(movie)
        db.session.commit()
    elif type == 'favs':
        print('favsss')
    # db.session.commit()
    return redirect(url_for('hello_world'))

@app.route("/single/<int:movie_id>")
def form(movie_id):
    showOne = db.session.query(models.Entertainment).get(movie_id)
    return render_template('singleMovie.html' , show=showOne)

@app.route('/signUp')
def signUp():
    return render_template('sillyForm.html')

@app.route("/sign-up", methods=["POST"])
def receive_data():
    name = request.form["username"]
    user = models.User(user_name=name)
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
    # Add friends
    # user1 = db.session.query(models.User).filter_by(user_name = 'happyladybug698').first()
    # user2 = db.session.query(models.User).filter_by(user_name = 'angrysnake216').first()
    # user1.follow.append(user2)
    # print('user 1: ', user1.user_name, ' friends: ', user1.follow)
    # db.session.commit()
    title = request.form["title"]
    showLookingFor = db.session.query(models.Entertainment).filter_by(title = title).first()

    if(showLookingFor == None):
        movie_res  = requests.get(url=f'{config.movie_api}/?apikey={config.api_key}&t={title}')
        movie_data = movie_res.json()

        showLookingFor = models.Entertainment(
            title = movie_data['Title'],
            year = movie_data['Year'],
            released = movie_data['Released'],
            runtime = movie_data['Runtime'],
            genre = movie_data['Genre'],
            plot = movie_data['Plot'],
            poster = movie_data['Poster'],
            imdbRating = movie_data['imdbRating'],
            type = movie_data['Type']
        )
        db.session.add(showLookingFor)
        db.session.commit()
    
    return render_template('singleMovie.html' , show=showLookingFor)

@app.route('/watching/<int:movie_id>', methods=['POST'])
def watching(movie_id):
    arr = request.form.getlist('current')
    print(movie_id)
    if 'watchList' in arr:
        showLookingFor = db.session.query(models.Entertainment).filter_by(id = movie_id).first()
        print(showLookingFor)
        user =  db.session.query(models.User).filter_by(user_name = current_user.user_name).first()
        user.shows.append(showLookingFor)
        print(current_user.shows)
    db.session.commit()
    return redirect(url_for('hello_world'))

#<var_name>
#7ec00cf9 movie apikey

if __name__ == '__main__':
    # seed()
    app.run(debug=True)
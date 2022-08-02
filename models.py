from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


watched = db.Table('watched',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('entertainment_id', db.Integer, db.ForeignKey('entertainment.id'), primary_key=True)
)
fav = db.Table('fav',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('entertainment_id', db.Integer, db.ForeignKey('entertainment.id'), primary_key=True)
)
later = db.Table('later',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('entertainment_id', db.Integer, db.ForeignKey('entertainment.id'), primary_key=True)
)
friends = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)  
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), unique=True)
    thumbnail = db.Column(db.String(2000))
    banner = db.Column(db.String(2000))
    profile_pic= db.Column(db.String(2000))
    friends = db.relationship('User', secondary=friends, backref= 'follow', primaryjoin=id==friends.c.user_id, secondaryjoin=id==friends.c.friend_id)


class Entertainment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    year = db.Column(db.String(200))
    released = db.Column(db.String(200))
    runtime = db.Column(db.String(200))
    rated = db.Column(db.String(200))
    actors = db.Column(db.String(200))
    director = db.Column(db.String(200))
    awards = db.Column(db.String(200))
    genre = db.Column(db.String(200))
    plot = db.Column(db.String(10000))
    poster = db.Column(db.String(200))
    imdbRating = db.Column(db.String(200))
    type = db.Column(db.String(200))
    watch = db.relationship('User', secondary=watched, backref= 'shows')
    fav = db.relationship('User', secondary=fav, backref= 'favorite')
    later = db.relationship('User', secondary=later, backref= 'watch_later')





# db.create_all()
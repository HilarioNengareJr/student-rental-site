from studentguide import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    username = db.Column(db.String(128), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128))
    profile_image = db.Column(db.String(20), default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_username(self, first_name, last_name):
        self.username = first_name + " " + last_name

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_folder = db.Column(JSON, nullable=False)
    location = db.Column(db.String(200))
    city = db.Column(db.String(200))
    phone_number = db.Column(db.String(10), nullable=False)
    whatsapp = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # comments = db.relationship('Comment', backref='post', lazy='dynamic')
    # likes = db.relationship('Like', backref='post', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.image_folder)

#
# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
#
#     def __repr__(self):
#         return '<Comment {}>'.format(self.body)
#
#
# class Like(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
#
#     def __repr__(self):
#         return '<Like {}>'.format(self.body)


def init_db():
    db.create_all()


if __name__ == '__main__':
    init_db()
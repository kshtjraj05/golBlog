from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog.search import add_to_index, remove_from_index, query_index

@login_manager.user_loader
def load_user(user_id):
    return User.query.get((int(user_id)))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
)
domain_followers = db.Table('domain_followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('domain.id')),
)

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)


class Domain(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    domain_name= db.Column(db.String, nullable=False, unique=True)
    domain_image = db.Column(db.String, nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posts=db.relationship('Post', backref='domain', lazy =True)

class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable = False)
    image_file = db.Column(db.String(120), nullable = False, default= 'default.jpeg')
    password = db.Column(db.String(60), nullable = False)
    can_view_tour = db.Column(db.Boolean, default=True, nullable=False)

    posts=db.relationship('Post', backref='author', lazy =True)
    
    comments=db.relationship('Comment', backref='author', lazy=True)
    
    children_upvoted_posts = db.relationship('Upvote_association', back_populates='user')
    children_downvoted_posts = db.relationship('Downvote_association', back_populates='user')

    domains=db.relationship('Domain', backref='creator', lazy =True)
    
    followed = db.relationship('User',
        secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', viewonly=True, lazy = 'dynamic',sync_backref=False),
        lazy = 'dynamic')
    
    followed_domain = db.relationship('Domain',
        secondary = domain_followers,
        primaryjoin = (domain_followers.c.follower_id == id),
        secondaryjoin = (domain_followers.c.followed_id == Domain.id),
        backref = db.backref('followers', viewonly=True, lazy = 'dynamic',sync_backref=False),
        lazy = 'dynamic')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User ('{self.username}',{self.email}','{self.image_file}')"

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()
            return self

    def is_following_domain(self, domain):
        return self.followed_domain.filter(domain_followers.c.followed_id == domain.id).count() > 0
    
    def follow_domain(self, domain):
        if not self.is_following_domain(domain):
            self.followed_domain.append(domain)
            db.session.commit()
            return self

    def unfollow_domain(self, domain):
        if self.is_following_domain(domain):
            self.followed_domain.remove(domain)
            db.session.commit()
            return self



class Post(SearchableMixin, db.Model):

    __searchable__= ['content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable = False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments=db.relationship('Comment',backref='post', lazy=True,cascade="delete, delete-orphan")

    upvoters = db.relationship('Upvote_association',back_populates='post', cascade="delete, delete-orphan")
    downvoters = db.relationship('Downvote_association', back_populates='post',cascade="delete, delete-orphan")
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), nullable =False)

    
    

    def __repr__(self):
        return f"Post ('{self.title}','{self.date_posted}')"


class Upvote_association(db.Model):
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    post_id= db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

    user=db.relationship('User', back_populates='children_upvoted_posts')
    post=db.relationship('Post', back_populates='upvoters')
    

class Downvote_association(db.Model):
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    post_id= db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

    user=db.relationship('User', back_populates='children_downvoted_posts')
    post=db.relationship('Post', back_populates='downvoters')

class Comment(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable = False)

    def __repr__(self):
        return f"Comment('{self.content}', by:'{self.user_id}', on:{self.post_id}')"














#domain = db.relationship('Domain', secondary=post_domain,
    #primaryjoin = (post_domain.c.domain_id == id),
    #backref = db.backref('post', viewonly=True, lazy = 'dynamic',sync_backref=False),
    #lazy = 'dynamic')
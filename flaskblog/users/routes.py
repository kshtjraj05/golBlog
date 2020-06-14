from flask import  current_app, render_template, url_for, flash, redirect, request, abort
from flaskblog.users.forms import Follow, ResetPasswordForm, RequestResetForm,RegistrationForm, LogIn, UpdateAccountForm
from flaskblog.models  import User, Post,followers, Upvote_association
from flaskblog import  db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os
from PIL import Image
from datetime import datetime
from flask_mail import Message
from flaskblog.users.utils import send_reset_email, save_picture
from sqlalchemy import func


from flask import Blueprint
users = Blueprint('users',__name__)
latest_posts=[]
top_rated_posts=[]



@users.route("/register", methods=[ 'GET','POST'])
def register():
    latest_posts=Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    top_rated_posts=Post.query.outerjoin(Upvote_association).group_by(Post.id).order_by(func.count().desc()).limit(6).all()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password = hashed_password, email = form.email.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form = form, top_rated_posts=top_rated_posts, latest_posts=latest_posts)

@users.route("/login", methods = ['GET', 'POST'])
def login():
    latest_posts=Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    top_rated_posts=Post.query.outerjoin(Upvote_association).group_by(Post.id).order_by(func.count().desc()).limit(6).all()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LogIn()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form, top_rated_posts=top_rated_posts, latest_posts=latest_posts)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account", methods=['GET','POST'])
@login_required
def account():
    latest_posts=Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    top_rated_posts=Post.query.outerjoin(Upvote_association).group_by(Post.id).order_by(func.count().desc()).limit(6).all()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data=current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename ="profile_pics/"+current_user.image_file)
    return render_template('account.html', title='Account', image_file= image_file, form = form, top_rated_posts=top_rated_posts, latest_posts=latest_posts)

@users.route("/reset_password",methods=['GET','POST'])
def reset_request():
    latest_posts=Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    top_rated_posts=Post.query.outerjoin(Upvote_association).group_by(Post.id).order_by(func.count().desc()).limit(6).all()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to your registered email id for resetting your password')
    return render_template('reset_request.html', title='Reset Password', form=form, top_rated_posts=top_rated_posts, latest_posts=latest_posts)

@users.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    latest_posts=Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    top_rated_posts=Post.query.outerjoin(Upvote_association).group_by(Post.id).order_by(func.count().desc()).limit(6).all()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is invalid or expired token','warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()    
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Password successfully changed', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form =form, top_rated_posts=top_rated_posts, latest_posts=latest_posts )

@users.route("/user/<string:username>")
@login_required
def user_profile(username):
    latest_posts=Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    top_rated_posts=Post.query.outerjoin(Upvote_association).group_by(Post.id).order_by(func.count().desc()).limit(6).all()
    follow_form = Follow()

    page=request.args.get('page',1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        follow_form.follow_button.label.text='Followed'

    posts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=5)
    return render_template('user_profile.html',posts = posts, user=user, current_user=current_user, follow_form=follow_form, top_rated_posts=top_rated_posts, latest_posts=latest_posts)

@users.route("/user/<int:user_id>/follow", methods=['POST'])
def follow(user_id):
    user=User.query.get_or_404(user_id)
    if request.args.get('str') == 'Follow':
        current_user.follow(user)
    else:
        current_user.unfollow(user)
    return redirect(url_for('users.user_profile', username=user.username))

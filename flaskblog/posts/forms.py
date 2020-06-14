
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flaskblog.models import Domain
from flask import url_for, current_app, Blueprint


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
    domain = SelectField('Domain', validators=[DataRequired()]) 
    submit = SubmitField('Post')
    
class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post')

class UpvoteForm(FlaskForm):
    upvote_button = SubmitField('Upvote')

class DownvoteForm(FlaskForm):
    downvote_button = SubmitField('Downvote')


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from flaskblog.models import Domain
from flask import current_app
from flask_wtf.file import FileField, FileAllowed

class DomainForm(FlaskForm):
    domain_name= StringField('Domain Name', validators=[DataRequired()])
    submit = SubmitField('Create')

class UpdateDomainForm(FlaskForm):
    domain_name = StringField('Domain Name', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpeg', 'jpg', 'png'])])
    submit = SubmitField('Update')

class Follow(FlaskForm):
    follow_button=SubmitField('Follow')
    
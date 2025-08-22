from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, URL, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), URL()])
    github_url = StringField('GitHub URL', validators=[Optional(), URL()])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'gif'])])

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    content = TextAreaField('Content')
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    demo_url = StringField('Demo URL', validators=[Optional(), URL()])
    github_url = StringField('GitHub URL', validators=[Optional(), URL()])
    technologies = StringField('Technologies (comma-separated)', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('desktop', 'Desktop Application'),
        ('data', 'Data Science'),
        ('ai', 'Artificial Intelligence'),
        ('other', 'Other')
    ])
    is_published = BooleanField('Published')
    is_featured = BooleanField('Featured')

class AchievementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date_achieved = DateField('Date Achieved', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('certification', 'Certification'),
        ('award', 'Award'),
        ('competition', 'Competition'),
        ('publication', 'Publication'),
        ('other', 'Other')
    ])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    certificate_url = StringField('Certificate URL', validators=[Optional(), URL()])
    is_published = BooleanField('Published')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=1000)])

class AboutMeForm(FlaskForm):
    content = TextAreaField('About Me', validators=[DataRequired()])
    skills = TextAreaField('Skills (one per line)')
    experience = TextAreaField('Experience')
    education = TextAreaField('Education')

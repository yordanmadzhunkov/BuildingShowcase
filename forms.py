from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, EmailField, TelField, \
    PasswordField, BooleanField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from models import User
from datetime import datetime

class ContactForm(FlaskForm):
    """Form for contact page"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[Length(max=20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=150)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')

class LoginForm(FlaskForm):
    """Form for admin login"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for admin registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ProjectForm(FlaskForm):
    """Form for adding/editing projects"""
    title = StringField('Project Title', validators=[DataRequired(), Length(min=3, max=100)])
    slug = StringField('Slug (URL path)', validators=[DataRequired(), Length(min=3, max=120)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20)])
    client = StringField('Client', validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=150)])
    completion_date = DateField('Completion Date', validators=[DataRequired()], default=datetime.utcnow)
    square_footage = IntegerField('Square Footage', validators=[Optional()])
    project_type = SelectField('Project Type', choices=[
        ('residential', 'Residential'), 
        ('commercial', 'Commercial'),
        ('institutional', 'Institutional'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure')
    ])
    featured = BooleanField('Featured Project')
    submit = SubmitField('Save Project')
    
    def validate_slug(self, slug):
        from models import Project
        project = Project.query.filter_by(slug=slug.data).first()
        if project is not None and project.id != getattr(self, '_project_id', None):
            raise ValidationError('This slug is already in use. Please use a different one.')

class ProjectImageForm(FlaskForm):
    """Form for adding project images"""
    image = FileField('Image File', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'svg'], 'Images only!')])
    caption = StringField('Caption', validators=[Optional(), Length(max=255)])
    is_primary = BooleanField('Primary Image')
    submit = SubmitField('Upload Image')

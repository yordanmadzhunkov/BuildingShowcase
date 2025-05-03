from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    """Form for contact page"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[Length(max=20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=150)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')

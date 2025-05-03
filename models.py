from datetime import datetime
from app import db

class Project(db.Model):
    """Model for construction projects"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    client = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    completion_date = db.Column(db.Date, default=datetime.utcnow)
    square_footage = db.Column(db.Integer)
    project_type = db.Column(db.String(50))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with images
    images = db.relationship('ProjectImage', backref='project', cascade='all, delete-orphan')

class ProjectImage(db.Model):
    """Model for project images"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    """Model for contact form submissions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded = db.Column(db.Boolean, default=False)

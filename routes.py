from flask import render_template, request, flash, redirect, url_for, abort, session
from werkzeug.exceptions import NotFound
from app import app, db
from models import Project, ProjectImage, ContactMessage, User
from forms import ContactForm, LoginForm, RegistrationForm, ProjectForm, ProjectImageForm
from flask_babel import gettext as _
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime
import uuid
import re

# Sample project data for initial setup
sample_projects = [
    {
        'title': 'Modern Office Tower',
        'slug': 'modern-office-tower',
        'description': 'A 15-story modern office tower featuring glass façade, sustainable design elements, and open floor plans.',
        'client': 'TechCorp Inc.',
        'location': 'Downtown, Metropolis',
        'completion_date': '2022-05-15',
        'square_footage': 125000,
        'project_type': 'Commercial',
        'featured': True,
        'images': [
            {
                'filename': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab',
                'caption': 'Front view of the glass facade',
                'is_primary': True
            },
            {
                'filename': 'https://images.unsplash.com/photo-1464082354059-27db6ce50048',
                'caption': 'Lobby interior with modern design',
                'is_primary': False
            }
        ]
    },
    {
        'title': 'Riverside Apartments',
        'slug': 'riverside-apartments',
        'description': 'Luxury riverside apartment complex with 200 units, featuring rooftop gardens, fitness center, and riverside walking paths.',
        'client': 'River Development LLC',
        'location': 'Riverside District, Metropolis',
        'completion_date': '2021-11-30',
        'square_footage': 250000,
        'project_type': 'Residential',
        'featured': True,
        'images': [
            {
                'filename': 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00',
                'caption': 'Riverside view of the apartment complex',
                'is_primary': True
            },
            {
                'filename': 'https://images.unsplash.com/photo-1515263487990-61b07816b324',
                'caption': 'Luxury apartment interior',
                'is_primary': False
            }
        ]
    },
    {
        'title': 'Community Health Center',
        'slug': 'community-health-center',
        'description': 'State-of-the-art community health center featuring 30 examination rooms, diagnostic imaging department, and community wellness spaces.',
        'client': 'Metropolis Health Department',
        'location': 'East Side, Metropolis',
        'completion_date': '2022-02-10',
        'square_footage': 75000,
        'project_type': 'Healthcare',
        'featured': True,
        'images': [
            {
                'filename': 'https://images.unsplash.com/photo-1586534646494-dafb910e2d62',
                'caption': 'Main entrance to the health center',
                'is_primary': True
            },
            {
                'filename': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d',
                'caption': 'Modern reception area',
                'is_primary': False
            }
        ]
    },
    {
        'title': 'Green Tech Industrial Park',
        'slug': 'green-tech-industrial-park',
        'description': 'Sustainable industrial park with solar-powered facilities, rainwater collection systems, and energy-efficient design.',
        'client': 'GreenFuture Industries',
        'location': 'Industrial Zone, Metropolis',
        'completion_date': '2021-07-22',
        'square_footage': 500000,
        'project_type': 'Industrial',
        'featured': False,
        'images': [
            {
                'filename': 'https://images.unsplash.com/photo-1584269655722-8b0359de2bc7',
                'caption': 'Aerial view of the industrial park',
                'is_primary': True
            },
            {
                'filename': 'https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122',
                'caption': 'Solar panel installation on roof',
                'is_primary': False
            }
        ]
    },
    {
        'title': 'Heritage Museum Renovation',
        'slug': 'heritage-museum-renovation',
        'description': 'Complete renovation and expansion of the historic Heritage Museum, including structural reinforcement, modern facilities, and accessibility improvements.',
        'client': 'Metropolis Historical Society',
        'location': 'Cultural District, Metropolis',
        'completion_date': '2022-04-05',
        'square_footage': 45000,
        'project_type': 'Cultural',
        'featured': False,
        'images': [
            {
                'filename': 'https://images.unsplash.com/photo-1574958269305-f7c2b36af922',
                'caption': 'Renovated facade of the Heritage Museum',
                'is_primary': True
            },
            {
                'filename': 'https://images.unsplash.com/photo-1566686153396-72180be89da2',
                'caption': 'New exhibition hall interior',
                'is_primary': False
            }
        ]
    }
]

def initialize_db():
    """Initialize the database with sample projects if empty"""
    # Check if projects already exist
    if Project.query.first() is None:
        for project_data in sample_projects:
            images_data = project_data.pop('images')
            # Convert completion_date string to date object
            from datetime import datetime
            project_data['completion_date'] = datetime.strptime(project_data['completion_date'], '%Y-%m-%d').date()
            # Create project
            project = Project(**project_data)
            db.session.add(project)
            db.session.flush()  # Get the project ID
            
            # Add images
            for image_data in images_data:
                image = ProjectImage(project_id=project.id, **image_data)
                db.session.add(image)
        
        db.session.commit()
        logging.info("Database initialized with sample projects")

# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br(value):
    """Convert newlines to <br> tags"""
    if not value:
        return ''
    return value.replace('\n', '<br>')

# Initialize database with sample data
with app.app_context():
    initialize_db()

@app.route('/')
def index():
    """Homepage route"""
    # Get featured projects for the homepage carousel
    featured_projects = Project.query.filter_by(featured=True).all()
    # Get recent projects limited to 3
    recent_projects = Project.query.order_by(Project.completion_date.desc()).limit(3).all()
    return render_template('index.html', 
                          featured_projects=featured_projects,
                          recent_projects=recent_projects)

@app.route('/projects')
def projects():
    """Projects gallery page"""
    # Get filter parameters from query string
    project_type = request.args.get('type')
    
    # Base query
    query = Project.query
    
    # Apply filters if provided
    if project_type:
        query = query.filter_by(project_type=project_type)
    
    # Get all projects with filters applied
    projects_list = query.order_by(Project.completion_date.desc()).all()
    
    # Get unique project types for filter options
    project_types = db.session.query(Project.project_type).distinct().all()
    project_types = [t[0] for t in project_types]
    
    return render_template('projects.html', 
                          projects=projects_list,
                          project_types=project_types,
                          current_type=project_type)

@app.route('/projects/<slug>')
def project_detail(slug):
    """Project detail page"""
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template('project_detail.html', project=project)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form"""
    form = ContactForm()
    
    if form.validate_on_submit():
        # Create new contact message
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(message)
        try:
            db.session.commit()
            flash('Your message has been sent. We will contact you shortly!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while sending your message. Please try again.', 'danger')
            logging.error(f"Error saving contact form: {str(e)}")
    
    return render_template('contact.html', form=form)

@app.route('/language/<lang_code>')
def set_language(lang_code):
    """Set the language"""
    # Check if the language is supported
    if lang_code in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = lang_code
        # Flash a message to confirm the language change
        if lang_code == 'en':
            flash('Language changed to English', 'info')
        elif lang_code == 'bg':
            flash('Езикът е променен на български', 'info')
    # Redirect back to the referring page or home page
    return redirect(request.referrer or url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page"""
    return render_template('404.html'), 404

# Utility functions
def generate_unique_filename(filename):
    """Generate a unique filename while preserving extension"""
    _, ext = os.path.splitext(filename)
    return f"{uuid.uuid4().hex}{ext}"

def save_project_image(image_file):
    """Save a project image and return the path"""
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(app.static_folder, 'uploads/projects')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Generate unique filename and save
    filename = secure_filename(image_file.filename)
    unique_filename = generate_unique_filename(filename)
    file_path = os.path.join(uploads_dir, unique_filename)
    image_file.save(file_path)
    
    # Return the relative path for database storage
    return f"/static/uploads/projects/{unique_filename}"

def slugify(text):
    """Convert text to URL-friendly slug"""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove special characters
    text = re.sub(r'[^\w\-]', '', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    return text

# Admin authentication routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html', title='Admin Login', form=form)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    """Admin registration - only available if no users exist"""
    # Check if any users exist
    if User.query.first():
        # If users exist, only allow authenticated users to register new users
        if not current_user.is_authenticated:
            flash('Registration is not available', 'warning')
            return redirect(url_for('admin_login'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.is_admin = True  # All registered users are admin by default
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin/register.html', title='Register', form=form)

# Admin dashboard routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics for dashboard
    projects_count = Project.query.count()
    messages_count = ContactMessage.query.count()
    featured_count = Project.query.filter_by(featured=True).count()
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          title='Dashboard',
                          projects_count=projects_count,
                          messages_count=messages_count,
                          featured_count=featured_count,
                          recent_projects=recent_projects)

# Project management routes
@app.route('/admin/projects')
@login_required
def admin_projects():
    """Admin projects list"""
    # Get filter parameters
    project_type = request.args.get('project_type')
    featured = request.args.get('featured')
    
    # Base query
    query = Project.query
    
    # Apply filters
    if project_type:
        query = query.filter_by(project_type=project_type)
    if featured:
        featured_bool = featured == '1'
        query = query.filter_by(featured=featured_bool)
    
    # Get projects
    projects_list = query.order_by(Project.created_at.desc()).all()
    
    return render_template('admin/projects.html', 
                          title='Manage Projects',
                          projects=projects_list)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@login_required
def admin_add_project():
    """Add new project"""
    form = ProjectForm()
    
    if form.validate_on_submit():
        # Create new project
        project = Project(
            title=form.title.data,
            slug=form.slug.data,
            description=form.description.data,
            client=form.client.data,
            location=form.location.data,
            completion_date=form.completion_date.data,
            square_footage=form.square_footage.data,
            project_type=form.project_type.data,
            featured=form.featured.data
        )
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('admin_project_images', project_id=project.id))
    
    # If slug field is empty and title is filled, generate a suggested slug
    if request.method == 'GET' and not form.slug.data and form.title.data:
        form.slug.data = slugify(form.title.data)
    
    return render_template('admin/project_form.html',
                          title='Add Project',
                          form=form)

@app.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_project(project_id):
    """Edit existing project"""
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    form._project_id = project_id  # Store project ID for slug validation
    
    if form.validate_on_submit():
        # Update project
        project.title = form.title.data
        project.slug = form.slug.data
        project.description = form.description.data
        project.client = form.client.data
        project.location = form.location.data
        project.completion_date = form.completion_date.data
        project.square_footage = form.square_footage.data
        project.project_type = form.project_type.data
        project.featured = form.featured.data
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html',
                          title='Edit Project',
                          form=form,
                          project=project)

@app.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def admin_delete_project(project_id):
    """Delete project"""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_projects'))

# Project image management routes
@app.route('/admin/projects/<int:project_id>/images')
@login_required
def admin_project_images(project_id):
    """Manage project images"""
    project = Project.query.get_or_404(project_id)
    form = ProjectImageForm()
    
    return render_template('admin/project_images.html',
                          title='Project Images',
                          project=project,
                          form=form)

@app.route('/admin/projects/<int:project_id>/images/add', methods=['POST'])
@login_required
def admin_add_project_image(project_id):
    """Add project image"""
    project = Project.query.get_or_404(project_id)
    form = ProjectImageForm()
    
    if form.validate_on_submit():
        # Handle image upload
        image_file = form.image.data
        file_path = save_project_image(image_file)
        
        # Check if this is set as primary and update other images if needed
        if form.is_primary.data:
            # Remove primary flag from all other images for this project
            for image in project.images:
                image.is_primary = False
        
        # Create new image record
        image = ProjectImage(
            filename=file_path,
            caption=form.caption.data,
            is_primary=form.is_primary.data,
            project_id=project.id
        )
        db.session.add(image)
        db.session.commit()
        
        flash('Image added successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('admin_project_images', project_id=project.id))

@app.route('/admin/projects/<int:project_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
def admin_delete_project_image(project_id, image_id):
    """Delete project image"""
    image = ProjectImage.query.get_or_404(image_id)
    
    # Check if image belongs to the specified project
    if image.project_id != project_id:
        abort(404)
    
    was_primary = image.is_primary
    
    # Delete the file from the filesystem if it's a local file
    if image.filename.startswith('/static'):
        try:
            file_path = os.path.join(app.static_folder, image.filename.replace('/static/', ''))
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.error(f"Error deleting image file: {str(e)}")
    
    # Delete the image record
    db.session.delete(image)
    
    # If this was the primary image, set another one as primary if available
    if was_primary:
        remaining_image = ProjectImage.query.filter_by(project_id=project_id).first()
        if remaining_image:
            remaining_image.is_primary = True
    
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_project_images', project_id=project_id))

@app.route('/admin/projects/<int:project_id>/images/<int:image_id>/set-primary', methods=['POST'])
@login_required
def admin_set_primary_image(project_id, image_id):
    """Set image as primary"""
    image = ProjectImage.query.get_or_404(image_id)
    
    # Check if image belongs to the specified project
    if image.project_id != project_id:
        abort(404)
    
    # Remove primary flag from all other images
    for proj_image in ProjectImage.query.filter_by(project_id=project_id):
        proj_image.is_primary = (proj_image.id == image_id)
    
    db.session.commit()
    flash('Primary image updated successfully!', 'success')
    return redirect(url_for('admin_project_images', project_id=project_id))

# Contact message management routes
@app.route('/admin/messages')
@login_required
def admin_messages():
    """Manage contact messages"""
    # Get filter parameters
    responded = request.args.get('responded')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = ContactMessage.query
    
    # Apply filters
    if responded is not None:
        responded_bool = responded == '1'
        query = query.filter_by(responded=responded_bool)
    
    # Paginate results
    pagination = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    messages = pagination.items
    
    return render_template('admin/messages.html',
                          title='Contact Messages',
                          messages=messages,
                          pagination=pagination)

@app.route('/admin/messages/<int:message_id>/toggle-status', methods=['POST'])
@login_required
def admin_toggle_message_status(message_id):
    """Toggle message responded status"""
    message = ContactMessage.query.get_or_404(message_id)
    message.responded = not message.responded
    db.session.commit()
    status = 'responded' if message.responded else 'unresponded'
    flash(f'Message marked as {status}!', 'success')
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def admin_delete_message(message_id):
    """Delete contact message"""
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin_messages'))

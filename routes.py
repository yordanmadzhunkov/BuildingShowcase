from flask import render_template, request, flash, redirect, url_for, abort, session
from werkzeug.exceptions import NotFound
from app import app, db
from models import Project, ProjectImage, ContactMessage
from forms import ContactForm
from flask_babel import gettext as _
import logging

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

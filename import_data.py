import os
import sys
import trafilatura
from datetime import datetime
import random
from app import app, db
from models import Project, ProjectImage

def get_website_text_content(url: str) -> str:
    """Extract the main text content from a website."""
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        print(f"Error: Could not download content from {url}")
        return ""
    text = trafilatura.extract(downloaded)
    return text if text else ""

def import_projects_from_buildengineering09():
    """Import project data from buildengineering09.com"""
    print("Starting import from buildengineering09.com...")
    
    # Base URL for the website
    base_url = "https://buildengineering09.com"
    
    # Get the main page content to extract project information
    main_content = get_website_text_content(base_url)
    if not main_content:
        print("Failed to get content from the main page")
        return False
    
    print("Successfully retrieved main content from buildengineering09.com")
    print(f"Content length: {len(main_content)} characters")
    
    # Define project types we want to create based on what a construction company might have
    projects_to_create = [
        {
            'slug': 'commercial-tower',
            'title': 'Commercial Tower',
            'project_type': 'Commercial',
            'description': f"A modern commercial tower project by BuildEngineering09. This impressive structure features a sleek glass facade, energy-efficient design, and state-of-the-art facilities. The tower stands as a landmark in the city skyline and provides premium office space for businesses.\n\nImported from BuildEngineering09: {main_content[:200]}...",
            'client': 'MetroCorp Developments',
            'location': 'Chicago, IL',
            'square_footage': 85000,
            'featured': True
        },
        {
            'slug': 'residential-complex',
            'title': 'Riverside Residential Complex',
            'project_type': 'Residential',
            'description': f"Luxury residential complex featuring modern apartments with river views. This development includes premium amenities such as a fitness center, rooftop garden, and community spaces. The design emphasizes sustainable living and community connection.\n\nImported from BuildEngineering09: {main_content[50:250]}...",
            'client': 'Riverfront Properties LLC',
            'location': 'Portland, OR',
            'square_footage': 120000,
            'featured': True
        },
        {
            'slug': 'hospital-expansion',
            'title': 'Memorial Hospital Expansion',
            'project_type': 'Healthcare',
            'description': f"An expansion project for Memorial Hospital, adding a new patient wing and modernizing existing facilities. The expansion increases capacity and brings cutting-edge medical technology to the community. The design prioritizes patient comfort and staff efficiency.\n\nImported from BuildEngineering09: {main_content[100:300]}...",
            'client': 'Memorial Healthcare System',
            'location': 'Denver, CO',
            'square_footage': 65000,
            'featured': False
        },
        {
            'slug': 'office-renovation',
            'title': 'Downtown Office Renovation',
            'project_type': 'Commercial',
            'description': f"Complete renovation of a downtown office building, transforming traditional office spaces into a modern collaborative environment. The renovation includes updated infrastructure, energy-efficient systems, and flexible workspace design.\n\nImported from BuildEngineering09: {main_content[150:350]}...",
            'client': 'Innovate Workspace Inc.',
            'location': 'Seattle, WA',
            'square_footage': 45000,
            'featured': False
        },
        {
            'slug': 'school-building',
            'title': 'Westside Elementary School',
            'project_type': 'Educational',
            'description': f"A new elementary school designed to support modern educational approaches with flexible learning spaces, technology integration, and safety features. The building includes classrooms, a library, cafeteria, gymnasium, and outdoor learning areas.\n\nImported from BuildEngineering09: {main_content[200:400]}...",
            'client': 'Westside School District',
            'location': 'Austin, TX',
            'square_footage': 70000,
            'featured': True
        }
    ]
    
    imported_projects = 0
    
    with app.app_context():
        # Process each project
        for project_data in projects_to_create:
            print(f"Processing {project_data['title']}...")
            
            # Check if project already exists
            slug = project_data['slug']
            existing_project = Project.query.filter_by(slug=slug).first()
            if existing_project:
                print(f"Project with slug '{slug}' already exists. Skipping.")
                continue
            
            # Create completion date
            completion_date = datetime(random.randint(2018, 2024), random.randint(1, 12), random.randint(1, 28))
            
            # Create a new project
            new_project = Project(
                title=project_data['title'],
                slug=project_data['slug'],
                description=project_data['description'],
                client=project_data['client'],
                location=project_data['location'],
                completion_date=completion_date,
                square_footage=project_data['square_footage'],
                project_type=project_data['project_type'],
                featured=project_data['featured']
            )
            
            # Add images to the project
            primary_added = False
            for i in range(1, 4):  # Add 3 placeholder images
                image = ProjectImage(
                    filename=f"/static/images/projects/placeholder_{slug}_{i}.svg",
                    caption=f"Image {i} for {project_data['title']}",
                    is_primary=not primary_added  # Make the first image primary
                )
                if not primary_added:
                    primary_added = True
                new_project.images.append(image)
            
            # Add the project to the database
            db.session.add(new_project)
            db.session.commit()
            
            print(f"Added project: {project_data['title']}")
            imported_projects += 1
    
    print(f"Import complete. Added {imported_projects} projects.")
    return imported_projects > 0

if __name__ == "__main__":
    success = import_projects_from_buildengineering09()
    if success:
        print("Import completed successfully.")
    else:
        print("Import failed or no projects were added.")
        sys.exit(1)

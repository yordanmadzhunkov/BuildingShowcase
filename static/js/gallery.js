/**
 * BuildCo Construction Website - Gallery JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Masonry layout for project gallery (if available)
    const projectGrid = document.querySelector('.project-grid');
    if (projectGrid) {
        // Check if Masonry is loaded
        if (typeof Masonry !== 'undefined') {
            new Masonry(projectGrid, {
                itemSelector: '.project-item',
                columnWidth: '.grid-sizer',
                percentPosition: true
            });
        }
    }

    // Filter functionality for projects
    const filterButtons = document.querySelectorAll('.filter-button');
    const projectItems = document.querySelectorAll('.project-card');

    if (filterButtons.length && projectItems.length) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const filterValue = this.getAttribute('data-filter');
                
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Filter projects
                projectItems.forEach(item => {
                    if (filterValue === 'all') {
                        item.style.display = 'block';
                    } else {
                        if (item.classList.contains(filterValue)) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    }
                });
                
                // Re-layout Masonry if available
                if (typeof Masonry !== 'undefined' && projectGrid) {
                    new Masonry(projectGrid).layout();
                }
            });
        });
    }

    // Lazy loading for project images
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
        document.body.appendChild(script);
    }

    // Initialize lightbox if available
    if (typeof lightbox !== 'undefined') {
        lightbox.option({
            'resizeDuration': 300,
            'wrapAround': true,
            'albumLabel': 'Image %1 of %2',
            'fadeDuration': 300
        });
    }

    // Add animation to project cards
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('project-hover');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('project-hover');
        });
    });
});

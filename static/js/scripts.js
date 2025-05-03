/**
 * BuildCo Construction Website - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Navbar scroll behavior
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled', 'shadow-sm');
            } else {
                navbar.classList.remove('navbar-scrolled', 'shadow-sm');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Animation on scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        const animateElement = function() {
            animatedElements.forEach(function(element) {
                const elementPosition = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;
                
                if (elementPosition < windowHeight - 50) {
                    element.classList.add('fade-in');
                }
            });
        };
        
        // Run once on load
        animateElement();
        
        // Run on scroll
        window.addEventListener('scroll', animateElement);
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    }

    // Back to top button
    const backToTopButton = document.getElementById('back-to-top');
    
    if (backToTopButton) {
        window.onscroll = function() {
            if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        };
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    }
});

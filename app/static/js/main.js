// Main JavaScript for GrameenConnect

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Image preview for file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const preview = document.querySelector('.image-preview');
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Location picker functionality
    const locationInput = document.getElementById('location');
    if (locationInput && navigator.geolocation) {
        const locationBtn = document.getElementById('get-location');
        if (locationBtn) {
            locationBtn.addEventListener('click', function() {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    locationInput.value = `${lat}, ${lng}`;
                });
            });
        }
    }
    
    // Handle logo image errors - replace with SVG if PNG doesn't load
    const logoImages = document.querySelectorAll('.logo-image');
    logoImages.forEach(function(img) {
        img.addEventListener('error', function() {
            // This will replace the src with the SVG if the PNG fails to load
            this.src = '/static/images/logo.svg';
        });
    });
    
    // Handle language toggling and page reload
    const languageLinks = document.querySelectorAll('.dropdown-item[href*="/language/"]');
    languageLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            
            // Send AJAX request to change language
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Reload the page to reflect language change
                    window.location.reload();
                }
            })
            .catch(function(error) {
                console.error('Error changing language:', error);
                // Fallback: navigate to the URL directly
                window.location.href = url;
            });
        });
    });
    
    // Scroll animations
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    // Function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8 &&
            rect.bottom >= 0
        );
    }
    
    // Apply initial animations for elements in viewport on load
    function checkAnimations() {
        animateElements.forEach(element => {
            if (isInViewport(element)) {
                // Get delay attribute or default to 0
                const delay = element.getAttribute('data-delay') || 0;
                
                // Set timeout based on delay
                setTimeout(() => {
                    element.classList.add('visible');
                }, delay);
            }
        });
    }
    
    // Check animations on scroll
    window.addEventListener('scroll', function() {
        checkAnimations();
    });
    
    // Run on initial load
    checkAnimations();
    
    // Animated counter for statistics
    const counters = document.querySelectorAll('.counter');
    
    function animateCounter(counter) {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const step = Math.ceil(target / (duration / 16)); // 60fps
        
        let current = 0;
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                clearInterval(timer);
                counter.textContent = target;
            } else {
                counter.textContent = current;
            }
        }, 16);
    }
    
    // Check if counter is in viewport and animate
    function checkCounters() {
        counters.forEach(counter => {
            if (isInViewport(counter) && !counter.classList.contains('animated')) {
                counter.classList.add('animated');
                animateCounter(counter);
            }
        });
    }
    
    // Check counters on scroll
    window.addEventListener('scroll', checkCounters);
    
    // Check on initial load
    checkCounters();
    
    // Wave SVG fallback animation for browsers that don't support path morphing
    const wavePath = document.querySelector('.wave-separator path');
    
    // Check if the browser supports SVG path animation
    const supportsPathMorphing = CSS.supports('d: path("M0 0")');
    
    if (!supportsPathMorphing && wavePath) {
        // Fallback animation - we'll use transform instead
        const waveElement = document.querySelector('.wave-separator svg');
        
        // Create animation
        function animateWave() {
            waveElement.animate([
                { transform: 'scaleX(1) translateY(0)' },
                { transform: 'scaleX(0.98) translateY(5px)' },
                { transform: 'scaleX(1.02) translateY(-5px)' },
                { transform: 'scaleX(1) translateY(0)' }
            ], {
                duration: 10000,
                iterations: Infinity,
                easing: 'ease-in-out'
            });
        }
        
        animateWave();
    }
    
    // Parallax effect for decorative elements
    const decorativeElements = document.querySelectorAll('.decorative-element, .floating-element');
    
    function parallaxMove(e) {
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        
        decorativeElements.forEach(element => {
            const speed = 0.03;
            const x = (window.innerWidth / 2 - mouseX) * speed;
            const y = (window.innerHeight / 2 - mouseY) * speed;
            
            element.style.transform = `translateX(${x}px) translateY(${y}px)`;
        });
    }
    
    // Add parallax effect if not on mobile
    if (window.innerWidth > 768) {
        document.addEventListener('mousemove', parallaxMove);
    }
}); 
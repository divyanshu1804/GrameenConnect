/**
 * GrameenConnect Overflow Fix
 * 
 * This script ensures that no horizontal scrollbar appears
 * by constantly monitoring the DOM and fixing any elements
 * that may cause horizontal overflow.
 */

(function() {
    // Run immediately when loaded
    fixOverflow();
    
    // Also run on page load
    document.addEventListener('DOMContentLoaded', function() {
        fixOverflow();
        
        // Run when window is resized
        window.addEventListener('resize', debounce(fixOverflow, 100));
        
        // Run periodically to catch any dynamic changes
        setInterval(fixOverflow, 500);
        
        // Run after images load
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.addEventListener('load', fixOverflow);
        });
        
        // Watch for DOM changes
        const observer = new MutationObserver(debounce(fixOverflow, 100));
        observer.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class', 'width']
        });
        
        // Fix dropdown menus
        fixDropdownMenus();
        
        // Add listeners for dropdown toggle
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('dropdown-toggle') || 
                e.target.closest('.dropdown-toggle')) {
                setTimeout(fixDropdownMenus, 10);
            }
        });
    });
    
    // Main function to fix overflow
    function fixOverflow() {
        // Force html and body to not have horizontal scroll
        document.documentElement.style.overflowX = 'hidden';
        document.body.style.overflowX = 'hidden';
        document.documentElement.style.maxWidth = '100vw';
        document.body.style.maxWidth = '100vw';
        
        // Check and fix wave-shape SVGs
        const waveSvgs = document.querySelectorAll('.wave-shape svg, .wave-shape-bottom svg');
        waveSvgs.forEach(svg => {
            svg.style.maxWidth = '100%';
            svg.style.width = '100%';
            svg.style.overflowX = 'hidden';
            svg.parentElement.style.overflowX = 'hidden';
            svg.parentElement.style.maxWidth = '100vw';
        });
        
        // Fix container elements
        const containers = document.querySelectorAll('.container, .container-fluid, .row');
        containers.forEach(container => {
            container.style.maxWidth = '100%';
            container.style.overflowX = 'hidden';
            container.style.marginLeft = '0';
            container.style.marginRight = '0';
        });
        
        // Fix any wide elements
        const allElements = document.querySelectorAll('*');
        const windowWidth = window.innerWidth;
        
        allElements.forEach(el => {
            // Get the actual width including any overflow
            const rect = el.getBoundingClientRect();
            if (rect.width > windowWidth) {
                el.style.maxWidth = '100vw';
                el.style.overflowX = 'hidden';
            }
        });
        
        // Make sure no element has a right margin or padding that causes overflow
        document.querySelectorAll('[style*="margin-right"], [style*="padding-right"]').forEach(el => {
            const style = window.getComputedStyle(el);
            const marginRight = parseInt(style.marginRight, 10);
            const paddingRight = parseInt(style.paddingRight, 10);
            
            if (marginRight > 50) {
                el.style.marginRight = '0';
            }
            
            if (paddingRight > 50) {
                el.style.paddingRight = '15px';
            }
        });
        
        // Fix dropdown menus
        fixDropdownMenus();
    }
    
    // Function to specifically fix dropdown menus
    function fixDropdownMenus() {
        const dropdownMenus = document.querySelectorAll('.dropdown-menu');
        const isMobile = window.innerWidth < 768;
        
        dropdownMenus.forEach(menu => {
            // Basic overflow fixes
            menu.style.overflowX = 'hidden';
            menu.style.maxWidth = isMobile ? '100%' : '260px';
            
            if (!isMobile) {
                // On desktop, position the menu correctly to avoid overflow
                const rect = menu.getBoundingClientRect();
                const parent = menu.closest('.dropdown');
                
                if (rect.right > window.innerWidth) {
                    menu.style.left = 'auto';
                    menu.style.right = '0';
                }
                
                // Make sure menu stays in viewport vertically too
                if (rect.bottom > window.innerHeight) {
                    menu.style.maxHeight = '60vh';
                    menu.style.overflowY = 'auto';
                }
            } else {
                // On mobile, ensure dropdown is static and within parent
                menu.style.position = 'static';
                menu.style.float = 'none';
                menu.style.width = '100%';
            }
            
            // Fix dropdown items
            const dropdownItems = menu.querySelectorAll('.dropdown-item');
            dropdownItems.forEach(item => {
                item.style.whiteSpace = 'normal';
                item.style.wordWrap = 'break-word';
                item.style.maxWidth = '100%';
            });
        });
        
        // Fix dropdown toggles
        document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            // Make sure it has the click listener only once
            if (!toggle.hasAttribute('data-has-click-listener')) {
                toggle.setAttribute('data-has-click-listener', 'true');
                toggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Get dropdown menu
                    const menu = this.nextElementSibling;
                    if (menu && menu.classList.contains('dropdown-menu')) {
                        // Close other open dropdowns
                        document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                            if (openMenu !== menu) {
                                openMenu.classList.remove('show');
                            }
                        });
                        
                        // Toggle this menu
                        menu.classList.toggle('show');
                        
                        // Position properly
                        if (window.innerWidth >= 768) {
                            menu.style.position = 'absolute';
                            menu.style.inset = '0px auto auto 0px';
                            menu.style.transform = 'translate(0px, 40px)';
                            
                            // Fix right alignment for dropdowns at right edge
                            if (menu.classList.contains('dropdown-menu-end')) {
                                menu.style.inset = '0px 0px auto auto';
                                menu.style.left = 'auto';
                                menu.style.right = '0';
                            }
                        }
                    }
                });
            }
        });
        
        // Close dropdowns when clicking outside
        if (!document.body.hasAttribute('data-has-dropdown-close-listener')) {
            document.body.setAttribute('data-has-dropdown-close-listener', 'true');
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.dropdown')) {
                    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                        menu.classList.remove('show');
                    });
                }
            });
        }
    }
    
    // Debounce function to prevent too many calls
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }
})(); 
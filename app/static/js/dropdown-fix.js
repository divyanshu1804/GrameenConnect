/**
 * GrameenConnect Dropdown Fix
 * This script fixes issues with Bootstrap dropdowns not displaying correctly
 */

document.addEventListener('DOMContentLoaded', function() {
    // Special handling for problematic pages
    const currentPath = window.location.pathname;
    const isProblematicPage = currentPath.includes('/issues') || 
                              currentPath.includes('/my_applications') ||
                              currentPath.includes('/profile');
    
    // Fix dropdown menus across the site
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(function(toggle) {
        // Remove any existing click handlers by cloning and replacing the element
        const newToggle = toggle.cloneNode(true);
        toggle.parentNode.replaceChild(newToggle, toggle);
        
        // Add our custom click handler
        newToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Special handling for problematic pages
            if (isProblematicPage) {
                // Force higher z-index on problematic pages
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.style.zIndex = '10000';
                });
            }
            
            // Get the dropdown menu - either next sibling or by class/ID relationship
            let dropdownMenu = this.nextElementSibling;
            
            // Special case for language dropdown
            if (this.id === 'languageDropdown' && (!dropdownMenu || !dropdownMenu.classList.contains('dropdown-menu'))) {
                dropdownMenu = document.querySelector('.language-dropdown');
            }
            
            // Special case for user dropdown
            if (this.id === 'userDropdown' && (!dropdownMenu || !dropdownMenu.classList.contains('dropdown-menu'))) {
                const userDropdown = document.querySelector('.user-dropdown');
                if (userDropdown) {
                    dropdownMenu = userDropdown.querySelector('.dropdown-menu');
                }
            }
            
            if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                // Toggle the dropdown menu
                if (dropdownMenu.classList.contains('show')) {
                    dropdownMenu.classList.remove('show');
                } else {
                    // Close all other open dropdowns
                    document.querySelectorAll('.dropdown-menu.show').forEach(function(menu) {
                        menu.classList.remove('show');
                    });
                    
                    // Show this dropdown menu
                    dropdownMenu.classList.add('show');
                    
                    // Position the dropdown menu properly
                    const rect = this.getBoundingClientRect();
                    const isDesktop = window.innerWidth >= 768;
                    
                    // For language dropdown
                    if (this.id === 'languageDropdown' || dropdownMenu.classList.contains('language-dropdown')) {
                        dropdownMenu.style.position = 'absolute';
                        dropdownMenu.style.top = rect.bottom + 'px';
                        dropdownMenu.style.left = 'auto';
                        dropdownMenu.style.right = '0';
                        dropdownMenu.style.width = '180px';
                        dropdownMenu.style.minWidth = '180px';
                        dropdownMenu.style.maxWidth = '180px';
                        dropdownMenu.style.zIndex = isProblematicPage ? '10000' : '9999';
                        dropdownMenu.style.display = 'block';
                    } 
                    // For user dropdown
                    else if (this.id === 'userDropdown' || this.closest('.user-dropdown')) {
                        dropdownMenu.style.position = 'absolute';
                        dropdownMenu.style.top = rect.bottom + 'px';
                        dropdownMenu.style.left = 'auto';
                        dropdownMenu.style.right = '0';
                        dropdownMenu.style.minWidth = '180px';
                        dropdownMenu.style.zIndex = isProblematicPage ? '10000' : '9999';
                        dropdownMenu.style.display = 'block';
                    }
                    // For other dropdowns
                    else {
                        dropdownMenu.style.position = 'absolute';
                        dropdownMenu.style.top = rect.bottom + 'px';
                        dropdownMenu.style.display = 'block';
                        
                        if (isDesktop) {
                            // Check if dropdown would go off-screen to the right
                            const rightEdge = rect.left + dropdownMenu.offsetWidth;
                            if (rightEdge > window.innerWidth) {
                                dropdownMenu.style.left = 'auto';
                                dropdownMenu.style.right = '0';
                            } else {
                                dropdownMenu.style.left = rect.left + 'px';
                                dropdownMenu.style.right = 'auto';
                            }
                        } else {
                            // On mobile, align based on parent position
                            if (this.closest('.navbar-nav.ms-auto')) {
                                dropdownMenu.style.left = 'auto';
                                dropdownMenu.style.right = '0';
                            } else {
                                dropdownMenu.style.left = '0';
                                dropdownMenu.style.right = 'auto';
                            }
                        }
                        
                        dropdownMenu.style.zIndex = isProblematicPage ? '10000' : '9999';
                    }
                    
                    // Add a click handler to close the dropdown when clicking outside
                    const closeDropdown = function(event) {
                        if (!newToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
                            dropdownMenu.classList.remove('show');
                            document.removeEventListener('click', closeDropdown);
                        }
                    };
                    
                    // Add the click handler with a small delay
                    setTimeout(function() {
                        document.addEventListener('click', closeDropdown);
                    }, 10);
                }
            }
        });
    });
    
    // Ensure dropdown menus close when pressing escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.dropdown-menu.show').forEach(function(menu) {
                menu.classList.remove('show');
            });
        }
    });
    
    // Make sure dropdown items work correctly
    document.querySelectorAll('.dropdown-item').forEach(function(item) {
        item.addEventListener('click', function(e) {
            // Don't close the dropdown if it's a submenu toggle
            if (this.classList.contains('dropdown-toggle')) {
                e.stopPropagation();
            }
        });
    });
    
    // On problematic pages, apply an additional fix after a short delay
    if (isProblematicPage) {
        setTimeout(function() {
            // Force show/hide for dropdowns that might be stuck
            document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                menu.style.display = menu.classList.contains('show') ? 'block' : 'none';
                menu.style.zIndex = '10000';
            });
        }, 500);
    }
}); 
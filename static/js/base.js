/**
 * Base JavaScript for Dashboard
 * Handles sidebar toggle, dropdown menus, and navigation
 */

(function() {
    'use strict';

    // Get language code from HTML element
    const LANGUAGE_CODE = document.documentElement.lang || 'ar';
    const isArabic = LANGUAGE_CODE === 'ar';

    /**
     * Toggle mobile menu
     */
    window.toggleMenu = function() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');

        if (!sidebar || !overlay) return;

        // For mobile, ensure starting transform matches language before toggling
        if (!sidebar.classList.contains('open')) {
            if (isArabic) {
                sidebar.style.transform = 'translateX(100%)';
                sidebar.style.right = '0';
                sidebar.style.left = 'auto';
            } else {
                sidebar.style.transform = 'translateX(-100%)';
                sidebar.style.left = '0';
                sidebar.style.right = 'auto';
            }
            // Trigger a frame so transition applies
            requestAnimationFrame(() => {
                sidebar.classList.add('open');
                sidebar.setAttribute('aria-hidden', 'false');
            });
            overlay.classList.add('show');
        } else {
            sidebar.classList.remove('open');
            sidebar.setAttribute('aria-hidden', 'true');
            overlay.classList.remove('show');
        }
    };

    /**
     * Toggle dropdown menu
     * @param {HTMLElement} button - The button that triggers the dropdown
     */
    window.toggleDropdown = function(button) {
        const dropdownContent = button.nextElementSibling;
        const arrowIcon = button.querySelector('svg:last-child');

        if (!dropdownContent || !arrowIcon) return;

        dropdownContent.classList.toggle('hidden');
        
        if (isArabic) {
            arrowIcon.classList.toggle('rotate-90');
            arrowIcon.classList.toggle('-rotate-90');
        } else {
            arrowIcon.classList.toggle('-rotate-90');
            arrowIcon.classList.toggle('rotate-0');
        }
    };

    /**
     * Close sidebar when clicking on navigation links (mobile)
     */
    function setupNavigationLinks() {
        const navLinks = document.querySelectorAll('.sidebar nav a');
        
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 768) {
                    toggleMenu();
                }
            });
        });
    }

    /**
     * Open dropdowns if any child link is active on page load
     */
    function openActiveDropdowns() {
        const dropdownContents = document.querySelectorAll('.nav-dropdown-content');
        
        dropdownContents.forEach(content => {
            if (content.querySelector('.active')) {
                content.classList.remove('hidden');
                const button = content.previousElementSibling;
                const arrowIcon = button?.querySelector('svg:last-child');
                
                if (arrowIcon) {
                    if (isArabic) {
                        arrowIcon.classList.remove('rotate-90');
                        arrowIcon.classList.add('-rotate-90');
                    } else {
                        arrowIcon.classList.remove('-rotate-90');
                        arrowIcon.classList.add('rotate-0');
                    }
                }
            }
        });
    }

    /**
     * Handle escape key to close sidebar
     */
    function setupKeyboardNavigation() {
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const sidebar = document.getElementById('sidebar');
                if (sidebar && sidebar.classList.contains('open')) {
                    toggleMenu();
                }
            }
        });
    }

    /**
     * Auto-dismiss messages after 5 seconds
     */
    function setupMessageDismissal() {
        const messages = document.querySelectorAll('[role="alert"]');
        
        messages.forEach(message => {
            setTimeout(() => {
                message.style.transition = 'opacity 0.3s ease-out';
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
    }

    /**
     * Initialize all functionality when DOM is ready
     */
    function init() {
        setupNavigationLinks();
        openActiveDropdowns();
        setupKeyboardNavigation();
        setupMessageDismissal();
    }

    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

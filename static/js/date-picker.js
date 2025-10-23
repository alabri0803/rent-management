/**
 * Date Picker Configuration
 * Handles multi-language date picker setup using Flatpickr
 */

const DatePicker = {
    /**
     * Initialize date pickers on the page
     * @param {string} selector - CSS selector for date inputs
     * @param {object} customOptions - Custom Flatpickr options
     */
    init(selector = 'input[type="date"]', customOptions = {}) {
        if (!window.flatpickr) {
            console.warn('Flatpickr library not loaded');
            return;
        }

        // Detect current language
        const currentLang = document.documentElement.lang || 'ar';
        const isArabic = currentLang === 'ar';

        // Default options
        const defaultOptions = {
            dateFormat: 'Y-m-d',
            altInput: true,
            altFormat: isArabic ? 'd/m/Y' : 'M d, Y',
            allowInput: true,
            locale: isArabic ? (flatpickr.l10ns.ar || flatpickr.l10ns.default) : flatpickr.l10ns.default,
            disableMobile: false,
            // Accessibility
            ariaDateFormat: 'F j, Y',
            // Theme
            theme: 'light',
        };

        // Merge options
        const options = { ...defaultOptions, ...customOptions };

        // Initialize all matching inputs
        const inputs = document.querySelectorAll(selector);
        inputs.forEach(input => {
            try {
                flatpickr(input, options);
            } catch (error) {
                console.error('Error initializing date picker:', error);
            }
        });
    },

    /**
     * Initialize specific date fields by name
     * @param {array} fieldNames - Array of field names
     * @param {object} options - Flatpickr options
     */
    initFields(fieldNames = [], options = {}) {
        fieldNames.forEach(fieldName => {
            this.init(`input[name="${fieldName}"]`, options);
        });
    },

    /**
     * Initialize date range picker
     * @param {string} startSelector - Start date selector
     * @param {string} endSelector - End date selector
     */
    initRange(startSelector, endSelector) {
        if (!window.flatpickr) return;

        const currentLang = document.documentElement.lang || 'ar';
        const isArabic = currentLang === 'ar';

        const startInput = document.querySelector(startSelector);
        const endInput = document.querySelector(endSelector);

        if (!startInput || !endInput) return;

        // Start date picker
        const startPicker = flatpickr(startInput, {
            dateFormat: 'Y-m-d',
            altInput: true,
            altFormat: isArabic ? 'd/m/Y' : 'M d, Y',
            locale: isArabic ? (flatpickr.l10ns.ar || flatpickr.l10ns.default) : flatpickr.l10ns.default,
            onChange: function(selectedDates, dateStr, instance) {
                // Set minimum date for end picker
                if (selectedDates[0]) {
                    endPicker.set('minDate', selectedDates[0]);
                }
            }
        });

        // End date picker
        const endPicker = flatpickr(endInput, {
            dateFormat: 'Y-m-d',
            altInput: true,
            altFormat: isArabic ? 'd/m/Y' : 'M d, Y',
            locale: isArabic ? (flatpickr.l10ns.ar || flatpickr.l10ns.default) : flatpickr.l10ns.default,
            onChange: function(selectedDates, dateStr, instance) {
                // Set maximum date for start picker
                if (selectedDates[0]) {
                    startPicker.set('maxDate', selectedDates[0]);
                }
            }
        });
    },

    /**
     * Destroy all date pickers
     */
    destroy() {
        const pickers = document.querySelectorAll('.flatpickr-input');
        pickers.forEach(picker => {
            if (picker._flatpickr) {
                picker._flatpickr.destroy();
            }
        });
    }
};

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize common date fields
    DatePicker.initFields([
        'start_date',
        'end_date',
        'payment_date',
        'check_date',
        'expense_date',
        'issue_date',
        'due_date',
        'collection_date',
        'received_date'
    ]);
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DatePicker;
}

/**
 * Form Utilities and Validation
 * Common form handling functions
 */

const FormUtils = {
    /**
     * Initialize form enhancements
     */
    init() {
        this.setupFileUploads();
        this.setupFormValidation();
        this.setupAutoSave();
        this.setupDynamicFields();
    },

    /**
     * Setup custom file upload styling
     */
    setupFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            // Get or create label
            let label = input.nextElementSibling;
            if (!label || !label.classList.contains('file-upload-text')) {
                label = document.createElement('span');
                label.className = 'file-upload-text text-sm text-gray-600 mt-2 block';
                input.parentNode.insertBefore(label, input.nextSibling);
            }

            // Get current language
            const currentLang = document.documentElement.lang || 'ar';
            const texts = {
                ar: {
                    noFile: 'لم يتم تحديد أي ملف',
                    chooseFile: 'اختيار ملف'
                },
                en: {
                    noFile: 'No file chosen',
                    chooseFile: 'Choose file'
                }
            };

            const lang = texts[currentLang] || texts.ar;
            label.textContent = lang.noFile;

            // Update on file selection
            input.addEventListener('change', function() {
                if (this.files && this.files.length > 0) {
                    label.textContent = this.files[0].name;
                    label.classList.add('text-green-600', 'font-semibold');
                } else {
                    label.textContent = lang.noFile;
                    label.classList.remove('text-green-600', 'font-semibold');
                }
            });
        });
    },

    /**
     * Setup client-side form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showValidationErrors(form);
                }
            });

            // Real-time validation
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
            });
        });
    },

    /**
     * Validate a single field
     * @param {HTMLElement} field - Input field to validate
     * @returns {boolean} - Validation result
     */
    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        let isValid = true;
        let errorMessage = '';

        // Required check
        if (required && !value) {
            isValid = false;
            errorMessage = 'هذا الحقل مطلوب';
        }

        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'البريد الإلكتروني غير صحيح';
            }
        }

        // Number validation
        if (type === 'number' && value) {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            
            if (min && parseFloat(value) < parseFloat(min)) {
                isValid = false;
                errorMessage = `القيمة يجب أن تكون ${min} أو أكثر`;
            }
            
            if (max && parseFloat(value) > parseFloat(max)) {
                isValid = false;
                errorMessage = `القيمة يجب أن تكون ${max} أو أقل`;
            }
        }

        // Phone validation (Oman format)
        if (field.name === 'phone_number' && value) {
            const phoneRegex = /^(9[0-9]{7}|[2-9][0-9]{6})$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = 'رقم الهاتف غير صحيح';
            }
        }

        // Update field state
        this.updateFieldState(field, isValid, errorMessage);
        
        return isValid;
    },

    /**
     * Validate entire form
     * @param {HTMLFormElement} form - Form to validate
     * @returns {boolean} - Validation result
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    },

    /**
     * Update field visual state
     * @param {HTMLElement} field - Input field
     * @param {boolean} isValid - Validation result
     * @param {string} errorMessage - Error message to display
     */
    updateFieldState(field, isValid, errorMessage = '') {
        const parent = field.closest('.form-group') || field.parentElement;
        
        // Remove previous states
        parent.classList.remove('has-error', 'has-success');
        
        // Remove previous error message
        const existingError = parent.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }

        if (!isValid) {
            parent.classList.add('has-error');
            
            // Add error message
            if (errorMessage) {
                const errorEl = document.createElement('p');
                errorEl.className = 'form-error';
                errorEl.textContent = errorMessage;
                field.parentNode.insertBefore(errorEl, field.nextSibling);
            }
        } else if (field.value.trim()) {
            parent.classList.add('has-success');
        }
    },

    /**
     * Show validation errors summary
     * @param {HTMLFormElement} form - Form element
     */
    showValidationErrors(form) {
        const errors = form.querySelectorAll('.has-error');
        
        if (errors.length > 0) {
            // Scroll to first error
            errors[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Focus first error field
            const firstErrorInput = errors[0].querySelector('input, select, textarea');
            if (firstErrorInput) {
                firstErrorInput.focus();
            }
        }
    },

    /**
     * Setup auto-save for forms
     */
    setupAutoSave() {
        const forms = document.querySelectorAll('form[data-autosave]');
        
        forms.forEach(form => {
            const formId = form.id || 'form_' + Date.now();
            let saveTimeout;

            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    clearTimeout(saveTimeout);
                    saveTimeout = setTimeout(() => {
                        this.saveFormData(formId, form);
                    }, 1000);
                });
            });

            // Restore saved data
            this.restoreFormData(formId, form);
        });
    },

    /**
     * Save form data to localStorage
     * @param {string} formId - Form identifier
     * @param {HTMLFormElement} form - Form element
     */
    saveFormData(formId, form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        try {
            localStorage.setItem(`form_${formId}`, JSON.stringify(data));
        } catch (e) {
            console.error('Failed to save form data:', e);
        }
    },

    /**
     * Restore form data from localStorage
     * @param {string} formId - Form identifier
     * @param {HTMLFormElement} form - Form element
     */
    restoreFormData(formId, form) {
        try {
            const savedData = localStorage.getItem(`form_${formId}`);
            if (savedData) {
                const data = JSON.parse(savedData);
                
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && !input.value) {
                        input.value = data[key];
                    }
                });
            }
        } catch (e) {
            console.error('Failed to restore form data:', e);
        }
    },

    /**
     * Clear saved form data
     * @param {string} formId - Form identifier
     */
    clearSavedData(formId) {
        localStorage.removeItem(`form_${formId}`);
    },

    /**
     * Setup dynamic form fields (show/hide based on conditions)
     */
    setupDynamicFields() {
        // Payment method fields
        const paymentMethodSelects = document.querySelectorAll('select[name="payment_method"]');
        paymentMethodSelects.forEach(select => {
            const updateFields = () => {
                const value = select.value;
                const checkFields = document.querySelectorAll('[data-show-for="check"]');
                
                checkFields.forEach(field => {
                    if (value === 'check') {
                        field.style.display = '';
                        field.querySelectorAll('input, select').forEach(input => {
                            input.removeAttribute('disabled');
                        });
                    } else {
                        field.style.display = 'none';
                        field.querySelectorAll('input, select').forEach(input => {
                            input.setAttribute('disabled', 'disabled');
                        });
                    }
                });
            };

            select.addEventListener('change', updateFields);
            updateFields(); // Initial state
        });
    },

    /**
     * Submit form via AJAX
     * @param {HTMLFormElement} form - Form to submit
     * @param {object} options - Submit options
     * @returns {Promise} - Submit promise
     */
    async submitForm(form, options = {}) {
        const {
            method = form.method || 'POST',
            url = form.action,
            onSuccess = () => {},
            onError = () => {},
            showLoading = true
        } = options;

        if (showLoading) {
            form.classList.add('form-loading');
        }

        try {
            const formData = new FormData(form);
            const response = await fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok) {
                onSuccess(data);
            } else {
                onError(data);
            }

            return data;
        } catch (error) {
            console.error('Form submission error:', error);
            onError(error);
            throw error;
        } finally {
            if (showLoading) {
                form.classList.remove('form-loading');
            }
        }
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    FormUtils.init();
});

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormUtils;
}

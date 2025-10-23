/**
 * Modal Management System
 * Handles opening, closing, and managing modal dialogs
 */

const ModalManager = {
    activeModal: null,
    
    /**
     * Open a modal
     * @param {string} modalId - ID of the modal element
     */
    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.error(`Modal with ID "${modalId}" not found`);
            return;
        }

        // Close any active modal first
        if (this.activeModal && this.activeModal !== modal) {
            this.close(this.activeModal.id);
        }

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
        
        this.activeModal = modal;

        // Focus first focusable element
        const focusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable) {
            setTimeout(() => focusable.focus(), 100);
        }

        // Emit event
        modal.dispatchEvent(new CustomEvent('modal:opened', { detail: { modalId } }));
    },

    /**
     * Close a modal
     * @param {string} modalId - ID of the modal element
     */
    close(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
        
        if (this.activeModal === modal) {
            this.activeModal = null;
        }

        // Emit event
        modal.dispatchEvent(new CustomEvent('modal:closed', { detail: { modalId } }));
    },

    /**
     * Toggle modal state
     * @param {string} modalId - ID of the modal element
     */
    toggle(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        if (modal.classList.contains('hidden')) {
            this.open(modalId);
        } else {
            this.close(modalId);
        }
    },

    /**
     * Initialize modal close handlers
     */
    init() {
        // Close on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                const modal = e.target.closest('[id$="Modal"]');
                if (modal) {
                    this.close(modal.id);
                }
            }
        });

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close(this.activeModal.id);
            }
        });

        // Close buttons
        document.querySelectorAll('[data-modal-close]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = btn.getAttribute('data-modal-close');
                this.close(modalId);
            });
        });

        // Open buttons
        document.querySelectorAll('[data-modal-open]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = btn.getAttribute('data-modal-open');
                this.open(modalId);
            });
        });
    },

    /**
     * Create a confirmation modal
     * @param {object} options - Modal options
     * @returns {Promise} - Resolves on confirm, rejects on cancel
     */
    confirm(options = {}) {
        const {
            title = 'تأكيد',
            message = 'هل أنت متأكد؟',
            confirmText = 'تأكيد',
            cancelText = 'إلغاء',
            confirmClass = 'bg-red-600 hover:bg-red-700',
            cancelClass = 'bg-gray-200 hover:bg-gray-300'
        } = options;

        return new Promise((resolve, reject) => {
            // Create modal HTML
            const modalId = 'confirmModal_' + Date.now();
            const modalHTML = `
                <div id="${modalId}" class="fixed inset-0 z-50 hidden items-center justify-center p-4 modal-backdrop bg-black/50">
                    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 transform transition-all" role="dialog" aria-modal="true">
                        <h3 class="text-xl font-bold text-gray-900 mb-4">${title}</h3>
                        <p class="text-gray-600 mb-6">${message}</p>
                        <div class="flex gap-3 justify-end">
                            <button type="button" class="px-4 py-2 rounded-lg font-semibold transition-colors ${cancelClass}" data-action="cancel">
                                ${cancelText}
                            </button>
                            <button type="button" class="px-4 py-2 rounded-lg font-semibold text-white transition-colors ${confirmClass}" data-action="confirm">
                                ${confirmText}
                            </button>
                        </div>
                    </div>
                </div>
            `;

            // Add to DOM
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modal = document.getElementById(modalId);

            // Handle actions
            modal.querySelector('[data-action="confirm"]').addEventListener('click', () => {
                this.close(modalId);
                setTimeout(() => modal.remove(), 300);
                resolve(true);
            });

            modal.querySelector('[data-action="cancel"]').addEventListener('click', () => {
                this.close(modalId);
                setTimeout(() => modal.remove(), 300);
                reject(false);
            });

            // Open modal
            this.open(modalId);
        });
    },

    /**
     * Show an alert modal
     * @param {object} options - Alert options
     */
    alert(options = {}) {
        const {
            title = 'تنبيه',
            message = '',
            type = 'info', // info, success, warning, error
            okText = 'حسناً'
        } = options;

        const icons = {
            info: '&#8505;',
            success: '&#10004;',
            warning: '&#9888;',
            error: '&#10006;'
        };

        const colors = {
            info: 'bg-blue-100 text-blue-600',
            success: 'bg-green-100 text-green-600',
            warning: 'bg-yellow-100 text-yellow-600',
            error: 'bg-red-100 text-red-600'
        };

        return new Promise((resolve) => {
            const modalId = 'alertModal_' + Date.now();
            const modalHTML = `
                <div id="${modalId}" class="fixed inset-0 z-50 hidden items-center justify-center p-4 modal-backdrop bg-black/50">
                    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 transform transition-all">
                        <div class="flex items-center gap-4 mb-4">
                            <div class="w-12 h-12 rounded-full ${colors[type]} flex items-center justify-center text-2xl">
                                ${icons[type]}
                            </div>
                            <h3 class="text-xl font-bold text-gray-900">${title}</h3>
                        </div>
                        <p class="text-gray-600 mb-6">${message}</p>
                        <div class="flex justify-end">
                            <button type="button" class="px-6 py-2 rounded-lg font-semibold bg-primary-700 text-white hover:bg-primary-800 transition-colors" data-action="ok">
                                ${okText}
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modal = document.getElementById(modalId);

            modal.querySelector('[data-action="ok"]').addEventListener('click', () => {
                this.close(modalId);
                setTimeout(() => modal.remove(), 300);
                resolve();
            });

            this.open(modalId);
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    ModalManager.init();
});

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalManager;
}

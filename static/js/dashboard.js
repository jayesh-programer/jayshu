/**
 * Admin Dashboard Vanilla JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  initModals();
  initStockAdjustment();
  initSidebarToggle();
});

function initModals() {
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modalId = this.getAttribute('data-modal-open');
      const modal = document.getElementById(modalId);
      if (modal) modal.classList.add('active');
    });
  });

  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modal = this.closest('.modal-overlay');
      if (modal) modal.classList.remove('active');
    });
  });

  // Close when clicking overlay backdrop
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
      if (e.target === this) {
        this.classList.remove('active');
      }
    });
  });
}

function initStockAdjustment() {
  document.querySelectorAll('.btn-adjust-stock').forEach(btn => {
    btn.addEventListener('click', function () {
      const productId = this.getAttribute('data-product-id');
      const productName = this.getAttribute('data-product-name');
      const currentStock = this.getAttribute('data-current-stock');

      const modal = document.getElementById('modal-stock-adjust');
      const form = document.getElementById('form-stock-adjust');
      const title = document.getElementById('adjust-product-title');
      const currentEl = document.getElementById('adjust-current-stock');

      if (modal && form) {
        form.action = `/dashboard/inventory/${productId}/adjust/`;
        if (title) title.textContent = productName;
        if (currentEl) currentEl.textContent = currentStock;
        modal.classList.add('active');
      }
    });
  });
}

function initSidebarToggle() {
  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.dashboard-sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
}

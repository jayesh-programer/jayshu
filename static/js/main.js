/**
 * Storefront Interactive Vanilla JavaScript
 * Zero external frameworks - Pure standard JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  initCsrf();
  initToast();
  initAddToCartForms();
  initQuantityControls();
  initWishlistButtons();
  initProductGallery();
  initMobileMenu();
  initAlertDismissal();
});

// CSRF Cookie extraction helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

let csrfToken = null;
function initCsrf() {
  csrfToken = getCookie('csrftoken');
}

// Toast notification helper
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
function initToast() {
  window.showToast = showToast;
}

// Alert dismissal
function initAlertDismissal() {
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', function () {
      const alert = this.closest('.alert');
      if (alert) alert.remove();
    });
  });
}

// AJAX Add to Cart
function initAddToCartForms() {
  document.querySelectorAll('.ajax-add-to-cart').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Adding...';
      }

      const formData = new FormData(form);

      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken || formData.get('csrfmiddlewaretoken')
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(data.message, 'success');
          // Update cart badges in header
          document.querySelectorAll('.cart-count-badge').forEach(badge => {
            badge.textContent = data.total_items;
          });
        } else {
          showToast(data.message || 'Could not add to cart.', 'error');
        }
      })
      .catch(err => {
        console.error(err);
        showToast('An error occurred. Please try again.', 'error');
      })
      .finally(() => {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }
      });
    });
  });
}

// Cart Quantity Stepper (+ / -)
function initQuantityControls() {
  document.querySelectorAll('.qty-stepper').forEach(stepper => {
    const minusBtn = stepper.querySelector('.btn-qty-minus');
    const plusBtn = stepper.querySelector('.btn-qty-plus');
    const input = stepper.querySelector('.qty-input');
    const form = stepper.closest('form');

    if (minusBtn && plusBtn && input) {
      minusBtn.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        if (val > 1) {
          input.value = val - 1;
          if (form && form.classList.contains('cart-update-form')) {
            updateCartItemAjax(form);
          }
        }
      });

      plusBtn.addEventListener('click', () => {
        let val = parseInt(input.value) || 1;
        input.value = val + 1;
        if (form && form.classList.contains('cart-update-form')) {
          updateCartItemAjax(form);
        }
      });

      input.addEventListener('change', () => {
        let val = parseInt(input.value) || 1;
        if (val < 1) input.value = 1;
        if (form && form.classList.contains('cart-update-form')) {
          updateCartItemAjax(form);
        }
      });
    }
  });
}

function updateCartItemAjax(form) {
  const formData = new FormData(form);
  fetch(form.action, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': csrfToken || formData.get('csrfmiddlewaretoken')
    },
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.message, 'success');
      // Update line total on page
      const row = form.closest('.cart-item-row');
      if (row && data.line_total !== undefined) {
        const lineTotalEl = row.querySelector('.item-line-total');
        if (lineTotalEl) lineTotalEl.textContent = '₹' + data.line_total.toFixed(2);
      }
      // Reload or refresh subtotal if needed
      window.location.reload();
    }
  })
  .catch(err => console.error(err));
}

// Wishlist Toggle
function initWishlistButtons() {
  document.querySelectorAll('.btn-wishlist-toggle').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.getAttribute('data-url');
      if (!url) return;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken
        }
      })
      .then(res => {
        if (res.status === 403 || res.redirected) {
          window.location.href = '/accounts/login/';
          return;
        }
        return res.json();
      })
      .then(data => {
        if (data && data.success) {
          showToast(data.message, 'success');
          if (data.saved) {
            btn.classList.add('active');
          } else {
            btn.classList.remove('active');
          }
          document.querySelectorAll('.wishlist-count-badge').forEach(badge => {
            badge.textContent = data.wishlist_count;
          });
        }
      })
      .catch(err => console.error(err));
    });
  });
}

// Product Detail Image Gallery
function initProductGallery() {
  const mainImage = document.getElementById('product-main-image');
  const thumbs = document.querySelectorAll('.product-thumb-item');

  if (mainImage && thumbs.length) {
    thumbs.forEach(thumb => {
      thumb.addEventListener('click', function () {
        thumbs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        const newSrc = this.getAttribute('data-full-src');
        if (newSrc) {
          mainImage.src = newSrc;
        }
      });
    });
  }
}

// Mobile Menu Toggle
function initMobileMenu() {
  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const menu = document.getElementById('mobile-drawer');
  if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', () => {
      menu.classList.toggle('active');
    });
  }
}

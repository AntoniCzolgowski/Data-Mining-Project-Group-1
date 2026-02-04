/* ============================================
   CU Boulder Data Mining Project - JavaScript
   Group 1: Sam Goodell, Will Creager, Antoni Czolgowski
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
  
  // ---------- Mobile Menu Toggle ----------
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const navList = document.querySelector('.nav-list');
  
  if (mobileMenuBtn && navList) {
    mobileMenuBtn.addEventListener('click', function() {
      navList.classList.toggle('active');
      
      // Animate hamburger icon
      const spans = this.querySelectorAll('span');
      spans.forEach(span => span.classList.toggle('active'));
    });
    
    // Close menu when clicking a link
    const navLinks = navList.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
          navList.classList.remove('active');
        }
      });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (!navList.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
        navList.classList.remove('active');
      }
    });
  }
  
  // ---------- Active Navigation Link ----------
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
  
  // ---------- Smooth Scroll for Anchor Links ----------
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const targetPosition = targetElement.offsetTop - headerHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // ---------- Scroll-based Header Shadow ----------
  const header = document.querySelector('.header');
  
  if (header) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 10) {
        header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
      } else {
        header.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
      }
    });
  }
  
  // ---------- Intersection Observer for Animations ----------
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in-visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  // Observe elements with fade-in class
  document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
  });
  
  // ---------- Research Question Expand/Collapse (Future Feature) ----------
  const questionItems = document.querySelectorAll('.question-item');
  
  questionItems.forEach(item => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', function() {
      const details = this.querySelector('.question-details');
      if (details) {
        details.classList.toggle('expanded');
      }
    });
  });
  
  // ---------- Console Welcome Message ----------
  console.log('%c🎓 CU Boulder Data Mining Project', 'font-size: 16px; font-weight: bold; color: #CFB87C;');
  console.log('%cGroup 1: Sam Goodell, Will Creager, Antoni Czolgowski', 'font-size: 12px; color: #565A5C;');
  console.log('%cCSCI 5502 - Spring 2026', 'font-size: 12px; color: #565A5C;');
  
});

// ---------- Utility Functions ----------

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Format date for display
 */
function formatDate(date) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(date).toLocaleDateString('en-US', options);
}

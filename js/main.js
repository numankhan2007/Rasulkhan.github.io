/**
 * Rasul Khan Personal Portfolio
 * Main Client-Side Controller (Vanilla ES6 + Modern Web APIs)
 * Compatibility: Pure static GitHub Pages hosting
 */

// 1. Client-side Skeleton Loading Screen Dismissal (Requirement R3)
(function initSkeletonLoader() {
  const minDisplayTime = 400; // Minimum display time (ms) to prevent jarring visual flash
  const maxSafetyTimeout = 1500; // Safety fallback timeout so content is never trapped
  const startTime = Date.now();

  function dismissSkeleton() {
    const skeleton = document.getElementById('skeleton-screen');
    const loader = document.getElementById('ftco-loader');

    if (skeleton && !skeleton.classList.contains('skeleton-hidden')) {
      const elapsed = Date.now() - startTime;
      const remainingTime = Math.max(0, minDisplayTime - elapsed);

      setTimeout(function() {
        skeleton.classList.add('skeleton-hidden');
        skeleton.classList.add('hidden');
        skeleton.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('is-loading');
        document.body.classList.add('is-loaded');

        // Cleanup from DOM flow after transition
        setTimeout(function() {
          skeleton.style.display = 'none';
        }, 450);
      }, remainingTime);
    }

    if (loader && loader.classList.contains('show')) {
      loader.classList.remove('show');
    }
  }

  // Primary trigger: window 'load' event (stylesheets, fonts, and assets ready)
  window.addEventListener('load', dismissSkeleton);

  // Fallback trigger: safety timeout in case of network latency
  setTimeout(dismissSkeleton, maxSafetyTimeout);
})();

// 2. High-Performance IntersectionObserver for Scroll-Triggered Reveals (Requirement R3)
(function initScrollReveals() {
  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(function(entries, observer) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          entry.target.classList.add('ftco-animated');
          entry.target.classList.add('fadeInUp');
          observer.unobserve(entry.target);
        }
      });
    }, {
      root: null,
      rootMargin: '0px 0px -40px 0px',
      threshold: 0.12
    });

    document.querySelectorAll('.reveal-on-scroll, .ftco-animate').forEach(function(el) {
      revealObserver.observe(el);
    });
  } else {
    // Fallback if IntersectionObserver is unsupported
    document.querySelectorAll('.reveal-on-scroll, .ftco-animate').forEach(function(el) {
      el.classList.add('is-revealed');
      el.classList.add('ftco-animated');
    });
  }
})();

// 3. Hardware-Accelerated Counter Roll Animation via requestAnimationFrame (Requirement R3)
(function initStatCounters() {
  const counterSection = document.getElementById('section-counter');
  if (!counterSection) return;

  let animated = false;

  function triggerCounterRoll() {
    if (animated) return;
    animated = true;

    const counterElements = counterSection.querySelectorAll('.number[data-number]');
    counterElements.forEach(function(numEl) {
      const target = parseInt(numEl.getAttribute('data-number'), 10) || 0;
      const duration = 1600; // ms
      const startTime = performance.now();

      function updateCounter(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Exponential ease-out curve
        const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const currentVal = Math.floor(ease * target);
        numEl.textContent = currentVal.toLocaleString();

        if (progress < 1) {
          requestAnimationFrame(updateCounter);
        } else {
          numEl.textContent = target.toLocaleString();
        }
      }
      requestAnimationFrame(updateCounter);
    });
  }

  if ('IntersectionObserver' in window) {
    const counterObserver = new IntersectionObserver(function(entries, observer) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          triggerCounterRoll();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.25 });

    counterObserver.observe(counterSection);
  } else {
    triggerCounterRoll();
  }
})();

// 4. Smooth Scrolling Navigation Interceptor (Requirement R3)
(function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (!targetId || targetId === '#') return;
      const targetElement = document.querySelector(targetId);
      if (!targetElement) return;

      e.preventDefault();
      targetElement.scrollIntoView({
        behavior: 'smooth'
      });

      // Auto-collapse mobile navbar after clicking a section link
      const navCollapse = document.getElementById('ftco-nav');
      if (navCollapse && navCollapse.classList.contains('show')) {
        const toggler = document.querySelector('.navbar-toggler');
        if (toggler) toggler.click();
      }
    });
  });
})();

// 5. Mobile Navbar Hamburger Toggle
(function initMobileNav() {
  document.querySelectorAll('.navbar-toggler').forEach(function(toggler) {
    toggler.addEventListener('click', function() {
      const targetSelector = this.getAttribute('data-target') || '#ftco-nav';
      const target = document.querySelector(targetSelector);
      if (target) {
        target.classList.toggle('show');
      }
    });
  });
})();

// 6. Role Typing Animation (Cycling through specified roles)
(function initTypingAnimation() {
  const typingElement = document.getElementById('typing-animation');
  if (!typingElement) return;

  const roles = [
    'Data Analyst',
    'Data operation analyst',
    'Data Scientist',
    'Business Analyst',
    'BI Developer'
  ];

  let roleIndex = 0;
  let charIndex = 0;
  let isDeleting = false;

  function typeTick() {
    const currentRole = roles[roleIndex];

    if (isDeleting) {
      typingElement.textContent = currentRole.substring(0, charIndex - 1);
      charIndex--;
      if (charIndex === 0) {
        isDeleting = false;
        roleIndex = (roleIndex + 1) % roles.length;
        setTimeout(typeTick, 400);
        return;
      }
      setTimeout(typeTick, 50);
    } else {
      typingElement.textContent = currentRole.substring(0, charIndex + 1);
      charIndex++;
      if (charIndex === currentRole.length) {
        isDeleting = true;
        setTimeout(typeTick, 2200);
        return;
      }
      setTimeout(typeTick, 110);
    }
  }

  typeTick();
})();

// 7. Legacy Library Enhancements (jQuery plugins graceful integration)
(function($) {
  if (typeof $ === 'undefined') return;

  $(document).ready(function() {
    // Navbar scroll state
    $(window).scroll(function() {
      const st = $(this).scrollTop();
      const navbar = $('.ftco_navbar');
      if (st > 150) {
        if (!navbar.hasClass('scrolled')) navbar.addClass('scrolled');
      } else {
        if (navbar.hasClass('scrolled')) navbar.removeClass('scrolled sleep');
      }
      if (st > 350) {
        if (!navbar.hasClass('awake')) navbar.addClass('awake');
      } else {
        if (navbar.hasClass('awake')) navbar.removeClass('awake');
      }
    });

    // Image popup if magnificPopup is available
    if ($.fn.magnificPopup) {
      $('.image-popup').magnificPopup({
        type: 'image',
        closeOnContentClick: true,
        closeBtnInside: false,
        fixedContentPos: true,
        mainClass: 'mfp-no-margins mfp-with-zoom',
        gallery: { enabled: true, navigateByImgClick: true, preload: [0, 1] },
        image: { verticalFit: true },
        zoom: { enabled: true, duration: 300 }
      });
    }

    // Single hero slide if owlCarousel is available
    if ($.fn.owlCarousel && $('.home-slider').length) {
      $('.home-slider').owlCarousel({
        loop: false,
        autoplay: false,
        margin: 0,
        nav: false,
        items: 1
      });
    }
  });
})(typeof jQuery !== 'undefined' ? jQuery : undefined);

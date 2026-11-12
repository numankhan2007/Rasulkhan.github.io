/**
 * Rasul Khan Personal Portfolio
 * Static Client-Side Controller (Pure Vanilla ES6, GitHub Pages Ready)
 */

(function () {
  'use strict';

  const prefersReducedMotion = () =>
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1. Initial Skeleton Screen Dismissal & Per-Image Shimmer Resolution
  (function initSkeletonLoaders() {
    const minDisplayTime = 220;
    const maxSafetyTimeout = 900;
    const startTime = Date.now();
    let dismissed = false;

    function dismissSkeleton() {
      if (dismissed) return;
      dismissed = true;

      const skeleton = document.getElementById('skeleton-screen');
      if (!skeleton) return;

      const elapsed = Date.now() - startTime;
      const delay = prefersReducedMotion() ? 0 : Math.max(0, minDisplayTime - elapsed);

      setTimeout(() => {
        skeleton.classList.add('skeleton-hidden', 'hidden');
        skeleton.setAttribute('aria-hidden', 'true');
        setTimeout(() => {
          skeleton.style.display = 'none';
        }, 380);
      }, delay);
    }

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
      dismissSkeleton();
    } else {
      document.addEventListener('DOMContentLoaded', dismissSkeleton, { once: true });
    }
    window.addEventListener('load', dismissSkeleton);
    setTimeout(dismissSkeleton, maxSafetyTimeout);

    // Per-image skeleton shimmer cleanup
    document.querySelectorAll('.img-skeleton img').forEach((img) => {
      const container = img.closest('.img-skeleton');
      if (!container) return;

      const markLoaded = () => container.classList.add('is-loaded');

      if (img.complete && img.naturalWidth > 0) {
        markLoaded();
      } else {
        img.addEventListener('load', markLoaded, { once: true });
        img.addEventListener('error', markLoaded, { once: true });
      }
    });
  })();

  // 2. Sticky Header Scroll Elevation & Scroll Progress Fallback
  (function initScrollChrome() {
    const header = document.getElementById('site-header');
    const progressEl = document.getElementById('scroll-progress');
    const supportsScrollTimeline =
      typeof CSS !== 'undefined' && CSS.supports && CSS.supports('animation-timeline: scroll()');

    let ticking = false;

    function updateOnScroll() {
      ticking = false;
      const scrollY = window.scrollY || window.pageYOffset || 0;

      if (header) {
        header.classList.toggle('is-scrolled', scrollY > 16);
      }

      if (progressEl && !supportsScrollTimeline) {
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const ratio = docHeight > 0 ? Math.min(1, Math.max(0, scrollY / docHeight)) : 0;
        progressEl.style.setProperty('--scroll-progress', ratio.toFixed(4));
      }
    }

    window.addEventListener(
      'scroll',
      () => {
        if (!ticking) {
          ticking = true;
          requestAnimationFrame(updateOnScroll);
        }
      },
      { passive: true }
    );
    updateOnScroll();
  })();

  // 3. Responsive Navigation (Popover on Mobile, Inline on Desktop)
  (function initResponsiveNav() {
    const menu = document.getElementById('site-menu');
    const toggleBtn = document.getElementById('menu-toggle');
    if (!menu || !toggleBtn) return;

    const mobileQuery = window.matchMedia('(max-width: 767px)');
    const supportsPopover = Object.prototype.hasOwnProperty.call(HTMLElement.prototype, 'popover');

    function syncNavMode() {
      if (mobileQuery.matches) {
        if (supportsPopover) {
          menu.setAttribute('popover', 'auto');
        }
      } else {
        if (supportsPopover && menu.matches(':popover-open')) {
          menu.hidePopover();
        }
        menu.removeAttribute('popover');
        menu.classList.remove('is-open');
        toggleBtn.setAttribute('aria-expanded', 'false');
      }
    }

    if (supportsPopover) {
      menu.addEventListener('toggle', (event) => {
        toggleBtn.setAttribute('aria-expanded', event.newState === 'open' ? 'true' : 'false');
      });
    } else {
      toggleBtn.addEventListener('click', () => {
        const isOpen = menu.classList.toggle('is-open');
        toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    }

    // Close mobile menu when a link is activated
    menu.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener('click', () => {
        if (mobileQuery.matches) {
          if (supportsPopover && menu.matches(':popover-open')) {
            menu.hidePopover();
          } else {
            menu.classList.remove('is-open');
            toggleBtn.setAttribute('aria-expanded', 'false');
          }
        }
      });
    });

    if (mobileQuery.addEventListener) {
      mobileQuery.addEventListener('change', syncNavMode);
    } else {
      mobileQuery.addListener(syncNavMode);
    }
    syncNavMode();
  })();

  // 4. Smooth Anchor Scrolling & Scrollspy
  (function initScrollspyAndSmoothNav() {
    const navLinks = Array.from(document.querySelectorAll('#site-menu a[href^="#"]'));
    const sections = Array.from(document.querySelectorAll('main section[id]'));

    navLinks.forEach((anchor) => {
      anchor.addEventListener('click', (event) => {
        const targetId = anchor.getAttribute('href');
        if (!targetId || targetId === '#') return;
        const target = document.querySelector(targetId);
        if (!target) return;

        event.preventDefault();
        target.scrollIntoView({
          behavior: prefersReducedMotion() ? 'auto' : 'smooth',
          block: 'start',
        });
        target.focus({ preventScroll: true });
      });
    });

    const supportsScrollTargetGroup =
      typeof CSS !== 'undefined' && CSS.supports && CSS.supports('scroll-target-group: auto');

    if (supportsScrollTargetGroup) {
      const syncAriaCurrent = () => {
        const active = document.querySelector('#site-menu a:target-current');
        navLinks.forEach((link) => {
          link.setAttribute('aria-current', link === active ? 'true' : 'false');
        });
      };
      syncAriaCurrent();
      document.addEventListener('scrollend', syncAriaCurrent);
    } else if ('IntersectionObserver' in window && sections.length) {
      const spyObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const activeHref = `#${entry.target.id}`;
            navLinks.forEach((link) => {
              const isActive = link.getAttribute('href') === activeHref;
              link.classList.toggle('target-current', isActive);
              link.setAttribute('aria-current', isActive ? 'true' : 'false');
            });
          });
        },
        { rootMargin: '-25% 0px -60% 0px', threshold: 0 }
      );

      sections.forEach((sec) => spyObserver.observe(sec));
    }
  })();

  // 5. Scroll Reveal Animations (IntersectionObserver Fallback)
  (function initScrollReveals() {
    const elements = document.querySelectorAll('.reveal-on-scroll');
    if (!elements.length) return;

    if (prefersReducedMotion() || !('IntersectionObserver' in window)) {
      elements.forEach((el) => el.classList.add('is-revealed'));
      return;
    }

    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -40px 0px', threshold: 0.1 }
    );

    elements.forEach((el) => revealObserver.observe(el));
  })();

  // 6. Animated Stat Counters (requestAnimationFrame)
  (function initStatCounters() {
    const counters = Array.from(document.querySelectorAll('.number[data-number]'));
    if (!counters.length) return;

    function animateValue(el) {
      if (el.dataset.counted === 'true') return;
      el.dataset.counted = 'true';

      const target = parseInt(el.getAttribute('data-number'), 10) || 0;
      if (prefersReducedMotion()) {
        el.textContent = target.toLocaleString();
        return;
      }

      const duration = 1100;
      const start = performance.now();

      function step(now) {
        const progress = Math.min(1, (now - start) / duration);
        const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        el.textContent = Math.round(eased * target).toLocaleString();
        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          el.textContent = target.toLocaleString();
        }
      }

      requestAnimationFrame(step);
      setTimeout(() => {
        el.textContent = target.toLocaleString();
      }, duration + 80);
    }

    if (!('IntersectionObserver' in window)) {
      counters.forEach(animateValue);
      return;
    }

    const counterObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateValue(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.25 }
    );

    counters.forEach((el) => counterObserver.observe(el));
  })();

  // 7. Role Typing Animation with WCAG 2.2.2 Pause/Play Control
  (function initTypingAnimation() {
    const typingEl = document.getElementById('typing-animation');
    const toggleBtn = document.getElementById('motion-toggle');
    if (!typingEl) return;

    const roles = [
      'Data Analyst',
      'Data operation analyst',
      'Data Scientist',
      'Business Analyst',
      'BI Developer',
    ];

    let roleIndex = 0;
    let charIndex = roles[0].length;
    let isDeleting = true;
    let isPaused = prefersReducedMotion();
    let timerId = null;

    function syncToggleUi() {
      if (!toggleBtn) return;
      const pauseIcon = toggleBtn.querySelector('.icon-pause');
      const playIcon = toggleBtn.querySelector('.icon-play');
      const label = toggleBtn.querySelector('.motion-toggle-label');
      if (pauseIcon) pauseIcon.hidden = isPaused;
      if (playIcon) playIcon.hidden = !isPaused;
      if (label) label.textContent = isPaused ? 'Play' : 'Pause';
      toggleBtn.setAttribute('aria-label', isPaused ? 'Play role animation' : 'Pause role animation');
    }

    function tick() {
      if (isPaused) return;
      const current = roles[roleIndex];

      if (isDeleting) {
        charIndex = Math.max(0, charIndex - 1);
        typingEl.textContent = current.slice(0, charIndex);
        if (charIndex === 0) {
          isDeleting = false;
          roleIndex = (roleIndex + 1) % roles.length;
          timerId = setTimeout(tick, 350);
          return;
        }
        timerId = setTimeout(tick, 48);
      } else {
        charIndex = Math.min(current.length, charIndex + 1);
        typingEl.textContent = current.slice(0, charIndex);
        if (charIndex === current.length) {
          isDeleting = true;
          timerId = setTimeout(tick, 2000);
          return;
        }
        timerId = setTimeout(tick, 95);
      }
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        isPaused = !isPaused;
        clearTimeout(timerId);
        if (isPaused) {
          typingEl.textContent = roles[roleIndex];
        } else {
          timerId = setTimeout(tick, 500);
        }
        syncToggleUi();
      });
    }

    syncToggleUi();
    if (!isPaused) {
      timerId = setTimeout(tick, 1800);
    } else {
      typingEl.textContent = roles[0];
    }
  })();

  // 8. Dynamic Copyright Year
  const yearEl = document.getElementById('copyright-year');
  if (yearEl) {
    yearEl.textContent = String(new Date().getFullYear());
  }
})();

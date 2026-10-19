/* Motion enhances the document; no content depends on an animation completing. */
const motion = (() => {
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const compact = window.matchMedia('(max-width: 700px)');
  const easing = 'cubic-bezier(0.22, 1, 0.36, 1)';
  const active = new Set();
  const owned = new WeakMap();
  let observer;
  const reduce = () => preference.matches;
  function stop(element) {
    const previous = owned.get(element);
    if (previous) { previous.cancel(); active.delete(previous); owned.delete(element); }
  }
  function animate(element, frames, options = {}) {
    if (!element || reduce() || !element.animate) return null;
    stop(element);
    const animation = element.animate(frames, {
      duration: compact.matches ? 480 : 680, easing, fill: 'backwards', ...options
    });
    active.add(animation);
    owned.set(element, animation);
    const clean = () => {
      active.delete(animation);
      if (owned.get(element) === animation) owned.delete(element);
    };
    animation.addEventListener('finish', clean, { once: true });
    animation.addEventListener('cancel', clean, { once: true });
    return animation;
  }
  function reveal(element, delay = 0) {
    return animate(element, [
      { opacity: 0, transform: 'translate3d(0,' + (compact.matches ? 12 : 22) + 'px,0)' },
      { opacity: 1, transform: 'translate3d(0,0,0)' }
    ], { delay, duration: compact.matches ? 520 : 820 });
  }
  function swap(element, delay = 0) {
    return animate(element, [
      { opacity: 0.3, transform: 'translate3d(0,8px,0)' },
      { opacity: 1, transform: 'translate3d(0,0,0)' }
    ], { duration: 420, delay });
  }
  function allStop() {
    active.forEach(animation => animation.cancel());
    active.clear();
  }
  preference.addEventListener('change', () => {
    if (reduce()) { allStop(); observer?.disconnect(); }
  });
  window.addEventListener('beforeprint', allStop);
  window.addEventListener('pagehide', allStop);
  document.addEventListener('focusin', event => {
    for (let el = event.target; el instanceof Element; el = el.parentElement) stop(el);
  });

  function initialise() {
    const header = document.querySelector('.site-header');
    let scheduled = false;
    function updateHeader() {
      scheduled = false;
      header?.classList.toggle('is-scrolled', window.scrollY > 24);
    }
    window.addEventListener('scroll', () => {
      if (!scheduled) { scheduled = true; requestAnimationFrame(updateHeader); }
    }, { passive: true });
    updateHeader();

    const route = location.pathname.split('/').pop();
    const current = route ? (route.includes('.') ? route : route + '.html') : 'index.html';
    document.querySelectorAll('#navigation a').forEach(link => {
      if (link.getAttribute('href') === current) {
        link.setAttribute('aria-current', 'page');
        link.closest('details')?.classList.add('is-current');
      }
    });
    if (reduce()) return;
    const firstSection = document.querySelector('main > section');
    const intro = firstSection?.querySelectorAll(
      '.hero-copy > *, .product-hero-grid > div:first-child > *, ' +
      '.platform-intro > *, .about-hero > div:first-child > *, .contact-copy > *, ' +
      '.detail-hero > .eyebrow, .detail-hero > h1, .detail-hero > .hero-description, ' +
      '.detail-hero > .detail-hero-bottom, .legal-hero > *'
    ) || [];
    [...intro].forEach((element, i) => {
      if (element.getBoundingClientRect().bottom > 0) reveal(element, Math.min(i * 65, 325));
    });
    const visual = firstSection?.querySelector('.hero-visual, .product-hero-preview, .about-photo, .contact-form-wrap');
    if (visual && visual.getBoundingClientRect().bottom > 0) {
      animate(visual, [
        { opacity: 0, clipPath: 'inset(7% 0 0 0 round 5px)', transform: 'translateY(18px)' },
        { opacity: 1, clipPath: 'inset(0% 0 0 0 round 5px)', transform: 'translateY(0)' }
      ], { duration: 1050, delay: 100 });
      const glass = visual.querySelector('.hero-glass');
      if (glass) reveal(glass, 450);
    }
    if (!('IntersectionObserver' in window)) return;
    const targets = [...document.querySelectorAll(
      '.section-heading, .product-card, .story-grid > div, .principles > div, ' +
      '.gallery-frame, .feature-grid > article, .workflow-grid > article, ' +
      '.platform-feature, .quote-section blockquote, .quote-person, ' +
      '.cta-inner > div, .split > div, .job-list > a, .press-assets > a, ' +
      '.contact-channels > div, .footer-col, .platform-preview'
    )];
    observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const element = entry.target;
        observer.unobserve(element);
        if (!element.closest('[hidden]')) reveal(element, Number(element.dataset.motionDelay || 0));
      });
    }, { threshold: 0.09, rootMargin: '0px 0px -24px 0px' });
    targets.forEach(element => {
      if (element.getBoundingClientRect().bottom <= 0) return;
      const siblings = [...element.parentElement.children];
      element.dataset.motionDelay = String(Math.min(siblings.indexOf(element) % 4, 3) * 55);
      observer.observe(element);
    });
  }
  initialise();
  return { animate, reveal, swap, stop, reduce };
})();

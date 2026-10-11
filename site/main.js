/* ============================================================
   TOTUS CRE, geteiltes Verhalten v4 (alle Seiten)
   Läuft fehlerfrei, wenn einzelne Hooks auf einer Seite fehlen.
   Hooks:
     [data-reveal]            einzelner Scroll-Reveal
     [data-reveal-group]      Kinder gestaffelt revealen
     [data-count-to]          Zahlen-Counter (data-count-prefix,
                              data-count-suffix, data-count-decimals)
     [data-tabs]              ARIA-Tab-Galerie mit Crossfade + Pfeiltasten
     [data-parallax="0.06"]   sanfter Parallax (rAF-gedrosselt)
     [data-scroll-progress]   Scroll-Fortschrittsbalken
     [data-menu-toggle] / [data-menu]  Mobile-Menü (ARIA, Escape, Outside-Click)
     [data-cookie-banner]     Cookie-Banner (localStorage 'cookie-choice',
                              Buttons: [data-cookie-accept] /
                              [data-cookie-essential], Escape blendet aus)
   No-JS-Schutz: html.js wird als allererstes gesetzt, Reveal-
   Verstecken existiert in CSS nur unter .js.
   ============================================================ */
(function () {
  'use strict';

  // No-JS-Schutz: sofort markieren (auch als Fallback zum Inline-Snippet).
  document.documentElement.classList.add('js');

  var mqReduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  function prefersReduced() { return !!(mqReduce && mqReduce.matches); }

  document.addEventListener('DOMContentLoaded', function () {

    /* ---------- 1. Scroll-Reveals (einzeln + gestaffelt) ---------- */
    (function initReveals() {
      var singles = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
      var groups = Array.prototype.slice.call(document.querySelectorAll('[data-reveal-group]'));

      function showAll() {
        singles.forEach(function (el) { el.classList.add('is-in'); });
        groups.forEach(function (g) {
          Array.prototype.forEach.call(g.children, function (c) { c.classList.add('is-in'); });
        });
      }

      if (!('IntersectionObserver' in window) || prefersReduced()) { showAll(); return; }

      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          if (el.hasAttribute('data-reveal-group')) {
            Array.prototype.forEach.call(el.children, function (child, i) {
              child.style.setProperty('--reveal-delay', (i * 90) + 'ms');
              child.classList.add('is-in');
            });
          } else {
            el.classList.add('is-in');
          }
          io.unobserve(el);
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

      singles.forEach(function (el) { io.observe(el); });
      groups.forEach(function (g) { io.observe(g); });

      // Wenn Nutzer reduced motion live aktiviert: alles sofort zeigen.
      if (mqReduce && mqReduce.addEventListener) {
        mqReduce.addEventListener('change', function (e) { if (e.matches) showAll(); });
      }
    })();

    /* ---------- 2. Zahlen-Counter ---------- */
    (function initCounters() {
      var counters = Array.prototype.slice.call(document.querySelectorAll('[data-count-to]'));
      if (!counters.length) return;

      // Zahlenformat folgt der Seitensprache (en/ setzt <html lang="en">).
      var pageLocale = ((document.documentElement.lang || 'de').toLowerCase().indexOf('en') === 0)
        ? 'en-US' : 'de-DE';

      function format(el, value) {
        var decimals = parseInt(el.getAttribute('data-count-decimals') || '0', 10);
        var suffix = el.getAttribute('data-count-suffix') || '';
        var prefix = el.getAttribute('data-count-prefix') || '';
        var locale = el.getAttribute('data-count-locale') || pageLocale;
        var text;
        try {
          text = value.toLocaleString(locale, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
          });
        } catch (e) {
          text = String(Math.round(value));
        }
        return prefix + text + suffix;
      }

      function setFinal(el) {
        var target = parseFloat(el.getAttribute('data-count-to'));
        if (!isNaN(target)) el.textContent = format(el, target);
      }

      function animate(el) {
        var target = parseFloat(el.getAttribute('data-count-to'));
        if (isNaN(target)) return;
        if (prefersReduced()) { setFinal(el); return; }
        var duration = 1400;
        var start = null;
        function tick(ts) {
          if (start === null) start = ts;
          var p = Math.min((ts - start) / duration, 1);
          var eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
          el.textContent = format(el, target * eased);
          if (p < 1) { requestAnimationFrame(tick); } else { setFinal(el); }
        }
        requestAnimationFrame(tick);
      }

      if (!('IntersectionObserver' in window)) {
        counters.forEach(setFinal);
        return;
      }
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          animate(entry.target);
          io.unobserve(entry.target);
        });
      }, { threshold: 0.4 });
      counters.forEach(function (el) { io.observe(el); });
    })();

    /* ---------- 3. ARIA-Tabs mit Crossfade + Pfeiltasten ---------- */
    (function initTabs() {
      var containers = Array.prototype.slice.call(document.querySelectorAll('[data-tabs]'));
      containers.forEach(function (container) {
        var tabs = Array.prototype.slice.call(container.querySelectorAll('[role="tab"]'));
        var panels = Array.prototype.slice.call(container.querySelectorAll('[role="tabpanel"]'));
        if (!tabs.length || !panels.length) return;

        // Panels ohne fokussierbaren Inhalt per Tab erreichbar machen (APG)
        panels.forEach(function (p) { p.tabIndex = 0; });

        function select(tab, focus) {
          tabs.forEach(function (t) {
            var active = t === tab;
            t.setAttribute('aria-selected', active ? 'true' : 'false');
            t.tabIndex = active ? 0 : -1;
          });
          panels.forEach(function (p) {
            var active = p.id === tab.getAttribute('aria-controls');
            // Nur Klassen togglen: CSS stapelt die Panels in einer Grid-Zelle
            // (visibility statt hidden), damit die Galeriehöhe konstant bleibt.
            p.classList.toggle('is-active', active);
            p.setAttribute('aria-hidden', active ? 'false' : 'true');
            p.tabIndex = active ? 0 : -1;
          });
          if (focus) tab.focus();
        }

        tabs.forEach(function (tab, i) {
          tab.addEventListener('click', function () { select(tab, false); });
          tab.addEventListener('keydown', function (e) {
            var next = null;
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = tabs[(i + 1) % tabs.length];
            else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = tabs[(i - 1 + tabs.length) % tabs.length];
            else if (e.key === 'Home') next = tabs[0];
            else if (e.key === 'End') next = tabs[tabs.length - 1];
            if (next) { e.preventDefault(); select(next, true); }
          });
        });

        // Initialzustand absichern
        var selected = tabs.filter(function (t) { return t.getAttribute('aria-selected') === 'true'; })[0] || tabs[0];
        select(selected, false);
      });
    })();

    /* ---------- 4. Parallax (rAF-gedrosselt, passive) ---------- */
    (function initParallax() {
      var els = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
      if (!els.length) return;

      var ticking = false;
      // Gleicher Breakpoint wie .hero-grid in CSS (960px), kein Parallax
      // auf dem gestapelten Layout.
      var mqDesktop = window.matchMedia ? window.matchMedia('(min-width: 960px)') : null;

      function update() {
        ticking = false;
        if (prefersReduced() || !mqDesktop || !mqDesktop.matches) {
          els.forEach(function (el) { el.style.transform = ''; });
          return;
        }
        var vh = window.innerHeight;
        els.forEach(function (el) {
          var speed = parseFloat(el.getAttribute('data-parallax')) || 0.05;
          var rect = el.getBoundingClientRect();
          var center = rect.top + rect.height / 2;
          var offset = (center - vh / 2) * -speed;
          el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)';
        });
      }

      function onScroll() {
        if (!ticking) { ticking = true; requestAnimationFrame(update); }
      }

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
      update();
    })();

    /* ---------- 5. Scroll-Progress ---------- */
    (function initProgress() {
      var bar = document.querySelector('[data-scroll-progress]');
      if (!bar) return;
      var ticking = false;
      function update() {
        ticking = false;
        var doc = document.documentElement;
        var max = doc.scrollHeight - window.innerHeight;
        var p = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
        bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      }
      window.addEventListener('scroll', function () {
        if (!ticking) { ticking = true; requestAnimationFrame(update); }
      }, { passive: true });
      update();
    })();

    /* ---------- 6. Mobile-Menü ---------- */
    (function initMenu() {
      var toggle = document.querySelector('[data-menu-toggle]');
      var menu = document.querySelector('[data-menu]');
      if (!toggle || !menu) return;

      function setOpen(open) {
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        menu.classList.toggle('is-open', open);
        // Scroll-Lock: Seite hinter dem offenen Menü nicht scrollen
        document.body.style.overflow = open ? 'hidden' : '';
      }
      function isOpen() { return toggle.getAttribute('aria-expanded') === 'true'; }

      toggle.addEventListener('click', function () { setOpen(!isOpen()); });

      // Menü schließen, wenn die Ansicht auf Desktop-Breite wechselt
      var mqMobileNav = window.matchMedia ? window.matchMedia('(max-width: 959.98px)') : null;
      if (mqMobileNav && mqMobileNav.addEventListener) {
        mqMobileNav.addEventListener('change', function (e) {
          if (!e.matches && isOpen()) setOpen(false);
        });
      }

      // Fokus verlässt das Menü (Tab hinaus) → schließen
      menu.addEventListener('focusout', function () {
        if (!isOpen()) return;
        requestAnimationFrame(function () {
          var ae = document.activeElement;
          if (ae && (menu.contains(ae) || toggle === ae || toggle.contains(ae))) return;
          setOpen(false);
        });
      });

      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && isOpen()) { setOpen(false); toggle.focus(); }
      });

      document.addEventListener('click', function (e) {
        if (!isOpen()) return;
        if (!menu.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
      });

      // Menü schließen, wenn ein Link gewählt wurde, Fokus folgt dem Sprungziel
      menu.addEventListener('click', function (e) {
        var t = e.target && e.target.closest ? e.target.closest('a') : e.target;
        if (!t || t.tagName !== 'A' || !menu.contains(t)) return;
        setOpen(false);
        var href = t.getAttribute('href') || '';
        if (href.length > 1 && href.charAt(0) === '#') {
          var target = document.querySelector(href);
          if (target) {
            target.setAttribute('tabindex', '-1');
            target.focus({ preventScroll: true });
          }
        }
      });
    })();

    /* ---------- 7. Cookie-Banner ---------- */
    (function initCookieBanner() {
      var banner = document.querySelector('[data-cookie-banner]');
      if (!banner) return; // Seite ohne Banner-Markup: nichts zu tun

      var KEY = 'cookie-choice';

      function getChoice() {
        try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
      }
      function setChoice(value) {
        try { window.localStorage.setItem(KEY, value); } catch (e) { /* z. B. Privatmodus */ }
      }

      // Auswahl vorhanden: Banner bleibt dauerhaft ausgeblendet.
      if (getChoice()) { banner.hidden = true; return; }

      banner.hidden = false;

      function dismiss(value) {
        if (value) setChoice(value);
        banner.hidden = true;
      }

      var acceptBtn = banner.querySelector('[data-cookie-accept]');
      var essentialBtn = banner.querySelector('[data-cookie-essential]');
      if (acceptBtn) {
        acceptBtn.addEventListener('click', function () { dismiss('accepted'); });
      }
      if (essentialBtn) {
        essentialBtn.addEventListener('click', function () { dismiss('essential'); });
      }

      // Escape blendet den Banner aus, speichert aber keine Auswahl, 
      // beim nächsten Besuch erscheint er erneut.
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !banner.hidden) dismiss(null);
      });
    })();

    /* ---------- 8. Lightbox (wiederverwendbar) ----------
       Auslöser: jedes Element mit [data-lightbox] (i. d. R. ein <img>).
       Öffnet ein Overlay mit dem großen Bild. Quelle: data-lightbox-src
       (höher aufgelöst) sonst src/currentSrc. Schließen per Esc, Klick auf
       den Backdrop oder den Schließen-Button. Fokus wird im Dialog gehalten
       und beim Schließen an den Auslöser zurückgegeben. */
    (function initLightbox() {
      var triggers = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]'));
      if (!triggers.length) return; // Guard: keine Bilder → kein Overlay

      var overlay = null, overlayImg = null, closeBtn = null, lastFocused = null;

      // Bilder sind nicht von Haus aus fokussierbar → tastaturbedienbar machen.
      triggers.forEach(function (el) {
        if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
        if (!el.hasAttribute('role')) el.setAttribute('role', 'button');
        if (!el.hasAttribute('aria-haspopup')) el.setAttribute('aria-haspopup', 'dialog');
      });

      function build() {
        overlay = document.createElement('div');
        overlay.className = 'lightbox';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.hidden = true;

        overlayImg = document.createElement('img');
        overlayImg.className = 'lightbox-img';
        overlayImg.alt = '';

        closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'lightbox-close';
        closeBtn.setAttribute('aria-label', 'Schließen');
        closeBtn.innerHTML =
          '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" ' +
          'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" ' +
          'stroke-linejoin="round" aria-hidden="true">' +
          '<path d="M18 6 6 18M6 6l12 12"/></svg>';

        overlay.appendChild(overlayImg);
        overlay.appendChild(closeBtn);
        document.body.appendChild(overlay);

        closeBtn.addEventListener('click', close);
        // Backdrop-Klick (nicht auf das Bild) schließt
        overlay.addEventListener('click', function (e) {
          if (e.target === overlay) close();
        });
        // Esc schließt, Tab bleibt im Dialog (nur der Button ist fokussierbar)
        overlay.addEventListener('keydown', function (e) {
          if (e.key === 'Escape') { e.preventDefault(); close(); return; }
          if (e.key === 'Tab') { e.preventDefault(); closeBtn.focus(); }
        });
        // Härtung: verlässt der Fokus den Dialog (Extension, Body-Klick),
        // wird er auf den Schließen-Button zurückgeholt, damit die Falle hält.
        overlay.addEventListener('focusout', function () {
          if (overlay.hidden) return;
          requestAnimationFrame(function () {
            var ae = document.activeElement;
            if (!overlay.hidden && (!ae || !overlay.contains(ae))) closeBtn.focus();
          });
        });
      }

      function open(trigger) {
        if (!overlay) build();
        lastFocused = trigger;
        var src = trigger.getAttribute('data-lightbox-src') ||
          trigger.getAttribute('src') || trigger.currentSrc || '';
        var alt = trigger.getAttribute('alt') || '';
        overlayImg.setAttribute('src', src);
        overlayImg.alt = alt;
        overlay.setAttribute('aria-label', alt || 'Bildvorschau');
        overlay.hidden = false;
        document.body.style.overflow = 'hidden'; // Scroll-Lock
        closeBtn.focus();
      }

      function close() {
        if (!overlay || overlay.hidden) return;
        overlay.hidden = true;
        document.body.style.overflow = '';
        overlayImg.removeAttribute('src');
        if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
        lastFocused = null;
      }

      // Delegierter Klick auf beliebige [data-lightbox]-Elemente
      document.addEventListener('click', function (e) {
        var t = e.target && e.target.closest ? e.target.closest('[data-lightbox]') : null;
        if (!t) return;
        e.preventDefault();
        open(t);
      });

      // Enter/Leertaste auf einem fokussierten Auslöser öffnet ebenfalls
      document.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
        var el = document.activeElement;
        if (!el || !el.hasAttribute || !el.hasAttribute('data-lightbox')) return;
        e.preventDefault();
        open(el);
      });
    })();

    /* ---------- 9. In-Page-Anker: Fokus folgt dem Sprungziel ----------
       Klick auf einen Seiten-internen Anker (#ziel) verschiebt den Tastatur-
       fokus in den Zielabschnitt, Parität zum Menü-Handler, damit AT-/
       Tastaturnutzer nach dem Sprung dort weiterlesen statt am Seitenanfang.
       Das Scrollen übernimmt weiterhin scroll-behavior/scroll-margin (CSS). */
    (function initAnchorFocus() {
      document.addEventListener('click', function (e) {
        var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
        if (!a) return;
        var href = a.getAttribute('href') || '';
        if (href.length < 2 || href.charAt(0) !== '#') return;
        var target = document.getElementById(href.slice(1));
        if (!target) return;
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        // preventScroll: die Positionierung erledigt das native Smooth-Scroll.
        requestAnimationFrame(function () { target.focus({ preventScroll: true }); });
      });
    })();

  });
})();

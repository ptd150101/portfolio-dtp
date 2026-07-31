(() => {
  const root = document.documentElement;
  let savedTheme = null;
  try { savedTheme = localStorage.getItem('portfolio-theme'); } catch {}
  const systemLight = window.matchMedia?.('(prefers-color-scheme: light)').matches;
  root.dataset.theme = savedTheme || (systemLight ? 'light' : 'dark');

  const menuButton = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('[data-nav-links]');
  const main = document.querySelector('main');

  if (main) {
    if (!main.id) main.id = 'main';
    if (!main.hasAttribute('tabindex')) main.tabIndex = -1;
  }
  if (nav && !nav.id) nav.id = 'primary-navigation';
  if (menuButton) {
    menuButton.setAttribute('aria-controls', nav?.id || 'primary-navigation');
    if (!menuButton.hasAttribute('aria-label')) menuButton.setAttribute('aria-label', 'Open navigation');
  }

  document.querySelectorAll('div[aria-label]:not([role])').forEach((element) => {
    element.setAttribute('role', 'group');
  });

  const normalizedPath = (value) => {
    const path = value.replace(/index\.html$/, '').replace(/\/+$/, '/');
    return path || '/';
  };
  const currentPath = normalizedPath(location.pathname);
  document.querySelectorAll('a[href]').forEach((link) => {
    try {
      const target = new URL(link.getAttribute('href'), location.href);
      if (target.origin === location.origin && !target.hash && normalizedPath(target.pathname) === currentPath) {
        link.setAttribute('aria-current', 'page');
      }
    } catch {}
  });

  const updateThemeButtons = () => {
    document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
      const light = root.dataset.theme === 'light';
      button.setAttribute('aria-label', light ? 'Switch to dark theme' : 'Switch to light theme');
      button.textContent = light ? '◐' : '◑';
    });
  };

  const setMenuOpen = (open, { returnFocus = false } = {}) => {
    if (!menuButton || !nav) return;
    nav.classList.toggle('open', open);
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    if (open) {
      nav.querySelector('a')?.focus();
    } else if (returnFocus) {
      menuButton.focus();
    }
  };

  document.addEventListener('click', async (event) => {
    const themeButton = event.target.closest('[data-theme-toggle]');
    if (themeButton) {
      root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
      try { localStorage.setItem('portfolio-theme', root.dataset.theme); } catch {}
      updateThemeButtons();
    }

    const clickedMenuButton = event.target.closest('[data-menu-toggle]');
    if (clickedMenuButton) {
      setMenuOpen(clickedMenuButton.getAttribute('aria-expanded') !== 'true');
      return;
    }

    if (nav?.classList.contains('open') && !event.target.closest('[data-nav-links]')) {
      setMenuOpen(false);
    }

    const copyButton = event.target.closest('[data-copy]');
    if (copyButton) {
      const selector = copyButton.getAttribute('data-copy');
      const target = selector ? document.querySelector(selector) : null;
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.textContent.trim());
        const previous = copyButton.textContent;
        copyButton.textContent = 'Copied';
        setTimeout(() => { copyButton.textContent = previous; }, 1400);
      } catch {
        copyButton.textContent = 'Select text';
      }
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav?.classList.contains('open')) {
      setMenuOpen(false, { returnFocus: true });
    }
  });

  document.querySelectorAll('[data-nav-links] a').forEach((link) => link.addEventListener('click', () => {
    setMenuOpen(false);
  }));

  const header = document.querySelector('[data-header]');
  const updateHeader = () => header?.classList.toggle('scrolled', window.scrollY > 12);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  const observer = 'IntersectionObserver' in window ? new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 }) : null;
  document.querySelectorAll('.reveal').forEach((element) => observer ? observer.observe(element) : element.classList.add('visible'));

  document.querySelectorAll('[data-year]').forEach((year) => {
    year.textContent = String(new Date().getFullYear());
  });
  updateThemeButtons();
})();

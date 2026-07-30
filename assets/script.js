(() => {
  const root = document.documentElement;
  let savedTheme = null;
  try { savedTheme = localStorage.getItem('portfolio-theme'); } catch {}
  const systemLight = window.matchMedia?.('(prefers-color-scheme: light)').matches;
  root.dataset.theme = savedTheme || (systemLight ? 'light' : 'dark');

  const updateThemeButtons = () => {
    document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
      const light = root.dataset.theme === 'light';
      button.setAttribute('aria-label', light ? 'Switch to dark theme' : 'Switch to light theme');
      button.textContent = light ? '◐' : '◑';
    });
  };

  document.addEventListener('click', async (event) => {
    const themeButton = event.target.closest('[data-theme-toggle]');
    if (themeButton) {
      root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
      try { localStorage.setItem('portfolio-theme', root.dataset.theme); } catch {}
      updateThemeButtons();
    }

    const menuButton = event.target.closest('[data-menu-toggle]');
    if (menuButton) {
      const nav = document.querySelector('[data-nav-links]');
      const open = nav?.classList.toggle('open') || false;
      menuButton.setAttribute('aria-expanded', String(open));
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
      } catch { copyButton.textContent = 'Select text'; }
    }
  });

  document.querySelectorAll('[data-nav-links] a').forEach((link) => link.addEventListener('click', () => {
    document.querySelector('[data-nav-links]')?.classList.remove('open');
    document.querySelector('[data-menu-toggle]')?.setAttribute('aria-expanded', 'false');
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

  const year = document.querySelector('[data-year]');
  if (year) year.textContent = String(new Date().getFullYear());
  updateThemeButtons();
})();

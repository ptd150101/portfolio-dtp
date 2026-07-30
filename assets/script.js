(() => {
  const root = document.documentElement;
  let savedTheme = null;
  try { savedTheme = localStorage.getItem('portfolio-theme'); } catch {}
  const systemLight = window.matchMedia?.('(prefers-color-scheme: light)').matches;
  root.dataset.theme = savedTheme || (systemLight ? 'light' : 'dark');

  const enhanceRemoteKeyStory = () => {
    const scriptSource = document.currentScript?.src;
    const assetUrl = (name) => scriptSource ? new URL(name, scriptSource).href : `assets/${name}`;
    const illustrationUrl = assetUrl('og-remotekey.svg');
    const problemUrl = assetUrl('remotekey-problem.webp');
    const solutionUrl = assetUrl('remotekey-solution.webp');

    const homeCard = document.querySelector('.project-card.remotekey');
    if (homeCard) {
      const description = homeCard.querySelector('.project-description');
      if (description) description.textContent = 'An Android-to-Windows shortcut bridge built for Parsec, StarDesk, Steam Link and similar remote sessions where Android consumes Alt+Tab, Win+E or Win+Tab before the remote client can forward them.';
      const visual = homeCard.querySelector('.project-visual');
      if (visual) {
        visual.setAttribute('aria-label', 'Android tablet running Parsec, StarDesk and Steam Link while Android intercepts Alt Tab and Win E; RemoteKey restores a side channel to Windows');
        visual.innerHTML = `<img src="${problemUrl}" alt="Android intercepts Alt+Tab, Win+E and Win+Tab before Parsec, StarDesk or Steam Link can send them to Windows." loading="lazy" style="width:min(100%,720px);height:auto;display:block;border:1px solid var(--line-strong);border-radius:20px;box-shadow:0 30px 75px rgba(0,0,0,.42)">`;
      }
    }

    const remoteHero = document.querySelector('.case-visual.remote');
    if (!remoteHero) return;
    const heroCopy = document.querySelector('.project-hero-copy');
    if (heroCopy) heroCopy.textContent = 'A shortcut-only keyboard bridge for Parsec, StarDesk, Steam Link and similar Android remote sessions, restoring Windows combinations that Android intercepts before the remote client can forward them.';
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) metaDescription.content = 'RemoteKey case study: restoring Alt+Tab, Win+E and Win+Tab when Android intercepts them before Parsec, StarDesk or Steam Link can forward them to Windows.';
    const ogDescription = document.querySelector('meta[property="og:description"]');
    if (ogDescription) ogDescription.content = 'Why Android tablets lose Alt+Tab and Windows shortcuts in Parsec, StarDesk and Steam Link — and how RemoteKey restores them through a safe side channel.';

    remoteHero.setAttribute('aria-label', 'RemoteKey problem illustration showing Android intercepting desktop shortcuts');
    remoteHero.innerHTML = `<figure style="width:min(100%,780px);margin:0"><img src="${problemUrl}" alt="Problem diagram: normal typing reaches Windows, but Android intercepts Alt+Tab, Win+E and Win+Tab before the remote app sees them." style="width:100%;height:auto;display:block;border:1px solid var(--line-strong);border-radius:24px;box-shadow:0 35px 90px rgba(0,0,0,.45)"><figcaption style="margin-top:14px;color:var(--muted);font-size:13px;text-align:center"><strong style="color:var(--text)">The pain point.</strong> The remote client cannot forward shortcuts Android never delivers to it.</figcaption></figure>`;

    const overview = document.querySelector('#overview .case-content');
    const intro = overview?.querySelector(':scope > p');
    if (intro) intro.innerHTML = 'On an Android tablet, a physical Bluetooth or USB keyboard can type normally inside <strong>Parsec</strong>, <strong>StarDesk</strong>, <strong>Steam Link</strong> and similar remote clients. The session looks complete until a desktop shortcut is needed: Android or vendor firmware may consume <code>Alt + Tab</code>, <code>Windows + E</code> and <code>Windows + Tab</code> before the focused remote app can forward those events to the Windows host.';

    if (overview && intro && !overview.querySelector('[data-remotekey-pain]')) {
      const comparison = document.createElement('div');
      comparison.className = 'decision-grid';
      comparison.dataset.remotekeyPain = '';
      comparison.style.margin = '30px 0';
      comparison.innerHTML = `
        <article class="decision-card" style="border-color:rgba(255,127,143,.35)"><span>Without RemoteKey</span><h4>Android consumes the shortcut</h4><p><strong>Alt+Tab</strong> switches Android apps and the Windows key may be handled locally. The focused remote client never receives a complete event sequence.</p></article>
        <article class="decision-card" style="border-color:rgba(255,127,143,.24)"><span>Parsec · StarDesk · Steam Link</span><h4>The remote session cannot forward what it never sees</h4><p>Video, mouse and ordinary typing still work, making the missing desktop shortcuts especially disruptive.</p></article>
        <article class="decision-card" style="border-color:rgba(102,228,167,.34)"><span>RemoteKey side channel</span><h4>Capture only selected combinations</h4><p>Android AccessibilityService handles <strong>Alt+Tab</strong>, <strong>Win+E</strong> and <strong>Win+Tab</strong>, then sends compact JSON Lines packets over TCP.</p></article>
        <article class="decision-card" style="border-color:rgba(102,228,167,.34)"><span>Windows host</span><h4>Recreate the intended desktop action</h4><p>The Python agent maps Android key codes and calls Win32 <strong>SendInput</strong>, while normal keyboard input remains on the remote app's native path.</p></article>`;
      intro.insertAdjacentElement('afterend', comparison);
    }

    if (overview && !overview.querySelector('[data-remotekey-visuals]')) {
      const gallery = document.createElement('section');
      gallery.dataset.remotekeyVisuals = '';
      gallery.style.margin = '48px 0';
      gallery.innerHTML = `
        <span class="section-label">Visual walkthrough</span>
        <h3 style="font-size:clamp(28px,4vw,44px);margin:10px 0 14px">From blocked shortcut to restored Windows action.</h3>
        <p style="color:var(--muted);max-width:760px;margin-bottom:26px">The first image proves the failure point. The second image shows the complete solution path while preserving the remote app's native input route.</p>
        <div style="display:grid;gap:26px">
          <figure style="margin:0"><img src="${problemUrl}" alt="RemoteKey problem: Android intercepts system shortcuts before remote desktop apps can forward them." loading="lazy" style="width:100%;height:auto;display:block;border:1px solid var(--line-strong);border-radius:24px"><figcaption style="margin-top:12px;color:var(--muted)"><strong style="color:var(--text)">01 — The problem.</strong> Letters and numbers arrive normally, but Android traps Alt+Tab, Win+E and Win+Tab.</figcaption></figure>
          <figure style="margin:0"><img src="${solutionUrl}" alt="RemoteKey solution architecture from Android AccessibilityService through TCP JSON Lines and Windows SendInput." loading="lazy" style="width:100%;height:auto;display:block;border:1px solid var(--line-strong);border-radius:24px"><figcaption style="margin-top:12px;color:var(--muted)"><strong style="color:var(--text)">02 — The solution.</strong> RemoteKey captures only missing shortcuts, sends them over a local TCP side channel and recreates them with Win32 SendInput.</figcaption></figure>
        </div>`;
      const anchor = overview.querySelector('[data-remotekey-pain]') || intro;
      anchor?.insertAdjacentElement('afterend', gallery);
    }

    const callout = overview?.querySelector('.callout.green');
    if (callout) callout.textContent = 'RemoteKey does not stream the screen and does not replace Parsec, StarDesk or Steam Link. It supplies only the missing shortcut path.';
  };

  enhanceRemoteKeyStory();

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
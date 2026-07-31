(() => {
  const token = '__CF_ANALYTICS_TOKEN__'.trim();
  const localHosts = new Set(['localhost', '127.0.0.1', '0.0.0.0']);
  if (!token || token.startsWith('__') || localHosts.has(location.hostname)) return;
  if (document.querySelector('script[data-portfolio-analytics]')) return;

  const script = document.createElement('script');
  script.defer = true;
  script.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  script.dataset.portfolioAnalytics = 'cloudflare';
  script.setAttribute('data-cf-beacon', JSON.stringify({ token }));
  document.head.appendChild(script);
})();

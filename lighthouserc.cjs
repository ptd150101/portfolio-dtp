module.exports = {
  ci: {
    collect: {
      startServerCommand: 'python3 scripts/build_site.py --output _site && python3 scripts/serve_portfolio.py --port 4173 --root _site',
      startServerReadyPattern: 'Serving portfolio',
      startServerReadyTimeout: 30000,
      url: [
        'http://127.0.0.1:4173/portfolio-dtp/',
        'http://127.0.0.1:4173/portfolio-dtp/projects/context-video-translator/',
        'http://127.0.0.1:4173/portfolio-dtp/projects/remotekey/',
        'http://127.0.0.1:4173/portfolio-dtp/resume/',
      ],
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--headless --no-sandbox --disable-dev-shm-usage',
        maxWaitForLoad: 90000,
      },
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.80 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.95 }],
        'categories:seo': ['error', { minScore: 0.95 }],
        'document-title': 'error',
        'html-has-lang': 'error',
        'image-alt': 'error',
        'link-name': 'error',
        'button-name': 'error',
        'meta-description': 'error',
        'viewport': 'error',
        'crawlable-anchors': 'error',
      },
    },
    upload: {
      target: 'filesystem',
      outputDir: '.lighthouseci',
      reportFilenamePattern: '%%PATHNAME%%-%%DATETIME%%-report.%%EXTENSION%%',
    },
  },
};

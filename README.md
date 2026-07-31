# Đạt Tiến — Engineering Portfolio

A multi-page static engineering portfolio presenting two product case studies:

- **Context Video Translator** — context-aware bilingual subtitle extension for YouTube and Udemy.
- **RemoteKey** — shortcut-only Android-to-Windows input bridge.

## Public pages

- `/` — homepage, selected work, engineering principles, background and contact.
- `/projects/context-video-translator/` — browser-extension and AI product case study.
- `/projects/remotekey/` — Android, networking and Win32 product case study.
- `/resume/` — print-friendly résumé with browser PDF export.
- `/privacy/` — privacy-first analytics disclosure.
- `/404.html` — custom not-found page.

## Product and accessibility features

- Responsive desktop, tablet and mobile layouts.
- Dark and light themes saved in `localStorage`.
- Reduced-motion and forced-colors safeguards.
- Semantic landmarks, skip links, focus management and keyboard-operable navigation.
- Lazy-loaded below-the-fold imagery with intrinsic dimensions.
- Original PNG product screenshots plus scalable SVG diagrams.
- Canonical URLs, Open Graph/Twitter previews, structured data, sitemap and robots file.
- No service worker or incomplete PWA manifest.

## Quality platform

The GitHub Pages workflow blocks deployment until these jobs pass:

1. **Static quality** — HTML validation, internal links and anchors, image/asset rules and sitemap coverage.
2. **Browser and accessibility quality** — Playwright smoke tests, mobile reflow and axe WCAG checks.
3. **Lighthouse quality** — performance ≥ 80 and accessibility, best practices and SEO ≥ 95.

Reports are uploaded as GitHub Actions artifacts. A separate scheduled workflow performs a non-blocking external-link audit.

## Local validation

Install the development-only quality dependencies:

```bash
npm install
npx playwright install chromium
```

Run static checks:

```bash
npm run quality
```

Run browser and accessibility checks:

```bash
npm run test:browser
```

Run Lighthouse CI:

```bash
npm run lhci
```

The local test server exposes the repository under the same `/portfolio-dtp/` prefix as GitHub Pages.

## Deployment

`.github/workflows/pages.yml` builds a clean `_site` artifact and deploys it through GitHub Pages after all quality jobs succeed.

Optional repository Actions variables:

- `SITE_URL` — final custom-domain origin, for example `https://example.dev`.
- `CF_ANALYTICS_TOKEN` — Cloudflare Web Analytics token. Analytics stays disabled when this variable is empty.

The build rewrites canonical, social, structured-data, sitemap and robots URLs for `SITE_URL`, creates `CNAME` for a custom hostname and injects analytics only into the deployment artifact.

Operational details:

- `docs/accessibility-audit.md`
- `docs/analytics.md`
- `docs/custom-domain.md`

## Project sources

- <https://github.com/ptd150101/context-video-translator>
- <https://github.com/ptd150101/android-remote-keyboard>

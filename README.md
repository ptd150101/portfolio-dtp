# Đạt Tiến — Engineering Portfolio

A dependency-free, multi-page technical portfolio presenting two engineering case studies:

- **Context Video Translator** — context-aware bilingual subtitle extension for YouTube and Udemy.
- **RemoteKey** — shortcut-only Android-to-Windows input bridge.

## Pages

- `/` — homepage, selected work, engineering principles, background and contact.
- `/projects/context-video-translator/` — full browser/AI case study.
- `/projects/remotekey/` — full Android/network/Win32 case study.
- `/resume/` — print-friendly résumé with browser PDF export.
- `/404.html` — custom not-found page.

## Features

- Responsive layout with mobile navigation.
- Dark and light themes saved in `localStorage`.
- Reduced-motion support.
- Semantic HTML, skip links, focus states and accessible navigation.
- CSS-only project illustrations and meaningful animations.
- Copyable protocol and prompt examples.
- Open Graph graphics, sitemap, robots file and web manifest.
- Automatic GitHub Pages deployment workflow.
- No runtime dependencies, build step or third-party asset requests.

## Local development

Serve the repository root with any static server:

```bash
npx http-server . -p 4173
```

or:

```bash
python -m http.server 4173
```

Then open `http://localhost:4173`.

## Deploying

The workflow at `.github/workflows/pages.yml` uploads the repository as a Pages artifact and deploys on every push to `main`. In repository settings, set **Pages → Source** to **GitHub Actions** once if it is not already enabled.

The site is written with relative internal links so it works as a GitHub project site under `/portfolio-dtp/` as well as on a custom domain.

## Project sources

- <https://github.com/ptd150101/context-video-translator>
- <https://github.com/ptd150101/android-remote-keyboard>

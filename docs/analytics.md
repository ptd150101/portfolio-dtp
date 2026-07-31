# Privacy-first analytics setup

The repository includes a conditional Cloudflare Web Analytics loader in `assets/analytics.js`.

Analytics is disabled by default. During GitHub Pages deployment, `scripts/prepare_site.py` replaces the token placeholder with the repository variable `CF_ANALYTICS_TOKEN`. When the variable is empty, no third-party analytics script is loaded.

## Activate

1. Create a Web Analytics site in Cloudflare.
2. Copy the site token from the Cloudflare beacon snippet.
3. In GitHub, open **Settings → Secrets and variables → Actions → Variables**.
4. Create `CF_ANALYTICS_TOKEN` with the token value.
5. Re-run the Pages workflow.

The loader skips localhost and `127.0.0.1`, so local development does not pollute production analytics.

## Collected scope

Cloudflare Web Analytics provides aggregate page, referrer, device, browser, operating-system and Core Web Vitals information. The portfolio does not add custom-event tracking, form tracking or user identifiers.

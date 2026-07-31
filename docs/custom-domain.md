# Custom domain migration

The deployment is domain-ready. Source files keep the current GitHub Pages canonical URL, while the deploy workflow accepts a repository variable named `SITE_URL`.

Example value:

```text
https://example.dev
```

When `SITE_URL` differs from the default GitHub Pages subpath, `scripts/prepare_site.py`:

- rewrites canonical, Open Graph, structured-data, sitemap and robots URLs;
- rewrites `/portfolio-dtp/` root paths for an apex domain;
- creates a `CNAME` file in the deployment artifact;
- keeps relative project and asset links unchanged.

## Activation checklist

1. Buy and choose the final domain.
2. Verify it in GitHub account settings using the requested DNS TXT record.
3. Add `SITE_URL` under repository Actions variables.
4. Configure the apex and `www` DNS records using GitHub Pages' current documentation.
5. Set the custom domain under **Repository Settings → Pages**.
6. Enable **Enforce HTTPS** after the certificate is issued.
7. Submit the new sitemap to Google Search Console and Bing Webmaster Tools.

Do not set a placeholder domain in `SITE_URL`; it becomes the canonical URL of every deployed page.

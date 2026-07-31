# Accessibility audit — Portfolio DTP

Audit target: WCAG 2.2 Level AA  
Routes: homepage, Context Video Translator, RemoteKey, résumé, privacy and 404.

## Automated coverage

The CI pipeline runs the following checks in Chromium for dark and light themes:

- axe-core rules tagged WCAG 2 A/AA, WCAG 2.1 AA and WCAG 2.2 AA;
- one `h1` and one `main` landmark per route;
- accessible names for links, buttons and images;
- keyboard operation of theme and mobile navigation controls;
- Escape closes the mobile navigation and returns focus;
- skip-link navigation;
- 390 px reflow without horizontal scrolling;
- JavaScript-disabled content availability;
- Lighthouse accessibility threshold of 95 or higher.

CI blocks deployment when a critical or serious axe violation is found.

## Manual review matrix

| Area | Status | Verification |
|---|---|---|
| Keyboard-only navigation | Covered by CI + owner spot check | Tab, Shift+Tab, Enter, Space and Escape |
| Focus visibility | Covered by CSS + CI interaction tests | Focus ring and sticky-header offset |
| Dark/light contrast | Automated axe check | Both themes tested |
| Mobile reflow | Automated at 390 px | Horizontal overflow must be zero |
| Reduced motion | CSS rule present | Reveal and hover motion disabled |
| Screen reader landmarks | Semantic HTML + axe | `header`, `nav`, `main`, `footer` |
| NVDA spoken-order review | Requires Windows owner verification | CI cannot emulate a real screen reader |
| 200%/400% browser zoom | Requires owner verification | Playwright narrow-viewport test is not a substitute |

## Remaining human verification

Before claiming full WCAG conformance, perform a five-minute manual pass using NVDA with Edge on Windows and browser zoom at 200% and 400%. Automated tools cannot certify conformance or judge whether every alt description is contextually ideal.

## Regression policy

- Critical or serious axe violation: deployment blocked.
- Broken keyboard interaction: deployment blocked.
- Horizontal overflow at 390 px: deployment blocked.
- Lighthouse accessibility below 95: deployment blocked.
- Moderate axe findings: review and resolve before the next content release.

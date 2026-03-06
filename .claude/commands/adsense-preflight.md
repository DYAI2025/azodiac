---
name: adsense-preflight
description: Pre-submission audit for Google AdSense compliance. Run before registering or re-submitting any site to AdSense.
---

# Google AdSense Pre-Flight Check

Run this complete checklist against the current project before submitting to Google AdSense. Report each check as PASS/FAIL/WARN with file paths and specific issues.

## Instructions

1. Identify the project's target domain (from deploy config, CLAUDE.md, CNAME, or ask user)
2. Run ALL checks below sequentially
3. Output a summary table at the end
4. BLOCK submission if any FAIL items exist

---

## Phase 1: Domain Consistency

Scan ALL non-node_modules files for URLs. Every internal reference must use the registered AdSense domain.

```
CHECK 1.1 — Sitemap domain match
  Search: public/sitemap.xml or dist/sitemap.xml
  Verify: Every <loc> URL uses the target domain
  Common bug: Old domain left over from migration

CHECK 1.2 — Canonical URL
  Search: index.html for <link rel="canonical">
  Verify: href matches target domain
  FAIL if: missing entirely

CHECK 1.3 — OpenGraph URL
  Search: index.html for <meta property="og:url">
  Verify: content matches target domain
  FAIL if: missing entirely

CHECK 1.4 — robots.txt sitemap reference
  Search: public/robots.txt
  Verify: Sitemap: URL uses target domain
  FAIL if: robots.txt missing

CHECK 1.5 — Cross-file domain scan
  Grep all src/**/*.{ts,tsx,js,html,xml,json,txt} for URLs
  Flag any URL that references a different domain that SHOULD be the target domain
  Ignore: legitimate external links (github.com, googleapis.com, CDNs, partner sites)

CHECK 1.6 — ads.txt publisher ID
  Search: public/ads.txt
  Verify: exists, contains google.com + correct pub-ID
  Cross-check: pub-ID matches <meta name="google-adsense-account"> in index.html
  FAIL if: missing or ID mismatch
```

## Phase 2: Crawler Accessibility

Google's AdSense crawler does NOT reliably render JavaScript. The site must have meaningful content without JS.

```
CHECK 2.1 — noscript fallback
  Search: index.html for <noscript> block
  Verify: contains real descriptive text (>200 chars), not just "enable JS"
  FAIL if: missing or trivially short

CHECK 2.2 — HTML body content
  Verify: index.html <body> contains more than just <div id="root">
  Measure: Content-Length of raw HTML should be >2KB of actual text
  WARN if: body is essentially empty without JS

CHECK 2.3 — Meta description
  Search: index.html for <meta name="description">
  Verify: content is >50 chars, describes the site
  FAIL if: missing or generic

CHECK 2.4 — Page title
  Search: index.html for <title>
  Verify: meaningful title, not default Vite/React placeholder
  FAIL if: "React App" or "Vite + React"

CHECK 2.5 — robots.txt allows crawling
  Verify: no Disallow: / for Googlebot or *
  Verify: Allow: / is present or no blocking rules
```

## Phase 3: Legal Pages

All three required for German/EU sites. Must be accessible from every page.

```
CHECK 3.1 — Privacy Policy exists
  Search for: Datenschutz, Privacy Policy, privacy page component
  Verify: real content (>500 chars), not placeholder
  Verify: mentions Google AdSense/advertising data collection
  Verify: mentions cookies and tracking
  FAIL if: missing or placeholder

CHECK 3.2 — Impressum exists
  Search for: Impressum, Legal Notice, imprint
  Verify: contains name, address, email/contact
  Verify: §5 TMG compliance (for German sites)
  FAIL if: missing or incomplete contact info

CHECK 3.3 — Terms of Service exists
  Search for: AGB, Terms, ToS, Nutzungsbedingungen
  Verify: real content (>300 chars)
  WARN if: missing (not strictly required but recommended)

CHECK 3.4 — Legal pages reachable
  Verify: legal pages are linked in footer OR sidebar
  Verify: links are present in navigation component, not hidden
  FAIL if: legal pages exist but have no navigation link
```

## Phase 4: Cookie Consent

Required for AdSense in EU (GDPR/ePrivacy).

```
CHECK 4.1 — Consent banner exists
  Search for: CookieConsent, cookie-consent, consent component
  Verify: component renders on first visit
  FAIL if: no consent mechanism found

CHECK 4.2 — Granular consent categories
  Verify: separates essential, analytics, advertising
  Verify: advertising consent controls ad_storage, ad_user_data, ad_personalization
  WARN if: only accept/reject without granularity

CHECK 4.3 — Google consent mode integration
  Search for: gtag('consent'), consent mode
  Verify: default is 'denied' for ad_storage
  Verify: updates to 'granted' only after user consent
  FAIL if: ads load without consent in EU context

CHECK 4.4 — Consent persistence
  Verify: consent choice saved to localStorage/cookie
  Verify: not re-prompted on every page load
```

## Phase 5: Content Quality

AdSense requires substantial, original content.

```
CHECK 5.1 — Content volume
  Count total words across all content pages/data files
  FAIL if: <1000 words total
  WARN if: <3000 words total
  PASS if: >5000 words

CHECK 5.2 — Multiple content pages
  Count distinct content pages (not legal/empty)
  FAIL if: only 1 page (landing only)
  WARN if: 2-3 pages
  PASS if: 4+ substantial pages

CHECK 5.3 — Original content
  Verify: content is not lorem ipsum or placeholder
  Verify: content relates to the site's stated purpose
  WARN if: content appears auto-generated or thin
```

## Phase 6: Navigation & UX

```
CHECK 6.1 — Navigation menu exists
  Verify: sidebar, header nav, or hamburger menu present
  Verify: links to main content sections
  FAIL if: no navigation component found

CHECK 6.2 — Mobile responsive
  Search for: viewport meta tag, responsive CSS classes, mobile hooks
  Verify: <meta name="viewport" content="width=device-width">
  FAIL if: no viewport meta tag

CHECK 6.3 — Footer with links
  Verify: footer component exists with navigation links
  Verify: legal pages accessible from footer
```

## Phase 7: Technical

```
CHECK 7.1 — HTTPS
  Verify: all internal URLs use https://
  Verify: canonical, og:url, sitemap all use https
  FAIL if: any http:// internal references

CHECK 7.2 — AdSense script installed
  Search: index.html for pagead2.googlesyndication.com
  Verify: script tag present with correct pub-ID
  Verify: async attribute present
  FAIL if: script missing

CHECK 7.3 — No conflicting ad networks
  Search codebase for other ad network scripts
  WARN if: multiple ad networks found (may conflict)

CHECK 7.4 — Build succeeds
  Run: npm run build (or equivalent)
  FAIL if: build errors
```

---

## Output Format

After running all checks, output:

```
## AdSense Pre-Flight Report: [domain]

| # | Check | Status | Details |
|---|-------|--------|---------|
| 1.1 | Sitemap domain | PASS/FAIL | ... |
| ... | ... | ... | ... |

### Summary
- PASS: X checks
- WARN: X checks
- FAIL: X checks

### Verdict
✅ READY — Submit to AdSense
⚠️ FIX WARNINGS — Submittable but risky
❌ BLOCKED — Fix FAIL items before submitting
```

### Blocking Issues (if any)
List each FAIL with exact file:line and fix instructions.

### Warnings (if any)
List each WARN with recommendation.

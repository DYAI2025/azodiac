# SEO and Internal Links Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish a robust AI SEO / GEO foundation to connect the Augmented_Ops platform to high-reach entities and properly interlink the VSA, MSA, RSA, and CSA services with their corresponding GitHub repository content.

**Architecture:** Implement semantic HTML, GEO-optimized meta tags, JSON-LD structured data (Organization, FAQPage), and integrate the external GitHub repositories as content sources/subdirectories for the four sub-agencies.

**Tech Stack:** HTML5, JSON-LD (Schema.org), Git.

---

### Task 1: Add JSON-LD Organization Schema to augmentd.html

**Files:**
- Modify: `/Users/benjaminpoersch/Projects/WEB/augmented_ops/augmentd.html`

**Step 1: Inject JSON-LD Schema**

Add the following JSON-LD script inside the `<head>` tag of `augmentd.html` to define the Organization entity and help AI engines (GEO) understand the structure.

```html
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Organization",
      "name": "Augmented_Ops",
      "url": "https://augmented-ops.com",
      "logo": "https://augmented-ops.com/logo.png",
      "founder": {
        "@type": "Person",
        "name": "Benjamin Poersch"
      },
      "description": "100% Automated AI Services. Built by the mesh. Approved by the human.",
      "subOrganization": [
        { "@type": "Organization", "name": "Virtual Service Agency (VSA)" },
        { "@type": "Organization", "name": "Customer Support Agency (CSA)" },
        { "@type": "Organization", "name": "Recruitment Service Agency (RSA)" },
        { "@type": "Organization", "name": "Marketing Service Agency (MSA)" }
      ]
    }
    </script>
```

**Step 2: Commit**

```bash
git add /Users/benjaminpoersch/Projects/WEB/augmented_ops/augmentd.html
git commit -m "feat: add JSON-LD organization schema for AI SEO"
```

---

### Task 2: Clone Sub-Agency Repositories

**Files:**
- Create: Directories for VSA, MSA, RSA, CSA

**Step 1: Clone the repositories into the augmented_ops directory**

Run the following commands to pull the correct content for each sub-agency into the project folder.

```bash
cd /Users/benjaminpoersch/Projects/WEB/augmented_ops
git clone https://github.com/DYAI2025/VSA.git VSA
git clone https://github.com/DYAI2025/CSA.git CSA
git clone https://github.com/DYAI2025/RSA.git RSA
git clone https://github.com/DYAI2025/MSA.git MSA
```

**Step 2: Verify Clone Success**

Run: `ls -la /Users/benjaminpoersch/Projects/WEB/augmented_ops/VSA`
Expected: Output showing the repository files (e.g., README.md, index.html).

**Step 3: Commit**

```bash
git add VSA CSA RSA MSA
git commit -m "feat: integrate sub-agency repositories"
```

---

### Task 3: Update Internal Links in augmentd.html

**Files:**
- Modify: `/Users/benjaminpoersch/Projects/WEB/augmented_ops/augmentd.html`

**Step 1: Update the anchor tags**

Ensure the links point correctly to the newly cloned directories, leveraging strong anchor text for SEO.

Modify the VSA link (around line 250):
```html
<div class="investment-deck">
    <a href="./VSA/index.html" title="Virtual Service Agency (VSA) - Pitchdecks">Deck anfragen</a>
    <small>System: VSA_MESH_ONLINE</small>
</div>
```

Modify the CSA link (around line 280):
```html
<div class="investment-deck">
    <a href="./CSA/index.html" title="Customer Support Agency (CSA) - AI Support">Support automatisieren</a>
    <small>System: CSA_MESH_ONLINE</small>
</div>
```

Modify the RSA link (around line 310):
```html
<div class="investment-deck">
    <a href="./RSA/index.html" title="Recruitment Service Agency (RSA) - AI Recruiting">Vakanz öffnen</a>
    <small>System: RSA_MESH_ONLINE</small>
</div>
```

Modify the MSA link (around line 340):
```html
<div class="investment-deck">
    <a href="./MSA/index.html" title="Marketing Service Agency (MSA) - AI Campaigns">Kampagne starten</a>
    <small>System: MSA_MESH_ONLINE</small>
</div>
```

**Step 2: Commit**

```bash
git add /Users/benjaminpoersch/Projects/WEB/augmented_ops/augmentd.html
git commit -m "feat: update internal links to cloned sub-agency repositories with SEO titles"
```

---

### Task 4: Add GEO Meta Tags & FAQ Schema

**Files:**
- Modify: `/Users/benjaminpoersch/Projects/WEB/augmented_ops/augmentd.html`

**Step 1: Add OpenGraph and GEO-friendly meta tags**

Add to the `<head>` section:
```html
    <meta property="og:title" content="Augmented_Ops | AI Agentur für Startups">
    <meta property="og:description" content="Autonome KI-Agenturen (VSA, CSA, RSA, MSA) für Startups. Kein Output ohne Signatur.">
    <meta property="og:type" content="website">
    <meta name="robots" content="index, follow">
```

**Step 2: Add FAQ Schema to footer/head**

To increase AI engine citations (Perplexity, ChatGPT), add an FAQ JSON-LD script representing core questions:

```html
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [{
        "@type": "Question",
        "name": "Was ist Augmented_Ops?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Augmented_Ops ist ein Mesh autonomer KI-Agenten, die spezialisierte Dienstleistungen in den Bereichen Marketing (MSA), Support (CSA), Recruiting (RSA) und Investment (VSA) zu 100% automatisiert abbilden. Human-in-the-loop bei jedem Checkpoint."
        }
      }]
    }
    </script>
```

**Step 3: Commit**

```bash
git add /Users/benjaminpoersch/Projects/WEB/augmented_ops/augmentd.html
git commit -m "feat: add GEO meta tags and FAQ schema for AI search optimization"
```

## Extrahierte Design- und Stil-Elemente

### 1. Markenarchitektur

Empfohlenes System:

Augmented_Ops
  - VSA: Virtual Service Agency - Investor Pitchdecks
  - RSA: Recruitment Service Agency - Recruiting
  - CSA: Customer Support Agency - Customer Service
  - MSA/DSA: Marketing / Direct Sales Agency - Marketing, Outreach, Sales

Jede Sub-Agentur braucht:

[Code] . [Full Name]
Autonome KI-[Domain]-Agentur . Berlin
[Outcome], gebaut von einem Mesh autonomer KI-Agenten. Freigegeben von dir.

Beispiele:

VSA . Virtual Service Agency
Investoren-Decks, gebaut von einem Mesh autonomer KI-Agenten. Freigegeben von dir.

RSA . Recruitment Service Agency
Vakanzen, besetzt von einem Mesh autonomer KI-Agenten. Freigegeben von dir.

CSA . Customer Support Agency
Supportfaelle, geloest von einem Mesh autonomer KI-Agenten. Freigegeben von dir.

MSA . Marketing Service Agency
Kampagnen, gebaut von einem Mesh autonomer KI-Agenten. Freigegeben von dir.

### 2. Farbsystem

**Primaer: Navy-Trust**

CSS

--ao-navy-900: #0B1437;
--ao-navy-800: #13205C;
--ao-navy-700: #1A237E;
--ao-navy-600: #3949AB;
--ao-navy-500: #5C6BC0;
--ao-navy-tint: #EEF0FB;

--ao-ink: #0F172A;
--ao-slate-700: #334155;
--ao-slate-500: #64748B;
--ao-slate-400: #94A3B8;
--ao-slate-200: #E2E8F0;
--ao-slate-100: #F1F5F9;
--ao-slate-50: #F8FAFC;
--ao-white: #FFFFFF;

--ao-success: #059669;
--ao-warn: #D97706;
--ao-danger: #DC2626;

**Sekundaer: Ops-Neon**

CSS

--ao-black: #000000;
--ao-dark: #0D0D0D;
--ao-neon-blue: #00F0FF;
--ao-neon-green: #39FF14;

Regel: Navy-Trust fuer oeffentliche Services. Neon nur fuer Holding, Dashboards, Live-Systempanels oder Pitchdeck-Drama.

### 3. Typografie

CSS

--ao-font-ui: "Inter", system-ui, sans-serif;
--ao-font-mono: "JetBrains Mono", ui-monospace, monospace;

Verwendung:

Inter fuer Headlines, Body, Navigation, Buttons.

JetBrains Mono fuer Agenten-IDs, Status, Timestamps, Metriken, Checkpoints, Microcopy.

Keine Serifenschriften.

Headlines eng gesetzt, technisch, selbstbewusst.

Eyebrows in ALL CAPS mit ca. 0.12em Tracking.

### 4. Layout-System

Kanonische Landingpage-Struktur:

1. Fixed Nav
2. Hero: Claim links, Live-Agent-Panel rechts
3. Metric Strip: dunkles Navy-Band
4. Agenten-Sektion: 5-6 Agent Cards
5. Workflow: 5 Checkpoints mit Human Gates
6. Prinzipien: 4 Trust-Regeln
7. Domain-spezifische Sektion:
   - VSA: Ablauf / 96h
   - RSA: Preise / Rollen
   - CSA: Support-Metriken / Kanaele
   - Marketing: Funnel / Kampagnenmodule
8. FAQ
9. CTA
10. Footer mit Legal, DSGVO, Art. 22, Kontakt

### 5. Komponenten

Pflichtkomponenten fuer Skalierung:

AOLogo
Navigation
HeroWithAgentMesh
AgentMeshPanel
MetricStrip
AgentCard
WorkflowFlow
HumanGateStep
PrincipleCard
PricingCard
FAQList
CTABand
LegalFooter
SubAgencySwitcher

### 6. Karten und Flaechen

CSS

card:
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 28px oder 32px;
  box-shadow: 0 1px 2px rgba(15,23,42,.06);

card:hover:
  transform: translateY(-2px);
  border-color: #3949AB;
  box-shadow: 0 4px 12px rgba(15,23,42,.08);

Keine farbigen linken Card-Stripes im Navy-System. Das gehoert eher zur Neon/Ops-Variante.

### 7. Buttons

CSS

primary:
  background: #1A237E;
  color: #FFFFFF;
  border-radius: 9999px;
  box-shadow: 0 12px 32px -8px rgba(26,35,126,.35);

primary:hover:
  background: #13205C;
  transform: translateY(-1px);

Buttons im Service-System: Sentence case.

Deck anfragen
Vakanz oeffnen
Support automatisieren
Kampagne starten
Wie es funktioniert

Neon/Ops-Variante darf uppercase sein:

REQUEST A DEMO
TRANSMIT DATA
SYSTEM ONLINE

### 8. Motion

CSS

--ao-ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ao-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ao-dur-fast: 150ms;
--ao-dur-base: 200ms;
--ao-dur-mid: 300ms;
--ao-dur-slow: 600ms;

Regeln:

Reveals: opacity + y-translate.

Cards: hover lift, kein Scale.

CTA: -1px lift.

Statuspunkte: 2s Pulse.

Arrow: +3px translateX.

`prefers-reduced-motion` respektieren.

### 9. Bildsprache

Primaere Website: kaum Bilder, keine Stockfotos, keine Menschenfotos. Marke wirkt bewusst post-human, systemisch, auditierbar.

Ops-/Deck-Bildwelt:

Cyan-blaue Hologramme.

Schwarzer Hintergrund.

Datenmatrix / Mesh / digitale Buehne.

Kuehl, technisch, nicht verspielt.

### 10. Copy-System

Markenstimme:

Deutsch, du-Form.
Sachlich.
Trocken-lakonisch.
Keine Ausrufezeichen.
Keine Hype-Woerter.
Keine "revolutionary", "cutting-edge", "disruptive".

Wiederkehrende Formeln:

Agenten empfehlen. Menschen entscheiden.
Built by the mesh. Approved by the human.
Kein Output ohne Signatur.
Jede Zahl hat eine Quelle.
Keine Blackbox. Kein Retainer. Keine Provision.
Human-in-the-loop bei jedem Checkpoint.

VSA nutzt genau diese Logik in den Prinzipien: kein Output ohne Signatur, jede Zahl mit Quelle, nur reale Unternehmen und selbstreferenzielle Transparenz. VSA — Virtual Service Agency

---

## Skalierbares Sub-Agency-Template

Fuer jede neue Primaerleistung sollte dasselbe Muster gelten:

[Service-Outcome], gebaut/geloest/besetzt von einem Mesh autonomer KI-Agenten.
Freigegeben von dir.

### Marketing Service Agency

Agenten:

SCOUT - Markt- und Zielgruppenanalyse
STRATEGIST - Positionierung und Kampagnenlogik
COPYWRITER - Ads, Landingpages, E-Mail-Sequenzen
MEDIA - Kanalplanung und Budgetallokation
ANALYST - Performance, Attribution, Experimente
AUDITOR - Claims, Compliance, Brand Safety

### Recruiting Service Agency

RSA ist schon nahe am Ziel. Beibehalten:

SOURCER
SCREENER
MATCHER
INTERVIEWER
BIAS AUDITOR
ORCHESTRATOR

### Customer Support Agency

CSA sollte neu aufgebaut werden:

TRIAGE - Ticketklassifikation
RESOLVER - Loesungsvorschlaege und Antworten
VOICE - Telefon/Voice-Agent
KNOWLEDGE - Helpcenter und interne Wissensbasis
ESCALATION - Eskalation an Menschen
AUDITOR - Qualitaet, DSGVO, Risk Flags

### Investor Pitchdeck Service

VSA beibehalten:

SCOUT
NARRATOR
QUANT
ATELIER
AUDITOR
ORCHESTRATOR

---

## Wichtigste Inkonsistenzen

**CSA bricht die Markenlogik.**

Es wirkt wie eine einfache SaaS-/Startup-Landingpage. Es fehlen Mesh, Checkpoints, Freigabe, Audit und Legal Layer.

**Holding vs. Service-Seiten sind visuell zu weit auseinander.**

Neon kann stark sein, aber braucht klare Rolle als "Ops Layer", nicht als allgemeines Corporate Design.

**Kontakt- und Legal-Daten muessen vereinheitlicht werden.**

VSA/RSA nutzen Benjamin Poersch, Fused Firmament, DYAI2025, Berlin, DSGVO, Art. 22. CSA tut das lokal nicht ausreichend.

**Investor-Deck-Links in CSA verweisen generisch/teilweise falsch.**

CSA enthaelt Download-Links zu VSA/CSA/RSA-Decks, aber ohne dieselbe Marken- und Vertrauenslogik.

**Sub-Agentur-Namen sind noch nicht konsistent.**

Holding nutzt "Growth Deck", "Talent Swarm", "Voice Crew", "Forge Reach". Die Subseiten nutzen VSA/RSA/CSA. Empfehlung: Produktnamen duerfen existieren, aber die Architektur muss klar bleiben:

`VSA -> Growth Deck`, `RSA -> Talent Swarm`, `CSA -> Voice Crew`, `MSA -> Forge Reach`.

---

## Synthese & Empfehlungen

### Entscheidung 1: VSA/RSA als externes Master-System setzen

Das Navy-Trust-System sollte der Standard fuer alle Kundenseiten sein. Es ist serioes, compliance-faehig, skalierbar und wiedererkennbar.

### Entscheidung 2: Holding als "Control Layer" positionieren

Die schwarze Neon-Holding kann bleiben, aber mit klarer Semantik:

Augmented_Ops Holding = Control Room / AI Agent Company / System Layer
Sub-Agenturen = Trust Navy / Service Conversion / Compliance

### Entscheidung 3: CSA migrieren

CSA sollte nicht nur visuell, sondern narrativ neu gefasst werden:

Alt:
24/7 AI Customer Support for Startups.

Neu:
Supportfaelle, geloest von einem Mesh autonomer KI-Agenten. Freigegeben von dir.

### Entscheidung 4: Design Tokens zentralisieren

Alle Seiten sollten dieselbe `colors_and_type.css` oder ein daraus erzeugtes Token-Paket nutzen. Keine Einzel-CSS-Sonderloesungen pro Subseite.

### Entscheidung 5: Jede Service-Seite braucht denselben Trust-Kern

Pflichtmodule:

DSGVO
EU-Hosting
Art. 22
Human-in-the-loop
Audit Log
Quellen / Confidence
No output without signature
Legal Footer mit Betreiberangaben

VSA zeigt, dass diese Trust-Elemente nicht nur juristische Fussnoten sind, sondern Teil des Produktversprechens. Die FAQ erklaert Haftung, DSGVO, menschliche Freigabe, Ausschlusskriterien und AI-Search-Auffindbarkeit konkret. VSA — Virtual Service Agency

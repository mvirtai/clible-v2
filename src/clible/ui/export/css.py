"""Shared HTML export stylesheet (embedded in exported documents)."""

from __future__ import annotations

HTML_EXPORT_THEME = """<style>
:root {
  --bg: #f2f5ff;
  --card: #ffffff;
  --accent: #5b8bf6;
  --accent-strong: #3b5fcc;
  --text: #0f1b2d;
  --text-muted: #4b5d73;
  --divider: rgba(15, 27, 45, 0.08);
}
* { box-sizing: border-box; }
body {
  background: radial-gradient(circle at top, rgba(91, 139, 246, 0.15), transparent 45%),
              radial-gradient(circle at 30% 40%, rgba(59, 95, 204, 0.12), transparent 50%),
              #f6f8ff;
  color: var(--text);
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
  margin: 0;
}
main.page-shell {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px clamp(16px, 3vw, 40px) 48px;
}
.page-card {
  background: var(--card);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 28px;
  box-shadow: 0 20px 45px rgba(15, 27, 45, 0.08);
}
.glow {
  border: 1px solid var(--divider);
  border-radius: 18px;
  padding: 18px;
  background: linear-gradient(145deg, rgba(91, 139, 246, 0.08), rgba(255, 255, 255, 0.9));
}
.eyebrow {
  letter-spacing: 0.4em;
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
}
h1 {
  margin: 0.35rem 0 0.4rem;
  font-size: clamp(1.9rem, 3vw, 2.5rem);
  color: var(--accent-strong);
}
h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #18233d;
}
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.section-title.section-title--center {
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  text-align: center;
}
.section-title span {
  font-size: 0.85rem;
  color: var(--text-muted);
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}
th, td {
  padding: 12px 14px;
  text-align: left;
}
th {
  background: rgba(91, 139, 246, 0.12);
  color: var(--text);
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
}
tbody tr {
  border-bottom: 1px solid var(--divider);
}
.token-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}
.token-card {
  padding: 18px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid rgba(15, 27, 45, 0.08);
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: 0 15px 35px rgba(15, 27, 45, 0.08);
}
.token-rank {
  font-size: 0.75rem;
  color: var(--text-muted);
  letter-spacing: 0.2em;
  text-transform: uppercase;
}
.token-term {
  font-size: 1.2rem;
  font-weight: 600;
}
.token-count {
  font-size: 0.9rem;
  color: var(--accent);
}
.compare-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
.compare-card {
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(160deg, rgba(91, 139, 246, 0.12), rgba(255, 255, 255, 0.9));
  border: 1px solid rgba(15, 27, 45, 0.08);
  box-shadow: 0 15px 30px rgba(15, 27, 45, 0.08);
}
.compare-translation-head {
  text-align: center;
}
.compare-translation-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #18233d;
}
.compare-translation-id {
  margin: 6px 0 0;
  font-size: 0.85rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.compare-similarity {
  margin-top: 14px;
}
.verse-pair {
  border-radius: 18px;
  border: 1px solid rgba(15, 27, 45, 0.08);
  background: #ffffff;
  padding: 18px;
  margin-bottom: 16px;
  box-shadow: 0 14px 28px rgba(15, 27, 45, 0.06);
}
.verse-pair h3 {
  margin: 0;
  font-size: 1rem;
}
.verse-text {
  margin: 10px 0 0;
  font-size: 0.95rem;
  color: var(--text-muted);
  line-height: 1.5;
  text-align: center;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
  padding: 4px 0;
  border-bottom: 1px dashed var(--divider);
}
.summary-row:last-child {
  border-bottom: none;
}
.summary-label {
  color: var(--text-muted);
}
.summary-value {
  font-weight: 600;
  color: var(--accent-strong);
}
.footer-note {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-align: center;
  margin-top: 32px;
}
.title-stack {
  text-align: center;
  margin: 0 0 12px;
}
.title-stack h1 {
  margin: 0;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  letter-spacing: 0.04em;
  color: var(--accent-strong);
}
.title-stack .title-acronym {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
  letter-spacing: 0.2em;
}
@media (max-width: 640px) {
  main {
    padding: 24px 16px 32px;
  }
  th, td {
    padding: 10px;
  }
}
</style>"""

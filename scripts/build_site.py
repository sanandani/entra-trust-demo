#!/usr/bin/env python3
"""Build a self-contained static dashboard from the checked-in sample export."""

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SAMPLE = ROOT / "examples" / "sample-export.json"


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    reports = {"json": SITE / "report.json", "sarif": SITE / "report.sarif"}
    for output_format, output_path in reports.items():
        subprocess.run(
            [
                sys.executable,
                "-m",
                "aceu_entra_trust.cli",
                "--input",
                str(SAMPLE),
                "--format",
                output_format,
                "--out",
                str(output_path),
            ],
            cwd=ROOT,
            check=True,
        )

    report = json.loads(reports["json"].read_text(encoding="utf-8"))
    embedded = json.dumps(report, separators=(",", ":")).replace("<", "\\u003c")
    page = f'''<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>ACE-U · Entra Trust Dashboard</title>
  <style>
    :root {{ color-scheme: light; --bg:#f4f6f8; --surface:#fff; --ink:#18232d; --muted:#596975; --line:#dce3e8; --accent:#136b67; --accent-soft:#e2f1ef; --shadow:0 12px 32px #152b3510; }}
    [data-theme="dark"] {{ color-scheme:dark; --bg:#11191d; --surface:#1a252a; --ink:#edf4f4; --muted:#b2c0c2; --line:#35464a; --accent:#72d1c3; --accent-soft:#233b3a; --shadow:0 12px 32px #0005; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
    a {{ color:var(--accent); text-underline-offset:3px; }}
    button,input,select {{ font:inherit; }}
    button,select,input {{ color:var(--ink); background:var(--surface); border:1px solid var(--line); border-radius:10px; min-height:44px; padding:.55rem .8rem; }}
    button {{ cursor:pointer; }} button:hover {{ border-color:var(--accent); }}
    :focus-visible {{ outline:3px solid #2c9d92; outline-offset:3px; }}
    .shell {{ max-width:1180px; width:calc(100% - 40px); margin:auto; }}
    header {{ border-bottom:1px solid var(--line); background:var(--surface); }}
    .topbar {{ min-height:76px; display:flex; align-items:center; justify-content:space-between; gap:1rem; }}
    .brand {{ font-weight:800; letter-spacing:.01em; }} .brand small {{ display:block; color:var(--muted); font-weight:500; font-size:.8rem; }}
    .actions {{ display:flex; gap:.55rem; flex-wrap:wrap; align-items:center; }}
    main {{ padding:2rem 0 3rem; }}
    .intro {{ display:flex; justify-content:space-between; align-items:end; gap:1rem; margin-bottom:1.4rem; }}
    h1 {{ margin:.1rem 0 .25rem; font-size:clamp(1.8rem,4vw,2.7rem); letter-spacing:-.04em; }}
    h2 {{ font-size:1.15rem; margin:0 0 .8rem; }}
    p {{ margin:.3rem 0; }} .muted {{ color:var(--muted); }}
    .sample {{ display:inline-flex; align-items:center; gap:.45rem; background:#fff1d5; color:#583a00; border-radius:999px; padding:.42rem .75rem; font-size:.85rem; font-weight:700; }}
    [data-theme="dark"] .sample {{ background:#4a3815; color:#ffe3a3; }}
    .cards {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; margin:1.4rem 0 2rem; }}
    .panel,.identity {{ background:var(--surface); border:1px solid var(--line); border-radius:16px; box-shadow:var(--shadow); }}
    .summary {{ padding:1rem 1.1rem; }} .summary .label {{ color:var(--muted); font-size:.85rem; }} .summary .value {{ font-size:1.8rem; font-weight:800; letter-spacing:-.04em; }}
    .toolbar {{ padding:1rem; display:grid; grid-template-columns:minmax(180px,1fr) repeat(3,minmax(145px,.5fr)); gap:.7rem; margin-bottom:1rem; }}
    .identity-list {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem; }}
    .identity {{ padding:1.1rem; min-width:0; }}
    .identity-head {{ display:flex; align-items:flex-start; justify-content:space-between; gap:.8rem; }}
    .identity h3 {{ font-size:1.08rem; margin:0; overflow-wrap:anywhere; }} .app-id {{ color:var(--muted); font: .78rem/1.5 ui-monospace,monospace; overflow-wrap:anywhere; }}
    .score {{ display:flex; align-items:baseline; gap:.35rem; white-space:nowrap; }} .score strong {{ font-size:1.65rem; }} .score span {{ color:var(--muted); font-size:.78rem; }}
    .band {{ display:inline-block; border-radius:999px; text-transform:capitalize; padding:.2rem .6rem; font-size:.78rem; font-weight:750; }}
    .band.trusted {{ background:#dff3e7;color:#145c34; }} .band.review {{ background:#fff0d1;color:#744700; }} .band.risky {{ background:#fce3e3;color:#8d2727; }}
    [data-theme="dark"] .band.trusted {{background:#204833;color:#b1f0c4}} [data-theme="dark"] .band.review {{background:#51401f;color:#ffdc91}} [data-theme="dark"] .band.risky {{background:#542c31;color:#ffb9bd}}
    .pillar-list {{ display:grid; gap:.55rem; margin:1.1rem 0; }} .pillar-row {{ display:grid; grid-template-columns:1.2rem 1fr 2.2rem; gap:.5rem; align-items:center; font-size:.84rem; }}
    .track {{ height:8px; background:var(--line); border-radius:99px; overflow:hidden; }} .fill {{ height:100%; background:var(--accent); border-radius:inherit; }}
    details {{ border-top:1px solid var(--line); padding-top:.7rem; }} summary {{ cursor:pointer; color:var(--accent); font-weight:700; min-height:34px; }}
    .finding-list {{ display:grid; gap:.55rem; padding:.4rem 0 0; }} .finding {{ border-left:3px solid var(--line); padding:.45rem .65rem; background:var(--bg); border-radius:0 8px 8px 0; font-size:.88rem; }}
    .finding strong {{ font-family:ui-monospace,monospace; font-size:.8rem; }} .severity {{ text-transform:uppercase; font-size:.69rem; letter-spacing:.05em; font-weight:800; }}
    .severity.high {{ color:#bf3636; }} .severity.medium {{ color:#9b6500; }} .severity.low,.severity.info {{ color:var(--accent); }}
    .empty {{ grid-column:1/-1; text-align:center; padding:2rem; }}
    .explain {{ margin:2rem 0 0; padding:1.25rem; }} .explain[hidden] {{ display:none; }} .explain-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1.2rem; }}
    .explain ul {{ padding-left:1.2rem; }} .rule-table {{ width:100%; border-collapse:collapse; }} .rule-table th,.rule-table td {{ border-bottom:1px solid var(--line); text-align:left; vertical-align:top; padding:.55rem .45rem; }}
    footer {{ border-top:1px solid var(--line); padding:1.3rem 0 2rem; color:var(--muted); font-size:.88rem; }} .footer-row {{ display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem 1rem; }}
    @media (max-width:760px) {{ .cards {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .toolbar {{ grid-template-columns:1fr 1fr; }} .identity-list {{ grid-template-columns:1fr; }} .intro {{ align-items:flex-start; flex-direction:column; }} .explain-grid {{ grid-template-columns:1fr; }} }}
    @media (max-width:480px) {{ .shell {{ width:calc(100% - 24px); }} .topbar {{ align-items:flex-start; flex-direction:column; padding:.9rem 0; }} .actions {{ width:100%; }} .toolbar {{ grid-template-columns:1fr; }} .summary {{ padding:.85rem; }} .summary .value {{ font-size:1.55rem; }} }}
    @media (prefers-reduced-motion:reduce) {{ *,*::before,*::after {{ scroll-behavior:auto!important; transition:none!important; }} }}
  </style>
</head>
<body>
<header><div class="shell topbar">
  <div class="brand">ACE-U <span aria-hidden="true">/</span> ENTRA TRUST <small>Workload identity dashboard</small></div>
  <div class="actions" aria-label="Dashboard actions">
    <a class="button-link" href="report.json" download>Download JSON</a>
    <a class="button-link" href="report.sarif" download>Download SARIF</a>
    <button id="explain-toggle" type="button" aria-expanded="false" aria-controls="explain-panel">Explain score</button>
    <button id="theme-toggle" type="button" aria-label="Switch to dark theme">Dark mode</button>
  </div>
</div></header>
<main class="shell">
  <section class="intro" aria-labelledby="page-title">
    <div><p class="muted">Microsoft Entra · ACE-U</p><h1 id="page-title">Trust overview</h1><p class="muted">A transparent snapshot of identity signals across three pillars.</p></div>
    <span class="sample">● Sample data only—not a live tenant assessment.</span>
  </section>
  <section class="cards" id="summary" aria-label="Assessment summary" aria-live="polite"></section>
  <section class="panel toolbar" aria-label="Search and filters">
    <label>Search identities<input id="search" type="search" placeholder="Name or application ID" autocomplete="off"></label>
    <label>Band<select id="band-filter"><option value="all">All bands</option><option value="trusted">Trusted</option><option value="review">Review</option><option value="risky">Risky</option></select></label>
    <label>Finding severity<select id="severity-filter"><option value="all">All severities</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option><option value="info">Info</option></select></label>
    <label>Sort<select id="sort"><option value="desc">Score: high to low</option><option value="asc">Score: low to high</option></select></label>
  </section>
  <section id="identity-list" class="identity-list" aria-label="Identity assessments" aria-live="polite"></section>
  <section class="panel explain" id="explain-panel" hidden aria-labelledby="explain-title">
    <h2 id="explain-title">How the score works</h2>
    <div class="explain-grid">
      <div><h3>Definitions and thresholds</h3>
        <p><strong>Authenticity (A)</strong> — credential method and age signals for the application identity.</p>
        <p><strong>Uniqueness (U)</strong> — display name, audience, and listed owner signals.</p>
        <p><strong>Credibility (C)</strong> — credential expiry and app role assignment count.</p>
        <p>Total = <code>0.4 × A + 0.2 × U + 0.4 × C</code>. Each pillar is clamped to 0–100. Trusted: 80+; review: 55–79.99; risky: below 55.</p>
        <p><strong>Definition unavailable:</strong> the project does not provide an independently validated definition or measure of “trust”; this is a rule-based triage score only.</p>
      </div>
      <div><h3>Rule explanations</h3>
        <table class="rule-table"><thead><tr><th>Rule</th><th>Effect</th></tr></thead><tbody>
          <tr><td>ACEU001 · A</td><td>Secret present: base A=40; federated or managed identity: A=100; certificate-only: A=75.</td></tr>
          <tr><td>ACEU002 · A</td><td>Secret older than 180 days: −15 per qualifying secret.</td></tr>
          <tr><td>ACEU003 · A</td><td>Certificate older than 365 days: −10 per qualifying certificate.</td></tr>
          <tr><td>ACEU010 · U</td><td>Duplicate display name: −40 (case-insensitive after trimming).</td></tr>
          <tr><td>ACEU011 · U</td><td>Multi-tenant or personal account audience: −30.</td></tr>
          <tr><td>ACEU012 · U</td><td>No listed owner: −20.</td></tr>
          <tr><td>ACEU020 · C</td><td>Any expired credential: −25 once per identity.</td></tr>
          <tr><td>ACEU021 · C</td><td>More than five app role assignments: −10 each over five, capped at −50.</td></tr>
        </tbody></table>
        <p class="muted"><strong>Definition unavailable:</strong> the source defines no additional meaning for an individual “severity”; this dashboard displays the severity emitted by the scoring rules.</p>
      </div>
    </div>
    <p class="muted">Scores depend on input completeness and freshness. “Trusted” is a score band, not a security certification. <a href="https://github.com/sanandani/entra-trust-demo/blob/main/docs/trust-model.md">Read the trust model</a>.</p>
  </section>
</main>
<footer><div class="shell footer-row"><span>© 2026 Shubham Anandani. <a href="../LICENSE">License (MIT)</a></span><span>Created by <a href="https://imshubh.com">Shubham Anandani · imshubh.com</a></span><a href="https://github.com/sanandani/entra-trust-demo">Repository</a></div></footer>
<script id="report-data" type="application/json">{embedded}</script>
<script>
(() => {{
  "use strict";
  const report = JSON.parse(document.getElementById("report-data").textContent);
  const identities = report.results || [];
  const summary = document.getElementById("summary");
  const list = document.getElementById("identity-list");
  const filters = {{ search: document.getElementById("search"), band: document.getElementById("band-filter"), severity: document.getElementById("severity-filter"), sort: document.getElementById("sort") }};
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[char]));

  function renderSummary(items) {{
    const avg = items.length ? (items.reduce((sum, item) => sum + item.total, 0) / items.length).toFixed(1) : "—";
    const bands = ["trusted", "review", "risky"];
    const counts = Object.fromEntries(bands.map((band) => [band, items.filter((item) => item.band === band).length]));
    summary.innerHTML = [
      ["Identities", items.length], ["Average score", avg], ["Trusted", counts.trusted], ["Need review or risky", counts.review + counts.risky]
    ].map(([label, value]) => `<article class="panel summary"><div class="label">${{esc(label)}}</div><div class="value">${{esc(value)}}</div></article>`).join("");
  }}

  function card(item) {{
    const pillarNames = [["A", "Authenticity"], ["U", "Uniqueness"], ["C", "Credibility"]];
    const pillarRows = pillarNames.map(([short, name]) => {{
      const value = item.scores[name];
      return `<div class="pillar-row"><strong>${{short}}</strong><div class="track" role="img" aria-label="${{name}} score ${{value}} out of 100"><div class="fill" style="width:${{Math.max(0, Math.min(100, value))}}%"></div></div><span>${{value}}</span></div>`;
    }}).join("");
    const findings = item.findings || [];
    const findingRows = findings.length ? findings.map((finding) => `<div class="finding"><div><strong>${{esc(finding.id)}}</strong> · <span class="severity ${{esc(finding.severity)}}">${{esc(finding.severity)}}</span></div><div>${{esc(finding.message)}}</div></div>`).join("") : `<p class="muted">No findings emitted by the configured rules.</p>`;
    return `<article class="identity">
      <div class="identity-head"><div><h3>${{esc(item.displayName || "Unnamed identity")}}</h3><div class="app-id">${{esc(item.id)}}${{item.appId ? ` · ${{esc(item.appId)}}` : ""}}</div></div>
      <div style="text-align:right"><div class="score"><strong>${{Number(item.total).toFixed(1)}}</strong><span>/ 100</span></div><span class="band ${{esc(item.band)}}">${{esc(item.band)}}</span></div></div>
      <div class="pillar-list">${{pillarRows}}</div>
      <details><summary>Findings (${{findings.length}})</summary><div class="finding-list">${{findingRows}}</div></details>
    </article>`;
  }}

  function render() {{
    const query = filters.search.value.trim().toLocaleLowerCase();
    const band = filters.band.value;
    const severity = filters.severity.value;
    let visible = identities.filter((item) => {{
      const matchesText = `${{item.displayName || ""}} ${{item.id || ""}} ${{item.appId || ""}}`.toLocaleLowerCase().includes(query);
      const matchesBand = band === "all" || item.band === band;
      const matchesSeverity = severity === "all" || (item.findings || []).some((finding) => finding.severity === severity);
      return matchesText && matchesBand && matchesSeverity;
    }});
    visible.sort((a, b) => filters.sort.value === "asc" ? a.total - b.total : b.total - a.total);
    renderSummary(identities);
    list.innerHTML = visible.length ? visible.map(card).join("") : `<div class="panel empty">No identities match these filters.</div>`;
  }}

  Object.values(filters).forEach((control) => control.addEventListener(control === filters.search ? "input" : "change", render));
  const explainButton = document.getElementById("explain-toggle");
  explainButton.addEventListener("click", () => {{
    const panel = document.getElementById("explain-panel");
    const open = panel.hidden;
    panel.hidden = !open;
    explainButton.setAttribute("aria-expanded", String(open));
    if (open) panel.scrollIntoView({{ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }});
  }});
  const themeButton = document.getElementById("theme-toggle");
  themeButton.addEventListener("click", () => {{
    const root = document.documentElement;
    const dark = root.dataset.theme !== "dark";
    root.dataset.theme = dark ? "dark" : "light";
    themeButton.textContent = dark ? "Light mode" : "Dark mode";
    themeButton.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
  }});
  render();
}})();
</script>
</body>
</html>
'''
    (SITE / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()

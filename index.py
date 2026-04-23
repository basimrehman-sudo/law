from flask import Flask, render_template_string, request, jsonify
import os, requests

app = Flask(__name__)

# ---------------------------------------------------------------------------
# GEMINI / GROK PLACEHOLDERS  (add your keys to a .env file later)
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROK_API_KEY   = os.getenv("GROK_API_KEY", "")

# ---------------------------------------------------------------------------
# SHARED LAYOUT
# ---------------------------------------------------------------------------
BASE_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inconsolata:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --navy:   #0b1628;
  --navy2:  #12213a;
  --navy3:  #1a2f4f;
  --gold:   #c9a84c;
  --gold2:  #e8c97a;
  --cream:  #f5f0e8;
  --cream2: #ede5d4;
  --text:   #e8dfc8;
  --muted:  #8a9ab5;
  --border: rgba(201,168,76,0.22);
  --radius: 6px;
}

html { scroll-behavior: smooth; }
body {
  font-family: 'Libre Baskerville', Georgia, serif;
  background: var(--navy);
  color: var(--text);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── SIDEBAR ── */
.sidebar {
  position: fixed; top: 0; left: 0;
  width: 230px; height: 100vh;
  background: var(--navy2);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  z-index: 100; padding: 0;
  overflow: hidden;
}
.sidebar-logo {
  padding: 28px 24px 20px;
  border-bottom: 1px solid var(--border);
}
.sidebar-logo .seal {
  font-family: 'IM Fell English', serif;
  font-size: 11px; letter-spacing: 0.15em;
  color: var(--gold); text-transform: uppercase;
  display: block; margin-bottom: 4px;
}
.sidebar-logo h1 {
  font-family: 'IM Fell English', serif;
  font-size: 19px; color: var(--cream);
  line-height: 1.25; font-weight: 400;
}
.sidebar-logo .tagline {
  font-family: 'Inconsolata', monospace;
  font-size: 10px; color: var(--muted);
  letter-spacing: 0.08em; margin-top: 6px;
  display: block;
}

nav { flex: 1; padding: 16px 0; overflow-y: auto; }
.nav-section { padding: 8px 20px 4px; }
.nav-section span {
  font-family: 'Inconsolata', monospace;
  font-size: 9px; letter-spacing: 0.2em;
  color: var(--muted); text-transform: uppercase;
}
.nav-link {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 20px; color: var(--muted);
  text-decoration: none; font-size: 13.5px;
  font-family: 'Libre Baskerville', serif;
  border-left: 3px solid transparent;
  transition: all 0.18s ease;
  position: relative;
}
.nav-link svg { width: 15px; height: 15px; opacity: 0.7; flex-shrink: 0; }
.nav-link:hover { color: var(--cream); background: rgba(201,168,76,0.07); border-left-color: var(--gold); }
.nav-link.active { color: var(--gold2); background: rgba(201,168,76,0.1); border-left-color: var(--gold); }
.nav-link.active svg { opacity: 1; }

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  font-family: 'Inconsolata', monospace;
  font-size: 10px; color: var(--muted);
  line-height: 1.6;
}

/* ── MAIN CONTENT ── */
.main { margin-left: 230px; flex: 1; display: flex; flex-direction: column; min-height: 100vh; }
.topbar {
  padding: 18px 36px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(11,22,40,0.7); backdrop-filter: blur(8px);
  position: sticky; top: 0; z-index: 50;
}
.topbar-title {
  font-family: 'IM Fell English', serif;
  font-size: 20px; color: var(--cream); font-weight: 400;
}
.topbar-meta {
  font-family: 'Inconsolata', monospace;
  font-size: 11px; color: var(--muted);
}
.content { padding: 40px 36px; flex: 1; }

/* ── CARDS ── */
.card {
  background: var(--navy2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px;
}
.card-sm { padding: 20px 24px; }
.card h2 {
  font-family: 'IM Fell English', serif;
  font-size: 17px; font-weight: 400;
  color: var(--cream2); margin-bottom: 12px;
}
.card p { font-size: 13.5px; color: var(--muted); line-height: 1.7; }

/* ── GRID ── */
.grid { display: grid; gap: 20px; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

/* ── STAT CARDS ── */
.stat {
  background: var(--navy2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 22px 24px;
  position: relative; overflow: hidden;
}
.stat::after {
  content: ''; position: absolute; top: 0; left: 0;
  width: 3px; height: 100%; background: var(--gold);
}
.stat .label { font-family:'Inconsolata',monospace; font-size:10px; letter-spacing:0.15em; color:var(--muted); text-transform:uppercase; }
.stat .value { font-family:'IM Fell English',serif; font-size:32px; color:var(--gold2); margin: 4px 0; }
.stat .sub { font-size:12px; color:var(--muted); }

/* ── SEARCH BAR ── */
.search-wrap { position: relative; }
.search-wrap input {
  width: 100%; padding: 14px 20px 14px 46px;
  background: var(--navy3); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--cream);
  font-family: 'Libre Baskerville', serif; font-size: 14px;
  outline: none; transition: border-color 0.2s;
}
.search-wrap input::placeholder { color: var(--muted); }
.search-wrap input:focus { border-color: var(--gold); }
.search-icon {
  position: absolute; left: 16px; top: 50%; transform: translateY(-50%);
  color: var(--muted); pointer-events: none;
}
.search-wrap select {
  margin-top: 12px; width: 100%; padding: 10px 16px;
  background: var(--navy3); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--text);
  font-family: 'Libre Baskerville', serif; font-size: 13px; outline: none;
}
.search-wrap select:focus { border-color: var(--gold); }

/* ── BUTTONS ── */
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 22px; border-radius: var(--radius);
  font-family: 'Inconsolata', monospace; font-size: 13px;
  letter-spacing: 0.05em; cursor: pointer; border: none;
  transition: all 0.18s ease; text-decoration: none;
}
.btn-gold { background: var(--gold); color: var(--navy); font-weight: 500; }
.btn-gold:hover { background: var(--gold2); }
.btn-outline { background: transparent; border: 1px solid var(--border); color: var(--muted); }
.btn-outline:hover { border-color: var(--gold); color: var(--gold2); }

/* ── RESULT ITEMS ── */
.result-item {
  background: var(--navy2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px 24px; margin-bottom: 14px;
  transition: border-color 0.18s;
}
.result-item:hover { border-color: rgba(201,168,76,0.5); }
.result-item .title {
  font-family: 'IM Fell English', serif; font-size: 16px;
  color: var(--gold2); margin-bottom: 6px;
}
.result-item .meta {
  font-family: 'Inconsolata', monospace; font-size: 11px;
  color: var(--muted); letter-spacing: 0.05em; margin-bottom: 8px;
}
.result-item .excerpt { font-size: 13px; color: var(--muted); line-height: 1.7; }
.badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  font-family: 'Inconsolata', monospace; font-size: 10px;
  letter-spacing: 0.08em; border: 1px solid var(--border);
  color: var(--gold); margin-right: 6px;
}

/* ── AI CHAT ── */
.chat-container {
  display: flex; flex-direction: column; height: calc(100vh - 180px);
  background: var(--navy2); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden;
}
.chat-header {
  padding: 16px 24px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
}
.ai-badge {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'IM Fell English', serif; font-size: 14px;
}
.ai-badge.research { background: rgba(201,168,76,0.15); color: var(--gold2); border: 1px solid var(--border); }
.ai-badge.draft { background: rgba(26,47,79,0.8); color: var(--muted); border: 1px solid var(--border); }
.chat-header h2 { font-family:'IM Fell English',serif; font-size:16px; font-weight:400; color:var(--cream); }
.chat-header p { font-size:12px; color:var(--muted); font-family:'Inconsolata',monospace; }
.chat-messages { flex:1; overflow-y:auto; padding: 24px; display:flex; flex-direction:column; gap:16px; }
.msg { max-width:80%; display:flex; flex-direction:column; gap:4px; }
.msg.user { align-self:flex-end; }
.msg.assistant { align-self:flex-start; }
.msg .bubble {
  padding: 12px 18px; border-radius: 8px;
  font-size: 13.5px; line-height: 1.7;
}
.msg.user .bubble { background: rgba(201,168,76,0.15); border: 1px solid rgba(201,168,76,0.3); color: var(--cream); }
.msg.assistant .bubble { background: var(--navy3); border: 1px solid var(--border); color: var(--text); }
.msg .time { font-family:'Inconsolata',monospace; font-size:10px; color:var(--muted); }
.msg.user .time { text-align:right; }
.chat-input-row {
  padding: 16px 24px; border-top: 1px solid var(--border);
  display: flex; gap: 12px; align-items: flex-end;
}
.chat-input-row textarea {
  flex: 1; background: var(--navy3); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--cream);
  font-family: 'Libre Baskerville', serif; font-size: 13.5px;
  padding: 12px 16px; resize: none; outline: none;
  min-height: 48px; max-height: 140px; transition: border-color 0.2s;
}
.chat-input-row textarea:focus { border-color: var(--gold); }
.chat-input-row textarea::placeholder { color: var(--muted); }

/* ── TABLE ── */
table { width:100%; border-collapse: collapse; font-size:13.5px; }
th {
  text-align:left; padding:10px 16px;
  font-family:'Inconsolata',monospace; font-size:10px;
  letter-spacing:0.12em; color:var(--muted);
  border-bottom: 1px solid var(--border); text-transform:uppercase;
}
td { padding:13px 16px; border-bottom: 1px solid rgba(201,168,76,0.08); color:var(--text); }
tr:hover td { background:rgba(201,168,76,0.04); }

/* ── DIVIDER ── */
.divider { border:none; border-top: 1px solid var(--border); margin: 28px 0; }
.section-heading {
  font-family:'IM Fell English',serif; font-size:13px; font-weight:400;
  color:var(--gold); letter-spacing:0.12em; text-transform:uppercase;
  margin-bottom: 16px; display:flex; align-items:center; gap:10px;
}
.section-heading::after { content:''; flex:1; height:1px; background:var(--border); }

/* ── LOADING SPINNER ── */
.spinner {
  width: 18px; height: 18px; border: 2px solid rgba(201,168,76,0.2);
  border-top-color: var(--gold); border-radius: 50%;
  animation: spin 0.7s linear infinite; display:none;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── ORNAMENT ── */
.ornament {
  text-align:center; color:var(--border); font-size:18px;
  letter-spacing:0.3em; user-select:none;
}

/* ── QUICK LINK TILES ── */
.tile {
  background: var(--navy2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 24px;
  display:flex; flex-direction:column; gap:10px;
  text-decoration:none; transition: all 0.2s;
  position:relative; overflow:hidden;
}
.tile::before {
  content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  opacity:0; transition: opacity 0.2s;
}
.tile:hover { border-color: rgba(201,168,76,0.45); transform: translateY(-2px); }
.tile:hover::before { opacity:1; }
.tile .tile-icon { font-size:22px; }
.tile .tile-title { font-family:'IM Fell English',serif; font-size:15px; color:var(--cream); }
.tile .tile-desc { font-size:12px; color:var(--muted); line-height:1.6; }

/* ── PLACEHOLDER NOTICE ── */
.api-notice {
  background: rgba(201,168,76,0.06); border: 1px solid rgba(201,168,76,0.2);
  border-radius: var(--radius); padding: 12px 18px;
  font-family:'Inconsolata',monospace; font-size:11.5px; color:var(--gold);
  margin-bottom: 20px; display:flex; align-items:center; gap:10px;
}

@media (max-width: 900px) {
  .sidebar { width: 64px; }
  .sidebar-logo h1, .sidebar-logo .seal, .sidebar-logo .tagline,
  .nav-section, .nav-link span, .sidebar-footer { display:none; }
  .nav-link { justify-content:center; padding:14px; }
  .main { margin-left: 64px; }
  .grid-4 { grid-template-columns: repeat(2,1fr); }
  .grid-3 { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
  .content { padding: 24px 18px; }
  .topbar { padding: 14px 18px; }
}
"""

SIDEBAR_HTML = """
<aside class="sidebar">
  <div class="sidebar-logo">
    <span class="seal">⚖ Meezan</span>
    <h1>Pakistan<br>Legal Suite</h1>
    <span class="tagline">For Advocates &amp; Counsel</span>
  </div>
  <nav>
    <div class="nav-section"><span>Main</span></div>
    <a href="/" class="nav-link {a_dash}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
      <span>Dashboard</span>
    </a>
    <div class="nav-section"><span>Research</span></div>
    <a href="/judgements" class="nav-link {a_judg}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/></svg>
      <span>Judgement Search</span>
    </a>
    <a href="/statutes" class="nav-link {a_stat}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>
      <span>Statute Search</span>
    </a>
    <div class="nav-section"><span>AI Tools</span></div>
    <a href="/research-ai" class="nav-link {a_rai}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
      <span>Research AI</span>
    </a>
    <a href="/draft-ai" class="nav-link {a_dai}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
      <span>Drafting AI</span>
    </a>
  </nav>
  <div class="sidebar-footer">
    Meezan Legal Suite<br>
    v1.0 &bull; Islamabad, PK
  </div>
</aside>
"""

def sidebar(active="dash"):
    flags = {"a_dash":"","a_judg":"","a_stat":"","a_rai":"","a_dai":""}
    key = {"dash":"a_dash","judgements":"a_judg","statutes":"a_stat","research":"a_rai","draft":"a_dai"}.get(active,"a_dash")
    flags[key] = "active"
    return SIDEBAR_HTML.format(**flags)

def page(title, active, content, topbar_sub=""):
    return render_template_string(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Meezan Legal Suite</title>
<style>{BASE_STYLE}</style>
</head>
<body>
{sidebar(active)}
<div class="main">
  <div class="topbar">
    <div>
      <div class="topbar-title">{title}</div>
      {f'<div class="topbar-meta">{topbar_sub}</div>' if topbar_sub else ''}
    </div>
    <div class="topbar-meta" id="clock"></div>
  </div>
  <div class="content">{content}</div>
</div>
<script>
(function(){{
  function tick(){{
    var d=new Date();
    document.getElementById('clock').textContent=
      d.toLocaleDateString('en-PK',{{weekday:'short',day:'numeric',month:'long',year:'numeric'}})
      +' · '+d.toLocaleTimeString('en-PK',{{hour:'2-digit',minute:'2-digit'}});
  }}
  tick(); setInterval(tick,30000);
}})();
</script>
</body>
</html>""")


# ===========================================================================
# ROUTES
# ===========================================================================

@app.route("/")
def dashboard():
    content = """
<div class="ornament" style="margin-bottom:32px; font-size:13px; letter-spacing:0.4em; color:var(--gold); opacity:0.6;">
  ✦  ✦  ✦
</div>

<div style="margin-bottom:36px;">
  <h2 style="font-family:'IM Fell English',serif; font-size:28px; font-weight:400; color:var(--cream); margin-bottom:8px;">
    Marhaba, Counsel.
  </h2>
  <p style="color:var(--muted); font-size:14px; line-height:1.7; max-width:560px;">
    Your integrated research and drafting suite for Pakistani law.
    Search judgements from superior courts, navigate statutes, and leverage AI for legal research and document drafting.
  </p>
</div>

<div class="grid grid-4" style="margin-bottom:36px;">
  <div class="stat">
    <div class="label">Judgements Indexed</div>
    <div class="value">1.2M+</div>
    <div class="sub">Supreme Court &amp; High Courts</div>
  </div>
  <div class="stat">
    <div class="label">Statutes &amp; Acts</div>
    <div class="value">4,800+</div>
    <div class="sub">Federal &amp; Provincial</div>
  </div>
  <div class="stat">
    <div class="label">AI Models</div>
    <div class="value">2</div>
    <div class="sub">Research &amp; Drafting</div>
  </div>
  <div class="stat">
    <div class="label">Jurisdictions</div>
    <div class="value">5</div>
    <div class="sub">SCP · LHC · SHC · PHC · BHC</div>
  </div>
</div>

<div class="section-heading">Quick Access</div>
<div class="grid grid-3" style="margin-bottom:36px;">
  <a href="/judgements" class="tile">
    <div class="tile-icon">📜</div>
    <div class="tile-title">Judgement Search</div>
    <div class="tile-desc">Search case law from the Supreme Court, High Courts, and Federal Shariat Court by citation, party name, or keyword.</div>
  </a>
  <a href="/statutes" class="tile">
    <div class="tile-icon">⚖️</div>
    <div class="tile-title">Statute Search</div>
    <div class="tile-desc">Browse and search all Federal and Provincial Acts, Ordinances, and Regulations of Pakistan.</div>
  </a>
  <a href="/research-ai" class="tile">
    <div class="tile-icon">🔍</div>
    <div class="tile-title">Research AI</div>
    <div class="tile-desc">Ask legal questions, find relevant precedents, and build case arguments with AI-powered research assistance.</div>
  </a>
  <a href="/draft-ai" class="tile">
    <div class="tile-icon">✍️</div>
    <div class="tile-title">Drafting AI</div>
    <div class="tile-desc">Draft plaints, written statements, contracts, legal notices, and petitions with AI guidance.</div>
  </a>
  <div class="tile" style="cursor:default; opacity:0.6;">
    <div class="tile-icon">📁</div>
    <div class="tile-title">Case Files <span style="font-size:10px; font-family:'Inconsolata',monospace; color:var(--gold); margin-left:6px;">COMING SOON</span></div>
    <div class="tile-desc">Organise your matters, upload documents, and keep case notes in one place.</div>
  </div>
  <div class="tile" style="cursor:default; opacity:0.6;">
    <div class="tile-icon">📅</div>
    <div class="tile-title">Cause List <span style="font-size:10px; font-family:'Inconsolata',monospace; color:var(--gold); margin-left:6px;">COMING SOON</span></div>
    <div class="tile-desc">Check daily cause lists from superior courts across Pakistan.</div>
  </div>
</div>

<div class="section-heading">Recent Landmark Cases</div>
<table>
  <thead>
    <tr>
      <th>Citation</th><th>Parties</th><th>Court</th><th>Year</th><th>Subject</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="color:var(--gold); font-family:'Inconsolata',monospace; font-size:12px;">PLD 2023 SC 1</td>
      <td>Imran Ahmad Khan Niazi v. Federation of Pakistan</td>
      <td>Supreme Court</td><td>2023</td><td>Constitutional — Article 10-A</td>
    </tr>
    <tr>
      <td style="color:var(--gold); font-family:'Inconsolata',monospace; font-size:12px;">PLD 2022 SC 590</td>
      <td>Ahmad Ali v. Province of Punjab</td>
      <td>Supreme Court</td><td>2022</td><td>Fundamental Rights</td>
    </tr>
    <tr>
      <td style="color:var(--gold); font-family:'Inconsolata',monospace; font-size:12px;">2021 SCMR 1001</td>
      <td>Zulfiqar Ali v. State</td>
      <td>Supreme Court</td><td>2021</td><td>Criminal — Bail Jurisprudence</td>
    </tr>
    <tr>
      <td style="color:var(--gold); font-family:'Inconsolata',monospace; font-size:12px;">PLD 2020 Lahore 1</td>
      <td>M/s Green Valley v. Bank of Punjab</td>
      <td>Lahore High Court</td><td>2020</td><td>Banking — Default</td>
    </tr>
  </tbody>
</table>
"""
    return page("Dashboard", "dash", content, "Pakistan Legal Research Suite")


@app.route("/judgements")
def judgements():
    query   = request.args.get("q","")
    court   = request.args.get("court","all")
    year    = request.args.get("year","")

    results_html = ""
    if query:
        results_html = f"""
<div class="section-heading" style="margin-top:28px;">Search Results</div>
<div class="api-notice">
  ⚠ Live database integration pending. Showing illustrative results for <em>"{query}"</em>.
  Connect PLD, SCMR, or the Law &amp; Justice Commission API to enable real search.
</div>
<div class="result-item">
  <div class="title">Muhammad Akbar v. Federation of Pakistan</div>
  <div class="meta">
    <span class="badge">PLD 2022 SC 45</span>
    <span class="badge">Supreme Court</span>
    <span class="badge">Constitutional</span>
  </div>
  <div class="excerpt">
    The apex court held that the impugned notification was ultra vires the Constitution insofar as it sought to curtail
    the fundamental rights guaranteed under Article 19-A. The principle of proportionality was extensively discussed…
  </div>
</div>
<div class="result-item">
  <div class="title">State v. Ghulam Hussain &amp; Others</div>
  <div class="meta">
    <span class="badge">2021 SCMR 812</span>
    <span class="badge">Supreme Court</span>
    <span class="badge">Criminal</span>
  </div>
  <div class="excerpt">
    Bail application dismissed. The court reiterated that where the sentence likely to be awarded is death or life imprisonment,
    the bar under Section 497 Cr.P.C. operates with full rigour…
  </div>
</div>
<div class="result-item">
  <div class="title">Fatima Enterprises v. NBP</div>
  <div class="meta">
    <span class="badge">2020 CLD 300</span>
    <span class="badge">Lahore High Court</span>
    <span class="badge">Banking</span>
  </div>
  <div class="excerpt">
    The honourable court found that the bank failed to comply with the mandatory notice provisions of the Financial Institutions
    (Recovery of Finances) Ordinance, 2001 before initiating recovery proceedings…
  </div>
</div>
"""

    content = f"""
<p style="color:var(--muted); font-size:13.5px; margin-bottom:28px; line-height:1.7; max-width:600px;">
  Search over 1.2 million judgements from the Supreme Court of Pakistan, Federal Shariat Court,
  and all four High Courts. Search by party name, citation, or legal keyword.
</p>

<div class="card" style="margin-bottom:24px;">
  <form method="GET" action="/judgements">
    <div class="search-wrap">
      <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input type="text" name="q" placeholder="Search by party name, citation (e.g. PLD 2022 SC 1), or keyword…"
        value="{query}">
    </div>
    <div style="display:flex; gap:12px; margin-top:12px; flex-wrap:wrap;">
      <select name="court" style="flex:1; min-width:160px;">
        <option value="all" {"selected" if court=="all" else ""}>All Courts</option>
        <option value="sc" {"selected" if court=="sc" else ""}>Supreme Court</option>
        <option value="fsc" {"selected" if court=="fsc" else ""}>Federal Shariat Court</option>
        <option value="lhc" {"selected" if court=="lhc" else ""}>Lahore High Court</option>
        <option value="shc" {"selected" if court=="shc" else ""}>Sindh High Court</option>
        <option value="phc" {"selected" if court=="phc" else ""}>Peshawar High Court</option>
        <option value="bhc" {"selected" if court=="bhc" else ""}>Balochistan High Court</option>
      </select>
      <input type="number" name="year" placeholder="Year (e.g. 2022)"
        value="{year}"
        style="flex:1; min-width:120px; padding:10px 16px; background:var(--navy3); border:1px solid var(--border); border-radius:var(--radius); color:var(--text); font-family:'Libre Baskerville',serif; font-size:13px; outline:none;">
      <button type="submit" class="btn btn-gold">Search Judgements</button>
    </div>
  </form>
</div>

{results_html if results_html else '''
<div class="section-heading">Browse by Court</div>
<div class="grid grid-3">
  <div class="card card-sm"><h2>Supreme Court of Pakistan</h2><p>Citations: PLD SC, SCMR, PTD — Landmark constitutional and civil matters.</p></div>
  <div class="card card-sm"><h2>Lahore High Court</h2><p>Citations: PLD Lahore, PLJ — Punjab&#39;s largest repository of High Court judgements.</p></div>
  <div class="card card-sm"><h2>Sindh High Court</h2><p>Citations: PLD Karachi, SBLR — Covering Karachi and Hyderabad benches.</p></div>
  <div class="card card-sm"><h2>Federal Shariat Court</h2><p>Citations: PLD FSC — Interpretation of laws against Quran and Sunnah.</p></div>
  <div class="card card-sm"><h2>Peshawar High Court</h2><p>Citations: PLD Peshawar — KP and former FATA territories.</p></div>
  <div class="card card-sm"><h2>Balochistan High Court</h2><p>Citations: PLD Quetta — Balochistan Provincial matters.</p></div>
</div>
'''}
"""
    return page("Judgement Search", "judgements", content, "Superior Courts of Pakistan")


@app.route("/statutes")
def statutes():
    query    = request.args.get("q","")
    category = request.args.get("cat","all")

    results_html = ""
    if query:
        results_html = f"""
<div class="section-heading" style="margin-top:28px;">Results for "{query}"</div>
<div class="api-notice">
  ⚠ Live statute database integration pending. Connect the Law &amp; Justice Commission of Pakistan API for real results.
</div>
<div class="result-item">
  <div class="title">Code of Civil Procedure, 1908</div>
  <div class="meta"><span class="badge">Federal</span><span class="badge">Procedural Law</span><span class="badge">Act V of 1908</span></div>
  <div class="excerpt">The primary legislation governing civil procedure in Pakistan. Contains 158 sections and Orders regulating institution, trial, and execution of civil suits in all courts.</div>
</div>
<div class="result-item">
  <div class="title">Contract Act, 1872</div>
  <div class="meta"><span class="badge">Federal</span><span class="badge">Civil Law</span><span class="badge">Act IX of 1872</span></div>
  <div class="excerpt">Foundational legislation on contracts, their formation, performance, and breach. Applies throughout Pakistan and forms the basis of commercial and civil obligations.</div>
</div>
<div class="result-item">
  <div class="title">Criminal Procedure Code, 1898</div>
  <div class="meta"><span class="badge">Federal</span><span class="badge">Criminal</span><span class="badge">Act V of 1898</span></div>
  <div class="excerpt">Governs procedure for investigation, inquiry, trial, and disposal of criminal cases. Includes provisions on arrest, bail, cognizance, and appeals.</div>
</div>
"""

    cats = [
        ("all","All Categories"),("const","Constitutional Law"),("civil","Civil Law"),
        ("crim","Criminal Law"),("corp","Corporate &amp; Commercial"),("tax","Tax &amp; Revenue"),
        ("land","Land &amp; Property"),("family","Family &amp; Personal Status"),("labor","Labour Law"),
    ]
    cat_opts = "".join(f'<option value="{v}" {"selected" if category==v else ""}>{l}</option>' for v,l in cats)

    content = f"""
<p style="color:var(--muted); font-size:13.5px; margin-bottom:28px; line-height:1.7; max-width:600px;">
  Browse and search Federal and Provincial legislation, including Acts, Ordinances, Statutory Rules and Orders (SROs),
  and Regulations currently in force in Pakistan.
</p>

<div class="card" style="margin-bottom:24px;">
  <form method="GET" action="/statutes">
    <div class="search-wrap">
      <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input type="text" name="q" placeholder="Search by Act name, subject, or section keyword…" value="{query}">
    </div>
    <div style="display:flex; gap:12px; margin-top:12px; flex-wrap:wrap;">
      <select name="cat" style="flex:1;">{cat_opts}</select>
      <button type="submit" class="btn btn-gold">Search Statutes</button>
    </div>
  </form>
</div>

{results_html if results_html else '''
<div class="section-heading">Key Legislation</div>
<div class="grid grid-2">
  <div class="card card-sm">
    <h2>Constitution of Pakistan, 1973</h2>
    <p>The supreme law. 280 Articles, 6 Schedules. Fundamental rights, federal structure, judicature, and emergency provisions.</p>
  </div>
  <div class="card card-sm">
    <h2>Pakistan Penal Code, 1860</h2>
    <p>Primary criminal statute defining offences and prescribing punishments — from general exceptions to specific crimes against the state, person, and property.</p>
  </div>
  <div class="card card-sm">
    <h2>Transfer of Property Act, 1882</h2>
    <p>Governs transfer of immovable property inter vivos — sale, mortgage, lease, exchange, gift, and actionable claims.</p>
  </div>
  <div class="card card-sm">
    <h2>Companies Act, 2017</h2>
    <p>Modern corporate legislation replacing the Companies Ordinance 1984 — incorporation, governance, and winding up.</p>
  </div>
</div>
'''}
"""
    return page("Statute Search", "statutes", content, "Federal & Provincial Legislation")


# ---------------------------------------------------------------------------
# SHARED AI CHAT FUNCTION
# ---------------------------------------------------------------------------
def ai_chat_page(ai_type):
    is_research = ai_type == "research"
    title    = "Research AI" if is_research else "Drafting AI"
    active   = "research" if is_research else "draft"
    badge_cls= "research" if is_research else "draft"
    badge_ltr= "R" if is_research else "D"
    desc     = ("Legal research assistant. Ask about case law, precedents, legal principles, and statutory interpretation.") if is_research \
               else ("Drafting assistant. Describe the document you need — pleadings, contracts, notices, or petitions.")
    placeholder = ("e.g. What is the law on adverse possession in Pakistan? Relevant cases?") if is_research \
                  else ("e.g. Draft a legal notice for recovery of Rs. 5 million from a defaulting contractor under Contract Act 1872.")
    sys_prompt = (
        "You are a senior Pakistani legal research assistant with deep knowledge of Pakistani law, "
        "jurisprudence, superior court judgements (Supreme Court, Federal Shariat Court, High Courts), "
        "and statutes. Provide accurate, well-cited answers referencing PLD, SCMR, and relevant Acts. "
        "Always note that users should verify citations independently. Be precise and professional."
    ) if is_research else (
        "You are an expert Pakistani legal drafter. Draft professional, court-ready legal documents "
        "including plaints, written statements, applications, contracts, legal notices, affidavits, and petitions "
        "following Pakistani legal conventions and court requirements. Ask for any missing details before drafting."
    )
    api_key_var = "GEMINI_API_KEY" if is_research else "GROK_API_KEY"
    model_name  = "Gemini (coming soon)" if is_research else "Grok (coming soon)"

    content = f"""
<div class="api-notice">
  ⚙ <strong>{model_name}</strong> — Add your <code style="font-size:11px; color:var(--gold2);">{api_key_var}</code> to <code style="font-size:11px; color:var(--gold2);">.env</code> to activate this assistant.
  Currently running in demo mode.
</div>

<div class="chat-container" id="chatBox">
  <div class="chat-header">
    <div class="ai-badge {badge_cls}">{badge_ltr}</div>
    <div>
      <h2>{title}</h2>
      <p>{desc}</p>
    </div>
  </div>
  <div class="chat-messages" id="messages">
    <div class="msg assistant">
      <div class="bubble">
        {'As-salamu alaykum. I am your legal research assistant for Pakistani law. I can help you find relevant case law, explain legal principles, interpret statutes, and build research arguments. How may I assist you today?' if is_research else 'As-salamu alaykum. I am your legal drafting assistant. I can help you draft plaints, written statements, legal notices, contracts, affidavits, and petitions following Pakistani legal conventions. What document would you like me to draft today?'}
      </div>
      <div class="time">Meezan AI · Ready</div>
    </div>
  </div>
  <div class="chat-input-row">
    <textarea id="userInput" rows="1" placeholder="{placeholder}" onkeydown="handleKey(event)"></textarea>
    <button class="btn btn-gold" onclick="sendMessage()" id="sendBtn">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
      </svg>
    </button>
    <div class="spinner" id="spinner"></div>
  </div>
</div>

<script>
const SYS = {repr(sys_prompt)};
const AI_TYPE = '{ai_type}';
let history = [];

function scrollDown() {{
  var m = document.getElementById('messages');
  m.scrollTop = m.scrollHeight;
}}

function now() {{
  return new Date().toLocaleTimeString('en-PK', {{hour:'2-digit',minute:'2-digit'}});
}}

function addMsg(role, text) {{
  var m = document.getElementById('messages');
  var d = document.createElement('div');
  d.className = 'msg ' + role;
  var safe = text.replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');
  d.innerHTML = '<div class="bubble">' + safe + '</div><div class="time">' + (role==='user' ? 'You' : 'Meezan AI') + ' · ' + now() + '</div>';
  m.appendChild(d);
  scrollDown();
}}

function handleKey(e) {{
  if (e.key==='Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }}
}}

async function sendMessage() {{
  var inp = document.getElementById('userInput');
  var msg = inp.value.trim();
  if (!msg) return;
  inp.value = '';
  inp.style.height = 'auto';
  addMsg('user', msg);
  history.push({{role:'user', content: msg}});

  document.getElementById('sendBtn').disabled = true;
  document.getElementById('spinner').style.display = 'block';

  try {{
    var r = await fetch('/api/chat', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json'}},
      body: JSON.stringify({{messages: history, system: SYS, ai_type: AI_TYPE}})
    }});
    var data = await r.json();
    var reply = data.reply || data.error || 'Sorry, I could not process that request.';
    addMsg('assistant', reply);
    history.push({{role:'assistant', content: reply}});
  }} catch(e) {{
    addMsg('assistant', 'Connection error. Please check your API key configuration.');
  }}
  document.getElementById('sendBtn').disabled = false;
  document.getElementById('spinner').style.display = 'none';
}}

// auto-resize textarea
document.getElementById('userInput').addEventListener('input', function() {{
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 140) + 'px';
}});
</script>
"""
    return page(title, active, content, "AI-Powered Legal Assistant")


@app.route("/research-ai")
def research_ai():
    return ai_chat_page("research")


@app.route("/draft-ai")
def draft_ai():
    return ai_chat_page("draft")


# ---------------------------------------------------------------------------
# AI CHAT API ENDPOINT
# ---------------------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data     = request.json
    messages = data.get("messages", [])
    system   = data.get("system", "")
    ai_type  = data.get("ai_type", "research")

    # ── Gemini (Research AI) ─────────────────────────────────────────────
    if ai_type == "research" and GEMINI_API_KEY:
        try:
            # Build Gemini-compatible history
            gem_contents = []
            for m in messages:
                role = "user" if m["role"] == "user" else "model"
                gem_contents.append({"role": role, "parts": [{"text": m["content"]}]})

            payload = {
                "system_instruction": {"parts": [{"text": system}]},
                "contents": gem_contents,
                "generationConfig": {"maxOutputTokens": 1500, "temperature": 0.3}
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            reply = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": reply})
        except Exception as e:
            return jsonify({"error": f"Gemini error: {str(e)}"}), 500

    # ── Grok (Drafting AI) ───────────────────────────────────────────────
    if ai_type == "draft" and GROK_API_KEY:
        try:
            payload = {
                "model": "grok-2-1212",
                "messages": [{"role": "system", "content": system}] + messages,
                "max_tokens": 2000, "temperature": 0.4
            }
            r = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
                json=payload, timeout=30
            )
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]
            return jsonify({"reply": reply})
        except Exception as e:
            return jsonify({"error": f"Grok error: {str(e)}"}), 500

    # ── Demo fallback (no API key configured) ────────────────────────────
    last = messages[-1]["content"] if messages else ""
    if ai_type == "research":
        demo = (
            f"Thank you for your query regarding: \"{last[:80]}…\"\n\n"
            "To activate this assistant, please add your GEMINI_API_KEY to a .env file in the project root.\n\n"
            "Once configured, I will be able to:\n"
            "• Search and cite relevant PLD and SCMR judgements\n"
            "• Explain legal principles under Pakistani law\n"
            "• Analyse statutory provisions and their judicial interpretation\n"
            "• Help you build case research arguments\n\n"
            "Demo mode — no live AI responses are being generated."
        )
    else:
        demo = (
            f"I have received your drafting request: \"{last[:80]}…\"\n\n"
            "To activate this assistant, please add your GROK_API_KEY to a .env file in the project root.\n\n"
            "Once configured, I will be able to draft:\n"
            "• Plaints and Written Statements\n"
            "• Legal Notices under Contract Act / Specific Relief Act\n"
            "• Bail Applications and Criminal Petitions\n"
            "• Affidavits, Undertakings, and Powers of Attorney\n"
            "• Commercial Contracts and MoUs\n\n"
            "Demo mode — no live AI responses are being generated."
        )
    return jsonify({"reply": demo})


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)

import streamlit as st
import requests
import json
import time
import json as json_lib
import os

st.set_page_config(
    page_title="OppInt — Analyzer",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)



# Load demo results
@st.cache_data
def load_demo_results():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "demo_results.json")
    with open(path) as f:
        return json_lib.load(f)

@st.cache_data
def load_sample_files():
    root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(root, "sam_opp.txt")) as f:
        opp = f.read()
    with open(os.path.join(root, "sam_org.txt")) as f:
        org = f.read()
    return opp, org


API_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');
* { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.block-container { padding: 2.5rem 3rem !important; max-width: 1000px !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; margin-bottom: 1rem; }
.stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 500; padding: 10px 16px; }

.oppint-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 1.25rem 0;
    border-bottom: 1px solid #e5e7eb; margin-bottom: 2.5rem;
}
.nav-logo { display: flex; align-items: center; gap: 12px; }
.nav-logo-icon {
    width: 36px; height: 36px; border-radius: 8px;
    background: #185FA5; display: flex; align-items: center; justify-content: center;
}
.nav-logo-icon i { color: #fff; font-size: 18px; }
.nav-logo-title { font-size: 17px; font-weight: 600; color: #111827; }
.nav-logo-sub { font-size: 13px; color: #6b7280; margin-top: 1px; }
.nav-back a {
    text-decoration: none; color: #4b5563;
    font-size: 14px; font-weight: 500; padding: 8px 16px;
    border-radius: 6px; border: 1px solid #e5e7eb;
}
.nav-back a:hover { background: #f3f4f6; color: #111827; }

.slabel {
    font-size: 13px; font-weight: 700; color: #4b5563;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 12px; margin-top: 2rem;
}

.trace-wrap { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; }
.trace-step {
    display: flex; align-items: center; gap: 14px;
    padding: 14px 18px; border-bottom: 1px solid #f3f4f6;
}
.trace-step:last-child { border-bottom: none; }
.si { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.si-done { background: #EAF3DE; }
.si-running { background: #E6F1FB; }
.si-pending { background: #f3f4f6; }
.step-name { font-size: 14px; font-weight: 600; color: #111827; }
.step-desc { font-size: 13px; color: #4b5563; margin-top: 2px; }
.step-time { font-size: 12px; color: #6b7280; white-space: nowrap; font-weight: 500; }
.ev-pill { font-size: 12px; background: #E6F1FB; color: #0C447C; padding: 4px 10px; border-radius: 20px; white-space: nowrap; font-weight: 600; }

.scorecard { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; }
.score-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.score-label { font-size: 14px; color: #4b5563; font-weight: 500; margin-bottom: 6px; }
.score-num { font-size: 42px; font-weight: 700; color: #185FA5; line-height: 1; }
.score-denom { font-size: 18px; color: #6b7280; font-weight: 500; margin-left: 2px; }
.vp { padding: 8px 18px; border-radius: 20px; background: #EAF3DE; color: #27500A; font-size: 14px; font-weight: 600; display:inline-block; }
.vc { padding: 8px 18px; border-radius: 20px; background: #FAEEDA; color: #633806; font-size: 14px; font-weight: 600; display:inline-block; }
.vn { padding: 8px 18px; border-radius: 20px; background: #FCEBEB; color: #791F1F; font-size: 14px; font-weight: 600; display:inline-block; }
.bar-track { height: 10px; background: #f3f4f6; border-radius: 20px; overflow: hidden; margin-bottom: 1.25rem; }
.bar-fill { height: 100%; border-radius: 20px; background: #185FA5; }
.metric-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; }
.metric { background: #f9fafb; border-radius: 8px; padding: 12px 14px; border: 1px solid #f3f4f6; }
.metric-label { font-size: 12px; color: #4b5563; font-weight: 500; margin-bottom: 4px; }
.metric-val { font-size: 16px; font-weight: 600; }
.mv-good { color: #27500A; }
.mv-warn { color: #633806; }
.mv-bad { color: #791F1F; }
.mv-default { color: #111827; }

.rs-title { font-size: 13px; font-weight: 700; color: #4b5563; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; margin-top: 1.25rem; }
.rs-body { font-size: 15px; color: #1f2937; line-height: 1.6; }
.tag-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.tag { font-size: 13px; padding: 5px 12px; border-radius: 20px; font-weight: 500; display: inline-block; }
.t-neutral { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
.t-match { background: #EAF3DE; color: #27500A; border: 1px solid #C0DD97; }
.t-gap { background: #FCEBEB; color: #791F1F; border: 1px solid #F7C1C1; }
.t-warn { background: #FAEEDA; color: #633806; border: 1px solid #FAC775; }

.risk-item { display: flex; gap: 12px; padding: 12px 14px; border-radius: 8px; margin-bottom: 8px; }
.risk-high { background: #FCEBEB; border: 1px solid #F7C1C1; }
.risk-medium { background: #FAEEDA; border: 1px solid #FAC775; }
.risk-low { background: #EAF3DE; border: 1px solid #C0DD97; }
.risk-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.dot-high { background: #A32D2D; }
.dot-medium { background: #854F0B; }
.dot-low { background: #3B6D11; }
.risk-text { font-size: 14px; line-height: 1.55; }
.rt-high { color: #791F1F; }
.rt-medium { color: #633806; }
.rt-low { color: #27500A; }

.rec-banner { border-radius: 10px; padding: 1.25rem 1.5rem; display: flex; align-items: center; gap: 14px; margin-bottom: 1.25rem; }
.rb-pursue { background: #EAF3DE; border: 1px solid #C0DD97; }
.rb-caution { background: #FAEEDA; border: 1px solid #FAC775; }
.rb-no { background: #FCEBEB; border: 1px solid #F7C1C1; }
.rb-pursue i { color: #3B6D11; font-size: 26px; }
.rb-caution i { color: #854F0B; font-size: 26px; }
.rb-no i { color: #A32D2D; font-size: 26px; }
.rec-title { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.rt-pursue { color: #27500A; }
.rt-caution { color: #633806; }
.rt-no { color: #791F1F; }
.rec-sub-pursue { font-size: 13px; color: #3B6D11; font-weight: 500; }
.rec-sub-caution { font-size: 13px; color: #854F0B; font-weight: 500; }
.rec-sub-no { font-size: 13px; color: #A32D2D; font-weight: 500; }

.check-item { display: flex; gap: 12px; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid #f3f4f6; }
.check-item:last-child { border-bottom: none; }
.check-item i { color: #6b7280; font-size: 16px; margin-top: 3px; flex-shrink: 0; }
.check-text { font-size: 14px; color: #1f2937; line-height: 1.5; }

.ev-card { background: #fff; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; border: 1px solid #e5e7eb; }
.ev-step { font-size: 12px; font-weight: 700; color: #4b5563; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.ev-query { font-size: 14px; color: #185FA5; margin-bottom: 8px; font-weight: 600; }
.ev-excerpt { font-size: 14px; color: #4b5563; line-height: 1.6; font-style: italic; background: #f9fafb; padding: 10px; border-radius: 6px; }

.dark-result-card {
    background: #111827; border: 1px solid #374151;
    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
}
.dark-card-title {
    font-size: 16px; font-weight: 600; color: #ffffff;
    margin-bottom: 10px; display: flex; align-items: center; gap: 8px;
}
.dark-card-body { font-size: 15px; color: #e5e7eb; line-height: 1.65; }
.dark-check-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 9px 0; border-bottom: 1px solid #374151;
}
.dark-check-item:last-child { border-bottom: none; }
.dark-check-item i { color: #9ca3af; font-size: 16px; margin-top: 3px; flex-shrink: 0; }
.dark-check-text { font-size: 14px; color: #e5e7eb; line-height: 1.5; }
.dark-section-title { font-size: 12px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; margin-top: 1.25rem; }
.dark-section-title:first-of-type { margin-top: 0; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 1s linear infinite; }
</style>
""", unsafe_allow_html=True)


# --- Nav ---
# st.markdown("""
# <div class="oppint-nav">
#     <div class="nav-logo">
#         <div class="nav-logo-icon"><i class="ti ti-bulb"></i></div>
#         <div>
#             <div class="nav-logo-title">OppInt</div>
#             <div class="nav-logo-sub">Opportunity Intelligence Agent</div>
#         </div>
#     </div>
#     <div class="nav-back"><a href="/" target="_self">← Home</a></div>
# </div>
# """, unsafe_allow_html=True)
st.markdown("""
<div class="oppint-nav">
    <div class="nav-logo">
        <div class="nav-logo-icon"><i class="ti ti-bulb"></i></div>
        <div>
            <div class="nav-logo-title">OppInt — Opportunity Evaluator</div>
            <div class="nav-logo-sub">Powered by Microsoft Foundry IQ</div>
        </div>
    </div>
    <div class="nav-back"><a href="/" target="_self">← Home</a></div>
</div>
""", unsafe_allow_html=True)

# Stats bar
st.markdown("""
<div style="display:flex;gap:24px;padding:12px 0;margin-bottom:1.5rem;border-bottom:1px solid #f3f4f6;">
    <div style="display:flex;align-items:center;gap:8px;">
        <i class="ti ti-brain" style="color:#185FA5;font-size:16px;"></i>
        <span style="font-size:13px;color:#4b5563;font-weight:500;">6-step reasoning pipeline</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <i class="ti ti-database" style="color:#185FA5;font-size:16px;"></i>
        <span style="font-size:13px;color:#4b5563;font-weight:500;">Foundry IQ grounding</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <i class="ti ti-shield-check" style="color:#185FA5;font-size:16px;"></i>
        <span style="font-size:13px;color:#4b5563;font-weight:500;">Evidence-backed decisions</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <i class="ti ti-clock" style="color:#185FA5;font-size:16px;"></i>
        <span style="font-size:13px;color:#4b5563;font-weight:500;">Results in ~60 seconds</span>
    </div>
</div>
""", unsafe_allow_html=True)


# --- Upload ---
# col1, col2 = st.columns(2, gap="large")
# with col1:
#     st.markdown("##### Opportunity document")
#     opp_file = st.file_uploader("Upload opportunity", type=["pdf","txt"], key="opp", label_visibility="collapsed")
#     if opp_file:
#         st.success(f"{opp_file.name} · {round(opp_file.size/1024)}KB · ready")

# with col2:
#     st.markdown("##### Organization documents")
#     st.caption("Upload up to 5 files — profiles, CVs, capability statements, past projects")
#     org_files = st.file_uploader(
#         "Upload organization",
#         type=["pdf", "txt"],
#         key="org",
#         accept_multiple_files=True,
#         label_visibility="collapsed"
#     )
#     if org_files:
#         for f in org_files:
#             st.success(f"{f.name} · {round(f.size/1024)}KB · ready")

# st.markdown("<br>", unsafe_allow_html=True)

# can_analyze = opp_file is not None and len(org_files) > 0
# if not can_analyze:
#     st.caption("Upload both documents to begin analysis.")

# st.markdown("<br>", unsafe_allow_html=True)
# Demo mode toggle
demo_col, _ = st.columns([1, 2])
with demo_col:
    demo_mode = st.toggle("⚡ Try instant demo", value=False, help="Load pre-built results instantly — no upload needed")

if demo_mode:
    st.info("**Demo mode active** — showing pre-built analysis of TechBridge Solutions vs Digital Innovation Fund 2024. All 6 reasoning steps completed.")
    opp_file = None
    org_files = []
    can_analyze = False
else:
    # Upload section
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("##### Opportunity document")
        st.caption("Grant announcement, RFP, tender document, or funding call")
        opp_file = st.file_uploader(
            "Upload opportunity",
            type=["pdf", "txt"],
            key="opp",
            label_visibility="collapsed"
        )

        # Sample file hint
        if not opp_file:
            st.markdown("""
            <div style="background:#f9fafb;border:1px dashed #d1d5db;border-radius:8px;padding:12px;margin-top:8px;">
                <div style="font-size:12px;color:#6b7280;margin-bottom:6px;font-weight:500;">Don't have a file?</div>
                <div style="font-size:12px;color:#4b5563;">Use <code>sample_opportunity.txt</code> from the project root — or toggle demo mode above.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success(f"{opp_file.name} · {round(opp_file.size/1024)}KB · ready")

    with col2:
        st.markdown("##### Organization documents")
        st.caption("Company profile, capability statement, past projects — up to 5 files")
        org_files = st.file_uploader(
            "Upload organization",
            type=["pdf", "txt"],
            key="org",
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        if not org_files:
            st.markdown("""
            <div style="background:#f9fafb;border:1px dashed #d1d5db;border-radius:8px;padding:12px;margin-top:8px;">
                <div style="font-size:12px;color:#6b7280;margin-bottom:6px;font-weight:500;">Don't have a file?</div>
                <div style="font-size:12px;color:#4b5563;">Use <code>sample_organization.txt</code> from the project root — or toggle demo mode above.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for f in org_files:
                st.success(f"{f.name} · {round(f.size/1024)}KB · ready")

    can_analyze = opp_file is not None and len(org_files) > 0
    if not can_analyze:
        st.caption("Upload both documents to begin — or toggle demo mode for an instant preview.")

st.markdown("<br>", unsafe_allow_html=True)

# --- Helpers ---
none_txt = '<p style="font-size:14px;color:#6b7280;margin:0;font-style:italic;">None identified</p>'


def verdict_info(decision: str):
    d = decision.upper()
    if "DO NOT" in d:
        return "vn", "rb-no", "ti-circle-x", "rt-no", "rec-sub-no"
    if "CAUTION" in d:
        return "vc", "rb-caution", "ti-alert-triangle", "rt-caution", "rec-sub-caution"
    return "vp", "rb-pursue", "ti-circle-check", "rt-pursue", "rec-sub-pursue"


def color_class(value: str, good, warn):
    v = value.lower()
    if any(g in v for g in good): return "mv-good"
    if any(w in v for w in warn): return "mv-warn"
    return "mv-default"


def render_trace_steps(current_step_index: int, status: str):
    step_labels = [
        ("Opportunity understanding", "Analyzing requirements and criteria"),
        ("Organization understanding", "Reviewing capabilities and profile"),
        ("Fit evaluation", "Matching profile against opportunity"),
        ("Risk assessment", "Identifying potential roadblocks"),
        ("Recommendation", "Generating evidence-based decision"),
        ("Action plan", "Finalizing your roadmap"),
    ]
    rows = ""
    for i, (name, desc) in enumerate(step_labels):
        is_done = i < current_step_index
        is_running = i == current_step_index and status == "processing"

        if is_done:
            ind = '<div class="si si-done"><i class="ti ti-check" style="color:#3B6D11;font-size:15px;"></i></div>'
            badge = '<span class="ev-pill">done</span>'
        elif is_running:
            ind = '<div class="si si-running"><span class="spinning" style="color:#185FA5;font-size:15px;">⟳</span></div>'
            badge = '<span style="font-size:12px;color:#185FA5;font-weight:600;">Running...</span>'
        else:
            ind = '<div class="si si-pending"><i class="ti ti-minus" style="color:#6b7280;font-size:15px;"></i></div>'
            badge = '<span style="font-size:12px;color:#9ca3af;">Pending</span>'

        rows += f"""
        <div class="trace-step">
            {ind}
            <div style="flex:1;">
                <div class="step-name">{name}</div>
                <div class="step-desc">{desc}</div>
            </div>
            {badge}
        </div>"""

    st.markdown(f'<div class="trace-wrap">{rows}</div>', unsafe_allow_html=True)


def render_scorecard(fit: dict, rec: dict, risks: dict):
    score = fit.get("fit_score", 0)
    pct = (score / 10) * 100
    decision = rec.get("decision", "PURSUE")
    eligibility = fit.get("eligibility_verdict", "Uncertain")
    confidence = rec.get("confidence_level", "Medium")
    # Pull actual risk level from risks dict
    risk_level = risks.get("overall_risk_level", "Medium")
    badge_cls, _, _, _, _ = verdict_info(decision)
    eli_cls = color_class(eligibility, ["yes","likely"], ["uncertain"])
    conf_cls = color_class(confidence, ["high"], ["medium"])
    risk_cls = color_class(risk_level, ["low"], ["medium", "high"])
    st.markdown(f"""
    <div class="scorecard">
        <div class="score-top">
            <div>
                <div class="score-label">Overall fit score</div>
                <div><span class="score-num">{score}</span><span class="score-denom">/ 10</span></div>
            </div>
            <div class="{badge_cls}">{decision.title()}</div>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>
        <div class="metric-grid">
            <div class="metric"><div class="metric-label">Eligibility</div><div class="metric-val {eli_cls}">{eligibility}</div></div>
            <div class="metric"><div class="metric-label">Risk level</div><div class="metric-val {risk_cls}">{risk_level}</div></div>
            <div class="metric"><div class="metric-label">Confidence</div><div class="metric-val {conf_cls}">{confidence}</div></div>
        </div>
    </div>""", unsafe_allow_html=True)


def render_summary(opp: dict):
    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-target"></i> Purpose</div>
        <div class="dark-card-body">{opp.get("purpose", "")}</div>
    </div>
    """, unsafe_allow_html=True)
    reqs = "".join([f'<span class="tag t-neutral">{r}</span>' for r in opp.get("requirements", [])])
    criteria = "".join([f'<span class="tag t-neutral">{c}</span>' for c in opp.get("evaluation_criteria", [])])
    deadlines = " · ".join(opp.get("deadlines", ["Not specified"]))
    st.markdown(f'<div class="rs-title">Key requirements</div><div class="tag-list">{reqs or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1.25rem;">Evaluation criteria</div><div class="tag-list">{criteria or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1.25rem;">Deadlines</div><p style="font-size:15px;color:#1f2937;margin:0;font-weight:500;">{deadlines}</p>', unsafe_allow_html=True)


def render_fit(fit: dict):
    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-chart-pie"></i> Evidence Summary</div>
        <div class="dark-card-body">{fit.get('evidence_summary', '')}</div>
    </div>
    """, unsafe_allow_html=True)
    strong = "".join([f'<span class="tag t-match">{m["area"]}</span>' for m in fit.get("strong_matches", [])])
    partial = "".join([f'<span class="tag t-warn">{m["area"]}</span>' for m in fit.get("partial_matches", [])])
    gaps = "".join([f'<span class="tag t-gap">{m["area"]}</span>' for m in fit.get("gaps", [])])
    st.markdown(f'<div class="rs-title">Strong matches</div><div class="tag-list">{strong or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1.25rem;">Partial matches</div><div class="tag-list">{partial or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1.25rem;">Gaps</div><div class="tag-list">{gaps or none_txt}</div>', unsafe_allow_html=True)


def render_risks(risks: dict):
    def rows(items, level, txt_cls):
        out = ""
        for r in items:
            mit = f'<div style="font-size:13px;margin-top:6px;opacity:0.9;"><strong>Mitigation:</strong> {r.get("mitigation","")}</div>' if r.get("mitigation") else ""
            out += f'<div class="risk-item risk-{level}"><div class="risk-dot dot-{level}"></div><div class="risk-text {txt_cls}">{r["description"]}{mit}</div></div>'
        return out or none_txt

    st.markdown(f'<div class="rs-title">High risks</div>{rows(risks.get("high_risks",[]),"high","rt-high")}', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1.25rem;">Medium risks</div>{rows(risks.get("medium_risks",[]),"medium","rt-medium")}', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1.25rem;">Low risks</div>{rows(risks.get("low_risks",[]),"low","rt-low")}', unsafe_allow_html=True)


def render_recommendation(rec: dict):
    # Strategic summary dark card
    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-bulb"></i> Strategic Summary</div>
        <div class="dark-card-body">{rec.get("strategic_summary", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    # Verdict banner
    decision = rec.get("decision", "PURSUE")
    _, rb, icon, title_cls, sub_cls = verdict_info(decision)
    st.markdown(f"""
    <div class="rec-banner {rb}">
        <i class="ti {icon}"></i>
        <div>
            <div class="rec-title {title_cls}">{decision.title()}</div>
            <div class="{sub_cls}">{rec.get('confidence_level','')} confidence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detailed analysis dark card — split into separate calls to avoid truncation
    pursue_rows = "".join([
        f'<div class="dark-check-item"><i class="ti ti-arrow-right"></i><span class="dark-check-text">{r}</span></div>'
        for r in rec.get("reasons_to_pursue", [])
    ]) or none_txt

    caution_rows = "".join([
        f'<div class="dark-check-item"><i class="ti ti-alert-triangle"></i><span class="dark-check-text">{r}</span></div>'
        for r in rec.get("reasons_for_caution", [])
    ]) or none_txt

    conditions = "".join([
        f'<div class="dark-check-item"><i class="ti ti-circle-dot"></i><span class="dark-check-text">{c}</span></div>'
        for c in rec.get("key_conditions", [])
    ]) or none_txt

    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-list-details"></i> Detailed Analysis</div>
        <div class="dark-section-title">Reasons to pursue</div>
        {pursue_rows}
        <div class="dark-section-title">Reasons for caution</div>
        {caution_rows}
        <div class="dark-section-title">Key conditions</div>
        {conditions}
    </div>
    """, unsafe_allow_html=True)


def render_action_plan(plan: dict):
    def checklist(items):
        if not items:
            return none_txt
        return "".join([
            f'<div class="dark-check-item"><i class="ti ti-square"></i><span class="dark-check-text">{item}</span></div>'
            for item in items
        ])

    # Split into separate st.markdown calls — one dark card per section
    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-clock" ></i> Immediate actions (next 48 hours)</div>
        {checklist(plan.get("immediate_actions", []))}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-calendar"></i> Short-term actions (this week)</div>
        {checklist(plan.get("short_term_actions", []))}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-file-text"></i> Documents to prepare</div>
        {checklist(plan.get("documents_to_prepare", []))}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-list-check"></i> Submission checklist</div>
        {checklist(plan.get("submission_checklist", []))}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dark-result-card">
        <div class="dark-card-title"><i class="ti ti-star"></i> Recommended priorities</div>
        {checklist(plan.get("recommended_priorities", []))}
    </div>
    """, unsafe_allow_html=True)


def render_evidence(trail: list):
    if not trail:
        st.markdown(none_txt, unsafe_allow_html=True)
        return
    for entry in trail:
        excerpt = entry.get('evidence_retrieved', '')[:400]
        st.markdown(f"""
        <div class="ev-card">
            <div class="ev-step">{entry.get('step','').replace('_',' ').title()}</div>
            <div class="ev-query">Query: "{entry.get('query_used','')}"</div>
            <div class="ev-excerpt">{excerpt}...</div>
        </div>""", unsafe_allow_html=True)


# --- Run Analysis ---
# button_placeholder = st.empty()
# is_analyzing = st.session_state.get("is_analyzing", False)

# with button_placeholder:
#     analyze_clicked = st.button(
#         "Analyzing..." if is_analyzing else "Analyze opportunity →",
#         disabled=is_analyzing or not can_analyze,
#         use_container_width=True,
#         type="primary"
#     )

# if analyze_clicked:
#     st.session_state.is_analyzing = True
#     st.session_state["results"] = None
#     st.session_state["evidence_trail"] = []
#     st.session_state["session_id"] = None
#     button_placeholder.empty()

#     with button_placeholder:
#         st.button("Analyzing...", disabled=True, use_container_width=True, type="primary")

#     try:
#         files = [("opportunity_file", (opp_file.name, opp_file.getvalue(), opp_file.type))]
#         for f in org_files:
#             files.append(("organization_files", (f.name, f.getvalue(), f.type)))

#         start_response = requests.post(f"{API_URL}/analyze", files=files, timeout=60)

#         if start_response.status_code != 200:
#             st.error(f"Failed to start: {start_response.json().get('detail','Unknown error')}")
#             st.session_state.is_analyzing = False
#             st.rerun()
#             st.stop()

#         session_id = start_response.json()["session_id"]
#         st.session_state["session_id"] = session_id  # ← fixed: save session_id

#         progress_placeholder = st.empty()
#         MAX_WAIT_SECONDS = 300
#         start_time = time.time()

#         while True:
#             elapsed = time.time() - start_time
#             if elapsed > MAX_WAIT_SECONDS:
#                 progress_placeholder.empty()
#                 st.error("Analysis timed out after 5 minutes.")
#                 st.session_state.is_analyzing = False
#                 break

#             try:
#                 status_response = requests.get(f"{API_URL}/status/{session_id}", timeout=10)
#                 data = status_response.json()
#             except Exception:
#                 time.sleep(3)
#                 continue

#             status = data.get("status")
#             steps_done = data.get("reasoning_steps_completed", 0)

#             with progress_placeholder.container():
#                 pct = min(int((steps_done / 6) * 100), 95) if status == "processing" else 100
#                 st.progress(pct, text=f"Step {steps_done}/6 complete · {int(elapsed)}s elapsed")
#                 render_trace_steps(steps_done, status)

#             if status == "complete":
#                 progress_placeholder.empty()
#                 st.session_state["results"] = data["results"]
#                 st.session_state["evidence_trail"] = data.get("evidence_trail", [])
#                 st.session_state["steps_completed"] = steps_done
#                 st.session_state.is_analyzing = False
#                 st.success("Analysis complete!")
#                 st.rerun()
#                 break

#             elif status == "failed":
#                 progress_placeholder.empty()
#                 st.error(f"Analysis failed: {data.get('error', 'Unknown')}")
#                 st.session_state.is_analyzing = False
#                 break

#             time.sleep(3)

#     except Exception as e:
#         st.error(f"Error: {str(e)}")
#         st.session_state.is_analyzing = False
#         st.rerun()

# --- Button ---
button_placeholder = st.empty()
is_analyzing = st.session_state.get("is_analyzing", False)

if demo_mode:
    if st.button("Load demo results ⚡", use_container_width=True, type="primary"):
        demo = load_demo_results()
        st.session_state["results"] = demo["opportunity"]["results"]
        st.session_state["evidence_trail"] = demo["opportunity"]["evidence_trail"]
        st.session_state["steps_completed"] = demo["opportunity"]["reasoning_steps_completed"]
        st.session_state["session_id"] = demo["opportunity"]["session_id"]
        st.rerun()
else:
    with button_placeholder:
        analyze_clicked = st.button(
            "Analyzing..." if is_analyzing else "Analyze opportunity →",
            disabled=is_analyzing or not can_analyze,
            use_container_width=True,
            type="primary"
        )

    if analyze_clicked:
        st.session_state.is_analyzing = True
        st.session_state["results"] = None
        st.session_state["evidence_trail"] = []
        st.session_state["session_id"] = None
        button_placeholder.empty()

        with button_placeholder:
            st.button("Analyzing...", disabled=True, use_container_width=True, type="primary")

        try:
            files = [("opportunity_file", (opp_file.name, opp_file.getvalue(), opp_file.type))]
            for f in org_files:
                files.append(("organization_files", (f.name, f.getvalue(), f.type)))

            start_response = requests.post(f"{API_URL}/analyze", files=files, timeout=60)

            if start_response.status_code != 200:
                st.error(f"Failed to start: {start_response.json().get('detail','Unknown error')}")
                st.session_state.is_analyzing = False
                st.rerun()
                st.stop()

            session_id = start_response.json()["session_id"]
            st.session_state["session_id"] = session_id

            progress_placeholder = st.empty()
            MAX_WAIT_SECONDS = 300
            start_time = time.time()

            while True:
                elapsed = time.time() - start_time
                if elapsed > MAX_WAIT_SECONDS:
                    progress_placeholder.empty()
                    st.error("Analysis timed out after 5 minutes.")
                    st.session_state.is_analyzing = False
                    break

                try:
                    status_response = requests.get(f"{API_URL}/status/{session_id}", timeout=10)
                    data = status_response.json()
                except Exception:
                    time.sleep(3)
                    continue

                status = data.get("status")
                steps_done = data.get("reasoning_steps_completed", 0)

                with progress_placeholder.container():
                    pct = min(int((steps_done / 6) * 100), 95) if status == "processing" else 100
                    st.progress(pct, text=f"Step {steps_done}/6 complete · {int(elapsed)}s elapsed")
                    render_trace_steps(steps_done, status)

                if status == "complete":
                    progress_placeholder.empty()
                    st.session_state["results"] = data["results"]
                    st.session_state["evidence_trail"] = data.get("evidence_trail", [])
                    st.session_state["steps_completed"] = data.get("reasoning_steps_completed", 6)
                    st.session_state.is_analyzing = False
                    st.success("Analysis complete!")
                    st.rerun()
                    break
                elif status == "failed":
                    progress_placeholder.empty()
                    st.error(f"Analysis failed: {data.get('error','Unknown')}")
                    st.session_state.is_analyzing = False
                    break

                time.sleep(3)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.is_analyzing = False
            st.rerun()

# --- Display Results ---
# if st.session_state.get("results"):
#     results = st.session_state["results"]
#     trail = st.session_state.get("evidence_trail", [])
#     steps_done = st.session_state.get("steps_completed", 6)

#     opp = results.get("opportunity_summary", {})
#     fit = results.get("fit_evaluation", {})
#     risks = results.get("risk_assessment", {})
#     rec = results.get("recommendation", {})
#     plan = results.get("action_plan", {})
if st.session_state.get("results"):
    results = st.session_state["results"]
    trail = st.session_state.get("evidence_trail", [])
    steps_done = st.session_state.get("steps_completed", 6)

    opp = results.get("opportunity_summary", {})
    fit = results.get("fit_evaluation", {})
    risks = results.get("risk_assessment", {})
    rec = results.get("recommendation", {})
    plan = results.get("action_plan", {})

    # --- Prominent verdict banner ---
    decision = rec.get("decision", "PURSUE").upper()
    score = fit.get("fit_score", 0)
    confidence = rec.get("confidence_level", "")
    risk_level = risks.get("overall_risk_level", "Medium")

    if "DO NOT" in decision:
        banner_bg = "#FCEBEB"
        banner_border = "#F7C1C1"
        banner_icon = "ti-circle-x"
        banner_color = "#791F1F"
        banner_title_color = "#A32D2D"
    elif "CAUTION" in decision:
        banner_bg = "#FAEEDA"
        banner_border = "#FAC775"
        banner_icon = "ti-alert-triangle"
        banner_color = "#633806"
        banner_title_color = "#854F0B"
    else:
        banner_bg = "#EAF3DE"
        banner_border = "#C0DD97"
        banner_icon = "ti-circle-check"
        banner_color = "#27500A"
        banner_title_color = "#3B6D11"

    st.markdown(f"""
    <div style="background:{banner_bg};border:1.5px solid {banner_border};border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;">
        <div style="display:flex;align-items:center;gap:14px;">
            <i class="ti {banner_icon}" style="font-size:32px;color:{banner_title_color};"></i>
            <div>
                <div style="font-size:20px;font-weight:700;color:{banner_title_color};">{decision.title()}</div>
                <div style="font-size:13px;color:{banner_color};margin-top:2px;">{confidence} confidence · Risk level: {risk_level}</div>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:11px;color:{banner_color};margin-bottom:4px;text-transform:uppercase;letter-spacing:0.05em;">Fit score</div>
            <div style="font-size:36px;font-weight:700;color:{banner_title_color};line-height:1;">{score}<span style="font-size:16px;font-weight:500;color:{banner_color};">/10</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Strategic summary
    st.markdown(f"""
    <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.5rem;">
        <div style="font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">Strategic summary</div>
        <div style="font-size:14px;color:#111827;line-height:1.7;">{rec.get('strategic_summary','')}</div>
    </div>
    """, unsafe_allow_html=True)


    # Single reasoning trace — no duplicate
    st.markdown('<div class="slabel">Reasoning trace</div>', unsafe_allow_html=True)
    render_trace_steps(steps_done or 6, "complete")

    st.markdown('<div class="slabel">Fit scorecard</div>', unsafe_allow_html=True)
    render_scorecard(fit, rec, risks)  # ← fixed: pass risks for real risk level

    st.markdown('<div class="slabel">Analysis results</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Summary", "✅ Fit", "⚠️ Risks",
        "🎯 Recommendation", "📝 Action plan", "🔍 Evidence trail"
    ])
    with tab1: render_summary(opp)
    with tab2: render_fit(fit)
    with tab3: render_risks(risks)
    with tab4: render_recommendation(rec)
    with tab5: render_action_plan(plan)
    with tab6: render_evidence(trail)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.download_button(
            "⬇️ Full report (JSON)",
            data=json.dumps(results, indent=2),
            file_name="oppint_report.json",
            mime="application/json",
            use_container_width=True
        )

    with col_b:
        plan_text = "\n".join([
            "OPPINT ACTION PLAN", "=" * 30, "",
            "IMMEDIATE ACTIONS:",
            *[f"- {a}" for a in plan.get("immediate_actions", [])],
            "\nSHORT TERM ACTIONS:",
            *[f"- {a}" for a in plan.get("short_term_actions", [])],
            "\nDOCUMENTS TO PREPARE:",
            *[f"- {d}" for d in plan.get("documents_to_prepare", [])],
            "\nPREPARATION CHECKLIST:",
            *[f"[ ] {c}" for c in plan.get("preparation_checklist", [])],
            "\nSUBMISSION CHECKLIST:",
            *[f"[ ] {c}" for c in plan.get("submission_checklist", [])],
        ])
        st.download_button(
            "⬇️ Action plan (TXT)",
            data=plan_text,
            file_name="oppint_action_plan.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_c:
        try:
            pdf_response = requests.post(
                f"{API_URL}/report/{st.session_state.get('session_id', 'report')}",
                json={"results": results, "evidence_trail": trail},
                timeout=30
            )
            if pdf_response.status_code == 200:
                st.download_button(
                    "⬇️ Full report (PDF)",
                    data=pdf_response.content,
                    file_name="oppint_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")
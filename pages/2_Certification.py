import os

import streamlit as st
import requests
import json
import time
from service.fabric_iq import get_role_certifications, load_certifications
from service.work_iq import analyze_study_capacity

st.set_page_config(
    page_title="OppInt — Certification Readiness",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_demo_results():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "demo_results.json")
    with open(path) as f:
        return json.load(f)
        
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');
* { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
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
    text-decoration: none; color: #4b5563; font-size: 14px;
    font-weight: 500; padding: 8px 16px;
    border-radius: 6px; border: 1px solid #e5e7eb;
}
.nav-back a:hover { background: #f3f4f6; color: #111827; }

.slabel {
    font-size: 13px; font-weight: 700; color: #4b5563;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 12px; margin-top: 2rem;
}

.iq-badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 11px; font-weight: 600; padding: 4px 10px;
    border-radius: 20px; margin-right: 6px; margin-bottom: 4px;
}
.iq-foundry { background: #E6F1FB; color: #0C447C; border: 1px solid #B5D4F4; }
.iq-work { background: #EAF3DE; color: #27500A; border: 1px solid #C0DD97; }
.iq-fabric { background: #EEEDFE; color: #3C3489; border: 1px solid #AFA9EC; }

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
.step-badge { font-size: 11px; padding: 3px 8px; border-radius: 20px; font-weight: 600; white-space: nowrap; }
.sb-foundry { background: #E6F1FB; color: #0C447C; }
.sb-fabric { background: #EEEDFE; color: #3C3489; }
.sb-work { background: #EAF3DE; color: #27500A; }

.scorecard { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; }
.score-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
.score-label { font-size: 14px; color: #4b5563; font-weight: 500; margin-bottom: 6px; }
.score-num { font-size: 42px; font-weight: 700; color: #185FA5; line-height: 1; }
.score-denom { font-size: 18px; color: #6b7280; font-weight: 500; margin-left: 2px; }
.bar-track { height: 10px; background: #f3f4f6; border-radius: 20px; overflow: hidden; margin-bottom: 1.25rem; }
.bar-fill { height: 100%; border-radius: 20px; }
.metric-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; }
.metric { background: #f9fafb; border-radius: 8px; padding: 12px 14px; border: 1px solid #f3f4f6; }
.metric-label { font-size: 11px; color: #4b5563; font-weight: 500; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.04em; }
.metric-val { font-size: 16px; font-weight: 600; }
.mv-good { color: #27500A; }
.mv-warn { color: #633806; }
.mv-bad { color: #791F1F; }
.mv-blue { color: #185FA5; }
.mv-purple { color: #534AB7; }
.mv-default { color: #111827; }

.dark-card {
    background: #111827; border: 1px solid #374151;
    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
}
.dark-card-title {
    font-size: 16px; font-weight: 600; color: #ffffff;
    margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.dark-card-body { font-size: 14px; color: #e5e7eb; line-height: 1.7; }
.dark-section { font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; margin-top: 1.25rem; }
.dark-section:first-of-type { margin-top: 0; }
.dark-check { display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid #374151; }
.dark-check:last-child { border-bottom: none; }
.dark-check i { color: #9ca3af; font-size: 15px; margin-top: 2px; flex-shrink: 0; }
.dark-check-text { font-size: 14px; color: #e5e7eb; line-height: 1.5; }

.tag-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.tag { font-size: 12px; padding: 4px 11px; border-radius: 20px; font-weight: 500; }
.t-match { background: #EAF3DE; color: #27500A; border: 1px solid #C0DD97; }
.t-gap { background: #FCEBEB; color: #791F1F; border: 1px solid #F7C1C1; }
.t-neutral { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
.t-purple { background: #EEEDFE; color: #3C3489; border: 1px solid #AFA9EC; }

.rs-title { font-size: 12px; font-weight: 700; color: #4b5563; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; margin-top: 1.25rem; }
.rs-body { font-size: 14px; color: #111827; line-height: 1.7; }

.ev-card { background: #f9fafb; border-radius: 8px; padding: 14px; margin-bottom: 10px; border: 1px solid #e5e7eb; }
.ev-step { font-size: 11px; font-weight: 700; color: #4b5563; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.ev-query { font-size: 13px; color: #185FA5; margin-bottom: 6px; font-weight: 600; }
.ev-excerpt { font-size: 13px; color: #4b5563; line-height: 1.6; font-style: italic; background: #fff; padding: 10px; border-radius: 6px; border: 1px solid #e5e7eb; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spinning { display: inline-block; animation: spin 1s linear infinite; }

.status-on-track { background: #EAF3DE; color: #27500A; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }
.status-attention { background: #FAEEDA; color: #633806; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }
.status-risk { background: #FCEBEB; color: #791F1F; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# --- Nav ---
st.markdown("""
<div class="oppint-nav">
    <div class="nav-logo">
        <div class="nav-logo-icon"><i class="ti ti-certificate"></i></div>
        <div>
            <div class="nav-logo-title">OppInt — Certification Readiness</div>
            <div class="nav-logo-sub">Powered by Foundry IQ · Work IQ · Fabric IQ</div>
        </div>
    </div>
    <div class="nav-back"><a href="/" target="_self">← Home</a></div>
</div>
""", unsafe_allow_html=True)

# IQ badges
st.markdown("""
<div style="margin-bottom:1.5rem;">
    <span class="iq-badge iq-foundry"><i class="ti ti-database"></i> Foundry IQ — Grounded Knowledge</span>
    <span class="iq-badge iq-work"><i class="ti ti-briefcase"></i> Work IQ — Work Context</span>
    <span class="iq-badge iq-fabric"><i class="ti ti-topology-star"></i> Fabric IQ — Semantic Layer</span>
</div>
""", unsafe_allow_html=True)

# --- Helpers ---
none_txt = '<p style="font-size:13px;color:#6b7280;margin:4px 0;font-style:italic;">None identified</p>'

AGENT_STEPS = [
    ("Learning Path Curator", "Retrieving grounded certification content", "sb-foundry"),
    ("Study Plan Generator", "Building capacity-aware study schedule", "sb-fabric"),
    ("Engagement Agent", "Adapting reminders to work rhythm", "sb-work"),
    ("Assessment Agent", "Evaluating readiness with grounded questions", "sb-foundry"),
    ("Manager Insights Agent", "Surfacing team-level visibility", "sb-work"),
]


def render_trace(steps_done: int, status: str):
    rows = ""
    for i, (name, desc, badge_cls) in enumerate(AGENT_STEPS):
        is_done = i < steps_done
        is_running = i == steps_done and status == "processing"
        if is_done:
            ind = '<div class="si si-done"><i class="ti ti-check" style="color:#3B6D11;font-size:15px;"></i></div>'
            right = f'<span class="step-badge {badge_cls}">done</span>'
        elif is_running:
            ind = '<div class="si si-running"><span class="spinning" style="color:#185FA5;font-size:14px;">⟳</span></div>'
            right = '<span style="font-size:12px;color:#185FA5;font-weight:600;">Running...</span>'
        else:
            ind = '<div class="si si-pending"><i class="ti ti-minus" style="color:#9ca3af;font-size:15px;"></i></div>'
            right = '<span style="font-size:12px;color:#9ca3af;">Pending</span>'
        rows += f"""
        <div class="trace-step">
            {ind}
            <div style="flex:1;">
                <div class="step-name">{name}</div>
                <div class="step-desc">{desc}</div>
            </div>
            {right}
        </div>"""
    st.markdown(f'<div class="trace-wrap">{rows}</div>', unsafe_allow_html=True)


def readiness_color(level: str) -> str:
    l = level.lower()
    if "ready" == l: return "mv-good"
    if "nearly" in l: return "mv-blue"
    if "needs" in l: return "mv-warn"
    return "mv-bad"


def workload_color(level: str) -> str:
    l = level.lower()
    if l in ["low"]: return "mv-good"
    if l in ["medium"]: return "mv-blue"
    if "high" in l: return "mv-warn"
    return "mv-default"


def render_scorecard(results: dict):
    readiness = results.get("fabric_readiness", {})
    schedule = results.get("work_schedule", {})
    capacity = results.get("work_capacity", {})

    score = readiness.get("readiness_score", 0)
    pct = score
    level = readiness.get("readiness_level", "Unknown")
    practice = readiness.get("practice_score", 0)
    hours_pct = readiness.get("hours_completion_pct", 0)
    weeks = schedule.get("estimated_weeks_to_ready", "?")
    workload = capacity.get("current_workload", "Unknown")

    r_color = readiness_color(level)
    w_color = workload_color(workload)

    if score >= 80: bar_color = "#3B6D11"
    elif score >= 65: bar_color = "#185FA5"
    elif score >= 50: bar_color = "#854F0B"
    else: bar_color = "#A32D2D"

    st.markdown(f"""
    <div class="scorecard">
        <div class="score-top">
            <div>
                <div class="score-label">Certification readiness score</div>
                <div><span class="score-num">{score}</span><span class="score-denom">/ 100</span></div>
            </div>
            <div>
                <span style="font-size:14px;font-weight:600;padding:8px 18px;border-radius:20px;background:#EEEDFE;color:#3C3489;">{level}</span>
            </div>
        </div>
        <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%;background:{bar_color};"></div>
        </div>
        <div class="metric-grid">
            <div class="metric">
                <div class="metric-label">Practice score</div>
                <div class="metric-val mv-blue">{practice}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Study progress</div>
                <div class="metric-val mv-purple">{hours_pct}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Weeks to ready</div>
                <div class="metric-val {w_color}">{weeks}w</div>
            </div>
            <div class="metric">
                <div class="metric-label">Workload</div>
                <div class="metric-val {w_color}">{workload}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_learning_path(lp: dict):
    matched = "".join([f'<span class="tag t-match">{s}</span>' for s in lp.get("matched_skills", [])])
    gaps = "".join([f'<span class="tag t-gap">{s}</span>' for s in lp.get("skill_gaps", [])])
    roles = "".join([f'<span class="tag t-neutral">{r}</span>' for r in lp.get("role_alignment", [])])
    match_pct = lp.get("match_percentage", 0)

    st.markdown(f"""
    <div class="dark-card">
        <div class="dark-card-title">
            <i class="ti ti-route"></i> {lp.get('certification_name','')}
            <span style="font-size:12px;background:#E6F1FB;color:#0C447C;padding:3px 8px;border-radius:20px;margin-left:8px;">Foundry IQ</span>
        </div>
        <div class="dark-card-body">Skill match: {match_pct}% of required skills already demonstrated</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="rs-title">Matched skills</div><div class="tag-list">{matched or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1rem;">Skill gaps to address</div><div class="tag-list">{gaps or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1rem;">Role alignment</div><div class="tag-list">{roles or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1rem;">Full learning path</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-body">{lp.get("raw_output","").replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)


def render_study_plan(sp: dict, schedule: dict):
    def checklist(items_text: str):
        lines = [l.strip() for l in items_text.split('\n') if l.strip() and not l.strip().startswith('#')]
        return "".join([
            f'<div class="dark-check"><i class="ti ti-square"></i><span class="dark-check-text">{l}</span></div>'
            for l in lines[:15]
        ])

    st.markdown(f"""
    <div class="dark-card">
        <div class="dark-card-title">
            <i class="ti ti-calendar-stats"></i> Study Schedule
            <span style="font-size:12px;background:#EEEDFE;color:#3C3489;padding:3px 8px;border-radius:20px;margin-left:8px;">Fabric IQ</span>
        </div>
        <div class="metric-grid" style="margin-bottom:1rem;">
            <div class="metric" style="background:#1f2937;border-color:#374151;">
                <div class="metric-label" style="color:#9ca3af;">Sessions/week</div>
                <div class="metric-val mv-blue">{sp.get('sessions_per_week','?')}</div>
            </div>
            <div class="metric" style="background:#1f2937;border-color:#374151;">
                <div class="metric-label" style="color:#9ca3af;">Session length</div>
                <div class="metric-val mv-blue">{sp.get('session_length_minutes','?')}min</div>
            </div>
            <div class="metric" style="background:#1f2937;border-color:#374151;">
                <div class="metric-label" style="color:#9ca3af;">Weekly hours</div>
                <div class="metric-val mv-blue">{sp.get('weekly_hours','?')}h</div>
            </div>
            <div class="metric" style="background:#1f2937;border-color:#374151;">
                <div class="metric-label" style="color:#9ca3af;">Pace</div>
                <div class="metric-val mv-purple">{sp.get('pace','?')}</div>
            </div>
        </div>
        <div class="dark-card-body">{sp.get('raw_output','').replace(chr(10),'<br>')}</div>
    </div>
    """, unsafe_allow_html=True)

    windows = schedule.get("recommended_windows", [])
    if windows:
        windows_html = "".join([f'<span class="tag t-neutral">{w}</span>' for w in windows])
        st.markdown(f'<div class="rs-title">Recommended study windows (Work IQ)</div><div class="tag-list">{windows_html}</div>', unsafe_allow_html=True)


def render_engagement(eng: dict):
    risk = eng.get("risk_flag")
    risk_html = f'<div style="background:#FCEBEB;border:1px solid #F7C1C1;border-radius:8px;padding:10px 14px;margin-top:8px;font-size:13px;color:#791F1F;"><i class="ti ti-alert-triangle"></i> {risk}</div>' if risk else ""

    st.markdown(f"""
    <div class="dark-card">
        <div class="dark-card-title">
            <i class="ti ti-bell"></i> Engagement Strategy
            <span style="font-size:12px;background:#EAF3DE;color:#27500A;padding:3px 8px;border-radius:20px;margin-left:8px;">Work IQ</span>
        </div>
        <div class="dark-card-body">{eng.get('raw_output','').replace(chr(10),'<br>')}</div>
    </div>
    """, unsafe_allow_html=True)

    windows_html = "".join([f'<span class="tag t-neutral">{w}</span>' for w in eng.get("best_windows", [])])
    if windows_html:
        st.markdown(f'<div class="rs-title">Best study windows</div><div class="tag-list">{windows_html}</div>', unsafe_allow_html=True)
    st.markdown(risk_html, unsafe_allow_html=True)


def render_assessment(asr: dict):
    score = asr.get("readiness_score", 0)
    verdict = asr.get("readiness_verdict", "Unknown")
    r_color = readiness_color(verdict)

    matched = "".join([f'<span class="tag t-match">{s}</span>' for s in asr.get("matched_skills", [])])
    gaps = "".join([f'<span class="tag t-gap">{s}</span>' for s in asr.get("skill_gaps", [])])

    st.markdown(f"""
    <div class="dark-card">
        <div class="dark-card-title">
            <i class="ti ti-clipboard-check"></i> Readiness Assessment
            <span style="font-size:12px;background:#E6F1FB;color:#0C447C;padding:3px 8px;border-radius:20px;margin-left:8px;">Foundry IQ</span>
        </div>
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:1rem;">
            <div>
                <div style="font-size:11px;color:#9ca3af;margin-bottom:4px;">READINESS SCORE</div>
                <div style="font-size:32px;font-weight:700;color:#185FA5;">{score}<span style="font-size:16px;color:#6b7280;">/100</span></div>
            </div>
            <div>
                <div style="font-size:11px;color:#9ca3af;margin-bottom:4px;">VERDICT</div>
                <div style="font-size:15px;font-weight:600;color:#e5e7eb;">{verdict}</div>
            </div>
            <div>
                <div style="font-size:11px;color:#9ca3af;margin-bottom:4px;">PRACTICE SCORE</div>
                <div style="font-size:15px;font-weight:600;color:#e5e7eb;">{asr.get('practice_score',0)}%</div>
            </div>
            <div>
                <div style="font-size:11px;color:#9ca3af;margin-bottom:4px;">PASS THRESHOLD</div>
                <div style="font-size:15px;font-weight:600;color:#e5e7eb;">{asr.get('pass_threshold',70)}%</div>
            </div>
        </div>
        <div class="dark-card-body">{asr.get('raw_output','').replace(chr(10),'<br>')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="rs-title">Strong areas</div><div class="tag-list">{matched or none_txt}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rs-title" style="margin-top:1rem;">Areas needing work</div><div class="tag-list">{gaps or none_txt}</div>', unsafe_allow_html=True)


def render_manager_insights(mi: dict):
    risk = mi.get("risk_flag")
    weeks = mi.get("weeks_to_ready", "?")
    workload = mi.get("workload", "Unknown")
    readiness = mi.get("readiness_level", "Unknown")

    risk_html = ""
    if risk:
        risk_html = f'<div style="background:#FCEBEB;border:1px solid #F7C1C1;border-radius:8px;padding:10px 14px;margin-top:1rem;font-size:13px;color:#791F1F;"><strong>Risk flag:</strong> {risk}</div>'

    st.markdown(f"""
    <div class="dark-card">
        <div class="dark-card-title">
            <i class="ti ti-chart-bar"></i> Manager Dashboard
            <span style="font-size:12px;background:#EAF3DE;color:#27500A;padding:3px 8px;border-radius:20px;margin-left:8px;">Work IQ + Fabric IQ</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:1rem;">
            <div style="background:#1f2937;border-radius:8px;padding:12px;border:1px solid #374151;">
                <div style="font-size:11px;color:#9ca3af;margin-bottom:4px;">TEAM MEMBER</div>
                <div style="font-size:14px;font-weight:600;color:#e5e7eb;">{mi.get('team_member','')}</div>
                <div style="font-size:12px;color:#9ca3af;">{mi.get('role','')} · {mi.get('department','')}</div>
            </div>
            <div style="background:#1f2937;border-radius:8px;padding:12px;border:1px solid #374151;">
                <div style="font-size:11px;color:#9ca3af;margin-bottom:4px;">CERTIFICATION</div>
                <div style="font-size:14px;font-weight:600;color:#e5e7eb;">{mi.get('certification','')}</div>
                <div style="font-size:12px;color:#9ca3af;">Readiness: {readiness}</div>
            </div>
            <div style="background:#1f2937;border-radius:8px;padding:12px;border:1px solid #374151;">
                <div style="font-size:11px;color:#9ca3af;margin-bottom:4px;">TIMELINE</div>
                <div style="font-size:14px;font-weight:600;color:#e5e7eb;">{weeks} weeks</div>
                <div style="font-size:12px;color:#9ca3af;">Workload: {workload}</div>
            </div>
        </div>
        <div class="dark-card-body">{mi.get('raw_output','').replace(chr(10),'<br>')}</div>
        {risk_html}
    </div>
    """, unsafe_allow_html=True)


def render_evidence(trail: list):
    if not trail:
        st.markdown(none_txt, unsafe_allow_html=True)
        return
    for entry in trail:
        step = entry.get('step', '').replace('_', ' ').title()
        st.markdown(f"""
        <div class="ev-card">
            <div class="ev-step">{step}</div>
            <div class="ev-query">Query: "{entry.get('query_used','')}"</div>
            <div class="ev-excerpt">{entry.get('evidence_retrieved','')[:350]}...</div>
        </div>""", unsafe_allow_html=True)

# Demo mode
demo_col, _ = st.columns([1, 2])
with demo_col:
    demo_mode = st.toggle("⚡ Try instant demo", value=False, help="Load Alex Chen's AZ-204 readiness analysis instantly")

if demo_mode:
    st.info("**Demo mode** — showing Alex Chen (Cloud Engineer) pursuing AZ-204 certification. All 5 agents completed.")
    if st.button("Load demo results ⚡", use_container_width=True, type="primary"):
        demo = load_demo_results()
        st.session_state["cert_results"] = demo["certification"]["results"]
        st.session_state["cert_trail"] = demo["certification"]["evidence_trail"]
        st.session_state["cert_steps"] = demo["certification"]["reasoning_steps_completed"]
        st.rerun()
    # Show profile preview
    st.markdown("""
    <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:1rem 1.25rem;margin-top:1rem;">
        <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:8px;">Alex Chen — Cloud Engineer</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
            <div style="font-size:12px;color:#6b7280;">Target: <strong style="color:#111827;">AZ-204</strong></div>
            <div style="font-size:12px;color:#6b7280;">Practice: <strong style="color:#111827;">67%</strong></div>
            <div style="font-size:12px;color:#6b7280;">Hours: <strong style="color:#111827;">12/20</strong></div>
            <div style="font-size:12px;color:#6b7280;">Workload: <strong style="color:#854F0B;">High</strong></div>
            <div style="font-size:12px;color:#6b7280;">Streak: <strong style="color:#111827;">5 days</strong></div>
            <div style="font-size:12px;color:#6b7280;">Capacity: <strong style="color:#111827;">Medium-Low</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # --- Learner Profile Form ---
    st.markdown("### Learner profile")
    st.caption("Enter employee details or select from synthetic dataset")

    use_synthetic = st.checkbox("Use synthetic learner profile", value=True)

    if use_synthetic:
        import json as json_lib
        with open("data/learner_profiles.json") as f:
            profiles_data = json_lib.load(f)

        learners = profiles_data["learners"]
        learner_names = [f"{l['name']} — {l['role']}" for l in learners]
        selected = st.selectbox("Select learner", learner_names)
        selected_learner = learners[learner_names.index(selected)]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Role:** {selected_learner['role']}")
            st.info(f"**Department:** {selected_learner['department']}")
        with col2:
            st.info(f"**Practice score:** {selected_learner['practice_score_avg']}%")
            st.info(f"**Hours studied:** {selected_learner['hours_studied']}h")
        with col3:
            st.info(f"**Study streak:** {selected_learner['study_streak_days']} days")
            st.info(f"**Current certs:** {', '.join(selected_learner['current_certifications'])}")

        learner_profile = selected_learner
        learner_id = selected_learner["id"]
        target_cert = selected_learner["target_certification"]

        st.markdown(f"**Target certification:** `{target_cert}`")

    else:
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full name", value="Jane Smith")
            role = st.selectbox("Role", [
                "Cloud Engineer", "DevOps Engineer", "Data Engineer",
                "AI Engineer", "Software Developer", "Solutions Architect"
            ])
            department = st.text_input("Department", value="Engineering")
            learner_id = st.text_input("Employee ID", value="EMP-001")
        with col2:
            practice_score = st.slider("Practice score average (%)", 0, 100, 65)
            hours_studied = st.number_input("Hours studied so far", 0, 100, 10)
            study_streak = st.number_input("Study streak (days)", 0, 100, 3)
            skills_input = st.text_input("Current skills (comma separated)", value="Python, Azure Basics")
            current_certs = st.multiselect("Current certifications", ["AZ-900", "AZ-204", "AZ-305", "AZ-400", "DP-203", "AI-102"])

        # Auto-recommend cert based on role
        cert_data = load_certifications()
        role_map = cert_data.get("role_certification_map", {})
        available_certs = role_map.get(role, ["AZ-900"])
        target_cert = st.selectbox("Target certification", available_certs)

        learner_profile = {
            "name": name,
            "role": role,
            "department": department,
            "target_certification": target_cert,
            "current_certifications": current_certs,
            "skills": [s.strip() for s in skills_input.split(",")],
            "practice_score_avg": practice_score,
            "hours_studied": hours_studied,
            "study_streak_days": study_streak
        }

    st.markdown("<br>", unsafe_allow_html=True)

# --- Analyze Button ---
button_placeholder = st.empty()
is_analyzing = st.session_state.get("cert_analyzing", False)

with button_placeholder:
    analyze_clicked = st.button(
        "Analyzing..." if is_analyzing else "Assess certification readiness →",
        disabled=is_analyzing,
        use_container_width=True,
        type="primary"
    )

# --- Run Analysis ---
if analyze_clicked:
    st.session_state.cert_analyzing = True
    st.session_state["cert_results"] = None
    st.session_state["cert_trail"] = []
    st.session_state["cert_session_id"] = None
    button_placeholder.empty()

    with button_placeholder:
        st.button("Analyzing...", disabled=True, use_container_width=True, type="primary")

    try:
        payload = {
            "learner_id": learner_id,
            "target_certification": target_cert,
            "learner_profile": learner_profile
        }

        start_response = requests.post(
            f"{API_URL}/analyze/certification",
            json=payload,
            timeout=30
        )

        if start_response.status_code != 200:
            st.error(f"Failed to start: {start_response.json().get('detail','Unknown error')}")
            st.session_state.cert_analyzing = False
            st.stop()

        session_id = start_response.json()["session_id"]
        st.session_state["cert_session_id"] = session_id

        progress_placeholder = st.empty()
        MAX_WAIT = 300
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > MAX_WAIT:
                progress_placeholder.empty()
                st.error("Analysis timed out.")
                st.session_state.cert_analyzing = False
                break

            try:
                status_resp = requests.get(f"{API_URL}/status/{session_id}", timeout=10)
                data = status_resp.json()
            except Exception:
                time.sleep(3)
                continue

            status = data.get("status")
            steps_done = data.get("reasoning_steps_completed", 0)

            with progress_placeholder.container():
                pct = min(int((steps_done / 5) * 100), 95) if status == "processing" else 100
                st.progress(pct, text=f"Agent {steps_done}/5 complete · {int(elapsed)}s elapsed")
                render_trace(steps_done, status)

            if status == "complete":
                progress_placeholder.empty()
                st.session_state["cert_results"] = data["results"]
                st.session_state["cert_trail"] = data.get("evidence_trail", [])
                st.session_state["cert_steps"] = steps_done
                st.session_state.cert_analyzing = False
                st.success("Certification analysis complete!")
                st.rerun()
                break
            elif status == "failed":
                progress_placeholder.empty()
                st.error(f"Analysis failed: {data.get('error','Unknown')}")
                st.session_state.cert_analyzing = False
                break

            time.sleep(3)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.cert_analyzing = False
        st.rerun()


# --- Display Results ---
if st.session_state.get("cert_results"):
    results = st.session_state["cert_results"]
    trail = st.session_state.get("cert_trail", [])
    steps_done = st.session_state.get("cert_steps", 5)

    lp = results.get("learning_path", {})
    sp = results.get("study_plan", {})
    eng = results.get("engagement_plan", {})
    asr = results.get("assessment_result", {})
    mi = results.get("manager_insights", {})
    schedule = results.get("work_schedule", {})

    # Always derive target_cert from results — safe for both demo and live mode
    target_cert = results.get("target_certification", lp.get("certification_id", "Unknown"))
    
    readiness = results.get("fabric_readiness", {})
    level = readiness.get("readiness_level", "Unknown")
    score = readiness.get("readiness_score", 0)
    weeks = results.get("work_schedule", {}).get("estimated_weeks_to_ready", "?")
    workload = results.get("work_capacity", {}).get("current_workload", "Unknown")

    if level == "Ready":
        b_bg, b_border, b_icon, b_color, b_title = "#EAF3DE","#C0DD97","ti-circle-check","#27500A","#3B6D11"
    elif "Nearly" in level:
        b_bg, b_border, b_icon, b_color, b_title = "#E6F1FB","#B5D4F4","ti-clock","#0C447C","#185FA5"
    elif "Needs" in level:
        b_bg, b_border, b_icon, b_color, b_title = "#FAEEDA","#FAC775","ti-alert-triangle","#633806","#854F0B"
    else:
        b_bg, b_border, b_icon, b_color, b_title = "#FCEBEB","#F7C1C1","ti-circle-x","#791F1F","#A32D2D"

    st.markdown(f"""
    <div style="background:{b_bg};border:1.5px solid {b_border};border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;">
        <div style="display:flex;align-items:center;gap:14px;">
            <i class="ti {b_icon}" style="font-size:32px;color:{b_title};"></i>
            <div>
                <div style="font-size:20px;font-weight:700;color:{b_title};">{level}</div>
                <div style="font-size:13px;color:{b_color};margin-top:2px;">
                    {mi.get('team_member','')} · {target_cert} · {workload} workload · {weeks} weeks to exam-ready
                </div>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:11px;color:{b_color};margin-bottom:4px;text-transform:uppercase;letter-spacing:0.05em;">Readiness score</div>
            <div style="font-size:36px;font-weight:700;color:{b_title};line-height:1;">{score}<span style="font-size:16px;font-weight:500;color:{b_color};">/100</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="slabel">Agent reasoning trace</div>', unsafe_allow_html=True)
    render_trace(steps_done or 5, "complete")

    st.markdown('<div class="slabel">Readiness scorecard</div>', unsafe_allow_html=True)
    render_scorecard(results)

    st.markdown('<div class="slabel">Agent outputs</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗺️ Learning path",
        "📅 Study plan",
        "🔔 Engagement",
        "📊 Assessment",
        "👔 Manager view",
        "🔍 Evidence trail"
    ])

    with tab1: render_learning_path(lp)
    with tab2: render_study_plan(sp, schedule)
    with tab3: render_engagement(eng)
    with tab4: render_assessment(asr)
    with tab5: render_manager_insights(mi)
    with tab6: render_evidence(trail)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        st.download_button(
            "⬇️ Full report (JSON)",
            data=json.dumps(results, indent=2),
            file_name=f"oppint_cert_{target_cert}.json",
            mime="application/json",
            use_container_width=True
        )

    with col_b:
        plan_text = "\n".join([
            f"OPPINT CERTIFICATION READINESS REPORT",
            f"Learner: {mi.get('team_member','')} | Cert: {target_cert}",
            "=" * 40, "",
            f"READINESS LEVEL: {asr.get('readiness_verdict','')}",
            f"READINESS SCORE: {asr.get('readiness_score','')}/100",
            f"PRACTICE SCORE: {asr.get('practice_score','')}%",
            f"WEEKS TO READY: {sp.get('estimated_weeks','')}",
            "",
            "SKILL GAPS:",
            *[f"- {g}" for g in asr.get("skill_gaps", [])],
            "",
            "STUDY SCHEDULE:",
            f"- {sp.get('sessions_per_week','')} sessions/week",
            f"- {sp.get('session_length_minutes','')} minutes per session",
            f"- {sp.get('weekly_hours','')} hours per week",
            "",
            "RECOMMENDED WINDOWS:",
            *[f"- {w}" for w in schedule.get("recommended_windows", [])],
        ])
        st.download_button(
            "⬇️ Readiness report (TXT)",
            data=plan_text,
            file_name=f"oppint_cert_{target_cert}_report.txt",
            mime="text/plain",
            use_container_width=True
        )
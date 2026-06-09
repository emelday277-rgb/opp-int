import streamlit as st

st.set_page_config(
    page_title="OppInt — Opportunity Intelligence",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');
* { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.oppint-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 3rem; border-bottom: 1px solid #e5e7eb;
    background: #fff; position: sticky; top: 0; z-index: 100;
}
.nav-logo { display: flex; align-items: center; gap: 10px; }
.nav-logo-icon { width: 34px; height: 34px; border-radius: 8px; background: #185FA5; display: flex; align-items: center; justify-content: center; }
.nav-logo-icon i { color: #fff; font-size: 17px; }
.nav-logo-title { font-size: 16px; font-weight: 600; color: #111827; }
.nav-logo-sub { font-size: 12px; color: #6b7280; margin-top: 1px; }
.nav-right a { text-decoration: none; background: #185FA5; color: #fff !important; padding: 8px 20px; border-radius: 8px; font-size: 13px; font-weight: 500; }

.hero-section { text-align: center; padding: 5rem 2rem 3.5rem; max-width: 700px; margin: 0 auto; }
.hero-badge { display: inline-flex; align-items: center; gap: 6px; background: #E6F1FB; color: #0C447C; font-size: 12px; font-weight: 500; padding: 5px 14px; border-radius: 20px; margin-bottom: 1.5rem; }
.hero-title { font-size: 42px; font-weight: 700; color: #111827; line-height: 1.2; margin-bottom: 1.25rem; }
.hero-title span { color: #185FA5; }
.hero-sub { font-size: 16px; color: #6b7280; line-height: 1.75; margin-bottom: 2rem; }
.hero-btns { display: flex; gap: 12px; justify-content: center; }
.btn-primary { padding: 12px 28px; border-radius: 8px; background: #185FA5; color: #fff !important; font-size: 14px; font-weight: 500; text-decoration: none; display: inline-block; }
.btn-outline { padding: 12px 28px; border-radius: 8px; background: transparent; color: #374151 !important; font-size: 14px; font-weight: 500; text-decoration: none; border: 1px solid #d1d5db; display: inline-block; }

.section-wrap { max-width: 900px; margin: 0 auto; padding: 3rem 2rem; }
.section-label { text-align: center; font-size: 12px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1.5rem; }
.section-divider { border: none; border-top: 1px solid #f3f4f6; margin: 0; }

.steps-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.step-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; }
.step-num { width: 30px; height: 30px; border-radius: 50%; background: #E6F1FB; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; color: #0C447C; margin-bottom: 12px; }
.step-card h3 { font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 6px; }
.step-card p { font-size: 13px; color: #6b7280; line-height: 1.65; }

.features-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.feature-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.25rem; display: flex; gap: 14px; align-items: flex-start; }
.feature-icon { width: 38px; height: 38px; border-radius: 9px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 19px; }
.fi-blue { background: #E6F1FB; color: #185FA5; }
.fi-green { background: #EAF3DE; color: #3B6D11; }
.fi-amber { background: #FAEEDA; color: #854F0B; }
.fi-purple { background: #EEEDFE; color: #534AB7; }
.feature-card h3 { font-size: 14px; font-weight: 600; color: #111827; margin-bottom: 5px; }
.feature-card p { font-size: 13px; color: #6b7280; line-height: 1.65; }

.iq-banner { background: #E6F1FB; border: 1px solid #B5D4F4; border-radius: 12px; padding: 1.25rem 1.5rem; display: flex; align-items: center; gap: 14px; }
.iq-banner i { font-size: 24px; color: #185FA5; flex-shrink: 0; }
.iq-banner h3 { font-size: 14px; font-weight: 600; color: #0C447C; margin-bottom: 4px; }
.iq-banner p { font-size: 13px; color: #185FA5; line-height: 1.55; margin: 0; }

.cta-section { background: #185FA5; padding: 4rem 2rem; text-align: center; }
.cta-section h2 { font-size: 28px; font-weight: 700; color: #fff; margin-bottom: 1rem; }
.cta-section p { font-size: 15px; color: #B5D4F4; margin-bottom: 2rem; }
.btn-white { padding: 12px 28px; border-radius: 8px; background: #fff; color: #185FA5 !important; font-size: 14px; font-weight: 600; text-decoration: none; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# Nav
st.markdown("""
<div class="oppint-nav">
    <div class="nav-logo">
        <div class="nav-logo-icon"><i class="ti ti-bulb"></i></div>
        <div>
            <div class="nav-logo-title">OppInt</div>
            <div class="nav-logo-sub">Opportunity Intelligence Agent</div>
        </div>
    </div>
    <div class="nav-right"><a href="/Analyzer" target="_self">Start analyzing →</a></div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero-section">
    <div class="hero-badge"><i class="ti ti-sparkles"></i> Powered by Microsoft Foundry IQ</div>
    <h1 class="hero-title">Pursue the right opportunities<br>with <span>confidence</span></h1>
    <p class="hero-sub">OppInt evaluates grants, RFPs, and contracts against your organization profile — turning a 3-day manual process into a 60-second evidence-backed decision.</p>
    <div class="hero-btns">
        <a class="btn-primary" href="/Analyzer" target="_self">Start analyzing →</a>
        <a class="btn-outline" href="#how">See how it works</a>
    </div>
</div>
<hr class="section-divider">
""", unsafe_allow_html=True)

# How it works
st.markdown('<div class="section-wrap"><div class="section-label">How it works</div>', unsafe_allow_html=True)
st.markdown("""
<div class="steps-grid">
    <div class="step-card">
        <div class="step-num">1</div>
        <h3>Upload documents</h3>
        <p>Drop in the opportunity document and your organization profile. PDF or TXT supported.</p>
    </div>
    <div class="step-card">
        <div class="step-num">2</div>
        <h3>Agent reasons</h3>
        <p>A 6-step reasoning pipeline analyzes fit, identifies risks, and builds an action plan — grounded in your documents via Foundry IQ.</p>
    </div>
    <div class="step-card">
        <div class="step-num">3</div>
        <h3>Decide with confidence</h3>
        <p>Get a fit score, evidence-backed recommendation, and a ready-to-use submission checklist.</p>
    </div>
</div>
</div>
<hr class="section-divider">
""", unsafe_allow_html=True)

# Features
st.markdown('<div class="section-wrap"><div class="section-label">What OppInt does</div>', unsafe_allow_html=True)
st.markdown("""
<div class="features-grid">
    <div class="feature-card">
        <div class="feature-icon fi-blue"><i class="ti ti-brain"></i></div>
        <div><h3>6-step reasoning agent</h3><p>Multi-step pipeline built on LangGraph — each step builds on the last, not a single prompt.</p></div>
    </div>
    <div class="feature-card">
        <div class="feature-icon fi-green"><i class="ti ti-file-check"></i></div>
        <div><h3>Evidence-backed decisions</h3><p>Every recommendation traces back to specific text in your documents. No hallucinations, no guessing.</p></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="features-grid" style="margin-top:14px;">
    <div class="feature-card">
        <div class="feature-icon fi-amber"><i class="ti ti-alert-triangle"></i></div>
        <div><h3>Risk identification</h3><p>Surfaces high, medium, and low risks with mitigation suggestions before you commit resources.</p></div>
    </div>
    <div class="feature-card">
        <div class="feature-icon fi-purple"><i class="ti ti-list-check"></i></div>
        <div><h3>Actionable plan output</h3><p>Leaves you with a preparation checklist, submission checklist, and clear next steps.</p></div>
    </div>
</div>
""", unsafe_allow_html=True)

# IQ Banner
st.markdown("""
<div style="margin-top:1.5rem;" class="iq-banner">
    <i class="ti ti-circuit-cell"></i>
    <div>
        <h3>Built on Microsoft Foundry IQ</h3>
        <p>Document retrieval and evidence grounding powered by Azure AI Search — part of the Microsoft IQ intelligence layer. Every recommendation is grounded in your uploaded documents, not generated from assumptions.</p>
    </div>
</div>
</div>
<hr class="section-divider">
""", unsafe_allow_html=True)

# CTA
# st.markdown("""
# <div class="cta-section">
#     <h2>Ready to evaluate your next opportunity?</h2>
#     <p>Upload two documents. Get a complete intelligence report in under 60 seconds.</p>
#     <a class="btn-white" href="/Analyzer" target="_self">Open the analyzer →</a>
# </div>
# """, unsafe_allow_html=True)
# Two module cards
st.markdown('<div class="section-wrap"><div class="section-label">Choose your module</div>', unsafe_allow_html=True)

st.markdown("""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:1.5rem;">
        <div style="width:38px;height:38px;border-radius:9px;background:#E6F1FB;display:flex;align-items:center;justify-content:center;margin-bottom:12px;">
            <i class="ti ti-file-search" style="color:#185FA5;font-size:19px;"></i>
        </div>
        <h3 style="font-size:16px;font-weight:600;color:#111827;margin-bottom:6px;">Opportunity Evaluator</h3>
        <p style="font-size:13px;color:#6b7280;line-height:1.65;margin-bottom:16px;">Upload a grant, RFP, or contract alongside your organization profile. Get a fit score, risk assessment, and action plan in 60 seconds.</p>
        <a href="/Analyzer" target="_self" style="display:inline-block;padding:9px 20px;background:#185FA5;color:#fff;border-radius:8px;font-size:13px;font-weight:500;text-decoration:none;">Evaluate an opportunity →</a>
    </div>
    <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:1.5rem;">
        <div style="width:38px;height:38px;border-radius:9px;background:#EEEDFE;display:flex;align-items:center;justify-content:center;margin-bottom:12px;">
            <i class="ti ti-certificate" style="color:#534AB7;font-size:19px;"></i>
        </div>
        <h3 style="font-size:16px;font-weight:600;color:#111827;margin-bottom:6px;">Certification Readiness</h3>
        <p style="font-size:13px;color:#6b7280;line-height:1.65;margin-bottom:16px;">Assess team certification readiness using Foundry IQ, Work IQ, and Fabric IQ. Get personalised study plans and manager insights.</p>
        <a href="/Certification" target="_self" style="display:inline-block;padding:9px 20px;background:#534AB7;color:#fff;border-radius:8px;font-size:13px;font-weight:500;text-decoration:none;">Assess readiness →</a>
    </div>
</div>
</div>
<hr class="section-divider">
""", unsafe_allow_html=True)

# CTA
st.markdown("""
<div class="cta-section">
    <h2>Pursue fewer opportunities. Win more of them.</h2>
    <p>The intelligence platform for smarter opportunity decisions — external and internal.</p>
    <div style="display:flex;gap:12px;justify-content:center;">
        <a class="btn-white" href="/Analyzer" target="_self">Evaluate opportunity →</a>
        <a style="padding:12px 28px;border-radius:8px;background:transparent;color:#fff;font-size:14px;font-weight:600;text-decoration:none;border:2px solid rgba(255,255,255,0.4);" href="/Certification" target="_self">Assess certification →</a>
    </div>
</div>
""", unsafe_allow_html=True)
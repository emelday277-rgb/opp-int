# OppInt — Opportunity Intelligence Platform

> Pursue fewer opportunities. Win more of them.

OppInt is a multi-agent reasoning platform that helps organizations make
smarter decisions about which opportunities to pursue external ones like
grants and contracts and internal ones like team certifications.

Built for the Microsoft Agents League Hackathon — Reasoning Agents track.

---

## What Problem Does OppInt Solve?

Organizations constantly encounter opportunities that could help them grow —
grants, RFPs, government contracts, funding calls, and certification programs.

Evaluating each one properly takes hours. Most organizations either skip the
evaluation entirely and waste resources on poor fits, or miss valuable
opportunities because the analysis felt too overwhelming to start.

OppInt does the evaluation for you — in under 60 seconds — and shows its work.

---

## Two Modules, One Platform

### Module 1 — Opportunity Evaluator
Upload an opportunity document (grant, RFP, contract) and your organization
profile. OppInt runs a 6-step reasoning pipeline and tells you whether to
pursue it, why, and exactly what to do next.

### Module 2 — Certification Readiness
Select a team member and their target certification. OppInt runs a 5-agent
pipeline that builds a personalized study plan, adapts it to their work
schedule, evaluates their readiness, and gives their manager a clear dashboard.

---

## How It Works

### Opportunity Evaluator — 6 Reasoning Steps
Step 1 — Understand the opportunity
Reads the document. Extracts purpose, requirements,
deadlines, and evaluation criteria.

Step 2 — Understand the organization
Reads the organization profile. Maps capabilities,
experience, certifications, and strengths.

Step 3 — Evaluate fit
Compares requirements against capabilities.
Scores the match. Identifies gaps.

Step 4 — Assess risks
Flags missing documents, tight deadlines,
compliance concerns, and resource constraints.

Step 5 — Generate recommendation
Delivers a clear PURSUE / PURSUE WITH CAUTION /
DO NOT PURSUE decision with reasoning.

Step 6 — Create action plan
Produces a preparation checklist, submission
checklist, and prioritized next steps.

### Certification Readiness — 5 Specialist Agents
Agent 1 — Learning Path Curator (Foundry IQ)
Retrieves grounded certification content.
Maps required skills against current skills.
Identifies gaps with cited evidence.

Agent 2 — Study Plan Generator (Fabric IQ)
Uses the certification semantic model to build
a capacity-aware, role-aligned study schedule.

Agent 3 — Engagement Agent (Work IQ)
Reads work signals — meetings, focus hours,
workload — and adapts reminders to work rhythm.

Agent 4 — Assessment Agent (Foundry IQ)
Evaluates readiness. Generates grounded practice
questions cited from the knowledge base.

Agent 5 — Manager Insights Agent (Work IQ + Fabric IQ)
Surfaces team-level progress, risk areas, and
recommended manager actions.

---

## Microsoft IQ Integration

OppInt uses all three Microsoft IQ intelligence layers.

| IQ Layer | Role in OppInt |
|---|---|
| **Foundry IQ** | Indexes uploaded documents into Azure AI Search. Every agent retrieves cited evidence rather than generating from memory. |
| **Work IQ** | Work signals (meeting hours, focus time, workload) inform the Engagement Agent's reminder strategy and study scheduling. |
| **Fabric IQ** | A certification ontology models the relationships between roles, skills, certifications, readiness thresholds, and study hours — giving agents structured business meaning to reason over. |

---

## What Makes OppInt Different

**Evidence trail on every decision**
Every conclusion links back to specific text retrieved from your documents.
You can see exactly what was retrieved, which query was used, and what the
agent concluded at each step. Nothing is fabricated.

**Reasoning you can follow**
The UI shows each agent step firing in real time with a live progress trace.
Judges and users can see the thinking, not just the output.

**Two modules, shared infrastructure**
Both modules run on the same LangGraph + Foundry IQ backbone. The platform
demonstrates that the same reasoning architecture applies to both external
opportunity evaluation and internal workforce development.

**Built for real decisions**
OppInt is not a chatbot or a summarizer. It is a decision-support system.
Every output is actionable — a score, a checklist, a plan, a recommendation.

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent framework | LangGraph |
| Backend API | FastAPI |
| Frontend | Streamlit |
| LLM | gpt-4.1-mini via Microsoft Foundry |
| Knowledge retrieval | Azure AI Search (Foundry IQ) |
| Semantic layer | Custom certification ontology (Fabric IQ) |
| Work context layer | Work signals dataset (Work IQ) |
| Document parsing | pypdf |
| PDF reports | ReportLab |

---

## Running Locally

### Prerequisites
- Python 3.10+
- Azure account with Foundry and AI Search set up

### Setup

```bash
# Clone the repo
git clone https://github.com/Etette/oppint.git
cd oppint

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
- AZURE_FOUNDRY_ENDPOINT=
- AZURE_FOUNDRY_API_KEY=
- AZURE_FOUNDRY_DEPLOYMENT=gpt-4.1-mini
- AZURE_SEARCH_ENDPOINT=
- AZURE_SEARCH_API_KEY=
- AZURE_SEARCH_INDEX=oppint-index

### Start the App

Open two terminals:

```bash
# Terminal 1 — Backend
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## Try the Demo

Both analyzer pages have an **instant demo mode** — toggle it on and click
"Load demo results" to see a complete analysis without uploading any files.

The demo uses synthetic data only. No real organization data, no PII.

---

## Sample Files

Two sample files are included in the project root for testing:

- `sample_opportunity.txt` — A fictional grant announcement
- `sample_organization.txt` — A fictional company profile

Upload both to the Opportunity Evaluator to run a live analysis.

---

## API Reference

The FastAPI backend exposes these endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/health` | GET | Server status |
| `/analyze` | POST | Start opportunity analysis |
| `/analyze/certification` | POST | Start certification analysis |
| `/status/{session_id}` | GET | Poll analysis progress |
| `/report/{session_id}` | POST | Generate PDF report |

Interactive API docs available at **http://localhost:8000/docs**

---

## Synthetic Data Notice

All data used in this project is synthetic and created for demonstration
purposes only. This includes:

- Learner profiles (L-1001 through L-1005)
- Work signals and team data
- Certification performance benchmarks
- Sample opportunity and organization documents

No real employee data, customer data, or PII is included anywhere in
this submission.

---

## Responsible AI

OppInt is designed as a decision-support tool, not a decision-making tool.

- Every recommendation is accompanied by the evidence that supports it
- Users are always shown the reasoning behind each conclusion
- The platform explicitly encourages human review before acting
- Confidence levels and risk flags are surfaced on every output
- The system does not store uploaded documents after analysis completes

---

## Hackathon Submission

- **Track:** Reasoning Agents — Microsoft Foundry
- **Microsoft IQ layers used:** Foundry IQ, Work IQ, Fabric IQ
- **Challenge alignment:** Multi-agent enterprise intelligence system
  demonstrating grounded reasoning, semantic business understanding,
  and work-context-aware decision support.

---

## License

Built for the Microsoft Agents League Hackathon 2026.
import os
import io
import uuid
import tempfile
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pypdf import PdfReader
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from service.foundry_iq import index_document, cleanup_session
from service.validator import validate_file_upload, validate_extracted_text
from fastapi.responses import Response
import json as json_lib
from service.report_generator import generate_pdf_report
from agent.opportunity_agent import opportunity_agent, session_progress
from agent.certification_agent import certification_agent, session_progress as cert_session_progress
load_dotenv()


# --- Lifespan (startup + graceful shutdown) ---
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("OppInt starting up...")
#     print("Opportunity Intelligence Agent is ready.")
#     yield
#     print("\nOppInt shutting down gracefully...")
#     print("All resources released. Goodbye.")
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("OppInt starting up...")
    print("Indexing certification knowledge into Foundry IQ...")
    try:
        index_certification_knowledge()
    except Exception as e:
        print(f"Knowledge indexing warning: {e}")
    print("Opportunity Intelligence Platform is ready.")
    yield
    print("\nOppInt shutting down gracefully...")
    print("All resources released. Goodbye.")


app = FastAPI(
    title="OppInt - Opportunity Intelligence Agent",
    description="Helping organizations pursue the right opportunities with confidence.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# --- Helpers ---
def extract_text(file: UploadFile) -> str:
    """Extract text from uploaded PDF or TXT file."""
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        reader = PdfReader(tmp_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        os.unlink(tmp_path)
        return text

    elif filename.endswith(".txt"):
        return file.file.read().decode("utf-8")

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or TXT file."
        )

def update_session_step(session_id: str, step_name: str, steps_completed: int):
    if session_id in analysis_sessions:
        analysis_sessions[session_id]["current_step"] = step_name
        analysis_sessions[session_id]["reasoning_steps_completed"] = steps_completed


def index_certification_knowledge():
    """Index synthetic certification guide into Foundry IQ at startup."""
    import os
    from service.foundry_iq import index_document, ensure_index_exists

    guide_path = os.path.join(os.path.dirname(__file__), "data", "certification_guides.txt")
    if not os.path.exists(guide_path):
        print("Certification guide not found — skipping indexing.")
        return

    with open(guide_path, "r") as f:
        content = f.read()

    ensure_index_exists()

    # Use a fixed session ID for permanent knowledge
    index_document(content, doc_type="certification", session_id="oppint-knowledge-base")
    print("Certification knowledge base indexed into Foundry IQ.")

# --- Routes ---
@app.get("/")
def root():
    return {
        "name": "OppInt",
        "status": "running",
        "message": "Opportunity Intelligence Agent is ready."
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

executor = ThreadPoolExecutor(max_workers=4)
analysis_sessions = {}  # in-memory session store


def run_analysis_sync(session_id: str, opportunity_text: str, org_text: str):
    try:
        # Register in agent's progress store
        session_progress[session_id] = {
            "current_step": "Indexing documents",
            "reasoning_steps_completed": 0
        }
        analysis_sessions[session_id]["current_step"] = "Indexing documents into Foundry IQ"

        index_document(opportunity_text, doc_type="opportunity", session_id=session_id)
        index_document(org_text, doc_type="organization", session_id=session_id)

        analysis_sessions[session_id]["current_step"] = "Running reasoning agent"

        initial_state = {
            "session_id": session_id,
            "opportunity_summary": "",
            "organization_summary": "",
            "fit_evaluation": "",
            "risk_assessment": "",
            "recommendation": "",
            "action_plan": "",
            "evidence": {},
            "evidence_trail": [],
            "parsed_opportunity": {},
            "parsed_organization": {},
            "parsed_fit": {},
            "parsed_risks": {},
            "parsed_recommendation": {},
            "parsed_action_plan": {}
        }

        final_state = opportunity_agent.invoke(initial_state)
        cleanup_session(session_id)

        analysis_sessions[session_id].update({
            "status": "complete",
            "current_step": "Complete",
            "results": {
                "opportunity_summary": final_state["parsed_opportunity"],
                "organization_summary": final_state["parsed_organization"],
                "fit_evaluation": final_state["parsed_fit"],
                "risk_assessment": final_state["parsed_risks"],
                "recommendation": final_state["parsed_recommendation"],
                "action_plan": final_state["parsed_action_plan"],
            },
            "evidence_trail": final_state.get("evidence_trail", []),
            "reasoning_steps_completed": len(final_state.get("evidence_trail", []))
        })

        # Clean up progress store
        session_progress.pop(session_id, None)

    except Exception as e:
        cleanup_session(session_id)
        session_progress.pop(session_id, None)
        analysis_sessions[session_id].update({
            "status": "failed",
            "error": str(e)
        })
        print(f"Analysis failed for session {session_id}: {e}")

def run_certification_sync(
    session_id: str,
    learner_id: str,
    learner_profile: dict,
    target_certification: str
):
    """Runs the certification analysis pipeline in a background thread."""
    try:
        cert_session_progress[session_id] = {
            "current_step": "Starting certification analysis",
            "reasoning_steps_completed": 0
        }
        analysis_sessions[session_id]["current_step"] = "Initializing agents"

        initial_state = {
            "session_id": session_id,
            "learner_id": learner_id,
            "learner_profile": learner_profile,
            "target_certification": target_certification,
            "learning_path": "",
            "study_plan": "",
            "engagement_plan": "",
            "assessment_result": "",
            "manager_insights": "",
            "parsed_learning_path": {},
            "parsed_study_plan": {},
            "parsed_engagement": {},
            "parsed_assessment": {},
            "parsed_manager_insights": {},
            "fabric_readiness": {},
            "fabric_skill_gaps": {},
            "work_capacity": {},
            "work_schedule": {},
            "evidence_trail": []
        }

        final_state = certification_agent.invoke(initial_state)

        analysis_sessions[session_id].update({
            "status": "complete",
            "current_step": "Complete",
            "module": "certification",
            "results": {
                "learner_id": learner_id,
                "target_certification": target_certification,
                "fabric_readiness": final_state.get("fabric_readiness", {}),
                "fabric_skill_gaps": final_state.get("fabric_skill_gaps", {}),
                "work_capacity": final_state.get("work_capacity", {}),
                "work_schedule": final_state.get("work_schedule", {}),
                "learning_path": final_state.get("parsed_learning_path", {}),
                "study_plan": final_state.get("parsed_study_plan", {}),
                "engagement_plan": final_state.get("parsed_engagement", {}),
                "assessment_result": final_state.get("parsed_assessment", {}),
                "manager_insights": final_state.get("parsed_manager_insights", {}),
            },
            "evidence_trail": final_state.get("evidence_trail", []),
            "reasoning_steps_completed": len(final_state.get("evidence_trail", []))
        })

        cert_session_progress.pop(session_id, None)

    except Exception as e:
        cert_session_progress.pop(session_id, None)
        analysis_sessions[session_id].update({
            "status": "failed",
            "error": str(e)
        })
        print(f"Certification analysis failed for session {session_id}: {e}")


@app.post("/analyze/certification")
async def analyze_certification(request: Request):
    """
    Certification readiness analysis endpoint.
    Accepts learner profile JSON and runs the 5-agent certification pipeline.
    """
    session_id = str(uuid.uuid4())
    body = await request.json()

    learner_id = body.get("learner_id")
    target_certification = body.get("target_certification")
    learner_profile = body.get("learner_profile", {})

    if not learner_id or not target_certification or not learner_profile:
        raise HTTPException(
            status_code=400,
            detail="learner_id, target_certification, and learner_profile are required."
        )

    print(f"\n{'='*50}")
    print(f"New certification session: {session_id}")
    print(f"Learner: {learner_id} | Cert: {target_certification}")
    print(f"{'='*50}\n")

    analysis_sessions[session_id] = {
        "status": "processing",
        "module": "certification",
        "current_step": "Starting certification analysis",
        "results": None,
        "evidence_trail": [],
        "reasoning_steps_completed": 0,
        "error": None
    }

    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor,
        run_certification_sync,
        session_id,
        learner_id,
        learner_profile,
        target_certification
    )

    return {
        "session_id": session_id,
        "status": "processing",
        "message": "Certification analysis started. Poll /status/{session_id} for updates."
    }

# @app.get("/status/{session_id}")
# async def get_status(session_id: str):
#     if session_id not in analysis_sessions:
#         raise HTTPException(status_code=404, detail="Session not found.")

#     session = dict(analysis_sessions[session_id])

#     # Merge live step progress from agent
#     if session_id in session_progress:
#         session["current_step"] = session_progress[session_id].get("current_step", session["current_step"])
#         session["reasoning_steps_completed"] = session_progress[session_id].get("reasoning_steps_completed", 0)

#     return session

@app.get("/status/{session_id}")
async def get_status(session_id: str):
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    session = dict(analysis_sessions[session_id])

    # Merge live step progress from either agent
    progress = (
        session_progress.get(session_id) or
        cert_session_progress.get(session_id)
    )
    if progress:
        session["current_step"] = progress.get("current_step", session["current_step"])
        session["reasoning_steps_completed"] = progress.get("reasoning_steps_completed", 0)

    return session

@app.post("/analyze")
async def analyze(
    opportunity_file: UploadFile = File(...),
    organization_files: List[UploadFile] = File(...)
):
    session_id = str(uuid.uuid4())
    print(f"\n{'='*50}")
    print(f"New session: {session_id}")
    print(f"{'='*50}\n")

    try:
        # Validate and extract
        opp_contents = validate_file_upload(opportunity_file, "Opportunity document")
        opportunity_file.file = io.BytesIO(opp_contents)
        opportunity_text = extract_text(opportunity_file)
        validate_extracted_text(opportunity_text, "Opportunity document")

        org_texts = []
        for i, org_file in enumerate(organization_files):
            org_contents = validate_file_upload(org_file, f"Organization document {i+1}")
            org_file.file = io.BytesIO(org_contents)
            text = extract_text(org_file)
            validate_extracted_text(text, f"Organization document {i+1}")
            org_texts.append(f"=== Document: {org_file.filename} ===\n{text}")

        combined_org_text = "\n\n".join(org_texts)

        # Register session
        analysis_sessions[session_id] = {
            "status": "processing",
            "current_step": "Starting analysis",
            "results": None,
            "evidence_trail": [],
            "reasoning_steps_completed": 0,
            "error": None
        }

        # Run in background thread
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor,
            run_analysis_sync,
            session_id,
            opportunity_text,
            combined_org_text
        )

        return {
            "session_id": session_id,
            "status": "processing",
            "message": "Analysis started. Poll /status/{session_id} for updates."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Startup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@app.post("/report/{session_id}")
async def generate_report(session_id: str, request: Request):
    """Generate a PDF report from cached results."""
    body = await request.json()
    results = body.get("results", {})
    evidence_trail = body.get("evidence_trail", [])
    pdf_bytes = generate_pdf_report(results, evidence_trail)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=oppint_report_{session_id}.pdf"}
    )
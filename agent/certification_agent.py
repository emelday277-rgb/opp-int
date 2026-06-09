import os
import json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from service.foundry_iq import retrieve_context, index_document
from service.fabric_iq import (
    evaluate_readiness_score,
    get_skill_gaps,
    get_team_readiness_summary,
    get_certification,
    get_role_certifications
)
from service.work_iq import (
    analyze_study_capacity,
    generate_study_schedule,
    get_team_capacity_summary
)
from service.retry import with_retry

load_dotenv()

llm = ChatOpenAI(
    base_url=f"{os.getenv('AZURE_FOUNDRY_ENDPOINT').rstrip('/')}/openai/v1/",
    api_key=os.getenv("AZURE_FOUNDRY_API_KEY"),
    model=os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4.1-mini"),
    temperature=0.3
)

# Shared progress store
session_progress = {}


def report_progress(session_id: str, step_name: str, steps_completed: int):
    if session_id in session_progress:
        session_progress[session_id]["current_step"] = step_name
        session_progress[session_id]["reasoning_steps_completed"] = steps_completed


@with_retry(max_attempts=3, delay=2.0, backoff=2.0)
def invoke_llm(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content


def safe_truncate(text: str, max_chars: int = 1000) -> str:
    if len(text) > max_chars:
        return text[:max_chars] + "\n[truncated]"
    return text


def build_evidence_entry(step: str, query: str, context: str, conclusion: str) -> dict:
    return {
        "step": step,
        "query_used": query,
        "evidence_retrieved": context[:500] + "..." if len(context) > 500 else context,
        "conclusion_summary": conclusion[:300] + "..." if len(conclusion) > 300 else conclusion
    }


# --- State ---
class CertAgentState(TypedDict):
    session_id: str
    learner_id: str
    learner_profile: dict
    target_certification: str

    # Agent outputs
    learning_path: str
    study_plan: str
    engagement_plan: str
    assessment_result: str
    manager_insights: str

    # Structured parsed outputs
    parsed_learning_path: dict
    parsed_study_plan: dict
    parsed_engagement: dict
    parsed_assessment: dict
    parsed_manager_insights: dict

    # Supporting data from IQ layers
    fabric_readiness: dict
    fabric_skill_gaps: dict
    work_capacity: dict
    work_schedule: dict

    # Evidence
    evidence_trail: list


# --- Agent 1: Learning Path Curator ---
def learning_path_curator(state: CertAgentState) -> CertAgentState:
    print("Cert Agent 1: Learning Path Curator...")
    report_progress(state["session_id"], "Curating learning path", 1)

    profile = state["learner_profile"]
    cert_id = state["target_certification"]
    learner_id = state["learner_id"]

    # Foundry IQ — retrieve grounded certification content
    query = f"{cert_id} certification requirements study areas learning resources"
    context = retrieve_context(
        query=query,
        session_id=state["session_id"],
        doc_type="certification",
        top=5
    )
    context = safe_truncate(context, 1200)

    # Fabric IQ — get semantic certification data
    cert_data = get_certification(cert_id)
    role_certs = get_role_certifications(profile.get("role", ""))
    skill_gaps = get_skill_gaps(profile.get("skills", []), cert_id)
    state["fabric_skill_gaps"] = skill_gaps

    prompt = f"""You are a Learning Path Curator agent for an enterprise certification platform.

LEARNER PROFILE:
- Name: {profile.get('name')}
- Role: {profile.get('role')}
- Target Certification: {cert_id}
- Current Certifications: {profile.get('current_certifications', [])}
- Current Skills: {profile.get('skills', [])}

CERTIFICATION DATA (Fabric IQ):
{json.dumps(cert_data, indent=2)}

SKILL GAPS IDENTIFIED (Fabric IQ):
- Matched skills: {skill_gaps.get('matched_skills', [])}
- Missing skills: {skill_gaps.get('skill_gaps', [])}
- Match percentage: {skill_gaps.get('match_percentage')}%

GROUNDED KNOWLEDGE (Foundry IQ):
{context}

Based on the above, curate a personalised learning path. Be specific and cite content from the knowledge base.

Respond in this exact format:

CERTIFICATION TARGET: [{cert_id} name]

PREREQUISITE CHECK:
[Are prerequisites met? What evidence supports this?]

RECOMMENDED LEARNING PATH:
[Ordered list of topics to study, mapped to skill gaps]

KEY RESOURCES:
[Specific study areas grounded in the knowledge base above]

ROLE ALIGNMENT:
[How this certification aligns to the learner's role]

ESTIMATED DIFFICULTY:
[Easy / Moderate / Challenging — with reasoning]
"""

    result = invoke_llm(prompt)
    entry = build_evidence_entry("learning_path_curator", query, context, result)
    report_progress(state["session_id"], "Learning path curated", 1)

    return {
        **state,
        "learning_path": result,
        "parsed_learning_path": {
            "certification_id": cert_id,
            "certification_name": cert_data.get("name", ""),
            "skill_gaps": skill_gaps.get("skill_gaps", []),
            "matched_skills": skill_gaps.get("matched_skills", []),
            "match_percentage": skill_gaps.get("match_percentage", 0),
            "required_skills": cert_data.get("skills", []),
            "role_alignment": cert_data.get("role_alignment", []),
            "raw_output": result
        },
        "evidence_trail": state.get("evidence_trail", []) + [entry]
    }


# --- Agent 2: Study Plan Generator ---
def study_plan_generator(state: CertAgentState) -> CertAgentState:
    print("Cert Agent 2: Study Plan Generator...")
    report_progress(state["session_id"], "Generating study plan", 2)

    profile = state["learner_profile"]
    cert_id = state["target_certification"]
    learner_id = state["learner_id"]

    # Fabric IQ — readiness evaluation
    readiness = evaluate_readiness_score(
        practice_score=profile.get("practice_score_avg", 0),
        hours_studied=profile.get("hours_studied", 0),
        cert_id=cert_id
    )
    state["fabric_readiness"] = readiness

    # Work IQ — capacity analysis
    capacity = analyze_study_capacity(learner_id)
    schedule = generate_study_schedule(
        learner_id,
        readiness.get("hours_remaining", 10)
    )
    state["work_capacity"] = capacity
    state["work_schedule"] = schedule

    prompt = f"""You are a Study Plan Generator agent. Your role is to convert certification requirements into practical, capacity-aware study schedules.

READINESS ASSESSMENT (Fabric IQ):
- Readiness Level: {readiness.get('readiness_level')}
- Readiness Score: {readiness.get('readiness_score')}/100
- Hours Studied: {readiness.get('hours_studied')}
- Hours Remaining: {readiness.get('hours_remaining')}
- Practice Score: {readiness.get('practice_score')}%
- Recommendation: {readiness.get('recommendation')}

WORK CAPACITY (Work IQ):
- Capacity Level: {capacity.get('capacity_level')}
- Current Workload: {capacity.get('current_workload')}
- Available Study Hours/Week: {schedule.get('weekly_study_hours')}
- Best Study Windows: {schedule.get('recommended_windows')}
- Estimated Weeks to Ready: {schedule.get('estimated_weeks_to_ready')}

LEARNING PATH:
{safe_truncate(state.get('learning_path', ''), 600)}

Generate a practical, capacity-aware study plan. Respond in this exact format:

READINESS LEVEL: [{readiness.get('readiness_level')}]

WEEKLY SCHEDULE:
[Day-by-day or session-by-session breakdown based on available hours]

MILESTONE PLAN:
[Week-by-week milestones toward exam readiness]

STUDY TECHNIQUES:
[Specific techniques suited to this learner's capacity and learning style]

PRACTICE ASSESSMENT SCHEDULE:
[When to take practice tests and target scores]

ESTIMATED EXAM DATE:
[Based on current pace and capacity]
"""

    result = invoke_llm(prompt)
    entry = build_evidence_entry(
        "study_plan_generator",
        "certification study schedule capacity workload",
        f"Readiness: {readiness.get('readiness_level')} | Capacity: {capacity.get('capacity_level')}",
        result
    )
    report_progress(state["session_id"], "Study plan generated", 2)

    return {
        **state,
        "study_plan": result,
        "fabric_readiness": readiness,
        "work_capacity": capacity,
        "work_schedule": schedule,
        "parsed_study_plan": {
            "readiness_level": readiness.get("readiness_level"),
            "readiness_score": readiness.get("readiness_score"),
            "hours_remaining": readiness.get("hours_remaining"),
            "weekly_hours": schedule.get("weekly_study_hours"),
            "estimated_weeks": schedule.get("estimated_weeks_to_ready"),
            "sessions_per_week": schedule.get("sessions_per_week"),
            "session_length_minutes": schedule.get("session_length_minutes"),
            "pace": schedule.get("pace"),
            "raw_output": result
        },
        "evidence_trail": state.get("evidence_trail", []) + [entry]
    }


# --- Agent 3: Engagement Agent ---
def engagement_agent(state: CertAgentState) -> CertAgentState:
    print("Cert Agent 3: Engagement Agent...")
    report_progress(state["session_id"], "Planning engagement strategy", 3)

    profile = state["learner_profile"]
    learner_id = state["learner_id"]
    capacity = state.get("work_capacity", {})
    schedule = state.get("work_schedule", {})

    prompt = f"""You are an Engagement Agent. Your role is to keep learners on track using work context signals.

LEARNER: {profile.get('name')} ({profile.get('role')})
STUDY STREAK: {profile.get('study_streak_days', 0)} days

WORK IQ SIGNALS:
- Capacity Level: {capacity.get('capacity_level')}
- Current Workload: {capacity.get('current_workload')}
- Best Study Windows: {schedule.get('recommended_windows', [])}
- Engagement Approach: {schedule.get('engagement_approach')}
- Risk Flag: {capacity.get('risk_flag', 'None')}
- Upcoming Deadlines: {capacity.get('upcoming_deadlines', 0)}
- Pace Required: {schedule.get('pace')}

STUDY PLAN SUMMARY:
{safe_truncate(state.get('study_plan', ''), 400)}

Design a personalised engagement strategy that adapts to this learner's work rhythm.

Respond in this exact format:

ENGAGEMENT APPROACH: [approach name]

REMINDER STRATEGY:
[When and how to send study reminders based on work patterns]

MOTIVATION TACTICS:
[Specific tactics suited to this learner's situation]

RISK MITIGATION:
[How to keep learner on track given their specific risk factors]

WEEKLY CHECK-IN PLAN:
[How progress will be monitored without disrupting work]

ADAPTATION TRIGGERS:
[What signals should trigger a schedule adjustment]
"""

    result = invoke_llm(prompt)
    entry = build_evidence_entry(
        "engagement_agent",
        "work patterns study reminders engagement timing",
        f"Workload: {capacity.get('current_workload')} | Windows: {schedule.get('recommended_windows')}",
        result
    )
    report_progress(state["session_id"], "Engagement strategy planned", 3)

    return {
        **state,
        "engagement_plan": result,
        "parsed_engagement": {
            "capacity_level": capacity.get("capacity_level"),
            "engagement_approach": schedule.get("engagement_approach"),
            "best_windows": schedule.get("recommended_windows", []),
            "risk_flag": capacity.get("risk_flag"),
            "study_streak": profile.get("study_streak_days", 0),
            "raw_output": result
        },
        "evidence_trail": state.get("evidence_trail", []) + [entry]
    }


# --- Agent 4: Assessment Agent ---
def assessment_agent(state: CertAgentState) -> CertAgentState:
    print("Cert Agent 4: Assessment Agent...")
    report_progress(state["session_id"], "Evaluating certification readiness", 4)

    profile = state["learner_profile"]
    cert_id = state["target_certification"]
    readiness = state.get("fabric_readiness", {})
    skill_gaps = state.get("fabric_skill_gaps", {})

    # Foundry IQ — retrieve grounded assessment content
    query = f"{cert_id} practice questions assessment criteria pass requirements exam topics"
    context = retrieve_context(
        query=query,
        session_id=state["session_id"],
        doc_type="certification",
        top=5
    )
    context = safe_truncate(context, 1000)

    prompt = f"""You are an Assessment Agent. Your role is to evaluate certification readiness and generate grounded practice questions.

LEARNER: {profile.get('name')} ({profile.get('role')})
TARGET: {cert_id}

READINESS DATA (Fabric IQ):
- Readiness Level: {readiness.get('readiness_level')}
- Readiness Score: {readiness.get('readiness_score')}/100
- Practice Score Average: {profile.get('practice_score_avg')}%
- Pass Threshold: {readiness.get('pass_threshold')}%

SKILL GAPS (Fabric IQ):
- Missing: {skill_gaps.get('skill_gaps', [])}
- Matched: {skill_gaps.get('matched_skills', [])}

GROUNDED KNOWLEDGE (Foundry IQ):
{context}

Generate a readiness assessment with grounded practice questions. Cite sources from the knowledge base.

Respond in this exact format:

READINESS VERDICT: [Ready / Nearly Ready / Needs Preparation / Not Ready]

READINESS SCORE: [{readiness.get('readiness_score')}/100]

GROUNDED PRACTICE QUESTIONS:
[3-5 questions grounded in the knowledge base above, with citations]

WEAK AREAS:
[Specific topics needing more attention, grounded in evidence]

STRONG AREAS:
[Topics where learner shows strength]

EXAM READINESS RECOMMENDATION:
[Clear go/no-go recommendation with reasoning]

NEXT ASSESSMENT:
[When to reassess and what score to target]
"""

    result = invoke_llm(prompt)
    entry = build_evidence_entry("assessment_agent", query, context, result)
    report_progress(state["session_id"], "Assessment complete", 4)

    return {
        **state,
        "assessment_result": result,
        "parsed_assessment": {
            "readiness_verdict": readiness.get("readiness_level"),
            "readiness_score": readiness.get("readiness_score"),
            "practice_score": profile.get("practice_score_avg"),
            "pass_threshold": readiness.get("pass_threshold"),
            "skill_gaps": skill_gaps.get("skill_gaps", []),
            "matched_skills": skill_gaps.get("matched_skills", []),
            "raw_output": result
        },
        "evidence_trail": state.get("evidence_trail", []) + [entry]
    }


# --- Agent 5: Manager Insights Agent ---
def manager_insights_agent(state: CertAgentState) -> CertAgentState:
    print("Cert Agent 5: Manager Insights Agent...")
    report_progress(state["session_id"], "Generating manager insights", 5)

    profile = state["learner_profile"]
    readiness = state.get("fabric_readiness", {})
    capacity = state.get("work_capacity", {})
    schedule = state.get("work_schedule", {})

    prompt = f"""You are a Manager Insights Agent. Your role is to surface team-level visibility without exposing sensitive personal details.

TEAM MEMBER: {profile.get('name')} — {profile.get('role')} ({profile.get('department')})
TARGET CERTIFICATION: {state.get('target_certification')}

READINESS SUMMARY (Fabric IQ):
- Status: {readiness.get('readiness_level')}
- Score: {readiness.get('readiness_score')}/100
- Hours Progress: {readiness.get('hours_studied')}/{readiness.get('recommended_hours')} hours

CAPACITY SUMMARY (Work IQ):
- Workload: {capacity.get('current_workload')}
- Available Hours/Week: {schedule.get('weekly_study_hours')}
- Estimated Completion: {schedule.get('estimated_weeks_to_ready')} weeks
- Risk Flag: {capacity.get('risk_flag', 'None')}

STUDY PLAN SUMMARY:
{safe_truncate(state.get('study_plan', ''), 300)}

ENGAGEMENT PLAN SUMMARY:
{safe_truncate(state.get('engagement_plan', ''), 300)}

Generate manager-level insights that help with team planning without exposing personal data.

Respond in this exact format:

TEAM MEMBER STATUS: [On Track / Needs Attention / At Risk]

READINESS SUMMARY:
[High-level progress update suitable for a manager dashboard]

CAPACITY CONCERNS:
[Workload or scheduling issues that need manager awareness]

RECOMMENDED MANAGER ACTIONS:
[Specific actions the manager should take to support this team member]

TIMELINE RISK:
[Will this person meet the team certification deadline? Why?]

TEAM PLANNING NOTE:
[How this individual's progress affects overall team readiness]
"""

    result = invoke_llm(prompt)
    entry = build_evidence_entry(
        "manager_insights_agent",
        "team readiness certification progress manager visibility",
        f"Status: {readiness.get('readiness_level')} | Workload: {capacity.get('current_workload')}",
        result
    )
    report_progress(state["session_id"], "Manager insights complete", 5)

    return {
        **state,
        "manager_insights": result,
        "parsed_manager_insights": {
            "team_member": profile.get("name"),
            "role": profile.get("role"),
            "department": profile.get("department"),
            "certification": state.get("target_certification"),
            "readiness_level": readiness.get("readiness_level"),
            "readiness_score": readiness.get("readiness_score"),
            "workload": capacity.get("current_workload"),
            "weeks_to_ready": schedule.get("estimated_weeks_to_ready"),
            "risk_flag": capacity.get("risk_flag"),
            "raw_output": result
        },
        "evidence_trail": state.get("evidence_trail", []) + [entry]
    }


# --- Build the Graph ---
def build_certification_agent():
    graph = StateGraph(CertAgentState)

    graph.add_node("learning_path_curator", learning_path_curator)
    graph.add_node("study_plan_generator", study_plan_generator)
    graph.add_node("engagement_agent", engagement_agent)
    graph.add_node("assessment_agent", assessment_agent)
    graph.add_node("manager_insights_agent", manager_insights_agent)

    graph.set_entry_point("learning_path_curator")
    graph.add_edge("learning_path_curator", "study_plan_generator")
    graph.add_edge("study_plan_generator", "engagement_agent")
    graph.add_edge("engagement_agent", "assessment_agent")
    graph.add_edge("assessment_agent", "manager_insights_agent")
    graph.add_edge("manager_insights_agent", END)

    return graph.compile()


certification_agent = build_certification_agent()
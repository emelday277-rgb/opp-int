# import os
# from typing import TypedDict
# from langgraph.graph import StateGraph, END
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# from service.foundry_iq import retrieve_context
# from models.analysis import (
#     OpportunitySummary, OrganizationSummary,
#     FitEvaluation, RiskAssessment,
#     Recommendation, ActionPlan
# )
# from service.parser import parse_to_structured
# from service.retry import with_retry
# import sys
# import os


# load_dotenv()
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# try:
#     from main import update_session_step
# except ImportError:
#     def update_session_step(session_id, step_name, steps_completed):
#         pass  # graceful fallback when running standalone

# # Initialize the LLM

# llm = ChatOpenAI(
#     base_url=f"{os.getenv('AZURE_FOUNDRY_ENDPOINT').rstrip('/')}/openai/v1/",
#     api_key=os.getenv("AZURE_FOUNDRY_API_KEY"),
#     model=os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4.1-mini"),
#     temperature=0.3
# )

# @with_retry(max_attempts=3, delay=2.0, backoff=2.0)
# def invoke_llm(prompt: str) -> str:
#     response = llm.invoke(prompt)
#     return response.content#

# # --- State Definition ---
# class AgentState(TypedDict):
#     session_id: str
#     opportunity_summary: str
#     organization_summary: str
#     fit_evaluation: str
#     risk_assessment: str
#     recommendation: str
#     action_plan: str
#     evidence: dict
#     # Parsed structured outputs
#     parsed_opportunity: dict
#     parsed_organization: dict
#     parsed_fit: dict
#     parsed_risks: dict
#     parsed_recommendation: dict
#     parsed_action_plan: dict
#     evidence_trail: list

# def build_evidence_entry(step: str, query: str, context: str, conclusion: str) -> dict:
#     """Creates a traceable evidence entry for a reasoning step."""
#     return {
#         "step": step,
#         "query_used": query,
#         "evidence_retrieved": context[:500] + "..." if len(context) > 500 else context,
#         "conclusion_summary": conclusion[:300] + "..." if len(conclusion) > 300 else conclusion
#     }

# # --- Step 1: Understand the Opportunity ---
# def understand_opportunity(state: AgentState) -> AgentState:
#     print("Step 1: Understanding the opportunity...")

#     context = retrieve_context(
#         query="opportunity purpose requirements deadlines eligibility evaluation criteria",
#         session_id=state["session_id"],
#         doc_type="opportunity"
#     )


#     prompt = f"""You are an expert opportunity analyst.

# Based on the following opportunity document excerpts, provide a structured summary.

# DOCUMENT EXCERPTS:
# {context}

# Provide your analysis in this exact format:

# PURPOSE:
# [What is this opportunity about? What problem does it solve or what does it fund?]

# REQUIREMENTS:
# [List the key requirements an applicant must meet]

# DEADLINES:
# [Any important dates and deadlines mentioned]

# EVALUATION CRITERIA:
# [How will applications be judged or evaluated?]

# SUBMISSION EXPECTATIONS:
# [What must be submitted? What format or documents are required?]

# Be specific and use only information found in the document excerpts above.
# """

#     response = invoke_llm(prompt)
#     summary = invoke_llm(prompt)
#     parsed = parse_to_structured(summary, OpportunitySummary)

#     entry = build_evidence_entry(
#         step="opportunity_understanding",
#         query="opportunity purpose requirements deadlines eligibility evaluation criteria",
#         context=context,
#         conclusion=summary
#     )
#     update_session_step(state["session_id"], "Opportunity understanding complete", 1)
#     return {
#         **state,
#         "opportunity_summary": summary,
#         "parsed_opportunity": parsed,
#         "evidence_trail": state.get("evidence_trail", []) + [entry],
#         "evidence": {
#             **state.get("evidence", {}),
#             "opportunity_context": context
#         }
#     }


# # --- Step 2: Understand the Organization ---
# def understand_organization(state: AgentState) -> AgentState:
#     print("Step 2: Understanding the organization...")

#     context = retrieve_context(
#         query="organization capabilities experience certifications past projects strengths",
#         session_id=state["session_id"],
#         doc_type="organization"
#     )

#     prompt = f"""You are an expert organizational analyst.

# Based on the following organizational documents, provide a structured summary.

# DOCUMENT EXCERPTS:
# {context}

# Provide your analysis in this exact format:

# CORE CAPABILITIES:
# [What does this organization do well? What are their main skills?]

# RELEVANT EXPERIENCE:
# [What past projects or work is relevant to opportunities they might pursue?]

# CERTIFICATIONS AND CREDENTIALS:
# [Any certifications, awards, or formal credentials mentioned]

# TEAM AND RESOURCES:
# [Information about team size, expertise, or available resources]

# ORGANIZATIONAL STRENGTHS:
# [Key strengths that would make them competitive]

# Be specific and use only information found in the document excerpts above.
# """

#     response = invoke_llm(prompt)
#     summary = invoke_llm(prompt)
#     parsed = parse_to_structured(summary, OrganizationSummary)

#     entry = build_evidence_entry(
#         step="organization_understanding",
#         query="organization capabilities experience certifications past projects strengths",
#         context=context,
#         conclusion=summary
#     )
#     update_session_step(state["session_id"], "Organization understanding complete", 2)
#     return {
#         **state,
#         "organization_summary": summary,
#         "parsed_organization": parsed,
#         "evidence_trail": state.get("evidence_trail", []) + [entry],
#         "evidence": {
#             **state.get("evidence", {}),
#             "organization_context": context
#         }
#     }


# # --- Step 3: Evaluate Fit ---
# def evaluate_fit(state: AgentState) -> AgentState:
#     print("Step 3: Evaluating fit...")

#     # Pull additional targeted context
#     opp_context = retrieve_context(
#         query="eligibility requirements qualifications mandatory criteria",
#         session_id=state["session_id"],
#         doc_type="opportunity",
#         top=3
#     )

#     org_context = retrieve_context(
#         query="qualifications experience proof evidence past work",
#         session_id=state["session_id"],
#         doc_type="organization",
#         top=3
#     )

#     prompt = f"""You are an expert at evaluating whether organizations are a good fit for opportunities.

# OPPORTUNITY SUMMARY:
# {state["opportunity_summary"]}

# ORGANIZATION SUMMARY:
# {state["organization_summary"]}

# ADDITIONAL OPPORTUNITY DETAILS:
# {opp_context}

# ADDITIONAL ORGANIZATION DETAILS:
# {org_context}

# Evaluate the fit between this organization and this opportunity.

# Provide your evaluation in this exact format:

# OVERALL FIT SCORE: [X/10]

# STRONG MATCHES:
# [Areas where the organization clearly meets or exceeds requirements - cite specific evidence]

# PARTIAL MATCHES:
# [Areas where the organization partially meets requirements but has some gaps]

# GAPS:
# [Requirements the organization does not appear to meet based on available information]

# ELIGIBILITY VERDICT:
# [Based on available information, is this organization likely eligible? Yes / Likely / Uncertain / Unlikely]

# EVIDENCE SUMMARY:
# [Key pieces of evidence that informed this evaluation]
# """

#     response = invoke_llm(prompt)
#     evaluation = response.content
#     parsed = parse_to_structured(evaluation, FitEvaluation)

#     entry = build_evidence_entry(
#         step="fit_evaluation",
#         query="eligibility requirements qualifications mandatory criteria",
#         context=opp_context,
#         conclusion=evaluation
#     )
#     update_session_step(state["session_id"], "Fit evaluation complete", 3)
#     return {
#         **state,
#         "fit_evaluation": evaluation,
#         "parsed_fit": parsed,
#         "evidence_trail": state.get("evidence_trail", []) + [entry],
#         "evidence": {
#             **state.get("evidence", {}),
#             "fit_opp_context": opp_context,
#             "fit_org_context": org_context
#         }
#     }


# # --- Step 4: Assess Risks ---
# def assess_risks(state: AgentState) -> AgentState:
#     print("Step 4: Assessing risks...")

#     context = retrieve_context(
#         query="compliance requirements documentation deadline restrictions limitations",
#         session_id=state["session_id"],
#         top=5
#     )

#     prompt = f"""You are an expert risk analyst specializing in opportunity evaluation.

# OPPORTUNITY SUMMARY:
# {state["opportunity_summary"]}

# ORGANIZATION SUMMARY:
# {state["organization_summary"]}

# FIT EVALUATION:
# {state["fit_evaluation"]}

# ADDITIONAL CONTEXT:
# {context}

# Identify risks that could reduce the likelihood of success if this organization pursues this opportunity.

# Provide your assessment in this exact format:

# HIGH RISKS:
# [Risks that could disqualify the application or severely impact success - explain each]

# MEDIUM RISKS:
# [Risks that could weaken the application but are manageable - explain each]

# LOW RISKS:
# [Minor concerns worth monitoring - explain each]

# MITIGATION SUGGESTIONS:
# [For each high and medium risk, suggest a practical mitigation action]

# OVERALL RISK LEVEL: [Low / Medium / High]
# """

#     response = invoke_llm(prompt)
#     risks = response.content
#     parsed = parse_to_structured(risks, RiskAssessment)
#     entry = build_evidence_entry(
#         step="risk_assessment",
#         query="compliance requirements documentation deadline restrictions limitations",
#         context=context,
#         conclusion=risks
#     )
#     update_session_step(state["session_id"], "Risk assessment complete", 4)
#     return {
#         **state,
#         "risk_assessment": risks,
#         "parsed_risks": parsed,
#         "evidence_trail": state.get("evidence_trail", []) + [entry],
#         "evidence": {
#             **state.get("evidence", {}),
#             "risk_context": context
#         },
#     }


# # --- Step 5: Generate Recommendation ---
# def generate_recommendation(state: AgentState) -> AgentState:
#     print("Step 5: Generating recommendation...")

#     prompt = f"""You are a senior opportunity strategist helping an organization decide whether to pursue an opportunity.

# OPPORTUNITY SUMMARY:
# {state["opportunity_summary"]}

# ORGANIZATION SUMMARY:
# {state["organization_summary"]}

# FIT EVALUATION:
# {state["fit_evaluation"]}

# RISK ASSESSMENT:
# {state["risk_assessment"]}

# Based on all the above analysis, provide a clear recommendation.

# Provide your recommendation in this exact format:

# RECOMMENDATION: [PURSUE / PURSUE WITH CAUTION / DO NOT PURSUE]

# CONFIDENCE LEVEL: [High / Medium / Low]

# REASONS TO PURSUE:
# [Strong arguments for going ahead - grounded in the evidence above]

# REASONS FOR CAUTION:
# [Important concerns or conditions that must be addressed]

# KEY CONDITIONS:
# [What must be true or done before committing to this opportunity]

# STRATEGIC SUMMARY:
# [2-3 sentence plain-language summary a non-technical decision maker can understand]
# """

#     response = invoke_llm(prompt)
#     recommendation = response.content
#     parsed = parse_to_structured(recommendation, Recommendation)

#     update_session_step(state["session_id"], "Recommendation complete", 5)
#     return {
#         **state,
#         "recommendation": recommendation,
#         "parsed_recommendation": parsed
#     }


# # --- Step 6: Create Action Plan ---
# def create_action_plan(state: AgentState) -> AgentState:
#     print("Step 6: Creating action plan...")

#     context = retrieve_context(
#         query="submission deadline required documents application process next steps",
#         session_id=state["session_id"],
#         doc_type="opportunity",
#         top=3
#     )

#     prompt = f"""You are an expert at creating practical action plans for opportunity applications.

# OPPORTUNITY SUMMARY:
# {state["opportunity_summary"]}

# RECOMMENDATION:
# {state["recommendation"]}

# RISK ASSESSMENT:
# {state["risk_assessment"]}

# SUBMISSION DETAILS:
# {context}

# Create a practical action plan for pursuing this opportunity.

# Provide your plan in this exact format:

# IMMEDIATE ACTIONS (Next 48 hours):
# [3-5 specific actions to take right away]

# SHORT-TERM ACTIONS (This week):
# [3-5 actions to complete within the week]

# DOCUMENTS TO PREPARE:
# [List every document that needs to be gathered or created]

# PREPARATION CHECKLIST:
# [A checklist of everything needed before submission]

# SUBMISSION CHECKLIST:
# [A checklist of everything to verify before hitting submit]

# RECOMMENDED PRIORITIES:
# [The 3 most important things to focus on to maximize success]
# """

#     response = invoke_llm(prompt)
#     action_plan = response.content
#     parsed = parse_to_structured(action_plan, ActionPlan)

#     entry = build_evidence_entry(
#         step="action_plan_creation",
#         query="submission deadline required documents application process next steps",
#         context=context,
#         conclusion=action_plan
#     )
#     update_session_step(state["session_id"], "Action plan complete", 6)
#     return {
#         **state,
#         "action_plan": action_plan,
#         "parsed_action_plan": parsed,
#         "evidence_trail": state.get("evidence_trail", []) + [entry]
#     }


# # --- Build the Graph ---
# def build_agent():
#     graph = StateGraph(AgentState)

#     graph.add_node("understand_opportunity", understand_opportunity)
#     graph.add_node("understand_organization", understand_organization)
#     graph.add_node("evaluate_fit", evaluate_fit)
#     graph.add_node("assess_risks", assess_risks)
#     graph.add_node("generate_recommendation", generate_recommendation)
#     graph.add_node("create_action_plan", create_action_plan)

#     graph.set_entry_point("understand_opportunity")
#     graph.add_edge("understand_opportunity", "understand_organization")
#     graph.add_edge("understand_organization", "evaluate_fit")
#     graph.add_edge("evaluate_fit", "assess_risks")
#     graph.add_edge("assess_risks", "generate_recommendation")
#     graph.add_edge("generate_recommendation", "create_action_plan")
#     graph.add_edge("create_action_plan", END)

#     return graph.compile()


# # Export
# opportunity_agent = build_agent()

import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from service.foundry_iq import retrieve_context
from service.retry import with_retry
from models.analysis import (
    OpportunitySummary, OrganizationSummary,
    FitEvaluation, RiskAssessment,
    Recommendation, ActionPlan
)
from service.parser import parse_to_structured

load_dotenv()

llm = ChatOpenAI(
    base_url=f"{os.getenv('AZURE_FOUNDRY_ENDPOINT').rstrip('/')}/openai/v1/",
    api_key=os.getenv("AZURE_FOUNDRY_API_KEY"),
    model=os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4.1-mini"),
    temperature=0.3
)

# Session progress store — shared with main.py
session_progress = {}


def report_progress(session_id: str, step_name: str, steps_completed: int):
    """Update progress for a session — read by the status endpoint."""
    if session_id in session_progress:
        session_progress[session_id]["current_step"] = step_name
        session_progress[session_id]["reasoning_steps_completed"] = steps_completed


@with_retry(max_attempts=3, delay=2.0, backoff=2.0)
def invoke_llm(prompt: str, max_tokens: int = 1500) -> str:
    """Invoke LLM with retry — always returns a plain string."""
    response = llm.invoke(
        prompt,
        config={"max_tokens": max_tokens}
    )
    return response.content

def safe_truncate(text: str, max_chars: int = 1000) -> str:
    """Prevents prompts from getting too long and causing timeouts."""
    if len(text) > max_chars:
        return text[:max_chars] + "\n[truncated for length]"
    return text

def build_evidence_entry(step: str, query: str, context: str, conclusion: str) -> dict:
    return {
        "step": step,
        "query_used": query,
        "evidence_retrieved": context[:500] + "..." if len(context) > 500 else context,
        "conclusion_summary": conclusion[:300] + "..." if len(conclusion) > 300 else conclusion
    }


class AgentState(TypedDict):
    session_id: str
    opportunity_summary: str
    organization_summary: str
    fit_evaluation: str
    risk_assessment: str
    recommendation: str
    action_plan: str
    evidence: dict
    evidence_trail: list
    parsed_opportunity: dict
    parsed_organization: dict
    parsed_fit: dict
    parsed_risks: dict
    parsed_recommendation: dict
    parsed_action_plan: dict


def understand_opportunity(state: AgentState) -> AgentState:
    print("Step 1: Understanding the opportunity...")
    query = "opportunity purpose requirements deadlines eligibility evaluation criteria"
    context = retrieve_context(query=query, session_id=state["session_id"], doc_type="opportunity")
    context = safe_truncate(context, 1500)
    prompt = f"""You are an expert opportunity analyst.

Based on the following opportunity document excerpts, provide a structured summary.

DOCUMENT EXCERPTS:
{context}

Provide your analysis in this exact format:

PURPOSE:
[What is this opportunity about?]

REQUIREMENTS:
[List the key requirements]

DEADLINES:
[Important dates and deadlines]

EVALUATION CRITERIA:
[How applications will be judged]

SUBMISSION EXPECTATIONS:
[What must be submitted]

Be specific and use only information found in the excerpts above.
"""
    summary = invoke_llm(prompt)
    parsed = parse_to_structured(summary, OpportunitySummary)
    entry = build_evidence_entry("opportunity_understanding", query, context, summary)
    report_progress(state["session_id"], "Opportunity understanding complete", 1)

    return {
        **state,
        "opportunity_summary": summary,
        "parsed_opportunity": parsed,
        "evidence_trail": state.get("evidence_trail", []) + [entry],
        "evidence": {**state.get("evidence", {}), "opportunity_context": context}
    }


def understand_organization(state: AgentState) -> AgentState:
    print("Step 2: Understanding the organization...")
    query = "organization capabilities experience certifications past projects strengths"
    context = retrieve_context(query=query, session_id=state["session_id"], doc_type="organization")
    context = safe_truncate(context, 1500)
    prompt = f"""You are an expert organizational analyst.

Based on the following organizational documents, provide a structured summary.

DOCUMENT EXCERPTS:
{context}

Provide your analysis in this exact format:

CORE CAPABILITIES:
[What does this organization do well?]

RELEVANT EXPERIENCE:
[Past projects or work]

CERTIFICATIONS AND CREDENTIALS:
[Certifications, awards, credentials]

TEAM AND RESOURCES:
[Team size, expertise, resources]

ORGANIZATIONAL STRENGTHS:
[Key competitive strengths]

Be specific and use only information found in the excerpts above.
"""
    summary = invoke_llm(prompt)
    parsed = parse_to_structured(summary, OrganizationSummary)
    entry = build_evidence_entry("organization_understanding", query, context, summary)
    report_progress(state["session_id"], "Organization understanding complete", 2)

    return {
        **state,
        "organization_summary": summary,
        "parsed_organization": parsed,
        "evidence_trail": state.get("evidence_trail", []) + [entry],
        "evidence": {**state.get("evidence", {}), "organization_context": context}
    }


# def evaluate_fit(state: AgentState) -> AgentState:
#     print("Step 3: Evaluating fit...")
#     query = "eligibility requirements qualifications mandatory criteria"
#     opp_context = retrieve_context(query=query, session_id=state["session_id"], doc_type="opportunity", top=3)
#     org_context = retrieve_context(query="qualifications experience proof evidence past work", session_id=state["session_id"], doc_type="organization", top=3)

#     prompt = f"""You are an expert at evaluating whether organizations are a good fit for opportunities.

# OPPORTUNITY SUMMARY:
# {state["opportunity_summary"]}

# ORGANIZATION SUMMARY:
# {state["organization_summary"]}

# ADDITIONAL OPPORTUNITY DETAILS:
# {opp_context}

# ADDITIONAL ORGANIZATION DETAILS:
# {org_context}

# Evaluate the fit between this organization and this opportunity.

# Provide your evaluation in this exact format:

# OVERALL FIT SCORE: [X/10]

# STRONG MATCHES:
# [Areas where the organization clearly meets requirements - cite specific evidence]

# PARTIAL MATCHES:
# [Areas where the organization partially meets requirements]

# GAPS:
# [Requirements the organization does not appear to meet]

# ELIGIBILITY VERDICT:
# [Yes / Likely / Uncertain / Unlikely]

# EVIDENCE SUMMARY:
# [Key evidence that informed this evaluation]
# """
#     evaluation = invoke_llm(prompt)
#     parsed = parse_to_structured(evaluation, FitEvaluation)
#     entry = build_evidence_entry("fit_evaluation", query, opp_context + org_context, evaluation)
#     report_progress(state["session_id"], "Fit evaluation complete", 3)

#     return {
#         **state,
#         "fit_evaluation": evaluation,
#         "parsed_fit": parsed,
#         "evidence_trail": state.get("evidence_trail", []) + [entry],
#         "evidence": {**state.get("evidence", {}), "fit_context": opp_context}
#     }

def evaluate_fit(state: AgentState) -> AgentState:
    print("Step 3: Evaluating fit...")
    query = "eligibility requirements qualifications mandatory criteria"

    opp_context = retrieve_context(
        query=query,
        session_id=state["session_id"],
        doc_type="opportunity",
        top=3
    )
    org_context = retrieve_context(
        query="qualifications experience proof evidence past work",
        session_id=state["session_id"],
        doc_type="organization",
        top=3
    )
    opp_summary = safe_truncate(state["opportunity_summary"], 800)
    # Keep prompt focused and shorter to avoid timeouts
    prompt = f"""You are an expert at evaluating whether organizations fit opportunities.

OPPORTUNITY REQUIREMENTS (from document):
{opp_summary}

ORGANIZATION PROFILE (from document):
{safe_truncate(state["organization_summary"], 800)}

Evaluate the fit. Use this exact format:

OVERALL FIT SCORE: [X/10]

STRONG MATCHES:
- [area]: [evidence from documents]

PARTIAL MATCHES:
- [area]: [evidence from documents]

GAPS:
- [area]: [what is missing]

ELIGIBILITY VERDICT: [Yes / Likely / Uncertain / Unlikely]

EVIDENCE SUMMARY:
[2-3 sentences summarizing key evidence]
"""
    evaluation = invoke_llm(prompt)
    parsed = parse_to_structured(evaluation, FitEvaluation)
    entry = build_evidence_entry("fit_evaluation", query, opp_context + org_context, evaluation)
    report_progress(state["session_id"], "Fit evaluation complete", 3)

    return {
        **state,
        "fit_evaluation": evaluation,
        "parsed_fit": parsed,
        "evidence_trail": state.get("evidence_trail", []) + [entry],
        "evidence": {**state.get("evidence", {}), "fit_context": opp_context}
    }

def assess_risks(state: AgentState) -> AgentState:
    print("Step 4: Assessing risks...")
    query = "compliance requirements documentation deadline restrictions limitations"
    context = retrieve_context(query=query, session_id=state["session_id"], top=5)
    context = safe_truncate(context, 1500)
    prompt = f"""You are an expert risk analyst specializing in opportunity evaluation.

OPPORTUNITY SUMMARY:
{safe_truncate(state["opportunity_summary"], 800)}

ORGANIZATION SUMMARY:
{safe_truncate(state["organization_summary"], 800)}

FIT EVALUATION:
{state["fit_evaluation"]}

ADDITIONAL CONTEXT:
{context}

Identify risks that could reduce the likelihood of success.

Provide your assessment in this exact format:

HIGH RISKS:
[Risks that could disqualify or severely impact success]

MEDIUM RISKS:
[Risks that are manageable but significant]

LOW RISKS:
[Minor concerns worth monitoring]

MITIGATION SUGGESTIONS:
[For each high and medium risk, suggest a practical mitigation]

OVERALL RISK LEVEL: [Low / Medium / High]
"""
    risks = invoke_llm(prompt)
    parsed = parse_to_structured(risks, RiskAssessment)
    entry = build_evidence_entry("risk_assessment", query, context, risks)
    report_progress(state["session_id"], "Risk assessment complete", 4)

    return {
        **state,
        "risk_assessment": risks,
        "parsed_risks": parsed,
        "evidence_trail": state.get("evidence_trail", []) + [entry],
        "evidence": {**state.get("evidence", {}), "risk_context": context}
    }


def generate_recommendation(state: AgentState) -> AgentState:
    print("Step 5: Generating recommendation...")

    prompt = f"""You are a senior opportunity strategist.

OPPORTUNITY SUMMARY:
{safe_truncate(state["opportunity_summary"], 800)}

ORGANIZATION SUMMARY:
{safe_truncate(state["organization_summary"], 800)}

FIT EVALUATION:
{state["fit_evaluation"]}

RISK ASSESSMENT:
{state["risk_assessment"]}

Provide a clear recommendation.

Provide your recommendation in this exact format:

RECOMMENDATION: [PURSUE / PURSUE WITH CAUTION / DO NOT PURSUE]

CONFIDENCE LEVEL: [High / Medium / Low]

REASONS TO PURSUE:
[Strong arguments for going ahead]

REASONS FOR CAUTION:
[Important concerns]

KEY CONDITIONS:
[What must be true before committing]

STRATEGIC SUMMARY:
[2-3 sentence plain-language summary]
"""
    recommendation = invoke_llm(prompt)
    parsed = parse_to_structured(recommendation, Recommendation)
    entry = build_evidence_entry("recommendation", "full analysis synthesis", "", recommendation)
    report_progress(state["session_id"], "Recommendation complete", 5)

    return {
        **state,
        "recommendation": recommendation,
        "parsed_recommendation": parsed,
        "evidence_trail": state.get("evidence_trail", []) + [entry],
    }


def create_action_plan(state: AgentState) -> AgentState:
    print("Step 6: Creating action plan...")
    query = "submission deadline required documents application process next steps"
    context = retrieve_context(query=query, session_id=state["session_id"], doc_type="opportunity", top=3)
    context = safe_truncate(context, 1500)
    prompt = f"""You are an expert at creating practical action plans for opportunity applications.

OPPORTUNITY SUMMARY:
{safe_truncate(state["opportunity_summary"], 800)}

RECOMMENDATION:
{safe_truncate(state["recommendation"], 800)}

RISK ASSESSMENT:
{safe_truncate(state["risk_assessment"], 800)}

SUBMISSION DETAILS:
{context}

Create a practical action plan.

Provide your plan in this exact format:

IMMEDIATE ACTIONS (Next 48 hours):
[3-5 specific actions to take right away]

SHORT-TERM ACTIONS (This week):
[3-5 actions to complete this week]

DOCUMENTS TO PREPARE:
[Every document that needs to be gathered or created]

PREPARATION CHECKLIST:
[Everything needed before submission]

SUBMISSION CHECKLIST:
[Everything to verify before submitting]

RECOMMENDED PRIORITIES:
[The 3 most important things to focus on]
"""
    action_plan = invoke_llm(prompt)
    parsed = parse_to_structured(action_plan, ActionPlan)
    entry = build_evidence_entry("action_planning", query, context, action_plan)
    report_progress(state["session_id"], "Action plan complete", 6)

    return {
        **state,
        "action_plan": action_plan,
        "parsed_action_plan": parsed,
        "evidence_trail": state.get("evidence_trail", []) + [entry],
    }


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("understand_opportunity", understand_opportunity)
    graph.add_node("understand_organization", understand_organization)
    graph.add_node("evaluate_fit", evaluate_fit)
    graph.add_node("assess_risks", assess_risks)
    graph.add_node("generate_recommendation", generate_recommendation)
    graph.add_node("create_action_plan", create_action_plan)
    graph.set_entry_point("understand_opportunity")
    graph.add_edge("understand_opportunity", "understand_organization")
    graph.add_edge("understand_organization", "evaluate_fit")
    graph.add_edge("evaluate_fit", "assess_risks")
    graph.add_edge("assess_risks", "generate_recommendation")
    graph.add_edge("generate_recommendation", "create_action_plan")
    graph.add_edge("create_action_plan", END)
    return graph.compile()


opportunity_agent = build_agent()
from pydantic import BaseModel, Field
from typing import Optional


# --- Step 1: Opportunity Summary ---
class OpportunitySummary(BaseModel):
    purpose: str = Field(description="What this opportunity is about")
    requirements: list[str] = Field(description="Key requirements an applicant must meet")
    deadlines: list[str] = Field(description="Important dates and deadlines")
    evaluation_criteria: list[str] = Field(description="How applications will be judged")
    submission_expectations: list[str] = Field(description="What must be submitted")


# --- Step 2: Organization Summary ---
class OrganizationSummary(BaseModel):
    core_capabilities: list[str] = Field(description="What the organization does well")
    relevant_experience: list[str] = Field(description="Relevant past projects or work")
    certifications: list[str] = Field(description="Certifications and credentials")
    team_and_resources: str = Field(description="Team size, expertise, available resources")
    organizational_strengths: list[str] = Field(description="Key competitive strengths")


# --- Step 3: Fit Evaluation ---
class FitMatch(BaseModel):
    area: str = Field(description="The requirement or area being evaluated")
    evidence: str = Field(description="Specific evidence supporting this assessment")


class FitEvaluation(BaseModel):
    fit_score: int = Field(description="Overall fit score from 1 to 10", ge=1, le=10)
    strong_matches: list[FitMatch] = Field(description="Areas where org clearly meets requirements")
    partial_matches: list[FitMatch] = Field(description="Areas where org partially meets requirements")
    gaps: list[FitMatch] = Field(description="Requirements the org does not meet")
    eligibility_verdict: str = Field(description="Yes / Likely / Uncertain / Unlikely")
    evidence_summary: str = Field(description="Key evidence informing this evaluation")


# --- Step 4: Risk Assessment ---
class Risk(BaseModel):
    description: str = Field(description="Description of the risk")
    mitigation: Optional[str] = Field(description="Suggested mitigation action", default=None)


class RiskAssessment(BaseModel):
    overall_risk_level: str = Field(description="Low / Medium / High")
    high_risks: list[Risk] = Field(description="Risks that could disqualify or severely impact")
    medium_risks: list[Risk] = Field(description="Risks that are manageable but significant")
    low_risks: list[Risk] = Field(description="Minor concerns worth monitoring")


# --- Step 5: Recommendation ---
class Recommendation(BaseModel):
    decision: str = Field(description="PURSUE / PURSUE WITH CAUTION / DO NOT PURSUE")
    confidence_level: str = Field(description="High / Medium / Low")
    reasons_to_pursue: list[str] = Field(description="Strong arguments for going ahead")
    reasons_for_caution: list[str] = Field(description="Important concerns to address")
    key_conditions: list[str] = Field(description="What must be true before committing")
    strategic_summary: str = Field(description="Plain language summary for decision makers")


# --- Step 6: Action Plan ---
class ActionPlan(BaseModel):
    immediate_actions: list[str] = Field(description="Actions to take in next 48 hours")
    short_term_actions: list[str] = Field(description="Actions to complete this week")
    documents_to_prepare: list[str] = Field(description="Documents to gather or create")
    preparation_checklist: list[str] = Field(description="Everything needed before submission")
    submission_checklist: list[str] = Field(description="Everything to verify before submitting")
    recommended_priorities: list[str] = Field(description="Top 3 things to focus on")


# --- Full Analysis Result ---
class AnalysisResult(BaseModel):
    session_id: str
    status: str
    opportunity_summary: OpportunitySummary
    organization_summary: OrganizationSummary
    fit_evaluation: FitEvaluation
    risk_assessment: RiskAssessment
    recommendation: Recommendation
    action_plan: ActionPlan

# --- Certification Module Models ---

class LearningPath(BaseModel):
    certification_id: str
    certification_name: str
    skill_gaps: list[str]
    matched_skills: list[str]
    match_percentage: float
    required_skills: list[str]
    role_alignment: list[str]
    raw_output: str


class StudyPlan(BaseModel):
    readiness_level: str
    readiness_score: int
    hours_remaining: float
    weekly_hours: float
    estimated_weeks: float
    sessions_per_week: int
    session_length_minutes: int
    pace: str
    raw_output: str


class EngagementPlan(BaseModel):
    capacity_level: str
    engagement_approach: str
    best_windows: list[str]
    risk_flag: Optional[str]
    study_streak: int
    raw_output: str


class AssessmentResult(BaseModel):
    readiness_verdict: str
    readiness_score: int
    practice_score: float
    pass_threshold: int
    skill_gaps: list[str]
    matched_skills: list[str]
    raw_output: str


class ManagerInsights(BaseModel):
    team_member: str
    role: str
    department: str
    certification: str
    readiness_level: str
    readiness_score: int
    workload: str
    weeks_to_ready: float
    risk_flag: Optional[str]
    raw_output: str


class CertificationAnalysisResult(BaseModel):
    session_id: str
    status: str
    learner_id: str
    target_certification: str
    fabric_readiness: dict
    fabric_skill_gaps: dict
    work_capacity: dict
    work_schedule: dict
    learning_path: LearningPath
    study_plan: StudyPlan
    engagement_plan: EngagementPlan
    assessment_result: AssessmentResult
    manager_insights: ManagerInsights
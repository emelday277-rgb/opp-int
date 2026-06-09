import json
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_certifications() -> dict:
    """Load the certification semantic model."""
    with open(os.path.join(DATA_DIR, "certifications.json"), "r") as f:
        return json.load(f)


def get_certification(cert_id: str) -> dict:
    """Get a specific certification by ID."""
    data = load_certifications()
    for cert in data["certifications"]:
        if cert["id"] == cert_id:
            return cert
    return {}


def get_role_certifications(role: str) -> list:
    """Get recommended certifications for a role."""
    data = load_certifications()
    role_map = data.get("role_certification_map", {})
    cert_ids = role_map.get(role, role_map.get("All Roles", []))
    certs = []
    for cert_id in cert_ids:
        cert = get_certification(cert_id)
        if cert:
            certs.append(cert)
    return certs


def evaluate_readiness_score(
    practice_score: float,
    hours_studied: float,
    cert_id: str
) -> dict:
    """
    Use Fabric IQ semantic thresholds to evaluate certification readiness.
    Returns a structured readiness assessment.
    """
    data = load_certifications()
    cert = get_certification(cert_id)
    thresholds = data.get("readiness_thresholds", {})

    if not cert:
        return {"error": f"Certification {cert_id} not found"}

    recommended_hours = cert.get("recommended_hours", 20)
    pass_threshold = cert.get("pass_threshold", 70)
    hours_pct = (hours_studied / recommended_hours) * 100

    # Semantic readiness calculation
    if practice_score >= thresholds.get("ready", 80) and hours_pct >= 90:
        readiness_level = "Ready"
        readiness_score = min(100, int(practice_score * 0.6 + hours_pct * 0.4))
        recommendation = "Proceed to schedule the exam"
    elif practice_score >= thresholds.get("nearly_ready", 65) and hours_pct >= 70:
        readiness_level = "Nearly Ready"
        readiness_score = int(practice_score * 0.6 + hours_pct * 0.4)
        recommendation = "1-2 more weeks of focused study recommended"
    elif practice_score >= thresholds.get("needs_preparation", 50) or hours_pct >= 50:
        readiness_level = "Needs Preparation"
        readiness_score = int(practice_score * 0.5 + hours_pct * 0.5)
        recommendation = "Structured study plan required before attempting exam"
    else:
        readiness_level = "Not Ready"
        readiness_score = int(practice_score * 0.5 + hours_pct * 0.5)
        recommendation = "Foundational gaps identified — start from beginning"

    hours_remaining = max(0, recommended_hours - hours_studied)

    return {
        "certification_id": cert_id,
        "certification_name": cert.get("name", ""),
        "readiness_level": readiness_level,
        "readiness_score": readiness_score,
        "practice_score": practice_score,
        "hours_studied": hours_studied,
        "recommended_hours": recommended_hours,
        "hours_remaining": hours_remaining,
        "hours_completion_pct": round(hours_pct, 1),
        "pass_threshold": pass_threshold,
        "recommendation": recommendation,
        "required_skills": cert.get("skills", []),
        "source": "Fabric IQ Semantic Layer"
    }


def get_skill_gaps(learner_skills: list, cert_id: str) -> dict:
    """
    Compare learner skills against certification requirements.
    Returns identified gaps and matched skills.
    """
    cert = get_certification(cert_id)
    if not cert:
        return {}

    required_skills = [s.lower() for s in cert.get("skills", [])]
    learner_skills_lower = [s.lower() for s in learner_skills]

    matched = []
    gaps = []

    for skill in cert.get("skills", []):
        skill_lower = skill.lower()
        is_matched = any(
            skill_lower in ls or ls in skill_lower
            for ls in learner_skills_lower
        )
        if is_matched:
            matched.append(skill)
        else:
            gaps.append(skill)

    match_pct = (len(matched) / len(required_skills) * 100) if required_skills else 0

    return {
        "certification_id": cert_id,
        "matched_skills": matched,
        "skill_gaps": gaps,
        "match_percentage": round(match_pct, 1),
        "total_required": len(required_skills),
        "source": "Fabric IQ Semantic Layer"
    }


def get_team_readiness_summary(learner_assessments: list) -> dict:
    """
    Aggregate individual readiness scores into team-level insights.
    """
    if not learner_assessments:
        return {}

    total = len(learner_assessments)
    ready_count = sum(1 for a in learner_assessments if a.get("readiness_level") == "Ready")
    nearly_ready = sum(1 for a in learner_assessments if a.get("readiness_level") == "Nearly Ready")
    needs_prep = sum(1 for a in learner_assessments if a.get("readiness_level") == "Needs Preparation")
    not_ready = sum(1 for a in learner_assessments if a.get("readiness_level") == "Not Ready")
    avg_score = sum(a.get("readiness_score", 0) for a in learner_assessments) / total

    if avg_score >= 80:
        team_status = "On Track"
    elif avg_score >= 60:
        team_status = "Needs Attention"
    else:
        team_status = "At Risk"

    return {
        "total_learners": total,
        "ready": ready_count,
        "nearly_ready": nearly_ready,
        "needs_preparation": needs_prep,
        "not_ready": not_ready,
        "average_readiness_score": round(avg_score, 1),
        "team_status": team_status,
        "completion_rate_pct": round((ready_count / total) * 100, 1),
        "at_risk_count": not_ready + needs_prep,
        "source": "Fabric IQ Semantic Layer"
    }
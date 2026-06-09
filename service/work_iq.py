import json
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_work_signals() -> dict:
    """Load work signals data."""
    with open(os.path.join(DATA_DIR, "work_signals.json"), "r") as f:
        return json.load(f)


def get_employee_signals(employee_id: str) -> dict:
    """Get work signals for a specific employee."""
    data = load_work_signals()
    for signal in data.get("work_signals", []):
        if signal["employee_id"] == employee_id:
            return signal
    return {}


def get_team_signals(team_id: str) -> dict:
    """Get aggregated work signals for a team."""
    data = load_work_signals()
    for signal in data.get("team_signals", []):
        if signal["team_id"] == team_id:
            return signal
    return {}


def analyze_study_capacity(employee_id: str) -> dict:
    """
    Use Work IQ signals to analyze a learner's capacity for study.
    Returns structured capacity assessment and recommendations.
    """
    signals = get_employee_signals(employee_id)
    if not signals:
        return {
            "employee_id": employee_id,
            "capacity_level": "Unknown",
            "available_hours_per_week": 5,
            "recommended_session_length": 60,
            "best_study_times": ["Morning"],
            "source": "Work IQ — default values (no signals found)"
        }

    meeting_hours = signals.get("meeting_hours_per_week", 0)
    focus_hours = signals.get("focus_hours_per_week", 0)
    workload = signals.get("current_workload", "Medium")
    available_hours = signals.get("available_study_hours_per_week", 5)
    preferred_slot = signals.get("preferred_learning_slot", "Morning")
    peak_hours = signals.get("peak_productivity_hours", [])
    upcoming_deadlines = signals.get("upcoming_deadlines", 0)

    # Capacity scoring based on work signals
    if workload == "Very High" or meeting_hours > 25:
        capacity_level = "Low"
        recommended_session = 30
        weekly_target = min(available_hours, 3)
        engagement_approach = "Micro-learning — short daily bursts"
        risk_flag = "High meeting load significantly impacts study time"
    elif workload == "High" or meeting_hours > 18:
        capacity_level = "Medium-Low"
        recommended_session = 45
        weekly_target = min(available_hours, 4)
        engagement_approach = "Focused sessions during peak hours only"
        risk_flag = "Monitor for burnout — schedule study carefully"
    elif workload == "Medium":
        capacity_level = "Medium"
        recommended_session = 60
        weekly_target = min(available_hours, 6)
        engagement_approach = "Consistent daily sessions recommended"
        risk_flag = None
    else:
        capacity_level = "High"
        recommended_session = 90
        weekly_target = min(available_hours, 10)
        engagement_approach = "Intensive study schedule — good conditions for fast progress"
        risk_flag = None

    # Adjust for upcoming deadlines
    if upcoming_deadlines >= 3:
        weekly_target = max(2, weekly_target - 2)
        risk_flag = risk_flag or "Upcoming deadlines may interrupt study schedule"

    # Study window recommendations
    study_windows = []
    if preferred_slot == "Morning":
        study_windows.append("Early morning (07:00-09:00) before meetings")
    elif preferred_slot == "Afternoon":
        study_windows.append("Post-lunch focus block (13:00-15:00)")
    elif preferred_slot == "Evening":
        study_windows.append("Evening wind-down study (18:00-20:00)")

    if peak_hours:
        study_windows.append(f"Peak productivity window: {', '.join(peak_hours)}")

    return {
        "employee_id": employee_id,
        "capacity_level": capacity_level,
        "current_workload": workload,
        "meeting_hours_per_week": meeting_hours,
        "focus_hours_per_week": focus_hours,
        "available_study_hours_per_week": weekly_target,
        "recommended_session_length_minutes": recommended_session,
        "best_study_windows": study_windows,
        "engagement_approach": engagement_approach,
        "risk_flag": risk_flag,
        "upcoming_deadlines": upcoming_deadlines,
        "source": "Work IQ Intelligence Layer"
    }


def generate_study_schedule(
    employee_id: str,
    hours_remaining: float,
    target_date: str = None
) -> dict:
    """
    Generate a personalised study schedule based on Work IQ signals.
    """
    capacity = analyze_study_capacity(employee_id)
    weekly_hours = capacity.get("available_study_hours_per_week", 4)
    session_length = capacity.get("recommended_session_length_minutes", 60)
    study_windows = capacity.get("best_study_windows", ["Morning"])

    if weekly_hours <= 0:
        weeks_needed = 99
    else:
        weeks_needed = round(hours_remaining / weekly_hours, 1)

    sessions_per_week = round((weekly_hours * 60) / session_length)
    sessions_per_week = max(1, sessions_per_week)

    if weeks_needed <= 2:
        urgency = "Low"
        pace = "Comfortable"
    elif weeks_needed <= 4:
        urgency = "Medium"
        pace = "Steady"
    elif weeks_needed <= 8:
        urgency = "Medium-High"
        pace = "Focused"
    else:
        urgency = "High"
        pace = "Intensive"

    return {
        "employee_id": employee_id,
        "hours_remaining": hours_remaining,
        "weekly_study_hours": weekly_hours,
        "estimated_weeks_to_ready": weeks_needed,
        "sessions_per_week": sessions_per_week,
        "session_length_minutes": session_length,
        "recommended_windows": study_windows,
        "pace": pace,
        "urgency": urgency,
        "capacity_level": capacity.get("capacity_level"),
        "engagement_approach": capacity.get("engagement_approach"),
        "risk_flag": capacity.get("risk_flag"),
        "source": "Work IQ Intelligence Layer"
    }


def get_team_capacity_summary(team_id: str, learner_ids: list) -> dict:
    """
    Summarize team-level capacity and study recommendations.
    """
    team_signals = get_team_signals(team_id)
    individual_capacities = []

    for lid in learner_ids:
        cap = analyze_study_capacity(lid)
        individual_capacities.append(cap)

    capacity_levels = [c.get("capacity_level", "Unknown") for c in individual_capacities]
    low_capacity = sum(1 for c in capacity_levels if "Low" in c)
    high_capacity = sum(1 for c in capacity_levels if "High" in c)

    at_risk = [
        c["employee_id"] for c in individual_capacities
        if c.get("risk_flag") is not None
    ]

    return {
        "team_id": team_id,
        "total_members": len(learner_ids),
        "low_capacity_count": low_capacity,
        "high_capacity_count": high_capacity,
        "at_risk_members": at_risk,
        "team_sprint_active": team_signals.get("sprint_active", False),
        "recommended_team_windows": team_signals.get("recommended_study_windows", []),
        "team_capacity": team_signals.get("team_capacity", "Unknown"),
        "individual_summaries": individual_capacities,
        "source": "Work IQ Intelligence Layer"
    }
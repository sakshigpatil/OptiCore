import re
from typing import List, Dict, Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _normalize_skill(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9+#\s-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _skills_to_text(skills: List[str]) -> str:
    return " ".join(_normalize_skill(s) for s in (skills or []))


def _tfidf_cosine(a: str, b: str) -> float:
    vec = TfidfVectorizer()
    X = vec.fit_transform([a, b])
    sim = cosine_similarity(X[0:1], X[1:2])[0][0]
    return float(sim)


def analyze_employee_skill(
    employee: Dict[str, Any], role_requirements: Dict[str, List[str]] | List[str], role_name: str | None = None
) -> Dict[str, Any]:
    """Compare an employee's skills with role requirements.

    Args:
        employee: dict with keys `name`, `role`, `skills` (list).
        role_requirements: either a list of required skills for the role,
            or a dict mapping role name -> list of skills.
        role_name: optional role name to look up in `role_requirements` when it's a dict.

    Returns:
        A dict with matched skills, missing skills, and match scores.
    """

    emp_name = employee.get("name", "Unknown")
    emp_role = employee.get("role", role_name)
    emp_skills = employee.get("skills", []) or []

    if isinstance(role_requirements, dict):
        lookup_role = role_name or emp_role
        required_skills = role_requirements.get(lookup_role, [])
    else:
        required_skills = role_requirements or []

    emp_norm_set = { _normalize_skill(s) for s in emp_skills }
    req_norm_list = [ _normalize_skill(s) for s in required_skills ]

    matched = [r for r, rn in zip(required_skills, req_norm_list) if rn in emp_norm_set]
    missing = [r for r, rn in zip(required_skills, req_norm_list) if rn not in emp_norm_set]

    tfidf_score = _tfidf_cosine(_skills_to_text(emp_skills), _skills_to_text(required_skills))

    skill_match_percent = round((len(matched) / max(len(required_skills), 1)) * 100, 1)
    tfidf_percent = round(tfidf_score * 100, 1)

    return {
        "employee": emp_name,
        "role": emp_role,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_percent": skill_match_percent,
        "tfidf_match_percent": tfidf_percent,
        "tfidf_score": tfidf_score,
    }


if __name__ == "__main__":
    # Quick demo
    role_reqs = {
        "Backend Developer": [
            "Python",
            "Django",
            "REST APIs",
            "Docker",
            "Kubernetes",
            "PostgreSQL",
            "Celery",
        ]
    }

    emp = {"name": "Rahul", "role": "Backend Developer", "skills": ["Python", "Django", "REST APIs", "PostgreSQL", "Celery"]}

    res = analyze_employee_skill(emp, role_reqs)
    print(f"Employee: {res['employee']}")
    print(f"Role: {res['role']}")
    print(f"Match Score: {res['tfidf_match_percent']}%")
    print("Missing Skills:", ", ".join(res['missing_skills']) if res['missing_skills'] else "None")

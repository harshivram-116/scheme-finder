"""Rule-based eligibility engine.

Design rule: CODE decides eligibility, the LLM only explains it later.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "schemes.json"


@dataclass
class Profile:
    age: int
    gender: str                      # "male" | "female" | "other"
    annual_income: int               # rupees per year
    is_bpl: bool = False
    owns_agri_land: bool = False
    is_student: bool = False
    district: Optional[str] = None


def load_schemes(path: Path = DATA_FILE) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_scheme(profile: Profile, scheme: dict) -> tuple[bool, list[str]]:
    """Return (eligible, reasons_failed). Empty reasons means eligible."""
    rules = scheme.get("rules", {})
    fails: list[str] = []

    if "min_age" in rules and profile.age < rules["min_age"]:
        fails.append(f"Minimum age is {rules['min_age']}")
    if "max_age" in rules and profile.age > rules["max_age"]:
        fails.append(f"Maximum age is {rules['max_age']}")
    if "max_income" in rules and profile.annual_income > rules["max_income"]:
        fails.append(f"Annual income must be at most Rs {rules['max_income']}")
    if "genders" in rules and profile.gender.lower() not in rules["genders"]:
        fails.append(f"Only for: {', '.join(rules['genders'])}")
    if rules.get("requires_bpl") and not profile.is_bpl:
        fails.append("Requires a BPL household")
    if rules.get("requires_agri_land") and not profile.owns_agri_land:
        fails.append("Requires agricultural land ownership")
    if rules.get("requires_student") and not profile.is_student:
        fails.append("Only for students")

    return (len(fails) == 0, fails)


def check_eligibility(profile: Profile, schemes: Optional[list[dict]] = None) -> dict:
    """Split all schemes into eligible and not eligible (with reasons)."""
    schemes = schemes if schemes is not None else load_schemes()
    eligible, not_eligible = [], []
    for s in schemes:
        ok, reasons = check_scheme(profile, s)
        if ok:
            eligible.append(s)
        else:
            not_eligible.append({"scheme": s["name"], "reasons": reasons})
    return {"eligible": eligible, "not_eligible": not_eligible}

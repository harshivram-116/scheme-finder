"""Rule-based eligibility engine.

Design rule: CODE decides eligibility, the LLM only explains it later.
Every reason is produced in English and Tamil.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "schemes.json"
GENDER_TA = {"male": "ஆண்", "female": "பெண்", "other": "மற்றவர்"}


@dataclass
class Profile:
    age: int
    gender: str                      # "male" | "female" | "other"
    annual_income: int               # rupees per year
    is_bpl: bool = False
    owns_agri_land: bool = False
    is_student: bool = False
    district: Optional[str] = None
    # PM-KISAN style exclusions (asked only when the person owns land)
    family_excluded_category: bool = False   # tax payer, govt employee, MP/MLA, professional...
    land_after_cutoff: bool = False          # bought/received land after 1 Feb 2019 (not inheritance)


def load_schemes(path: Path = DATA_FILE) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _failures(profile: Profile, scheme: dict) -> list[tuple[str, str]]:
    """Return a list of (english_reason, tamil_reason). Empty list means eligible."""
    rules = scheme.get("rules", {})
    f: list[tuple[str, str]] = []

    if "min_age" in rules and profile.age < rules["min_age"]:
        n = rules["min_age"]
        f.append((f"Minimum age is {n}", f"குறைந்தபட்ச வயது {n}"))
    if "max_age" in rules and profile.age > rules["max_age"]:
        n = rules["max_age"]
        f.append((f"Maximum age is {n}", f"அதிகபட்ச வயது {n}"))
    if "max_income" in rules and profile.annual_income > rules["max_income"]:
        n = rules["max_income"]
        f.append((f"Annual income must be at most Rs {n}",
                  f"ஆண்டு வருமானம் அதிகபட்சம் ₹{n} ஆக இருக்க வேண்டும்"))
    if "genders" in rules and profile.gender.lower() not in rules["genders"]:
        en = ", ".join(rules["genders"])
        ta = ", ".join(GENDER_TA.get(g, g) for g in rules["genders"])
        f.append((f"Only for: {en}", f"இவர்களுக்கு மட்டும்: {ta}"))
    if rules.get("requires_bpl") and not profile.is_bpl:
        f.append(("Requires a BPL household",
                  "BPL (வறுமைக் கோட்டுக்குக் கீழ்) குடும்பமாக இருக்க வேண்டும்"))
    if rules.get("requires_agri_land") and not profile.owns_agri_land:
        f.append(("Requires cultivable land in your own name (tenant farmers are not covered)",
                  "உங்கள் சொந்தப் பெயரில் விவசாய நிலம் இருக்க வேண்டும் (குத்தகை விவசாயிகளுக்குப் பொருந்தாது)"))
    if rules.get("requires_student") and not profile.is_student:
        f.append(("Only for students", "மாணவர்களுக்கு மட்டும்"))

    # Data-driven exclusions: {"profile_field": "reason" or {"en": "...", "ta": "..."}}
    for field, reason in rules.get("excluded_if", {}).items():
        if getattr(profile, field, False):
            if isinstance(reason, dict):
                f.append((reason["en"], reason.get("ta", reason["en"])))
            else:
                f.append((reason, reason))
    return f


def check_scheme(profile: Profile, scheme: dict) -> tuple[bool, list[str]]:
    """Return (eligible, english_reasons_failed). Empty reasons means eligible."""
    fails = _failures(profile, scheme)
    return (len(fails) == 0, [en for en, _ in fails])


def check_eligibility(profile: Profile, schemes: Optional[list[dict]] = None) -> dict:
    """Split all schemes into eligible and not eligible (with reasons in both languages)."""
    schemes = schemes if schemes is not None else load_schemes()
    eligible, not_eligible = [], []
    for s in schemes:
        fails = _failures(profile, s)
        if not fails:
            eligible.append(s)
        else:
            not_eligible.append({
                "scheme": s["name"],
                "scheme_ta": s.get("name_ta", s["name"]),
                "reasons": [en for en, _ in fails],
                "reasons_ta": [ta for _, ta in fails],
            })
    return {"eligible": eligible, "not_eligible": not_eligible}

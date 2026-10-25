from app.eligibility import Profile, check_eligibility


def names(result):
    return {s["id"] for s in result["eligible"]}


def test_senior_bpl_gets_pension():
    p = Profile(age=65, gender="male", annual_income=40000, is_bpl=True)
    assert "old_age_pension" in names(check_eligibility(p))


def test_young_person_not_pension():
    p = Profile(age=30, gender="male", annual_income=40000, is_bpl=True)
    assert "old_age_pension" not in names(check_eligibility(p))


def test_farmer_gets_pm_kisan():
    p = Profile(age=45, gender="male", annual_income=100000, owns_agri_land=True)
    assert "pm_kisan" in names(check_eligibility(p))


def test_woman_bpl_gets_ujjwala():
    p = Profile(age=35, gender="female", annual_income=60000, is_bpl=True)
    assert "ujjwala" in names(check_eligibility(p))


def test_high_income_loses_income_capped_schemes():
    p = Profile(age=40, gender="female", annual_income=900000)
    assert "magalir_urimai" not in names(check_eligibility(p))


def test_not_eligible_includes_reasons():
    p = Profile(age=30, gender="male", annual_income=40000)
    result = check_eligibility(p)
    assert all(item["reasons"] for item in result["not_eligible"])


def test_farmer_with_excluded_family_member_loses_pm_kisan():
    p = Profile(age=45, gender="male", annual_income=100000, owns_agri_land=True,
                family_excluded_category=True)
    result = check_eligibility(p)
    assert "pm_kisan" not in names(result)
    reasons = [r for item in result["not_eligible"] if "PM-KISAN" in item["scheme"] for r in item["reasons"]]
    assert any("excluded category" in r for r in reasons)


def test_land_bought_after_cutoff_loses_pm_kisan():
    p = Profile(age=45, gender="male", annual_income=100000, owns_agri_land=True,
                land_after_cutoff=True)
    assert "pm_kisan" not in names(check_eligibility(p))


def test_no_land_means_not_pm_kisan_even_without_flags():
    p = Profile(age=45, gender="male", annual_income=100000, owns_agri_land=False)
    assert "pm_kisan" not in names(check_eligibility(p))


def _has_tamil(text):
    return any("\u0b80" <= ch <= "\u0bff" for ch in text)


def test_every_scheme_has_complete_tamil_fields():
    from app.eligibility import load_schemes
    for s in load_schemes():
        for key in ("name_ta", "benefit_ta", "apply_at_ta"):
            assert s.get(key) and _has_tamil(s[key]), (s["id"], key)
        assert len(s["documents_ta"]) == len(s["documents"]), s["id"]
        assert all(_has_tamil(d) for d in s["documents_ta"]), s["id"]


def test_every_reason_has_a_tamil_twin():
    # worst-case profile: fails as many rules as possible, including PM-KISAN exclusions
    p = Profile(age=10, gender="male", annual_income=9999999)
    result = check_eligibility(p)
    p2 = Profile(age=10, gender="male", annual_income=9999999, owns_agri_land=True,
                 family_excluded_category=True, land_after_cutoff=True)
    for res in (result, check_eligibility(p2)):
        for item in res["not_eligible"]:
            assert len(item["reasons_ta"]) == len(item["reasons"]) > 0
            assert all(_has_tamil(r) for r in item["reasons_ta"]), item
            assert _has_tamil(item["scheme_ta"])

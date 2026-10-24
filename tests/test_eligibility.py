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

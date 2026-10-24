# Scheme Finder

Voice-first government scheme finder (Tamil + English).
Week 1: dataset + rule-based eligibility engine.

## Run
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    pytest
    uvicorn app.main:app --reload   # then open /docs

## Important
All scheme data in data/schemes.json is a PLACEHOLDER (verified: false).
Verify every rule against the official source before trusting it.

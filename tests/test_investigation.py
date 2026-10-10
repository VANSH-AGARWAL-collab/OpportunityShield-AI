"""
Tests for Investigation Engine & Heuristic Rule Calculations
"""

import pytest
from services.investigation_engine import InvestigationEngine


@pytest.fixture
def engine():
    return InvestigationEngine()


def test_investigation_high_risk_scam(engine):
    extracted = {
        "company_name": "Apex Tech Solutions",
        "domain": "apextech-careers-india.online",
        "role_title": "Remote Data Entry Trainee",
        "has_free_email": True,
        "email_domains": ["gmail.com"],
        "emails": ["hr.apex@gmail.com"],
        "has_telegram": True,
        "telegram_handles": ["@apex_hr_team"],
        "has_whatsapp": False,
        "compensation": {"is_suspicious_compensation": True, "reason": "High wage for data entry"},
        "red_flag_triggers": [{
            "label": "Security Deposit demanded",
            "severity": "critical",
            "context_snippet": "₹2,500 refundable security deposit required"
        }],
        "brand_spoof_alert": None,
    }

    search_results = {
        "evidence_items": [
            {
                "title": "Apex Tech Solutions Scam Complaint",
                "snippet": "Fake company asking for laptop deposit on Telegram",
                "link": "https://consumercomplaints.in/c123",
                "domain": "consumercomplaints.in",
                "engine": "Google Search",
                "stance": "contradicts",
            }
        ],
        "comparable_jobs": [],
        "has_knowledge_graph": False,
        "knowledge_graph": {},
        "is_demo_mode": True,
    }

    report = engine.analyze(extracted, search_results)

    assessment = report["assessment"]
    assert assessment["risk_score"] >= 65
    assert assessment["label"] == "Elevated concern"
    assert len(report["warning_signals"]) >= 3
    assert len(assessment["factors"]) >= 3


def test_investigation_legitimate_startup(engine):
    extracted = {
        "company_name": "Hasura",
        "domain": "hasura.io",
        "role_title": "Software Engineering Intern",
        "has_free_email": False,
        "email_domains": ["hasura.io"],
        "emails": ["talent@hasura.io"],
        "has_telegram": False,
        "has_whatsapp": False,
        "compensation": {"is_suspicious_compensation": False},
        "red_flag_triggers": [],
        "brand_spoof_alert": None,
    }

    search_results = {
        "evidence_items": [
            {
                "title": "Hasura Official Website",
                "snippet": "Instant GraphQL APIs on databases",
                "link": "https://hasura.io",
                "domain": "hasura.io",
                "engine": "Google Search",
                "stance": "supports",
            },
            {
                "title": "TechCrunch: Hasura Launches DDN",
                "snippet": "Hasura expands its data delivery network",
                "link": "https://techcrunch.com/article",
                "domain": "techcrunch.com",
                "engine": "Google News",
                "stance": "supports",
            }
        ],
        "comparable_jobs": [
            {
                "title": "Software Engineer Intern",
                "company_name": "Hasura",
                "is_target_company": True,
                "via": "via LinkedIn",
            }
        ],
        "has_knowledge_graph": True,
        "knowledge_graph": {"title": "Hasura", "type": "Software Company"},
        "is_demo_mode": False,
    }

    report = engine.analyze(extracted, search_results)

    assessment = report["assessment"]
    assert assessment["risk_score"] <= 35
    assert assessment["label"] == "Low observed concern"
    assert len(report["positive_signals"]) >= 2


def test_investigation_insufficient_evidence_unconfigured_search(engine):
    """
    Priority 1 & 3:
    When live search is unconfigured / offline and no explicit payment red flags
    exist in the prompt text, the engine must return 'Insufficient public evidence'.
    """
    extracted = {
        "company_name": "New Local Studio",
        "domain": "newlocalstudio.com",
        "role_title": "Frontend Intern",
        "has_free_email": False,
        "email_domains": ["newlocalstudio.com"],
        "emails": ["contact@newlocalstudio.com"],
        "has_telegram": False,
        "has_whatsapp": False,
        "compensation": {"is_suspicious_compensation": False},
        "red_flag_triggers": [],
        "brand_spoof_alert": None,
    }

    search_results = {
        "evidence_items": [],
        "comparable_jobs": [],
        "has_knowledge_graph": False,
        "knowledge_graph": {},
        "total_sources_retrieved": 0,
        "is_demo_mode": False,
        "is_benchmark_demonstration": False,
        "search_status": "unconfigured_key",
        "search_error": "SerpApi API key is not configured in server environment.",
    }

    report = engine.analyze(extracted, search_results)
    assessment = report["assessment"]

    assert assessment["status_code"] == "insufficient_evidence"
    assert "Insufficient public evidence" in assessment["label"]
    assert report["metadata"]["search_status"] == "unconfigured_key"
    assert "Live search evidence could not be retrieved" in assessment["summary"]


def test_investigation_zero_search_results_insufficient_evidence(engine):
    """
    When live search returns zero results for a company without red flags,
    it must return 'Insufficient public evidence' with an explicit disclaimer
    that absent online footprint is common for new startups and NOT proof of fraud.
    """
    extracted = {
        "company_name": "Obscure New Enterprise",
        "domain": "",
        "role_title": "Trainee",
        "has_free_email": False,
        "email_domains": [],
        "emails": [],
        "has_telegram": False,
        "has_whatsapp": False,
        "compensation": {"is_suspicious_compensation": False},
        "red_flag_triggers": [],
        "brand_spoof_alert": None,
    }

    search_results = {
        "evidence_items": [],
        "comparable_jobs": [],
        "has_knowledge_graph": False,
        "knowledge_graph": {},
        "total_sources_retrieved": 0,
        "is_demo_mode": False,
        "is_benchmark_demonstration": False,
        "search_status": "success",
    }

    report = engine.analyze(extracted, search_results)
    assessment = report["assessment"]

    assert assessment["status_code"] == "insufficient_evidence"
    assert "NOT proof of fraud" in assessment["summary"]


def test_investigation_positive_signals_qualified_not_guarantee(engine):
    """
    Priority 3:
    Knowledge Panel, domain match, and Google Jobs presence must be qualified
    as corporate entity presence, NOT conclusive proof that an individual recruiter is genuine.
    """
    extracted = {
        "company_name": "Hasura",
        "domain": "hasura.io",
        "role_title": "Software Engineering Intern",
        "has_free_email": False,
        "email_domains": ["hasura.io"],
        "emails": ["recruiter@hasura.io"],
        "has_telegram": False,
        "has_whatsapp": False,
        "compensation": {"is_suspicious_compensation": False},
        "red_flag_triggers": [],
        "brand_spoof_alert": None,
    }

    search_results = {
        "evidence_items": [
            {
                "title": "Hasura Official Website",
                "snippet": "Instant GraphQL APIs on databases",
                "link": "https://hasura.io",
                "domain": "hasura.io",
                "engine": "Google Search",
                "stance": "supports",
            }
        ],
        "comparable_jobs": [
            {
                "title": "Software Engineer Intern",
                "company_name": "Hasura",
                "is_target_company": True,
                "via": "via LinkedIn",
            }
        ],
        "has_knowledge_graph": True,
        "knowledge_graph": {"title": "Hasura", "type": "Software Company"},
        "is_demo_mode": False,
    }

    report = engine.analyze(extracted, search_results)

    # Check that factors include nature tags and caveats
    factors = report["assessment"]["factors"]
    for factor in factors:
        assert "nature" in factor
        if factor["rule_id"] == "POS_KNOWLEDGE_PANEL":
            assert "does not certify that the individual recruiter contacting you is an authorized representative" in factor["rationale"]
        if factor["rule_id"] == "POS_DOMAIN_MATCH":
            assert "verify that incoming emails originate from authentic SPF/DKIM mail servers" in factor["rationale"]


def test_investigation_search_failed_returns_insufficient_evidence(engine):
    """
    Issue 1:
    When live searches fail, the engine must return 'Insufficient public evidence'
    instead of falling back to a benchmark or escalating risk without red flags.
    """
    extracted = {
        "company_name": "Midsize Logistics Corp",
        "domain": "midsizelogistics.in",
        "role_title": "Operations Trainee",
        "has_free_email": False,
        "email_domains": ["midsizelogistics.in"],
        "emails": ["jobs@midsizelogistics.in"],
        "has_telegram": False,
        "has_whatsapp": False,
        "compensation": {"is_suspicious_compensation": False},
        "red_flag_triggers": [],
        "brand_spoof_alert": None,
    }

    search_results = {
        "evidence_items": [],
        "comparable_jobs": [],
        "has_knowledge_graph": False,
        "knowledge_graph": {},
        "total_sources_retrieved": 0,
        "is_demo_mode": False,
        "is_benchmark_demonstration": False,
        "search_status": "search_failed",
        "search_error": "Live SerpApi searches failed: Rate limit exceeded",
    }

    report = engine.analyze(extracted, search_results)
    assessment = report["assessment"]

    assert assessment["status_code"] == "insufficient_evidence"
    assert "Insufficient public evidence" in assessment["label"]
    assert report["metadata"]["search_status"] == "search_failed"
    assert "Live search evidence could not be retrieved" in assessment["summary"]


def test_investigation_does_not_certify_offer_authentic(engine):
    """
    Issue 3:
    Even with Knowledge Panel, official indexed domain, and matching recruiter email,
    the assessment must explicitly warn that corporate presence does NOT certify
    that the individual offer is genuine or recruiter is authorized.
    """
    extracted = {
        "company_name": "Hasura",
        "domain": "hasura.io",
        "role_title": "Software Engineering Intern",
        "has_free_email": False,
        "email_domains": ["hasura.io"],
        "emails": ["recruiter@hasura.io"],
        "has_telegram": False,
        "has_whatsapp": False,
        "compensation": {"is_suspicious_compensation": False},
        "red_flag_triggers": [],
        "brand_spoof_alert": None,
    }

    search_results = {
        "evidence_items": [
            {
                "title": "Hasura Official Website",
                "snippet": "Instant GraphQL APIs on databases",
                "link": "https://hasura.io",
                "domain": "hasura.io",
                "engine": "Google Search",
                "stance": "supports",
            }
        ],
        "comparable_jobs": [
            {
                "title": "Software Engineer Intern",
                "company_name": "Hasura",
                "is_target_company": True,
                "via": "via LinkedIn",
            }
        ],
        "has_knowledge_graph": True,
        "knowledge_graph": {"title": "Hasura", "type": "Software Company"},
        "is_demo_mode": False,
    }

    report = engine.analyze(extracted, search_results)
    summary = report["assessment"]["summary"]

    # Must explicitly state entity presence caveats
    assert "Confirms corporate entity presence; always verify individual recruiter identity" in summary




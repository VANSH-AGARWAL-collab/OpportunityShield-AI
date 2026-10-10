"""
Tests for Entity Extractor Service
"""

import pytest
from services.extractor_service import extract_entities, _clean_domain


def test_clean_domain():
    assert _clean_domain("https://www.example.com/path?arg=1") == "example.com"
    assert _clean_domain("sub.domain.co.in") == "sub.domain.co.in"
    assert _clean_domain("http://hasura.io") == "hasura.io"
    assert _clean_domain("") == ""


def test_extract_entities_advance_fee_scam():
    text = """
    Company: Apex Tech Solutions
    Role: Remote Python Trainee
    Stipend: ₹75,000 / month
    Contact: hr.apex@gmail.com
    Telegram: @apex_hr_team
    Website: http://apextech-careers.online

    Congratulations! A 100% refundable security deposit of ₹2,500 is required via UPI
    for laptop courier dispatch and document verification.
    """
    extracted = extract_entities(text)

    assert extracted["company_name"] == "Apex Tech Solutions"
    assert "apextech-careers.online" in extracted["domain"]
    assert extracted["has_free_email"] is True
    assert "@apex_hr_team" in extracted["telegram_handles"]
    assert extracted["has_telegram"] is True

    # Red flag triggers
    assert len(extracted["red_flag_triggers"]) >= 1
    trigger_labels = [t["label"] for t in extracted["red_flag_triggers"]]
    assert any("Security Deposit" in lbl for lbl in trigger_labels)


def test_extract_entities_brand_spoofing():
    text = """
    Tata Consultancy Services is hiring Cloud Interns.
    Please send your resume to recruiter@tcs-careers-onboarding.in.
    Visit https://tcs-careers-onboarding.in
    """
    extracted = extract_entities(text)
    assert extracted["brand_spoof_alert"] is not None
    assert extracted["brand_spoof_alert"]["is_spoof"] is True
    assert extracted["brand_spoof_alert"]["brand_claimed"] == "Tata Consultancy Services"


def test_extract_entities_legitimate_startup():
    text = """
    Company: Hasura
    Role: Software Engineering Intern
    Website: https://hasura.io
    Recruiter: hiring@hasura.io
    Stipend: ₹50,000 / month
    No registration fee or deposit is ever required.
    """
    extracted = extract_entities(text)

    assert extracted["company_name"] == "Hasura"
    assert extracted["domain"] == "hasura.io"
    assert extracted["has_free_email"] is False
    assert extracted["brand_spoof_alert"] is None


def test_dns_label_matching_exact_and_subdomain():
    from services.extractor_service import is_valid_dns_match, are_domains_dns_affiliated, is_recruiter_email_domain_affiliated

    # Exact matches
    assert is_valid_dns_match("tcs.com", "tcs.com") is True
    assert is_valid_dns_match("hasura.io", "hasura.io") is True

    # Legitimate subdomains
    assert is_valid_dns_match("careers.tcs.com", "tcs.com") is True
    assert is_valid_dns_match("mail.careers.tcs.com", "tcs.com") is True
    assert are_domains_dns_affiliated("tcs.com", "careers.tcs.com") is True
    assert are_domains_dns_affiliated("careers.tcs.com", "tcs.com") is True

    # Recruiter email domain affiliation
    assert is_recruiter_email_domain_affiliated("tcs.com", "tcs.com") is True
    assert is_recruiter_email_domain_affiliated("mail.tcs.com", "tcs.com") is True


def test_dns_label_matching_prevents_malicious_suffix_and_lookalikes():
    from services.extractor_service import is_valid_dns_match, are_domains_dns_affiliated, is_recruiter_email_domain_affiliated

    # Malicious suffix attacks (e.g. tcs.com.attacker.example) must NOT match tcs.com
    assert is_valid_dns_match("tcs.com.attacker.example", "tcs.com") is False
    assert is_valid_dns_match("tcs.com.evil.co.in", "tcs.com") is False
    assert are_domains_dns_affiliated("tcs.com.attacker.example", "tcs.com") is False
    assert are_domains_dns_affiliated("tcs.com", "tcs.com.attacker.example") is False
    assert is_recruiter_email_domain_affiliated("tcs.com.attacker.example", "tcs.com") is False

    # Lookalikes and hyphenated variations
    assert is_valid_dns_match("evil-tcs.com", "tcs.com") is False
    assert is_valid_dns_match("tcs-careers.in", "tcs.com") is False
    assert is_valid_dns_match("tcs.co", "tcs.com") is False
    assert is_recruiter_email_domain_affiliated("gmail.com", "tcs.com") is False

    # Empty and invalid cases
    assert is_valid_dns_match("", "tcs.com") is False
    assert is_valid_dns_match("tcs.com", "") is False


def test_extract_entities_detects_malicious_suffix_spoof():
    text = """
    TCS hiring! Official portal at https://tcs.com.attacker.example.
    Send CV to recruiter@tcs.com.attacker.example
    """
    extracted = extract_entities(text)
    assert extracted["brand_spoof_alert"] is not None
    assert extracted["brand_spoof_alert"]["is_spoof"] is True
    assert extracted["brand_spoof_alert"]["brand_claimed"] == "Tata Consultancy Services"


def test_spoofed_enterprise_brand_domains():
    """
    Issue 2 Regression tests:
    Ensures safe hostname normalization and subdomain-boundary matching catches
    various spoofed domain forms (hyphenated lookalikes, rogue prefixes, attacker subdomains).
    """
    from services.extractor_service import is_valid_dns_match, are_domains_dns_affiliated

    authoritative_tcs = "tcs.com"
    authoritative_infosys = "infosys.com"
    authoritative_wipro = "wipro.com"

    spoofed_candidates = [
        "tcs.com.attacker.example",
        "tcs.com-careers.net",
        "tcs-onboarding-portal.in",
        "fake-tcs.com",
        "careers-tcs.co.in",
        "infosys-jobs.org",
        "infosys.com.phishing.ru",
        "wipro-hr-team.in",
        "wipro.com.server.dev"
    ]

    for candidate in spoofed_candidates:
        assert is_valid_dns_match(candidate, authoritative_tcs) is False
        assert is_valid_dns_match(candidate, authoritative_infosys) is False
        assert is_valid_dns_match(candidate, authoritative_wipro) is False
        assert are_domains_dns_affiliated(candidate, authoritative_tcs) is False

    # Legitimate subdomains must still be accepted
    legitimate_subdomains = [
        "careers.tcs.com",
        "mail.tcs.com",
        "apac.careers.tcs.com",
        "hub.infosys.com",
        "talent.wipro.com"
    ]

    assert is_valid_dns_match("careers.tcs.com", authoritative_tcs) is True
    assert is_valid_dns_match("apac.careers.tcs.com", authoritative_tcs) is True
    assert is_valid_dns_match("hub.infosys.com", authoritative_infosys) is True
    assert is_valid_dns_match("talent.wipro.com", authoritative_wipro) is True




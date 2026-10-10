"""
Tests for SerpApi Service, Normalization & Safeguards
"""

import pytest
from services.serpapi_service import SerpApiService
from services.benchmark_data import list_benchmarks, get_benchmark


def test_serpapi_benchmark_loading():
    benchmarks = list_benchmarks()
    assert len(benchmarks) >= 4
    case_ids = [b["id"] for b in benchmarks]
    assert "apex_scam" in case_ids
    assert "tcs_spoof" in case_ids
    assert "hasura_legit" in case_ids
    assert "unindexed_entity" in case_ids


def test_serpapi_unconfigured_key_does_not_fake_results():
    """
    Priority 1 & 4 Safeguard:
    When no API key is configured and a custom company is queried,
    the service must NOT substitute a benchmark or fabricate search results.
    It must return search_status == 'unconfigured_key' with 0 sources retrieved.
    """
    service = SerpApiService(api_key="")
    assert not service.is_configured

    res = service.search_all_engines(
        company_name="Arbitrary Real Company Pvt Ltd",
        domain="arbitrary-real-company.in",
        role_title="Backend Intern"
    )

    assert res["is_benchmark_demonstration"] is False
    assert res["is_demo_mode"] is False
    assert res["search_status"] == "unconfigured_key"
    assert res["total_sources_retrieved"] == 0
    assert len(res["evidence_items"]) == 0
    assert "SerpApi API key is not configured" in res["search_error"]


def test_serpapi_all_searches_fail_does_not_fake_results(monkeypatch):
    """
    Issue 1:
    When live searches fail (e.g. rate limit, bad API key, network error),
    the service must NOT fall back to a benchmark or fabricate results.
    It must return search_status == 'search_failed' with 0 sources retrieved.
    """
    service = SerpApiService(api_key="invalid_test_key_123")
    assert service.is_configured

    # Mock all queries to return error dicts simulating failed network/bad key
    monkeypatch.setattr(service, "_query_google_search", lambda q, num=8: {"error": "Invalid API key"})
    monkeypatch.setattr(service, "_query_google_news", lambda q, num=6: {"error": "Invalid API key"})
    monkeypatch.setattr(service, "_query_google_jobs", lambda q, num=6: {"error": "Invalid API key"})

    res = service.search_all_engines(
        company_name="Real Custom Enterprise",
        domain="realenterprise.co.in",
        role_title="Software Intern"
    )

    assert res["is_benchmark_demonstration"] is False
    assert res["is_demo_mode"] is False
    assert res["search_status"] == "search_failed"
    assert res["total_sources_retrieved"] == 0
    assert len(res["evidence_items"]) == 0
    assert "Live SerpApi searches failed" in res["search_error"]



def test_serpapi_explicit_benchmark_demonstration():
    """
    When benchmark_case_id is explicitly passed, the service returns
    the simulation dataset honestly labeled with is_benchmark_demonstration=True.
    """
    service = SerpApiService(api_key="")
    res = service.search_all_engines(
        company_name="Apex Tech Solutions",
        domain="apextech-careers-india.online",
        role_title="Data Entry Intern",
        benchmark_case_id="apex_scam"
    )

    assert res["is_benchmark_demonstration"] is True
    assert res["is_demo_mode"] is True
    assert res["search_status"] == "benchmark_demonstration"
    assert res["total_sources_retrieved"] > 0
    assert len(res["evidence_items"]) > 0
    # Every simulated item must be clearly qualified
    for item in res["evidence_items"]:
        assert "[Simulated Example]" in item["title"] or "[Simulated Example]" in item["snippet"]
        assert item["source_timestamp"] == "Simulated benchmark fixture"


def test_serpapi_domain_extraction():
    service = SerpApiService(api_key="")
    assert service._extract_domain("https://www.google.co.in/search?q=test") == "google.co.in"
    assert service._extract_domain("http://subdomain.tcs.com/careers") == "subdomain.tcs.com"
    assert service._extract_domain("") == ""


def test_serpapi_news_classification_relevance_check():
    """
    Priority 3 Safeguard:
    Ensure negative news is relevant to the target company before it increases risk.
    Articles mentioning generic scam terms without the company name must not contradict.
    """
    service = SerpApiService(api_key="")

    # News mentioning scam/fraud, but NOT mentioning Acme Corp
    generic_news = {
        "title": "Police bust multi-crore job scam across Delhi-NCR",
        "snippet": "Authorities arrested suspects running fake job consultancies and demanding security deposits.",
        "link": "https://indiatoday.in/crime/123",
        "date": "2 days ago"
    }
    stance, category = service._classify_news_evidence(
        generic_news["title"], generic_news["snippet"], company="Acme Corp"
    )
    assert stance != "contradicts"
    assert stance == "inconclusive"

    # News specifically naming Acme Corp in a scam/fraud context
    targeted_news = {
        "title": "FIR registered against Acme Corp for fake internship racket",
        "snippet": "Acme Corp accused of taking refundable deposits from students and vanishing.",
        "link": "https://thehindu.com/news/456",
        "date": "1 day ago"
    }
    stance_tgt, category_tgt = service._classify_news_evidence(
        targeted_news["title"], targeted_news["snippet"], company="Acme Corp"
    )
    assert stance_tgt == "contradicts"


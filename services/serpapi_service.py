"""
OpportunityShield AI - SerpApi Multi-Engine Search Service
Orchestrates live queries to SerpApi (Google Search, Google News, Google Jobs),
normalizes, deduplicates, and categorizes evidentiary records.
Includes graceful error handling and standalone benchmark demonstration datasets.
"""

import time
import hashlib
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import requests
from config import Config
from services.benchmark_data import BENCHMARK_CASES
from services.extractor_service import are_domains_dns_affiliated, is_valid_dns_match

logger = logging.getLogger("OpportunityShield.SerpApi")


class SerpApiService:
    """Server-side integration layer for SerpApi."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else Config.SERPAPI_KEY
        self.base_url = Config.SERPAPI_BASE_URL
        self.timeout = Config.SEARCH_TIMEOUT

    @property
    def is_configured(self) -> bool:
        """Returns True if a plausible SerpApi key is configured."""
        return bool(self.api_key and len(self.api_key.strip()) > 8)

    def search_all_engines(self, company_name: str, domain: str = "",
                           role_title: str = "", benchmark_case_id: str = "") -> Dict[str, Any]:
        """
        Executes multi-engine search across Google Search, Google News, and Google Jobs.
        Returns normalized evidence, raw engine responses, and execution metadata.
        Never substitutes benchmark data for arbitrary company queries.
        """
        start_time = time.time()
        engine_errors = []

        # 1. If explicitly requested as benchmark, use curated demonstration dataset
        if benchmark_case_id and benchmark_case_id in BENCHMARK_CASES:
            bm = BENCHMARK_CASES[benchmark_case_id]
            norm_res = self._normalize_benchmark_data(bm, role_title)
            norm_res["is_demo_mode"] = True
            norm_res["is_benchmark_demonstration"] = True
            norm_res["demo_reason"] = (
                f"Simulated Benchmark Demonstration ('{benchmark_case_id}'): "
                "This report uses synthetic test data for educational demonstration, NOT live search results."
            )
            norm_res["search_status"] = "benchmark_demonstration"
            norm_res["search_error"] = ""
            norm_res["engine_errors"] = []
            norm_res["execution_time_seconds"] = round(time.time() - start_time, 2)
            return norm_res

        # 2. If SerpApi key is unconfigured, do NOT substitute a fake benchmark!
        # Return an honest unconfigured-key search state
        if not self.is_configured:
            return {
                "evidence_items": [],
                "comparable_jobs": [],
                "has_knowledge_graph": False,
                "knowledge_graph": {},
                "total_sources_retrieved": 0,
                "is_demo_mode": False,
                "is_benchmark_demonstration": False,
                "search_status": "unconfigured_key",
                "search_error": (
                    "SerpApi API key is not configured in server environment (SERPAPI_KEY). "
                    "Live external search evidence could not be retrieved. "
                    "To test the platform, select one of the 4 benchmark test cases or configure a free key in .env."
                ),
                "engine_errors": ["No SERPAPI_KEY found in server environment."],
                "execution_time_seconds": round(time.time() - start_time, 2),
            }

        # 3. Live SerpApi Queries
        organic_results = []
        news_results = []
        jobs_results = []
        knowledge_graph = None

        # Query 1: Google Search - Official corporate presence & domain check
        try:
            q_official = f'"{company_name}" official website careers'
            if domain:
                q_official = f'"{company_name}" site:{domain} OR "{company_name}" careers'
            res_official = self._query_google_search(q_official, num=Config.MAX_ORGANIC_RESULTS)
            if "error" in res_official:
                engine_errors.append(f"Google Search (Official): {res_official['error']}")
            else:
                organic_results.extend(res_official.get("organic_results", []))
                knowledge_graph = res_official.get("knowledge_graph")
        except Exception as e:
            logger.error(f"Error querying official Google Search: {e}")
            engine_errors.append(f"Google Search: {str(e)}")

        # Query 2: Google Search - Scam, fraud, complaints, and registration fee check
        try:
            q_scam = f'"{company_name}" (scam OR fraud OR fake OR complaints OR "registration fee" OR review)'
            res_scam = self._query_google_search(q_scam, num=Config.MAX_ORGANIC_RESULTS)
            if "error" in res_scam:
                engine_errors.append(f"Google Search (Scam check): {res_scam['error']}")
            else:
                organic_results.extend(res_scam.get("organic_results", []))
        except Exception as e:
            logger.error(f"Error querying scam Google Search: {e}")
            engine_errors.append(f"Google Search (Scam): {str(e)}")

        # Query 3: Google News - Recent corporate press & public sentiment
        try:
            q_news = f'"{company_name}"'
            res_news = self._query_google_news(q_news, num=Config.MAX_NEWS_RESULTS)
            if "error" in res_news:
                engine_errors.append(f"Google News: {res_news['error']}")
            else:
                news_results = res_news.get("news_results", [])
        except Exception as e:
            logger.error(f"Error querying Google News: {e}")
            engine_errors.append(f"Google News: {str(e)}")

        # Query 4: Google Jobs - Active job listings and market comparability
        try:
            q_jobs = f'"{role_title}" "{company_name}"' if role_title else f'"{company_name}"'
            res_jobs = self._query_google_jobs(q_jobs, num=Config.MAX_JOBS_RESULTS)
            if "error" in res_jobs:
                # If specific company jobs query returned empty/error, try broader role jobs in India
                if role_title:
                    res_jobs = self._query_google_jobs(f'"{role_title}" India', num=Config.MAX_JOBS_RESULTS)
                if "error" in res_jobs:
                    engine_errors.append(f"Google Jobs: {res_jobs['error']}")
                else:
                    jobs_results = res_jobs.get("jobs_results", [])
            else:
                jobs_results = res_jobs.get("jobs_results", [])
                # If no jobs found for company, also fetch comparable market roles
                if not jobs_results and role_title:
                    res_comp = self._query_google_jobs(f'"{role_title}" India', num=4)
                    jobs_results.extend(res_comp.get("jobs_results", []))
        except Exception as e:
            logger.error(f"Error querying Google Jobs: {e}")
            engine_errors.append(f"Google Jobs: {str(e)}")

        total_retrieved = len(organic_results) + len(news_results) + len(jobs_results)

        # Check if all calls failed due to bad API key or credit exhaustion
        if total_retrieved == 0 and engine_errors:
            return {
                "evidence_items": [],
                "comparable_jobs": [],
                "has_knowledge_graph": False,
                "knowledge_graph": {},
                "total_sources_retrieved": 0,
                "is_demo_mode": False,
                "is_benchmark_demonstration": False,
                "search_status": "search_failed",
                "search_error": f"Live SerpApi searches failed: {'; '.join(engine_errors[:2])}",
                "engine_errors": engine_errors,
                "execution_time_seconds": round(time.time() - start_time, 2),
            }

        # Normalize and deduplicate real SerpApi results
        normalized_evidence = self._normalize_live_results(
            company_name=company_name,
            claimed_domain=domain,
            organic_results=organic_results,
            news_results=news_results,
            jobs_results=jobs_results,
            knowledge_graph=knowledge_graph,
        )

        normalized_evidence["is_demo_mode"] = False
        normalized_evidence["is_benchmark_demonstration"] = False
        normalized_evidence["demo_reason"] = ""
        normalized_evidence["search_status"] = "success" if total_retrieved > 0 else "no_results"
        normalized_evidence["search_error"] = ""
        normalized_evidence["engine_errors"] = engine_errors
        normalized_evidence["execution_time_seconds"] = round(time.time() - start_time, 2)
        return normalized_evidence

    def _query_google_search(self, query: str, num: int = 8) -> Dict[str, Any]:
        """Queries SerpApi Google Search engine."""
        params = {
            "engine": "google",
            "q": query,
            "location": "India",
            "gl": "in",
            "hl": "en",
            "num": num,
            "api_key": self.api_key,
        }
        return self._execute_serpapi_request(params)

    def _query_google_news(self, query: str, num: int = 6) -> Dict[str, Any]:
        """Queries SerpApi Google News engine."""
        params = {
            "engine": "google_news",
            "q": query,
            "gl": "in",
            "hl": "en",
            "api_key": self.api_key,
        }
        return self._execute_serpapi_request(params)

    def _query_google_jobs(self, query: str, num: int = 6) -> Dict[str, Any]:
        """Queries SerpApi Google Jobs engine."""
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": "India",
            "hl": "en",
            "api_key": self.api_key,
        }
        return self._execute_serpapi_request(params)

    def _execute_serpapi_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes HTTP request to SerpApi endpoint with timeout & error handling."""
        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "Invalid or unauthorized SerpApi key (HTTP 401)."}
            elif response.status_code == 429:
                return {"error": "SerpApi monthly search credits exhausted or rate limited (HTTP 429)."}
            else:
                return {"error": f"SerpApi returned HTTP {response.status_code}: {response.text[:120]}"}
        except requests.exceptions.Timeout:
            return {"error": f"SerpApi query timed out after {self.timeout}s."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error contacting SerpApi: {str(e)}"}

    def _normalize_live_results(self, company_name: str, claimed_domain: str,
                                organic_results: List[Dict[str, Any]],
                                news_results: List[Dict[str, Any]],
                                jobs_results: List[Dict[str, Any]],
                                knowledge_graph: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deduplicates, normalizes, categorizes, and scores stance on real SerpApi records."""
        evidence_items = []
        seen_urls = set()
        seen_snippets = set()

        # 1. Knowledge Graph (if present in Google Search)
        has_verified_kg = False
        kg_info = {}
        if knowledge_graph and isinstance(knowledge_graph, dict):
            kg_title = knowledge_graph.get("title", "")
            kg_website = knowledge_graph.get("website", "")
            kg_desc = knowledge_graph.get("description", "")
            if kg_title:
                has_verified_kg = True
                kg_info = {
                    "title": kg_title,
                    "type": knowledge_graph.get("type", "Enterprise / Organization"),
                    "website": kg_website,
                    "description": kg_desc,
                }
                item_id = hashlib.md5(f"kg_{kg_title}".encode()).hexdigest()[:12]
                evidence_items.append({
                    "id": item_id,
                    "title": f"Google Knowledge Panel: {kg_title}",
                    "snippet": kg_desc or f"Verified knowledge graph listing for {kg_title}. Website: {kg_website}",
                    "link": kg_website or f"https://www.google.com/search?q={company_name}",
                    "domain": self._extract_domain(kg_website) or "google.com",
                    "engine": "Google Search (Knowledge Panel)",
                    "category": "Corporate Identity & Entity Footprint",
                    "source_timestamp": "Verified Real-time",
                    "stance": "supports",
                    "relevance_score": 0.98,
                    "details": kg_info,
                })

        # 2. Organic Google Search Results
        for org in organic_results:
            link = org.get("link", "")
            if not link or link in seen_urls:
                continue
            snippet = org.get("snippet", "")
            snip_hash = hashlib.md5(snippet[:60].encode()).hexdigest()
            if snip_hash in seen_snippets:
                continue

            seen_urls.add(link)
            seen_snippets.add(snip_hash)

            title = org.get("title", "Search Result")
            domain = self._extract_domain(link)
            stance, category = self._classify_search_evidence(title, snippet, company_name, claimed_domain, domain)

            item_id = hashlib.md5(link.encode()).hexdigest()[:12]
            evidence_items.append({
                "id": item_id,
                "title": title,
                "snippet": snippet,
                "link": link,
                "domain": domain,
                "engine": "Google Search",
                "category": category,
                "source_timestamp": org.get("date", ""),
                "stance": stance,
                "relevance_score": self._compute_relevance(title, snippet, company_name),
            })

        # 3. Google News Results
        for news in news_results:
            link = news.get("link", "")
            if not link or link in seen_urls:
                continue
            title = news.get("title", "News Article")
            snippet = news.get("snippet", news.get("source", {}).get("name", ""))
            seen_urls.add(link)

            domain = self._extract_domain(link)
            stance, category = self._classify_news_evidence(title, snippet, company_name)

            item_id = hashlib.md5(link.encode()).hexdigest()[:12]
            evidence_items.append({
                "id": item_id,
                "title": title,
                "snippet": snippet,
                "link": link,
                "domain": domain,
                "engine": "Google News",
                "category": category,
                "source_timestamp": news.get("date", "Recent"),
                "stance": stance,
                "relevance_score": 0.85,
            })

        # 4. Google Jobs Results
        comparable_jobs = []
        for job in jobs_results:
            j_title = job.get("title", "")
            j_comp = job.get("company_name", "")
            j_loc = job.get("location", "India")
            j_via = job.get("via", "")
            j_desc = job.get("description", "")
            j_link = job.get("share_link", job.get("related_links", [{}])[0].get("link", "https://google.com"))

            # Determine whether this job matches target company
            is_target_company = company_name.lower() in j_comp.lower() if j_comp else False

            comparable_jobs.append({
                "title": j_title,
                "company_name": j_comp,
                "location": j_loc,
                "via": j_via,
                "link": j_link,
                "description_preview": j_desc[:240] + "..." if len(j_desc) > 240 else j_desc,
                "is_target_company": is_target_company,
            })

            # Also create an evidence item if it matches the target company or provides strong market anchor
            if is_target_company:
                item_id = hashlib.md5(f"job_{j_title}_{j_comp}".encode()).hexdigest()[:12]
                evidence_items.append({
                    "id": item_id,
                    "title": f"Active Listing: {j_title} at {j_comp}",
                    "snippet": f"Found open position on {j_via}. Location: {j_loc}. {j_desc[:160]}",
                    "link": j_link,
                    "domain": self._extract_domain(j_link) or "google.com",
                    "engine": "Google Jobs",
                    "category": "Job Market & Listing Consistency",
                    "source_timestamp": "Active Listing",
                    "stance": "supports",
                    "relevance_score": 0.95,
                })

        return {
            "evidence_items": evidence_items,
            "comparable_jobs": comparable_jobs,
            "has_knowledge_graph": has_verified_kg,
            "knowledge_graph": kg_info,
            "total_sources_retrieved": len(evidence_items),
        }

    def _normalize_benchmark_data(self, benchmark: Dict[str, Any], role_title: str = "") -> Dict[str, Any]:
        """Converts curated benchmark dataset into normalized evidence format with honest simulated labels."""
        evidence_items = []
        seen_urls = set()
        bm_res = benchmark.get("serpapi_results", {})
        comp_name = benchmark["explicit_fields"]["company"]
        claimed_domain = benchmark["explicit_fields"]["domain"]

        # Search items
        for s in bm_res.get("google_search", []):
            link = s.get("link", "")
            seen_urls.add(link)
            domain = self._extract_domain(link)
            stance, cat = self._classify_search_evidence(s["title"], s["snippet"], comp_name, claimed_domain, domain)
            evidence_items.append({
                "id": hashlib.md5(link.encode()).hexdigest()[:12],
                "title": f"[Simulated Example] {s['title']}",
                "snippet": s["snippet"],
                "link": link,
                "domain": domain,
                "engine": "Google Search (Benchmark Sample)",
                "category": cat,
                "source_timestamp": "Simulated benchmark fixture",
                "stance": stance,
                "relevance_score": 0.92,
            })

        # News items
        for n in bm_res.get("google_news", []):
            link = n.get("link", "")
            seen_urls.add(link)
            domain = self._extract_domain(link)
            stance, cat = self._classify_news_evidence(n["title"], n["snippet"], comp_name)
            evidence_items.append({
                "id": hashlib.md5(link.encode()).hexdigest()[:12],
                "title": f"[Simulated Example] {n['title']}",
                "snippet": n["snippet"],
                "link": link,
                "domain": domain,
                "engine": "Google News (Benchmark Sample)",
                "category": cat,
                "source_timestamp": "Simulated benchmark fixture",
                "stance": stance,
                "relevance_score": 0.88,
            })

        # Jobs items
        comparable_jobs = []
        for j in bm_res.get("google_jobs", []):
            j_title = j.get("title", "")
            j_comp = j.get("company_name", "")
            is_target = comp_name.lower() in j_comp.lower()
            comparable_jobs.append({
                "title": j_title,
                "company_name": j_comp,
                "location": j.get("location", "India"),
                "via": f"{j.get('via', 'Google Jobs')} (Simulated sample)",
                "link": "https://careers.google.com/jobs",
                "description_preview": j.get("description", "")[:200],
                "is_target_company": is_target,
            })
            if is_target:
                evidence_items.append({
                    "id": hashlib.md5(f"bmjob_{j_title}".encode()).hexdigest()[:12],
                    "title": f"[Simulated Example] Job Posting: {j_title} at {j_comp}",
                    "snippet": j.get("description", "")[:180],
                    "link": "https://careers.google.com/jobs",
                    "domain": "careers.google.com",
                    "engine": "Google Jobs (Benchmark Sample)",
                    "category": "Job Market & Listing Consistency",
                    "source_timestamp": "Simulated benchmark sample",
                    "stance": "supports",
                    "relevance_score": 0.95,
                })

        return {
            "evidence_items": evidence_items,
            "comparable_jobs": comparable_jobs,
            "has_knowledge_graph": benchmark["id"] == "hasura_legit",
            "knowledge_graph": {
                "title": comp_name,
                "type": "Software & Technology Company",
                "website": f"https://{claimed_domain}",
                "description": "High performance data access and GraphQL engine developer."
            } if benchmark["id"] == "hasura_legit" else {},
            "total_sources_retrieved": len(evidence_items),
        }

    def _classify_search_evidence(self, title: str, snippet: str, company: str,
                                 claimed_domain: str, result_domain: str) -> (str, str):
        """Classifies stance (supports/contradicts/inconclusive) and evidentiary category using DNS boundaries."""
        text = f"{title} {snippet}".lower()

        # Contradicts / Warning flags
        contradict_words = ["scam", "fraud", "fake", "duped", "cheated", "complaint", "warning", "police", "arrest", "fir"]
        if any(w in text for w in contradict_words):
            return "contradicts", "Public Sentiment, Complaints & Risk Reports"

        # Official domain match with strict DNS label boundaries (no substring matching)
        if claimed_domain and are_domains_dns_affiliated(claimed_domain, result_domain):
            return "supports", "Corporate Identity & Entity Footprint"

        # Official careers / corporate profile
        corporate_words = ["official website", "careers", "about us", "who we are", "overview", "crunchbase", "linkedin.com/company"]
        if any(w in text for w in corporate_words) and company.lower() in text:
            return "supports", "Corporate Identity & Entity Footprint"

        # MCA / Government / Registrar verification (strict DNS boundaries)
        is_registrar = any(is_valid_dns_match(result_domain, reg) for reg in ["mca.gov.in", "zaubacorp.com", "tofler.in"])
        if is_registrar:
            return "supports", "Corporate Identity & Entity Footprint"

        return "inconclusive", "General Web Footprint & Independent References"

    def _classify_news_evidence(self, title: str, snippet: str, company: str = "") -> (str, str):
        """
        Classifies news stance and category.
        Ensures adverse news is strictly relevant to target company before increasing risk.
        """
        text = f"{title} {snippet}".lower()
        comp_lower = company.lower().strip() if company else ""

        # Check for specific recruitment / fraud / criminal misconduct terms
        adverse_terms = ["scam", "fraud", "arrest", "raid", "duped", "cheated", "fir", "police complaint", "fake job"]
        if any(w in text for w in adverse_terms):
            if comp_lower and comp_lower in text:
                return "contradicts", "Public Sentiment, Complaints & Risk Reports"
            # If target company is not explicitly mentioned, do not classify as contradicting
            return "inconclusive", "General Web Footprint & Independent References"

        # Check for legitimate business milestones
        if any(w in text for w in ["raises", "funding", "expands", "launches", "partnership", "award", "hires"]):
            if comp_lower and comp_lower in text:
                return "supports", "Public Sentiment, Complaints & Risk Reports"
            return "inconclusive", "General Web Footprint & Independent References"

        return "inconclusive", "Public Sentiment, Complaints & Risk Reports"

    def _compute_relevance(self, title: str, snippet: str, company: str) -> float:
        """Calculates rough text relevance score between 0.5 and 1.0."""
        score = 0.60
        if not company:
            return score
        comp_lower = company.lower()
        if comp_lower in title.lower():
            score += 0.25
        if comp_lower in snippet.lower():
            score += 0.15
        return min(0.99, round(score, 2))

    def _extract_domain(self, url: str) -> str:
        """Extracts clean hostname from URL."""
        if not url:
            return ""
        if not url.startswith("http"):
            url = "https://" + url
        try:
            netloc = urlparse(url).netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc.split(":")[0]
        except Exception:
            return ""


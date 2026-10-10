"""
OpportunityShield AI - Transparent Rule-Based Investigation Engine
Synthesizes normalized SerpApi search evidence and extracted opportunity vectors.
Calculates an explainable, auditable risk score with explicit rationale and citations.
Produces the comprehensive 7-section investigation report.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from services.extractor_service import are_domains_dns_affiliated, is_recruiter_email_domain_affiliated


class InvestigationEngine:
    """Explainable Investigation Engine for job & internship authenticity."""

    def analyze(self, extracted: Dict[str, Any], search_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conducts comprehensive evidentiary analysis and generates structured investigation report.
        """
        evidence_items = search_results.get("evidence_items", [])
        comparable_jobs = search_results.get("comparable_jobs", [])
        has_kg = search_results.get("has_knowledge_graph", False)
        kg_data = search_results.get("knowledge_graph", {})

        company = extracted.get("company_name", "Unknown Company")
        claimed_domain = extracted.get("domain", "")
        role = extracted.get("role_title", "Intern / Trainee")
        compensation = extracted.get("compensation", {})
        red_flags = extracted.get("red_flag_triggers", [])
        brand_spoof = extracted.get("brand_spoof_alert")
        has_free_email = extracted.get("has_free_email", False)
        has_telegram = extracted.get("has_telegram", False)
        has_whatsapp = extracted.get("has_whatsapp", False)

        # 1. Rule-Based Factor Evaluation
        factors: List[Dict[str, Any]] = []
        positive_signals: List[Dict[str, Any]] = []
        warning_signals: List[Dict[str, Any]] = []

        # Count evidence stances
        supporting_sources = [e for e in evidence_items if e.get("stance") == "supports"]
        contradicting_sources = [e for e in evidence_items if e.get("stance") == "contradicts"]
        neutral_sources = [e for e in evidence_items if e.get("stance") == "inconclusive"]

        # RULE 1: Upfront Fee or Security Deposit Demanded (CRITICAL)
        if red_flags:
            top_flag = red_flags[0]
            severity_impact = 45 if top_flag["severity"] == "critical" else 30
            factor = {
                "rule_id": "CRIT_FEE_DEMAND",
                "name": "Upfront Payment or Deposit Demand",
                "type": "warning",
                "impact": f"+{severity_impact}",
                "numeric_impact": severity_impact,
                "confidence": "High",
                "rationale": f"Explicit payment requirement detected: {top_flag['label']}. Legitimate employers in India do not demand upfront fees or refundable deposits under Ministry of Labour guidelines.",
                "evidence_quote": top_flag["context_snippet"],
                "citation": "Extracted Opportunity Text",
            }
            factors.append(factor)
            warning_signals.append({
                "title": f"Upfront Fee / Deposit: {top_flag['label']}",
                "severity": top_flag["severity"].upper(),
                "description": f"The opportunity specifies an advance payment requirement ({top_flag['context_snippet']}). Advance-fee fraud is the #1 tactic used in fake recruitment syndicates.",
                "source": "Submitted Offer Details",
            })

        # RULE 2: Brand Impersonation / Lookalike Domain
        if brand_spoof and brand_spoof.get("is_spoof"):
            impact = 35
            factor = {
                "rule_id": "CRIT_BRAND_SPOOF",
                "name": "Enterprise Brand Impersonation",
                "type": "warning",
                "impact": f"+{impact}",
                "numeric_impact": impact,
                "confidence": "High",
                "rationale": brand_spoof["warning"],
                "evidence_quote": f"Claimed brand: {brand_spoof['brand_claimed']}, Active domain: {brand_spoof['actual_domain']}",
                "citation": f"Brand registry match (legitimate domain: {brand_spoof['legitimate_domains'][0]})",
            }
            factors.append(factor)
            warning_signals.append({
                "title": f"Brand Lookalike Domain Spoof ({brand_spoof['brand_claimed']})",
                "severity": "CRITICAL",
                "description": brand_spoof["warning"],
                "source": "Domain & Email Verification",
            })

        # RULE 3: Telegram / WhatsApp Interview Channels
        if has_telegram:
            impact = 22
            factors.append({
                "rule_id": "WARN_MESSAGING_CHANNEL",
                "name": "Anonymous Messaging Channel Interview",
                "type": "warning",
                "impact": f"+{impact}",
                "numeric_impact": impact,
                "confidence": "High",
                "rationale": "Interviewing, onboarding, or task dispatch is conducted via Telegram. Telegram channels offer identity obfuscation and are heavily exploited for untraceable employment schemes.",
                "evidence_quote": f"Telegram references: {', '.join(extracted.get('telegram_handles', ['Telegram channel mentioned']))}",
                "citation": "Submitted Offer Details",
            })
            warning_signals.append({
                "title": "Recruitment Conducted via Telegram",
                "severity": "HIGH",
                "description": "Communication directed to Telegram handles rather than enterprise email or verified ATS portals.",
                "source": "Submitted Offer Details",
            })
        elif has_whatsapp and not claimed_domain:
            impact = 12
            factors.append({
                "rule_id": "WARN_WHATSAPP_ONLY",
                "name": "Exclusive WhatsApp Communication",
                "type": "warning",
                "impact": f"+{impact}",
                "numeric_impact": impact,
                "confidence": "Medium",
                "rationale": "Direct recruitment communication conducted solely over WhatsApp without verified enterprise infrastructure.",
                "evidence_quote": "WhatsApp communication identified",
                "citation": "Submitted Offer Details",
            })
            warning_signals.append({
                "title": "Recruiter Communicates Solely via WhatsApp",
                "severity": "MEDIUM",
                "description": "Lack of corporate communication infrastructure.",
                "source": "Submitted Offer Details",
            })

        # RULE 4: Recruiter using Free Consumer Email Domain
        if has_free_email:
            impact = 18
            free_domains = [d for d in extracted.get("email_domains", []) if d in ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "proton.me", "protonmail.com"]]
            factors.append({
                "rule_id": "WARN_FREE_EMAIL",
                "name": "Free Consumer Email Domain",
                "type": "warning",
                "impact": f"+{impact}",
                "numeric_impact": impact,
                "confidence": "High",
                "rationale": f"Recruiter contacted candidate from a free webmail account (@{', @'.join(free_domains)}) while representing an organization. Legitimate corporate HR departments utilize domain-authenticated mail servers.",
                "evidence_quote": f"Recruiter email: {', '.join(extracted.get('emails', []))}",
                "citation": "Extracted Email Headers",
            })
            warning_signals.append({
                "title": "Recruiter Uses Free Webmail (@gmail / @yahoo / @outlook)",
                "severity": "HIGH",
                "description": f"HR contact is using free email (@{', @'.join(free_domains)}) instead of official corporate domain email.",
                "source": "Extracted Contact Info",
            })

        # RULE 5: Suspicious Compensation Bait
        if compensation.get("is_suspicious_compensation"):
            impact = 15
            factors.append({
                "rule_id": "WARN_UNREALISTIC_WAGE",
                "name": "Unrealistic Compensation Bait",
                "type": "warning",
                "impact": f"+{impact}",
                "numeric_impact": impact,
                "confidence": "Medium",
                "rationale": compensation.get("reason", "Disproportionate compensation promised for entry-level work."),
                "evidence_quote": f"Claimed compensation: {compensation.get('claimed_amount', 'High stipend')}",
                "citation": "Compensation Evaluation",
            })
            warning_signals.append({
                "title": "Disproportionate Compensation Claim",
                "severity": "MEDIUM",
                "description": compensation.get("reason", "Stipend significantly exceeds prevailing industry benchmarks for comparable tasks."),
                "source": "Submitted Compensation Claim",
            })

        # RULE 6: Contradictory / Scam Search Results in Google Search or News
        if contradicting_sources:
            scam_impact = min(35, len(contradicting_sources) * 15)
            top_scam_source = contradicting_sources[0]
            factors.append({
                "rule_id": "WARN_PUBLIC_SCAM_EVIDENCE",
                "name": "Public Scam Reports / Adverse Press Discovered",
                "type": "warning",
                "impact": f"+{scam_impact}",
                "numeric_impact": scam_impact,
                "confidence": "High",
                "rationale": f"SerpApi Google Search / News uncovered {len(contradicting_sources)} independent result(s) reporting fraud, police complaints, or recruitment warnings associated with this entity.",
                "evidence_quote": top_scam_source.get("snippet", "")[:180],
                "citation": f"{top_scam_source.get('engine')}: {top_scam_source.get('title')}",
                "link": top_scam_source.get("link", ""),
            })
            warning_signals.append({
                "title": f"Adverse Media / Public Scam Reports ({len(contradicting_sources)} sources)",
                "severity": "HIGH",
                "description": f"Found public consumer warnings or legal reporting: {top_scam_source.get('title')} ({top_scam_source.get('domain')}).",
                "source": top_scam_source.get("domain", "Search Results"),
            })

        # RULE 7: Positive Signal - Verified Google Knowledge Panel (Entity Existence Only)
        if has_kg:
            impact = -18
            kg_title = kg_data.get("title", company)
            factors.append({
                "rule_id": "POS_KNOWLEDGE_PANEL",
                "name": "Google Knowledge Graph Verification (Entity Existence)",
                "nature": "entity_verification_only",
                "type": "positive",
                "impact": f"{impact}",
                "numeric_impact": impact,
                "confidence": "High",
                "rationale": f"SerpApi retrieved a Google Knowledge Panel for entity '{kg_title}', indicating an established indexed organization. Note: While corporate entity existence is confirmed, this does not certify that the individual recruiter contacting you is an authorized representative.",
                "evidence_quote": kg_data.get("description", "Verified entity listing"),
                "citation": "Google Search Knowledge Graph",
            })
            positive_signals.append({
                "title": f"Verified Entity Knowledge Panel ({kg_title})",
                "strength": "MODERATE",
                "description": f"Google indexes {kg_title} as an established entity ({kg_data.get('type', 'Organization')}). Does not guarantee individual recruiter authorization.",
                "source": "Google Knowledge Graph",
            })

        # RULE 8: Positive Signal - Official Website & Domain Match (Strict DNS Label Boundaries)
        matching_domain_sources = [
            e for e in supporting_sources
            if claimed_domain and are_domains_dns_affiliated(claimed_domain, e.get("domain", ""))
        ]
        if matching_domain_sources:
            impact = -15
            top_dom = matching_domain_sources[0]
            factors.append({
                "rule_id": "POS_DOMAIN_MATCH",
                "name": "Official Corporate Domain Indexed",
                "nature": "entity_verification_only",
                "type": "positive",
                "impact": f"{impact}",
                "numeric_impact": impact,
                "confidence": "High",
                "rationale": f"Official domain '{claimed_domain}' actively ranks on Google Search with corporate metadata. Note: Confirms corporate web footprint; verify that incoming emails originate from authentic SPF/DKIM mail servers.",
                "evidence_quote": top_dom.get("snippet", "")[:150],
                "citation": f"{top_dom.get('title')} ({top_dom.get('domain')})",
                "link": top_dom.get("link", ""),
            })
            positive_signals.append({
                "title": f"Official Corporate Domain Verified ({claimed_domain})",
                "strength": "MODERATE",
                "description": f"Domain is properly indexed with verifiable corporate presence: {top_dom.get('title')}. Individual recruiter authority remains unverified.",
                "source": top_dom.get("domain", claimed_domain),
            })

        # RULE 9: Positive Signal - Active Job Postings on Google Jobs
        active_jobs_for_company = [j for j in comparable_jobs if j.get("is_target_company")]
        if active_jobs_for_company:
            impact = -12
            top_j = active_jobs_for_company[0]
            factors.append({
                "rule_id": "POS_GOOGLE_JOBS_ACTIVE",
                "name": "Active Postings on Google Jobs",
                "nature": "entity_verification_only",
                "type": "positive",
                "impact": f"{impact}",
                "numeric_impact": impact,
                "confidence": "High",
                "rationale": f"Verified active hiring listings for {company} found on Google Jobs via reputable channels ({top_j.get('via', 'Google Jobs')}). Confirms company conducts recruitment, but specific offer terms must be cross-checked.",
                "evidence_quote": f"Listing: {top_j.get('title')} - {top_j.get('location')}",
                "citation": f"Google Jobs ({top_j.get('via', 'Active listing')})",
            })
            positive_signals.append({
                "title": f"Active Postings on Google Jobs ({len(active_jobs_for_company)} listing(s))",
                "strength": "MODERATE",
                "description": f"Found legitimate open positions: {top_j.get('title')} ({top_j.get('via', 'Job Boards')}).",
                "source": "Google Jobs",
            })

        # RULE 10: Positive Signal - Matching Corporate Email Domain (Strict DNS Boundaries)
        if claimed_domain and not has_free_email and extracted.get("email_domains"):
            matching_emails = [
                ed for ed in extracted.get("email_domains", [])
                if is_recruiter_email_domain_affiliated(ed, claimed_domain)
            ]
            if matching_emails:
                impact = -10
                factors.append({
                    "rule_id": "POS_CORPORATE_EMAIL",
                    "name": "Authenticated Corporate Email Domain Alignment",
                    "nature": "channel_alignment_signal",
                    "type": "positive",
                    "impact": f"{impact}",
                    "numeric_impact": impact,
                    "confidence": "High",
                    "rationale": f"Recruiter email domain '@{matching_emails[0]}' belongs to the verified corporate domain '{claimed_domain}'. Note: Check for display name spoofing; legitimate corporate email alignment.",
                    "evidence_quote": f"Email: {extracted.get('emails', [''])[0]}",
                    "citation": "Email Domain Consistency",
                })
                positive_signals.append({
                    "title": "Corporate Email Matches Official Domain",
                    "strength": "MODERATE",
                    "description": f"Recruiter corresponds using authenticated company domain (@{matching_emails[0]}).",
                    "source": "Recruiter Channel Check",
                })

        # RULE 11: Sparse Footprint / Unindexed Company (Contextual Signal, Not Fraud Proof)
        if len(evidence_items) <= 2 and not red_flags and not brand_spoof:
            impact = 10
            factors.append({
                "rule_id": "WARN_SPARSE_FOOTPRINT",
                "name": "Sparse Online Corporate Footprint",
                "nature": "contextual_signal",
                "type": "warning",
                "impact": f"+{impact}",
                "numeric_impact": impact,
                "confidence": "Low",
                "rationale": "Company has minimal search engine indexing across Google Search, News, and Jobs. An absent online footprint is common for new startups or local entities and is NOT proof of fraud. Candidates should independently verify identity before sharing sensitive personal records.",
                "evidence_quote": f"Only {len(evidence_items)} search result(s) returned.",
                "citation": "SerpApi Multi-Engine Coverage",
            })
            warning_signals.append({
                "title": "Minimal Public Search Indexing (Contextual Signal)",
                "severity": "LOW",
                "description": "Entity has very limited online documentation or media coverage. Not proof of fraud, but requires independent verification.",
                "source": "SerpApi Index Coverage",
            })

        # 2. Compute Numerical Heuristic Risk Score (0 - 100) & Qualitative Assessment
        base_score = 45  # Unverified baseline
        total_warning_impact = sum(f["numeric_impact"] for f in factors if f["numeric_impact"] > 0)
        total_positive_impact = sum(f["numeric_impact"] for f in factors if f["numeric_impact"] < 0)

        raw_score = base_score + total_warning_impact + total_positive_impact
        final_risk_score = max(5, min(98, raw_score))

        search_status = search_results.get("search_status", "success")
        search_error = search_results.get("search_error", "")
        is_benchmark = search_results.get("is_benchmark_demonstration", False)
        has_critical_red_flags = bool(red_flags or (brand_spoof and brand_spoof.get("is_spoof")))

        # Determine Qualitative Assessment Indicator with Insufficient Evidence Support
        if search_status in ("unconfigured_key", "search_failed") and not is_benchmark:
            if has_critical_red_flags:
                assessment_label = "Elevated concern (Direct text triggers; external search unavailable)"
                status_code = "elevated_concern"
                badge_color = "rose"
                summary_statement = (
                    f"Direct advance-fee or lookalike red flags were detected in the submitted opportunity text. "
                    f"However, live external search verification via SerpApi was unavailable ({search_error}). "
                    "The elevated concern reflects observed text payment triggers; public search indexing could not be verified."
                )
            else:
                assessment_label = "Insufficient public evidence"
                status_code = "insufficient_evidence"
                badge_color = "amber"
                final_risk_score = 50
                summary_statement = (
                    f"Live search evidence could not be retrieved ({search_error}). "
                    "No explicit advance-fee red flags were found in the text, but the opportunity cannot be verified "
                    "without public search indexing. Please treat the opportunity as unverified until independent checks are completed."
                )
        elif len(evidence_items) == 0 and not has_critical_red_flags and not is_benchmark:
            assessment_label = "Insufficient public evidence"
            status_code = "insufficient_evidence"
            badge_color = "amber"
            final_risk_score = 50
            summary_statement = (
                f"Public search queries across Google Search, News, and Jobs returned zero indexed results for '{company}'. "
                "An absent online footprint is common for brand-new startups or local entities and is NOT proof of fraud. "
                "Due to insufficient public evidence, independent verification through official registrar directories (e.g. MCA21) is strongly recommended."
            )
        elif final_risk_score <= 30:
            assessment_label = "Low observed concern"
            status_code = "low_concern"
            badge_color = "emerald"
            summary_statement = (
                f"Public evidentiary signals retrieved via SerpApi support the corporate legitimacy of '{company}'. "
                "Official web presence, standard hiring channels, and absence of upfront payment requirements "
                "indicate low observable risk. Note: Confirms corporate entity presence; always verify individual recruiter identity through official portals."
            )
        elif final_risk_score <= 65:
            assessment_label = "Needs further verification"
            status_code = "needs_verification"
            badge_color = "amber"
            summary_statement = (
                f"Available evidence for '{company}' is incomplete or mixed. "
                "While direct criminal red flags were not decisively confirmed, sparse indexing, unverified recruiter "
                "channels, or lack of official listings suggest you should exercise prudent caution before submitting "
                "sensitive identification documents."
            )
        else:
            assessment_label = "Elevated concern"
            status_code = "elevated_concern"
            badge_color = "rose"
            summary_statement = (
                f"High-risk indicators were detected for this opportunity. "
                "Observable factors such as upfront payment/deposit requests, lookalike domain spoofing, "
                "anonymous communication channels, or public scam reports strongly indicate elevated danger of financial loss or fraud."
            )

        # 3. Actionable Checklist tailored for Indian students
        recommended_actions = self._generate_recommendations(final_risk_score, extracted, brand_spoof)

        # 4. Construct Full 7-Section Investigation Report
        report = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "opportunity_title": role,
                "target_company": company,
                "target_domain": claimed_domain or "Not Provided",
                "recruiter_email": extracted.get("emails", ["Not provided"])[0] if extracted.get("emails") else "Not provided",
                "total_sources": len(evidence_items),
                "is_demo_mode": search_results.get("is_demo_mode", False),
                "is_benchmark_demonstration": search_results.get("is_benchmark_demonstration", False),
                "search_status": search_status,
                "search_error": search_error,
                "demo_reason": search_results.get("demo_reason", ""),
                "execution_time_seconds": search_results.get("execution_time_seconds", 0.0),
                "coverage_limitations": (
                    "Search results reflect public Google Search, Google News, and Google Jobs indexing at the time of query. "
                    "An absence of records does not conclusively prove fraud, nor does a clean domain guarantee individual recruiter legitimacy."
                ),
            },
            "assessment": {
                "label": assessment_label,
                "status_code": status_code,
                "risk_score": final_risk_score,
                "badge_color": badge_color,
                "summary": summary_statement,
                "base_score": base_score,
                "total_warning_impact": total_warning_impact,
                "total_positive_impact": total_positive_impact,
                "factors": factors,
                "formula_explanation": (
                    f"Heuristic Score = Clamp(Base: {base_score} + Risk Factors: +{total_warning_impact} - Positive Signals: {abs(total_positive_impact)}, [0, 100]) = {final_risk_score}/100"
                ),
            },
            "positive_signals": positive_signals,
            "warning_signals": warning_signals,
            "evidence_items": evidence_items,
            "recommended_actions": recommended_actions,
            "comparable_jobs": comparable_jobs,
            "extracted_entities": extracted,
        }

        return report

    def _generate_recommendations(self, score: int, extracted: Dict[str, Any], brand_spoof: Any) -> List[Dict[str, str]]:
        """Generates prioritized, actionable verification checklist for Indian candidates."""
        checklist = []

        # 1. Financial advice (Universal)
        checklist.append({
            "priority": "P0 (Immediate Rule)",
            "action": "Never Pay Security Deposits or Training Charges",
            "details": (
                "Under Indian Ministry of Labour & Employment guidelines, legitimate employers and campus recruiters NEVER demand "
                "refundable deposits, laptop courier fees, or training costs from candidates. If asked for money via UPI or QR code, cease communication immediately."
            ),
            "status": "critical",
        })

        # 2. Domain / Official Careers Portal Verification
        domain = extracted.get("domain", "")
        company = extracted.get("company_name", "")
        if brand_spoof and brand_spoof.get("is_spoof"):
            checklist.append({
                "priority": "P0 (Brand Alert)",
                "action": f"Avoid Spoofed Portal '{brand_spoof.get('actual_domain')}'",
                "details": (
                    f"This opportunity uses an unverified domain mimicking {brand_spoof.get('brand_claimed')}. "
                    f"Visit the genuine career portal directly at https://{brand_spoof['legitimate_domains'][0]} and check the official job ID."
                ),
                "status": "critical",
            })
        elif domain:
            checklist.append({
                "priority": "P1 (Portal Check)",
                "action": "Verify Opportunity on Official Corporate Careers Page",
                "details": (
                    f"Type 'https://{domain}' directly into your browser address bar. Check if the job opening is listed under their official /careers or /jobs portal. "
                    "Do not click unverified links sent via SMS, WhatsApp, or unsolicited emails."
                ),
                "status": "recommended",
            })

        # 3. Recruiter Verification on LinkedIn
        checklist.append({
            "priority": "P1 (Identity Check)",
            "action": "Cross-Verify Recruiter Profile on LinkedIn",
            "details": (
                f"Search for the recruiter's name and '{company}' on LinkedIn. Check their employee duration, official company tag, "
                "and whether their profile has active professional connections and recommendations."
            ),
            "status": "recommended",
        })

        # 4. Ministry of Corporate Affairs (MCA) Verification
        checklist.append({
            "priority": "P2 (Corporate Check)",
            "action": "Verify Company Incorporation on MCA21 (mca.gov.in)",
            "details": (
                "Search the official Ministry of Corporate Affairs database (mca.gov.in) or Zauba Corp to confirm whether the company is "
                "a legally registered Private Limited or LLP entity in India with an active CIN (Corporate Identification Number)."
            ),
            "status": "info",
        })

        # 5. Incident Reporting for High-Risk Cases
        if score >= 65:
            checklist.append({
                "priority": "P0 (Incident Reporting)",
                "action": "Report Phishing / Fraud to National Cyber Crime Portal",
                "details": (
                    "If a scammer attempted financial extortion or identity theft, report the incident immediately at https://cybercrime.gov.in "
                    "or call the National Cyber Crime Helpline at 1930. Provide phone numbers, UPI IDs, and chat screenshots."
                ),
                "status": "critical",
            })

        return checklist


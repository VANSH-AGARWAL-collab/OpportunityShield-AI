"""
OpportunityShield AI - Entity & Trigger Extractor Service
Extracts company names, domains, recruiter channels, compensation claims,
and suspicious deposit/payment triggers from unstructured opportunity text.
"""

import re
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional

# Known free/personal email domains often misused by scammers impersonating corporates
FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "yahoo.co.in",
    "hotmail.com",
    "outlook.com",
    "live.com",
    "rediffmail.com",
    "protonmail.com",
    "proton.me",
    "aol.com",
    "zoho.com",
    "icloud.com",
    "mail.com",
    "yandex.com",
}

# Major known brands targeted for impersonation/phishing in India
KNOWN_ENTERPRISE_BRANDS = {
    "tcs": {"name": "Tata Consultancy Services", "domains": ["tcs.com"]},
    "tata consultancy services": {"name": "Tata Consultancy Services", "domains": ["tcs.com"]},
    "infosys": {"name": "Infosys", "domains": ["infosys.com"]},
    "wipro": {"name": "Wipro", "domains": ["wipro.com"]},
    "accenture": {"name": "Accenture", "domains": ["accenture.com"]},
    "cognizant": {"name": "Cognizant", "domains": ["cognizant.com"]},
    "amazon": {"name": "Amazon", "domains": ["amazon.com", "amazon.jobs", "amazon.in"]},
    "google": {"name": "Google", "domains": ["google.com", "careers.google.com"]},
    "microsoft": {"name": "Microsoft", "domains": ["microsoft.com", "careers.microsoft.com"]},
    "flipkart": {"name": "Flipkart", "domains": ["flipkart.com", "flipkartcareers.com"]},
    "swiggy": {"name": "Swiggy", "domains": ["swiggy.com"]},
    "zomato": {"name": "Zomato", "domains": ["zomato.com"]},
    "reliance": {"name": "Reliance", "domains": ["ril.com", "jio.com"]},
    "jio": {"name": "Jio", "domains": ["jio.com"]},
    "hcl": {"name": "HCLTech", "domains": ["hcltech.com", "hcl.com"]},
    "tech mahindra": {"name": "Tech Mahindra", "domains": ["techmahindra.com"]},
}

# Critical red flag keywords in Indian hiring context
SUSPICIOUS_FEE_PATTERNS = [
    (r"registration\s+fee[s]?", "Registration Fee requested", "high"),
    (r"security\s+deposit", "Security Deposit demanded", "critical"),
    (r"refundable\s+deposit", "Refundable Deposit claim (common advance-fee tactic)", "critical"),
    (r"laptop\s+(?:courier|delivery|security|charges?)", "Laptop courier/delivery fee demanded", "critical"),
    (r"training\s+(?:fee|charges|cost)", "Upfront Training Fee required", "high"),
    (r"processing\s+(?:fee|charges?)", "Processing/Administrative Fee", "high"),
    (r"document\s+verification\s+charges?", "Document verification charges", "high"),
    (r"gateway\s+charges?", "Payment Gateway charges", "high"),
    (r"pay\s+via\s+upi", "Direct UPI payment requested for onboarding", "critical"),
    (r"google\s+play\s+(?:recharge|card|code)", "Gift Card / Voucher payment requested", "critical"),
    (r"usdt|crypto|bitcoin|binance", "Cryptocurrency transfer requested", "critical"),
    (r"telegram\s+(?:channel|id|group|interview|hr|task)", "Interview or tasks conducted via Telegram", "high"),
    (r"whatsapp\s+(?:interview|task|hiring|hr)", "Sole communication via WhatsApp group/number", "medium"),
    (r"daily\s+earning\s+of\s+rs", "Unrealistic daily payout promise", "high"),
    (r"data\s+entry\s+task.*deposit", "Data entry task requiring security deposit", "critical"),
    (r"bank\s+account\s+details\s+before\s+interview", "Premature bank account details request", "critical"),
]

# Common roles
ROLE_PATTERNS = [
    r"(?:software\s+engineer(?:ing)?(?:\s+intern)?|frontend\s+developer|backend\s+developer|full\s*stack\s+developer)",
    r"(?:data\s+analyst|data\s+scientist|machine\s+learning\s+intern|ai\s+intern)",
    r"(?:data\s+entry(?:\s+operator|\s+intern)?|typing\s+work|form\s+filling|sms\s+sending)",
    r"(?:product\s+manager\s+intern|ui/ux\s+designer|graphic\s+designer)",
    r"(?:business\s+development\s+intern|bda|sales\s+intern|marketing\s+intern)",
    r"(?:hr\s+intern|human\s+resources\s+trainee|talent\s+acquisition\s+intern)",
    r"(?:content\s+writer|technical\s+writer|social\s+media\s+intern)",
]


def extract_entities(text: str, explicit_company: str = "", explicit_domain: str = "",
                     explicit_role: str = "", explicit_email: str = "") -> Dict[str, Any]:
    """
    Extracts structured entities, contact vectors, compensation claims, and red-flag signals.
    Combines text parsing with optional user-supplied explicit fields.
    """
    cleaned_text = text.strip() if text else ""
    full_context = f"{cleaned_text} {explicit_company} {explicit_domain} {explicit_role} {explicit_email}"

    # 1. Company Name
    company = explicit_company.strip()
    if not company:
        company = _extract_company_name(cleaned_text)

    # 2. Domains / URLs
    domain = _clean_domain(explicit_domain.strip())
    extracted_urls = _extract_urls(full_context)
    if not domain and extracted_urls:
        domain = _clean_domain(extracted_urls[0])

    # 3. Emails & Recruiter Channels
    emails = _extract_emails(full_context)
    if explicit_email.strip() and explicit_email.strip() not in emails:
        emails.insert(0, explicit_email.strip())

    email_domains = []
    has_free_email = False
    for em in emails:
        parts = em.split("@")
        if len(parts) == 2:
            ed = parts[1].lower()
            email_domains.append(ed)
            if ed in FREE_EMAIL_DOMAINS:
                has_free_email = True

    # 4. Messaging channels (Telegram, WhatsApp)
    telegram_handles = _extract_telegram_handles(full_context)
    whatsapp_mentions = _extract_whatsapp_mentions(full_context)

    # 5. Role Title
    role = explicit_role.strip()
    if not role:
        role = _extract_role(cleaned_text)

    # 6. Compensation Claims
    compensation = _extract_compensation(cleaned_text)

    # 7. Red Flag Trigger Words
    triggers = _extract_triggers(cleaned_text)

    # 8. Brand Spoofing Check
    spoof_check = _check_brand_spoofing(company, domain, email_domains)

    # Infer domain from email if domain still empty and email is custom domain
    if not domain and email_domains and not has_free_email:
        domain = email_domains[0]

    # Infer company from domain if company still empty
    if not company and domain:
        company = _infer_company_from_domain(domain)

    return {
        "company_name": company or "Unknown Company",
        "domain": domain,
        "extracted_urls": extracted_urls,
        "role_title": role or "Intern / Trainee",
        "emails": emails,
        "email_domains": list(set(email_domains)),
        "has_free_email": has_free_email,
        "telegram_handles": telegram_handles,
        "has_telegram": bool(telegram_handles or "telegram" in cleaned_text.lower()),
        "has_whatsapp": bool(whatsapp_mentions or "whatsapp" in cleaned_text.lower()),
        "compensation": compensation,
        "red_flag_triggers": triggers,
        "brand_spoof_alert": spoof_check,
        "raw_text_length": len(cleaned_text),
    }


def _extract_company_name(text: str) -> str:
    """Heuristic extraction of company name from text."""
    if not text:
        return ""

    # Check explicit field patterns in text
    field_match = re.search(
        r"(?:Company(?:\s+Name)?|Organization|Employer|Firm|Hiring\s+Company)\s*[:\-–]\s*([A-Za-z0-9\s&.,'-]{2,50})",
        text,
        re.IGNORECASE,
    )
    if field_match:
        cand = field_match.group(1).strip()
        cand = re.split(r"[\n\r|,;]", cand)[0].strip()
        if len(cand) >= 2:
            return cand

    # Pattern: "[Company] is hiring / is looking for"
    hiring_match = re.search(
        r"(?:^|[\n\r.]\s*)([A-Z][A-Za-z0-9\s&]{2,40}?)\s+(?:is hiring|is looking|is offering|announces|has openings)",
        text,
    )
    if hiring_match:
        return hiring_match.group(1).strip()

    # Pattern: "Welcome to [Company]" or "Join [Company]" or "Offer from [Company]"
    offer_match = re.search(
        r"(?:Welcome\s+to|Join\s+our\s+team\s+at|Offer\s+Letter\s+(?:from|by)|Opportunity\s+at)\s+([A-Z][A-Za-z0-9\s&]{2,35})",
        text,
    )
    if offer_match:
        return offer_match.group(1).strip()

    # Pattern: "at [Company] as a"
    at_match = re.search(r"\bat\s+([A-Z][A-Za-z0-9&]{2,30}(?:\s+[A-Z][A-Za-z0-9&]{2,20})?)\s+(?:as|for|is|are)\b", text)
    if at_match:
        return at_match.group(1).strip()

    # Check known enterprise brand names in text
    text_lower = text.lower()
    for brand_key, brand_info in KNOWN_ENTERPRISE_BRANDS.items():
        if re.search(rf"\b{re.escape(brand_key)}\b", text_lower):
            return brand_info["name"]

    return ""


def _extract_urls(text: str) -> List[str]:
    """Finds URLs and bare web addresses in text."""
    urls = []
    # Standard http/https URL
    matches = re.findall(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{2,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", text)
    for m in matches:
        clean = m.rstrip(".,;)>]")
        if clean not in urls:
            urls.append(clean)

    # Bare domains like www.xyz.com or xyz.co.in
    bare_matches = re.findall(r"\b(?:www\.)?([a-zA-Z0-9-]{2,40}\.(?:com|in|org|co\.in|io|tech|ai|net|edu))\b", text, re.IGNORECASE)
    for bm in bare_matches:
        full = f"https://{bm}"
        if full not in urls:
            urls.append(full)

    return urls


def _clean_domain(domain_str: str) -> str:
    """Strips protocols, paths, and www to return clean hostname."""
    if not domain_str:
        return ""
    d = domain_str.strip()
    if not d.startswith("http://") and not d.startswith("https://"):
        d = "https://" + d
    try:
        parsed = urlparse(d)
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        # Remove port if any
        host = host.split(":")[0]
        return host
    except Exception:
        return ""


def _extract_emails(text: str) -> List[str]:
    """Extracts email addresses from text."""
    matches = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    seen = set()
    res = []
    for m in matches:
        em = m.lower()
        if em not in seen:
            seen.add(em)
            res.append(em)
    return res


def _extract_telegram_handles(text: str) -> List[str]:
    """Extracts Telegram mentions, t.me links, and usernames."""
    handles = []
    tme = re.findall(r"t\.me/([a-zA-Z0-9_]{4,32})", text, re.IGNORECASE)
    for h in tme:
        handles.append(f"@{h}")

    tg_mentions = re.findall(r"(?:telegram|tg)\s*[:\-–]?\s*@?([a-zA-Z0-9_]{4,32})", text, re.IGNORECASE)
    for m in tg_mentions:
        val = f"@{m.lstrip('@')}"
        if val not in handles:
            handles.append(val)

    return handles


def _extract_whatsapp_mentions(text: str) -> List[str]:
    """Extracts WhatsApp communication indicators."""
    wa = []
    if "whatsapp" in text.lower() or "wa.me" in text.lower():
        # Check for phone numbers nearby
        nums = re.findall(r"(?:whatsapp|contact|wa)\s*[:\-–]?\s*(\+?91[\s-]?\d{10}|\d{10})", text, re.IGNORECASE)
        for n in nums:
            wa.append(n.strip())
        if not wa:
            wa.append("WhatsApp channel mentioned")
    return wa


def _extract_role(text: str) -> str:
    """Identifies role or designation from text."""
    field_match = re.search(
        r"(?:Role|Position|Job\s+Title|Designation|Opportunity)\s*[:\-–]\s*([A-Za-z0-9\s/&()-]{3,50})",
        text,
        re.IGNORECASE,
    )
    if field_match:
        cand = field_match.group(1).strip()
        cand = re.split(r"[\n\r|,;]", cand)[0].strip()
        if len(cand) >= 3:
            return cand

    # Search common role patterns
    for pat in ROLE_PATTERNS:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(0).title()

    return ""


def _extract_compensation(text: str) -> Dict[str, Any]:
    """Extracts compensation/stipend claims and detects suspicious wage indicators."""
    claim = ""
    suspicious = False
    details = ""

    # Matches ₹50,000, Rs. 25,000, 10 LPA, 15,000/month
    stipend_match = re.search(
        r"(?:₹|Rs\.?|INR)\s*([\d,]+(?:\s*-\s*[\d,]+)?)\s*(?:/month|per\s+month|pm|stipend|daily|per\s+day|lpa)?",
        text,
        re.IGNORECASE,
    )
    lpa_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:LPA|lakhs?\s+per\s+annum)", text, re.IGNORECASE)

    if stipend_match:
        claim = stipend_match.group(0).strip()
    elif lpa_match:
        claim = f"{lpa_match.group(1)} LPA"

    # Suspicious compensation check: high payout for low skill work
    is_data_entry = bool(re.search(r"data\s+entry|typing|sms\s+sending|form\s+filling|copy\s+paste", text, re.IGNORECASE))
    high_pay_regex = re.search(r"(?:₹|Rs\.?|INR)\s*([3-9]\d{4,}|[1-9]\d{5,})", text, re.IGNORECASE)

    if is_data_entry and high_pay_regex:
        suspicious = True
        details = "Unrealistically high stipend promised for simple typing/data-entry tasks (classic advance-fee bait)."
    elif "daily earning" in text.lower() or "earn per day" in text.lower():
        suspicious = True
        details = "Guaranteed daily payout claim without formal employment terms."

    return {
        "claimed_amount": claim,
        "is_suspicious_compensation": suspicious,
        "reason": details,
    }


def _extract_triggers(text: str) -> List[Dict[str, str]]:
    """Identifies critical red flag trigger patterns in text."""
    triggers = []
    lowered = text.lower()

    for pattern, description, severity in SUSPICIOUS_FEE_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            # Extract surrounding context for explainability
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            snippet = text[start:end].strip().replace("\n", " ")

            triggers.append({
                "pattern": match.group(0),
                "label": description,
                "severity": severity,
                "context_snippet": f"...{snippet}...",
            })

    return triggers


def _check_brand_spoofing(company: str, domain: str, email_domains: List[str]) -> Optional[Dict[str, Any]]:
    """
    Checks if opportunity claims to be a well-known MNC / enterprise brand
    while operating from an unrelated or spoofed domain.
    """
    if not company:
        return None

    comp_lower = company.lower()
    for brand_key, brand_info in KNOWN_ENTERPRISE_BRANDS.items():
        if brand_key in comp_lower:
            valid_domains = brand_info["domains"]

            # If user has a domain, check if it matches valid domains with strict DNS label boundaries
            if domain:
                is_valid = any(is_valid_dns_match(domain, vd) for vd in valid_domains)
                if not is_valid:
                    return {
                        "is_spoof": True,
                        "brand_claimed": brand_info["name"],
                        "actual_domain": domain,
                        "legitimate_domains": valid_domains,
                        "warning": (
                            f"Opportunity claims affiliation with '{brand_info['name']}', but uses "
                            f"unverified domain '{domain}'. Legitimate corporate domain is '{valid_domains[0]}'."
                        ),
                    }

            # Check email domains
            for ed in email_domains:
                if ed in FREE_EMAIL_DOMAINS:
                    return {
                        "is_spoof": True,
                        "brand_claimed": brand_info["name"],
                        "actual_domain": ed,
                        "legitimate_domains": valid_domains,
                        "warning": (
                            f"Opportunity claims affiliation with '{brand_info['name']}', but recruiter uses "
                            f"a free consumer email address (@{ed}). Enterprise recruiters use corporate domain emails."
                        ),
                    }
                is_valid_email = any(is_valid_dns_match(ed, vd) for vd in valid_domains)
                if not is_valid_email:
                    return {
                        "is_spoof": True,
                        "brand_claimed": brand_info["name"],
                        "actual_domain": ed,
                        "legitimate_domains": valid_domains,
                        "warning": (
                            f"Recruiter email domain '@{ed}' does not match official '{brand_info['name']}' corporate domain."
                        ),
                    }

    return None


def is_valid_dns_match(candidate_domain: str, authoritative_domain: str) -> bool:
    """
    Checks if candidate_domain is equal to authoritative_domain,
    or a legitimate DNS subdomain of authoritative_domain.
    Respects strict DNS label boundaries.

    Examples:
    - candidate="tcs.com", authoritative="tcs.com" -> True
    - candidate="careers.tcs.com", authoritative="tcs.com" -> True
    - candidate="tcs.com.attacker.example", authoritative="tcs.com" -> False
    - candidate="evil-tcs.com", authoritative="tcs.com" -> False
    - candidate="tcs.co", authoritative="tcs.com" -> False
    """
    if not candidate_domain or not authoritative_domain:
        return False
    cand = _clean_domain(candidate_domain).lower().rstrip(".")
    auth = _clean_domain(authoritative_domain).lower().rstrip(".")
    if not cand or not auth:
        return False
    if cand == auth:
        return True
    return cand.endswith("." + auth)


def are_domains_dns_affiliated(domain_1: str, domain_2: str) -> bool:
    """
    Checks if domain_1 equals domain_2, or if one is a valid DNS subdomain of the other.
    Never uses substring matching; strictly respects DNS label boundaries.
    """
    return is_valid_dns_match(domain_1, domain_2) or is_valid_dns_match(domain_2, domain_1)


def is_recruiter_email_domain_affiliated(email_domain: str, company_domain: str) -> bool:
    """
    Verifies that the recruiter's email domain belongs to the claimed corporate domain
    or a legitimate subdomain thereof.
    E.g. recruiter@mail.tcs.com or recruiter@tcs.com for company tcs.com.
    Prevents lookalikes like recruiter@tcs.com.attacker.example or recruiter@tcs-careers.com.
    """
    return is_valid_dns_match(email_domain, company_domain)


def _infer_company_from_domain(domain: str) -> str:
    """Derives a human-readable company name candidate from domain."""
    if not domain:
        return ""
    root = domain.split(".")[0]
    return root.replace("-", " ").replace("_", " ").title()

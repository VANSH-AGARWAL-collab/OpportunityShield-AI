"""
OpportunityShield AI - Benchmark Cases
Curated high-fidelity investigation benchmark datasets representing realistic scenarios
faced by Indian students and jobseekers. Clearly labeled as benchmark reference cases.
"""

from typing import Dict, Any, List

BENCHMARK_CASES: Dict[str, Dict[str, Any]] = {
    "apex_scam": {
        "id": "apex_scam",
        "title": "Advance-Fee Laptop Deposit Scam (Apex Tech Solutions)",
        "badge": "High Risk Scam",
        "description": "Targeted WhatsApp/Telegram offer demanding ₹2,500 laptop security deposit via UPI for a remote data entry role.",
        "input_text": """
Company: Apex Tech Solutions
Role: Remote Python & Data Entry Trainee
Stipend: ₹75,000 / month
Location: Remote (Work From Home)
Contact: hr.apextechcareers@gmail.com
Telegram: @apex_hr_onboarding
Website: http://apextech-careers-india.online

Offer Details:
Congratulations! You have been selected for the Remote Trainee role at Apex Tech Solutions.
We will ship a company-configured Dell Latitude laptop and high-speed Wi-Fi dongle to your residence.
Before courier dispatch, candidate must transfer a 100% refundable security deposit of ₹2,500 via UPI (GooglePay / PhonePe) to complete document verification and hardware insurance.
Deposit will be refunded in your first monthly stipend payout.
Connect with Senior HR Priya on Telegram @apex_hr_onboarding to receive the UPI QR code.
        """.strip(),
        "explicit_fields": {
            "company": "Apex Tech Solutions",
            "domain": "apextech-careers-india.online",
            "role": "Remote Python & Data Entry Trainee",
            "email": "hr.apextechcareers@gmail.com",
        },
        "serpapi_results": {
            "google_search": [
                {
                    "title": "Apex Tech Solutions Job Scam Alert - Consumer Complaints Court",
                    "link": "https://www.consumercomplaints.in/complaints/apex-tech-solutions-c294819.html",
                    "snippet": "Beware of Apex Tech Solutions asking ₹2,500 for laptop courier fee and document verification on Telegram. After UPI payment, they blocked my number and deleted the Telegram chat.",
                    "source": "Consumer Complaints India",
                },
                {
                    "title": "Fake Data Entry Jobs demanding UPI Security Deposits - Reddit r/developersIndia",
                    "link": "https://reddit.com/r/developersIndia/comments/fake_internship_deposit_warning",
                    "snippet": "Received an offer from apextech-careers-india.online promising 75k stipend for typing work. They ask for refundable courier deposit. Classic advance fee fraud targeting college students.",
                    "source": "Reddit",
                },
                {
                    "title": "Apex Tech Solutions - Website Domain Registration Details",
                    "link": "https://whois.domaintools.com/apextech-careers-india.online",
                    "snippet": "Domain apextech-careers-india.online was registered 14 days ago. Privacy protected registrant. Zero corporate MCA records found.",
                    "source": "Whois Lookup",
                },
                {
                    "title": "Advisory on Fake Employment Letters - National Cyber Crime Reporting Portal",
                    "link": "https://cybercrime.gov.in/Webform/Crime_EmploymentFrauds.aspx",
                    "snippet": "Citizens are advised that genuine companies never demand security deposits, courier fees, or gate charges via personal UPI IDs or Telegram channels.",
                    "source": "National Cyber Crime Reporting Portal",
                },
            ],
            "google_news": [
                {
                    "title": "Cyber Police bust fake work-from-home syndicate charging laptop security fees",
                    "link": "https://timesofindia.indiatimes.com/city/bengaluru/cyber-cell-busts-job-fraud-gang/articleshow/99823120.cms",
                    "snippet": "Bengaluru Cyber Crime Police arrested three individuals running dummy portals pretending to offer data entry jobs while collecting refundable laptop deposits from students.",
                    "source": "Times of India",
                    "date": "3 days ago",
                }
            ],
            "google_jobs": [
                {
                    "title": "Junior Python Intern",
                    "company_name": "Credgenics",
                    "location": "Bengaluru, Karnataka, India",
                    "via": "via LinkedIn",
                    "detected_extensions": {"posted_at": "1 day ago", "schedule_type": "Full-time"},
                    "description": "Legitimate junior python role requiring Git, Django, and SQL knowledge. No application fees required.",
                },
                {
                    "title": "Data Analyst Trainee",
                    "company_name": "Mu Sigma",
                    "location": "Bengaluru, Karnataka, India",
                    "via": "via Naukri.com",
                    "detected_extensions": {"posted_at": "4 days ago", "schedule_type": "Full-time"},
                    "description": "Entry-level analytics trainee position for engineering and math graduates.",
                }
            ],
        },
    },

    "tcs_spoof": {
        "id": "tcs_spoof",
        "title": "Brand Impersonation & Lookalike Phishing (TCS Spoof)",
        "badge": "Brand Spoofing",
        "description": "Phishing offer using lookalike domain 'tcs-careers-onboarding.in' demanding ₹4,999 onboarding verification fee.",
        "input_text": """
Company: Tata Consultancy Services (TCS)
Role: Cloud Operations Engineer Trainee
Stipend: ₹45,000 / month
Location: Mumbai / Remote
Recruiter: onboarding.desk@tcs-careers-onboarding.in
Website: https://tcs-careers-onboarding.in/portal/verify

Candidate Notice:
You have been shortlisted for TCS Cloud Trainee Batch 2026 under the fast-track campus direct hiring initiative.
Please download your provisional letter of intent.
To confirm your seat in the induction batch, a mandatory Training Infrastructure & Medical Verification fee of ₹4,999 must be paid via our onboarding payment portal.
Official TCS Email: onboarding.desk@tcs-careers-onboarding.in
        """.strip(),
        "explicit_fields": {
            "company": "Tata Consultancy Services",
            "domain": "tcs-careers-onboarding.in",
            "role": "Cloud Operations Engineer Trainee",
            "email": "onboarding.desk@tcs-careers-onboarding.in",
        },
        "serpapi_results": {
            "google_search": [
                {
                    "title": "Tata Consultancy Services Official Website - Global IT Services",
                    "link": "https://www.tcs.com",
                    "snippet": "TCS is a global leader in IT services, consulting & business solutions. Official domain: tcs.com. Explore official careers at ibegin.tcs.com.",
                    "source": "TCS Official Portal",
                },
                {
                    "title": "TCS Warning: Beware of Fake Job Offers and Fraudulent Communications",
                    "link": "https://www.tcs.com/careers/fraud-alert",
                    "snippet": "Official TCS Disclaimer: TCS does not ask for money at any stage of the recruitment process. All official emails originate strictly from '@tcs.com'. Do not trust lookalike domains.",
                    "source": "TCS Fraud Advisory",
                },
                {
                    "title": "Freshers duped by fake TCS onboarding domains demanding medical fee",
                    "link": "https://www.thehindu.com/news/national/freshers-warned-against-fake-it-placement-letters/article668912.ece",
                    "snippet": "Cyber crime cells register complaints against spoofed domains mimicking premier IT services companies like TCS and Infosys asking for verification fees.",
                    "source": "The Hindu",
                },
                {
                    "title": "Whois record for tcs-careers-onboarding.in",
                    "link": "https://whois.inregistry.net/tcs-careers-onboarding.in",
                    "snippet": "Domain registered recently via commercial registrar. Not owned or authorized by Tata Sons Private Limited.",
                    "source": "INRegistry Whois",
                },
            ],
            "google_news": [
                {
                    "title": "IT Giants reiterate zero-fee recruitment policy as phishing attempts rise",
                    "link": "https://economictimes.indiatimes.com/tech/ites/tcs-infosys-wipro-warn-candidates-against-fraudulent-job-offers/articleshow/102914561.cms",
                    "snippet": "Indian IT majors issue stern advisories warning engineering students against paying onboarding or training fees to unverified intermediaries.",
                    "source": "The Economic Times",
                    "date": "1 week ago",
                }
            ],
            "google_jobs": [
                {
                    "title": "TCS NQT Fresher Hiring - Trainee Engineer",
                    "company_name": "Tata Consultancy Services",
                    "location": "India (Multiple Locations)",
                    "via": "via TCS NextStep / LinkedIn",
                    "detected_extensions": {"posted_at": "2 days ago", "schedule_type": "Full-time"},
                    "description": "Official TCS National Qualifier Test (NQT) campus recruitment. Registration is free on official TCS NextStep portal.",
                }
            ],
        },
    },

    "hasura_legit": {
        "id": "hasura_legit",
        "title": "Legitimate High-Growth Startup (Hasura Intern)",
        "badge": "Legitimate Opportunity",
        "description": "Authentic GraphQL engineering internship with verifiable corporate footprint, matching corporate email, and zero fee demands.",
        "input_text": """
Company: Hasura
Role: Software Engineering Intern (Backend / GraphQL)
Stipend: ₹60,000 / month
Location: Bengaluru / Remote
Website: https://hasura.io
Recruiter: talent@hasura.io

Job Description:
Hasura is looking for passionate Software Engineering Interns to join our core engine team.
You will work on our high-performance GraphQL and metadata engine written in Haskell and Go.
Requirements:
- Strong problem-solving skills in data structures and algorithms.
- Experience with databases (PostgreSQL, MySQL).
- Familiarity with Git and distributed systems.
Process:
1. Technical take-home assessment
2. Architecture discussion
3. Culture fit conversation
No fee or deposit is ever charged at any step.
Apply directly via our Greenhouse portal: https://hasura.io/careers
        """.strip(),
        "explicit_fields": {
            "company": "Hasura",
            "domain": "hasura.io",
            "role": "Software Engineering Intern (Backend / GraphQL)",
            "email": "talent@hasura.io",
        },
        "serpapi_results": {
            "google_search": [
                {
                    "title": "Hasura - Instant GraphQL APIs on Your Data",
                    "link": "https://hasura.io",
                    "snippet": "Hasura makes your data instantly accessible over GraphQL and REST APIs. Used by thousands of companies worldwide. Headquarters in San Francisco and Bengaluru.",
                    "source": "Hasura Official Website",
                },
                {
                    "title": "Careers at Hasura - Open Roles in Engineering and Product",
                    "link": "https://hasura.io/careers",
                    "snippet": "Explore internships and full-time roles at Hasura. Work remotely or from our Bengaluru engineering office. Competitive compensation, health insurance, and learning stipend.",
                    "source": "Hasura Careers",
                },
                {
                    "title": "Hasura GitHub Repository - GraphQL Engine (30k+ Stars)",
                    "link": "https://github.com/hasura/graphql-engine",
                    "snippet": "Fast, instant GraphQL & REST APIs on databases with fine-grained access control. Open-source flagship project with global contributor base.",
                    "source": "GitHub",
                },
                {
                    "title": "Hasura Company Profile - Crunchbase",
                    "link": "https://www.crunchbase.com/organization/hasura",
                    "snippet": "Hasura raised $100M in Series C led by Greenoaks. Backed by Lightspeed Venture Partners, Vertex Ventures, and Nexus Venture Partners.",
                    "source": "Crunchbase",
                },
            ],
            "google_news": [
                {
                    "title": "Hasura launches Data Delivery Network (DDN) for unified microservices",
                    "link": "https://techcrunch.com/2024/04/16/hasura-launches-ddn-next-gen-api-layer/",
                    "snippet": "Enterprise GraphQL pioneer Hasura introduces next-generation data federation architecture for global development teams.",
                    "source": "TechCrunch",
                    "date": "2 months ago",
                }
            ],
            "google_jobs": [
                {
                    "title": "Software Engineer Intern (Backend)",
                    "company_name": "Hasura",
                    "location": "Bengaluru, Karnataka, India (Remote)",
                    "via": "via Greenhouse / LinkedIn",
                    "detected_extensions": {"posted_at": "5 days ago", "schedule_type": "Internship"},
                    "description": "Internship opening in backend engineering. Work on database connectors, compiler tooling, and developer docs.",
                },
                {
                    "title": "Frontend Engineer Intern",
                    "company_name": "Postman",
                    "location": "Bengaluru, Karnataka, India",
                    "via": "via LinkedIn",
                    "detected_extensions": {"posted_at": "1 week ago", "schedule_type": "Internship"},
                    "description": "Comparable developer tooling internship in Bengaluru tech hub.",
                }
            ],
        },
    },

    "unindexed_entity": {
        "id": "unindexed_entity",
        "title": "Unregistered / Emerging Studio (NovaSphere Media)",
        "badge": "Needs Verification",
        "description": "Local boutique design shop with sparse online presence, no corporate registration found, but no explicit red flags or fee requests.",
        "input_text": """
Company: NovaSphere Media
Role: Social Media Graphic Design Intern
Stipend: ₹12,000 / month
Location: Pune (Hybrid)
Website: https://novaspheremedia.in
Email: contact@novaspheremedia.in

Details:
We are a newly formed independent boutique creative agency in Pune helping local D2C brands with Instagram reels, poster graphics, and Canva templates.
Duration: 3 months.
Requirements: Familiarity with Figma, Photoshop, and Adobe Premiere Pro.
Selection is based on portfolio review and a 30-minute design interview.
No application fee.
        """.strip(),
        "explicit_fields": {
            "company": "NovaSphere Media",
            "domain": "novaspheremedia.in",
            "role": "Social Media Graphic Design Intern",
            "email": "contact@novaspheremedia.in",
        },
        "serpapi_results": {
            "google_search": [
                {
                    "title": "NovaSphere Media - Creative Design Studio (Under Construction)",
                    "link": "https://novaspheremedia.in",
                    "snippet": "Welcome to NovaSphere Media. Creative design, branding and social media collateral for lifestyle brands in Pune. Portfolio coming soon.",
                    "source": "NovaSphere Portal",
                },
                {
                    "title": "NovaSphere Media - Instagram Business Profile",
                    "link": "https://www.instagram.com/novasphere_media",
                    "snippet": "Creative agency based in Pune, Maharashtra. 1,420 followers. Showcasing branding work and typography designs.",
                    "source": "Instagram",
                },
            ],
            "google_news": [],
            "google_jobs": [
                {
                    "title": "Graphic Design Intern",
                    "company_name": "Schbang",
                    "location": "Mumbai / Pune, India",
                    "via": "via Internshala",
                    "detected_extensions": {"posted_at": "3 days ago", "schedule_type": "Internship"},
                    "description": "Comparable creative agency design internship sample for visual artists.",
                }
            ],
        },
    },
}


def get_benchmark(case_id: str) -> Dict[str, Any]:
    """Retrieves a specific benchmark case by ID or returns the first case as default."""
    return BENCHMARK_CASES.get(case_id, BENCHMARK_CASES["apex_scam"])


def list_benchmarks() -> List[Dict[str, Any]]:
    """Returns metadata for all benchmark cases for UI display."""
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "badge": c["badge"],
            "description": c["description"],
            "company": c["explicit_fields"]["company"],
            "role": c["explicit_fields"]["role"],
        }
        for c in BENCHMARK_CASES.values()
    ]


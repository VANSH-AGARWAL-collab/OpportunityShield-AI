"""
OpportunityShield AI - Flask Application Entry Point
Competition-ready AI Opportunity Investigation Platform for the SerpApi India Hackathon 2026.
"""

import logging
from flask import Flask, render_template, request, jsonify
from config import Config
from services.extractor_service import extract_entities
from services.serpapi_service import SerpApiService
from services.investigation_engine import InvestigationEngine
from services.benchmark_data import BENCHMARK_CASES, list_benchmarks, get_benchmark
from services import database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("OpportunityShield.App")

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
database.init_db()

# Services
serpapi_service = SerpApiService()
engine = InvestigationEngine()


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"success": False, "error": "Request payload exceeds 1MB limit."}), 413


@app.route("/")
def index():
    """Renders the main dashboard interface."""
    return render_template(
        "index.html",
        has_serpapi_key=Config.has_serpapi_key(),
    )


@app.route("/api/extract", methods=["POST"])
def api_extract():
    """
    Extracts entities, contact channels, and payment triggers from raw text.
    Provides real-time feedback in the workspace before starting investigation.
    """
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", ""))[:50000]
    explicit_company = str(data.get("company", ""))[:120]
    explicit_domain = str(data.get("domain", ""))[:120]
    explicit_role = str(data.get("role", ""))[:120]
    explicit_email = str(data.get("email", ""))[:120]

    extracted = extract_entities(
        text=text,
        explicit_company=explicit_company,
        explicit_domain=explicit_domain,
        explicit_role=explicit_role,
        explicit_email=explicit_email,
    )
    return jsonify({"success": True, "extracted": extracted})


@app.route("/api/investigate", methods=["POST"])
def api_investigate():
    """
    Primary investigation endpoint:
    1. Extracts candidate entities & red-flag triggers.
    2. Executes multi-engine SerpApi queries (Google Search, News, Jobs).
    3. Normalizes and synthesizes evidentiary findings.
    4. Evaluates explainable heuristic rules.
    5. Saves report to SQLite persistence.
    """
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", ""))[:50000]
    explicit_company = str(data.get("company", ""))[:120]
    explicit_domain = str(data.get("domain", ""))[:120]
    explicit_role = str(data.get("role", ""))[:120]
    explicit_email = str(data.get("email", ""))[:120]
    benchmark_case_id = str(data.get("benchmark_case_id", ""))[:50]

    # If benchmark case specified, auto-populate any empty fields from benchmark definition
    if benchmark_case_id and benchmark_case_id in BENCHMARK_CASES:
        bm = BENCHMARK_CASES[benchmark_case_id]
        if not text:
            text = bm.get("input_text", "")
        ef = bm.get("explicit_fields", {})
        if not explicit_company:
            explicit_company = ef.get("company", "")
        if not explicit_domain:
            explicit_domain = ef.get("domain", "")
        if not explicit_role:
            explicit_role = ef.get("role", "")
        if not explicit_email:
            explicit_email = ef.get("email", "")

    # 1. Entity Extraction
    extracted = extract_entities(
        text=text,
        explicit_company=explicit_company,
        explicit_domain=explicit_domain,
        explicit_role=explicit_role,
        explicit_email=explicit_email,
    )

    company = extracted["company_name"]
    domain = extracted["domain"]
    role = extracted["role_title"]

    if not company or company == "Unknown Company":
        if not text and not benchmark_case_id:
            return jsonify({
                "success": False,
                "error": "Please provide an opportunity description or company name to investigate.",
            }), 400

    logger.info(f"Initiating investigation for company='{company}', role='{role}', benchmark='{benchmark_case_id}'")

    # 2. SerpApi Multi-Engine Search
    search_results = serpapi_service.search_all_engines(
        company_name=company,
        domain=domain,
        role_title=role,
        benchmark_case_id=benchmark_case_id,
    )

    # 3. Investigation Analysis & Heuristic Scoring
    report = engine.analyze(extracted=extracted, search_results=search_results)

    # 4. Save to Database
    inv_id = database.save_investigation(report)
    report["id"] = inv_id

    return jsonify({
        "success": True,
        "investigation_id": inv_id,
        "report": report,
    })


@app.route("/api/benchmarks", methods=["GET"])
def api_benchmarks():
    """Returns list of curated benchmark reference cases."""
    return jsonify({
        "success": True,
        "benchmarks": list_benchmarks(),
    })


@app.route("/api/benchmarks/<case_id>", methods=["GET"])
def api_benchmark_detail(case_id):
    """Retrieves full details for a specific benchmark case."""
    bm = BENCHMARK_CASES.get(case_id)
    if not bm:
        return jsonify({"success": False, "error": "Benchmark case not found"}), 404
    return jsonify({"success": True, "benchmark": bm})


@app.route("/api/history", methods=["GET"])
def api_history():
    """Lists past investigations from SQLite persistence."""
    limit = request.args.get("limit", 50, type=int)
    history = database.list_investigations(limit=limit)
    return jsonify({"success": True, "history": history})


@app.route("/api/history/<inv_id>", methods=["GET"])
def api_history_item(inv_id):
    """Retrieves a specific past investigation report."""
    item = database.get_investigation(inv_id)
    if not item:
        return jsonify({"success": False, "error": "Investigation not found"}), 404
    return jsonify({"success": True, "report": item})


@app.route("/api/history/<inv_id>", methods=["DELETE"])
def api_delete_history(inv_id):
    """Deletes an investigation from history."""
    success = database.delete_investigation(inv_id)
    return jsonify({"success": success})


@app.route("/api/history/clear", methods=["POST"])
def api_clear_history():
    """Clears all investigation history."""
    database.clear_all_investigations()
    return jsonify({"success": True})


@app.route("/api/status", methods=["GET"])
def api_status():
    """Returns platform health and SerpApi configuration status without exposing sensitive key data."""
    has_key = Config.has_serpapi_key()
    history_items = database.list_investigations(limit=100)

    return jsonify({
        "success": True,
        "status": "online",
        "serpapi_configured": has_key,
        "serpapi_status_label": "Configured (Server-Side)" if has_key else "Not Configured (Demo Mode Available)",
        "total_investigations": len(history_items),
        "app_name": "OpportunityShield AI",
        "track": "Knowledge & Public Interest",
        "version": "1.0.0",
    })


if __name__ == "__main__":
    logger.info(f"Starting OpportunityShield AI on port {Config.PORT} (Debug={Config.DEBUG})...")
    app.run(host="127.0.0.1", port=Config.PORT, debug=Config.DEBUG)

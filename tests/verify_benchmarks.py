"""
OpportunityShield AI — Automated Benchmark Verification Script
Tests all 4 curated archetype cases through API investigation pipeline.
Supports both live HTTP server and Flask in-process test client.
"""

import sys
import os
import json
import requests

# Ensure repository root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

base = 'http://127.0.0.1:5000'
cases = ['apex_scam', 'tcs_spoof', 'hasura_legit', 'unindexed_entity']

print("=" * 80)
print("OpportunityShield AI — Automated Benchmark Verification")
print("=" * 80)

use_http = True
try:
    requests.get(f"{base}/api/status", timeout=1)
except Exception:
    use_http = False
    print("(*) Local HTTP server not running on port 5000; executing via Flask application context.")

with app.test_client() as client:
    for c in cases:
        if use_http:
            res = requests.post(f'{base}/api/investigate', json={'benchmark_case_id': c}).json()
        else:
            resp = client.post('/api/investigate', json={'benchmark_case_id': c})
            res = json.loads(resp.data)

        assert res['success'] is True, f"Failed for {c}"
        rep = res['report']
        company = rep['metadata']['target_company']
        score = rep['assessment']['risk_score']
        label = rep['assessment']['label']
        sources = rep['metadata']['total_sources']
        warnings = len(rep['warning_signals'])
        positives = len(rep['positive_signals'])
        is_sim = rep['metadata'].get('is_benchmark_demonstration', False)
        sim_tag = "[Simulated]" if is_sim else "[Live]"
        print(f"[{c.upper():<16}] {company:<28} | Score: {score:>2}/100 | {label:<25} | {sim_tag} | Warn: {warnings} | Pos: {positives} | Sources: {sources}")

print("=" * 80)
print("All 4 benchmark archetypes verified successfully!")

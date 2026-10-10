/**
 * OpportunityShield AI — Report Renderer Module
 * Generates the 7-section investigation dossier, factor breakdown,
 * interactive evidence filtering, and export/print workflows.
 */

const ReportRenderer = {
  currentReport: null,
  activeFilterEngine: 'all',
  activeFilterStance: 'all',
  searchQuery: '',

  /**
   * Main render function for report container
   */
  render(containerId, report) {
    this.currentReport = report;
    const container = document.getElementById(containerId);
    if (!container) return;

    const metadata = report.metadata || {};
    const assessment = report.assessment || {};
    const positiveSignals = report.positive_signals || [];
    const warningSignals = report.warning_signals || [];
    const evidenceItems = report.evidence_items || [];
    const checklist = report.recommended_actions || [];
    const comparableJobs = report.comparable_jobs || [];

    const badgeColor = assessment.badge_color || 'amber';
    const riskScore = assessment.risk_score || 50;

    let html = `
      <div class="report-wrapper" id="investigation-report-dossier">
        
        <!-- Sticky Action Toolbar -->
        <div class="report-toolbar">
          <div class="toolbar-info">
            <span class="meta-pill">
              <svg class="icon-xs text-teal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
              <span>${this.formatDate(metadata.generated_at)}</span>
            </span>
            ${metadata.is_benchmark_demonstration ? `
              <span class="meta-pill" style="color: var(--teal-hover); border-color: rgba(14,165,233,0.4); background: rgba(14,165,233,0.1);">
                Simulated Benchmark Demonstration
              </span>
            ` : metadata.search_status === 'unconfigured_key' || metadata.search_status === 'search_failed' ? `
              <span class="meta-pill" style="color: var(--amber-primary); border-color: rgba(245,158,11,0.4); background: rgba(245,158,11,0.1);">
                Live Search Unavailable (Text Only)
              </span>
            ` : `
              <span class="meta-pill" style="color: var(--emerald-primary); border-color: rgba(16,185,129,0.3);">
                Live SerpApi Evidence
              </span>
            `}
          </div>
          <div class="toolbar-actions">
            <button type="button" class="btn btn-secondary btn-sm" id="btn-copy-report" title="Copy markdown summary">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
              <span>Copy Summary</span>
            </button>
            <button type="button" class="btn btn-secondary btn-sm" id="btn-export-json" title="Download JSON dossier">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
              <span>Export JSON</span>
            </button>
            <button type="button" class="btn btn-primary btn-sm" id="btn-print-report" title="Print or save as PDF">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9V2h12v7M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2M6 14h12v8H6z"/></svg>
              <span>Print / PDF</span>
            </button>
          </div>
        </div>

        <div class="report-content">

          ${metadata.is_benchmark_demonstration ? `
            <div class="alert-box alert-info" style="margin-bottom: 1.25rem; border-left: 4px solid var(--teal-primary);">
              <strong>Simulated Benchmark Demonstration</strong>: This report uses an illustrative synthetic test case for educational demonstration purposes. It does NOT represent live search engine results for an active company.
            </div>
          ` : ''}

          ${metadata.search_status === 'unconfigured_key' || metadata.search_status === 'search_failed' ? `
            <div class="alert-box alert-danger" style="margin-bottom: 1.25rem;">
              <strong>Live SerpApi Search Offline</strong>: ${this.escape(metadata.search_error || 'Live search queries could not be executed.')} Risk evaluation reflects only opportunity text analysis; external corporate presence could not be established.
            </div>
          ` : ''}

          <!-- Section A: Overview Banner -->
          <section class="report-section-overview" aria-label="Investigation Overview">
            <div class="overview-grid">
              <div class="overview-main">
                <div class="target-badge">
                  <svg class="icon-xs text-teal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                  <span>Forensic Investigation Subject</span>
                </div>
                <h2 class="target-company-title">${this.escape(metadata.target_company)}</h2>
                <div class="target-role-sub">${this.escape(metadata.opportunity_title)}</div>

                <div class="target-meta-pills">
                  <span class="meta-pill">
                    <strong>Claimed Domain:</strong> ${this.escape(metadata.target_domain || 'Not specified')}
                  </span>
                  <span class="meta-pill">
                    <strong>Recruiter Contact:</strong> ${this.escape(metadata.recruiter_email || 'Not specified')}
                  </span>
                  <span class="meta-pill">
                    <strong>Engines Queried:</strong> Google Search, News, Jobs
                  </span>
                </div>
              </div>

              <div class="overview-metrics">
                <div class="metric-row">
                  <span class="text-muted">Sources Retrieved:</span>
                  <span class="metric-val">${metadata.total_sources || 0}</span>
                </div>
                <div class="metric-row">
                  <span class="text-muted">Warning Flags:</span>
                  <span class="metric-val text-rose">${warningSignals.length}</span>
                </div>
                <div class="metric-row">
                  <span class="text-muted">Positive Signals:</span>
                  <span class="metric-val text-emerald">${positiveSignals.length}</span>
                </div>
                <div class="metric-row">
                  <span class="text-muted">Execution Latency:</span>
                  <span class="metric-val">${metadata.execution_time_seconds || 0.8}s</span>
                </div>
              </div>
            </div>
          </section>

          <!-- Section B: Overall Assessment & Factor Breakdown -->
          <section class="report-section-assessment" aria-label="Assessment & Heuristic Breakdown">
            <div class="assessment-banner">
              <div class="assessment-indicator-box">
                <div class="risk-score-circle score-circle-${badgeColor}">
                  <span class="score-num">${riskScore}</span>
                  <span class="score-denom">/ 100</span>
                </div>
                <div class="assessment-text">
                  <span class="assessment-label label-${badgeColor}">${this.escape(assessment.label)}</span>
                  <p class="assessment-summary-desc">${this.escape(assessment.summary)}</p>
                </div>
              </div>
            </div>

            <!-- Mathematical Formula Transparency -->
            <div class="factors-heading">
              <span>Auditable Heuristic Breakdown (Rule Factors & Citations)</span>
            </div>
            <p class="text-muted" style="font-size: 0.78rem; margin-block-end: 1rem;">
              <code>${this.escape(assessment.formula_explanation || '')}</code>
            </p>

            <div class="factor-grid">
              ${(assessment.factors || []).map(f => `
                <div class="factor-card factor-${f.type}">
                  <div class="factor-top">
                    <span class="factor-name">${this.escape(f.name)}</span>
                    <span class="factor-impact-badge">${this.escape(f.impact)} pts</span>
                  </div>
                  <p class="factor-rationale">${this.escape(f.rationale)}</p>
                  <div class="factor-citation">
                    <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
                    <span>Citation: ${this.escape(f.citation || 'SerpApi Record')}</span>
                  </div>
                </div>
              `).join('')}
            </div>
          </section>

          <!-- Sections C & D: Signals Dual Grid -->
          <div class="signals-dual-grid">
            
            <!-- Section C: Positive Signals -->
            <section class="signal-column" aria-label="Positive Indicators">
              <div class="signal-col-header">
                <svg class="icon-sm text-emerald" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
                <h3 class="text-emerald">Positive Legitimacy Signals (${positiveSignals.length})</h3>
              </div>
              <div class="signal-items-list">
                ${positiveSignals.length === 0 ? `
                  <div class="signal-item">
                    <span class="text-muted" style="font-size: 0.82rem; font-style: italic;">No verified positive signals discovered in public search indexing.</span>
                  </div>
                ` : positiveSignals.map(pos => `
                  <div class="signal-item">
                    <span class="signal-item-title">${this.escape(pos.title)}</span>
                    <p class="signal-item-desc">${this.escape(pos.description)}</p>
                    <span class="signal-item-source">Source: ${this.escape(pos.source)}</span>
                  </div>
                `).join('')}
              </div>
            </section>

            <!-- Section D: Warning Signals -->
            <section class="signal-column" aria-label="Warning Red Flags">
              <div class="signal-col-header">
                <svg class="icon-sm text-rose" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                <h3 class="text-rose">Observed Red Flags & Warning Signals (${warningSignals.length})</h3>
              </div>
              <div class="signal-items-list">
                ${warningSignals.length === 0 ? `
                  <div class="signal-item">
                    <span class="text-muted" style="font-size: 0.82rem; font-style: italic;">No critical advance-fee or domain impersonation warning flags detected.</span>
                  </div>
                ` : warningSignals.map(warn => `
                  <div class="signal-item" style="border-inline-start: 3px solid var(--rose-primary);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                      <span class="signal-item-title text-rose">${this.escape(warn.title)}</span>
                      <span class="check-badge badge-critical">${this.escape(warn.severity)}</span>
                    </div>
                    <p class="signal-item-desc">${this.escape(warn.description)}</p>
                    <span class="signal-item-source">Trigger Source: ${this.escape(warn.source)}</span>
                  </div>
                `).join('')}
              </div>
            </section>

          </div>

          <!-- Section E: Interactive Evidence Explorer -->
          <section class="report-section-explorer" aria-label="Evidence Explorer">
            <div class="explorer-header">
              <div class="explorer-title-group">
                <h3>Multi-Source Evidence Explorer</h3>
                <p>Verified SerpApi results across Google Search, News & Jobs. Filter by stance or engine.</p>
              </div>
              <div class="explorer-filter-controls">
                <input type="text" id="evidence-search-input" class="search-input-inline" placeholder="Search evidence snippets...">
                
                <select id="evidence-filter-engine" class="filter-select">
                  <option value="all">All Engines</option>
                  <option value="Google Search">Google Search</option>
                  <option value="Google News">Google News</option>
                  <option value="Google Jobs">Google Jobs</option>
                </select>

                <select id="evidence-filter-stance" class="filter-select">
                  <option value="all">All Stances</option>
                  <option value="supports">Supports</option>
                  <option value="contradicts">Contradicts / Adverse</option>
                  <option value="inconclusive">Inconclusive / Neutral</option>
                </select>
              </div>
            </div>

            <div class="evidence-cards-list" id="evidence-filtered-container">
              <!-- Rendered by this.renderEvidenceList() -->
            </div>
          </section>

          <!-- Section F: Actionable Checklist for Indian Applicants -->
          <section class="report-section-checklist" aria-label="Actionable Safety Checklist">
            <div class="checklist-header">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <svg class="icon-sm text-teal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
                <h3>Prioritized Applicant Verification Checklist (India Guidelines)</h3>
              </div>
              <p class="text-muted" style="font-size: 0.8rem;">Step-by-step verification protocols recommended before sending Aadhaar, PAN, or responding to offers.</p>
            </div>

            <div class="checklist-grid">
              ${checklist.map(item => `
                <div class="check-item">
                  <span class="check-badge badge-${item.status}">${this.escape(item.priority)}</span>
                  <div class="check-content">
                    <span class="check-title">${this.escape(item.action)}</span>
                    <p class="check-desc">${this.escape(item.details)}</p>
                  </div>
                </div>
              `).join('')}
            </div>
          </section>

          <!-- Section G: Comparable Google Jobs (Market Benchmark) -->
          <section class="report-section-jobs" aria-label="Comparable Market Opportunities">
            <div class="jobs-header">
              <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <svg class="icon-sm text-teal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>
                <h3>Comparable Verified Job Postings (Google Jobs Index)</h3>
              </div>
              <p class="text-muted" style="font-size: 0.8rem;">Independent market listings discovered via Google Jobs. Helps candidates cross-check realistic market standards.</p>
            </div>

            <div class="jobs-grid">
              ${comparableJobs.length === 0 ? `
                <div class="job-card">
                  <span class="text-muted" style="font-size: 0.82rem;">No active market job listings retrieved for this query.</span>
                </div>
              ` : comparableJobs.map(j => `
                <div class="job-card">
                  <div class="job-card-top">
                    <span class="job-title">${this.escape(j.title)}</span>
                    <span class="job-company">${this.escape(j.company_name)}</span>
                    <div class="job-meta-row">
                      <span>${this.escape(j.location || 'India')}</span>
                      <span>•</span>
                      <span>${this.escape(j.via || 'Google Jobs')}</span>
                    </div>
                  </div>
                  <p class="job-desc-preview">${this.escape(j.description_preview || '')}</p>
                  ${j.link ? `
                    <a href="${this.escape(j.link)}" target="_blank" rel="noopener noreferrer" class="evidence-title-link" style="font-size: 0.78rem;">
                      <span>Inspect Listing on Google Jobs</span>
                      <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                    </a>
                  ` : ''}
                </div>
              `).join('')}
            </div>
          </section>

        </div>
      </div>
    `;

    container.innerHTML = html;
    container.classList.remove('hidden');

    // Attach event listeners
    this.attachEventListeners();
    this.renderEvidenceList();

    // Smooth scroll into view
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  /**
   * Filters and renders evidence items in Section E
   */
  renderEvidenceList() {
    const container = document.getElementById('evidence-filtered-container');
    if (!container || !this.currentReport) return;

    let items = this.currentReport.evidence_items || [];

    // Filter by engine
    if (this.activeFilterEngine !== 'all') {
      items = items.filter(it => (it.engine || '').toLowerCase().includes(this.activeFilterEngine.toLowerCase()));
    }

    // Filter by stance
    if (this.activeFilterStance !== 'all') {
      items = items.filter(it => (it.stance || '').toLowerCase() === this.activeFilterStance.toLowerCase());
    }

    // Search query filter
    if (this.searchQuery) {
      const q = this.searchQuery.toLowerCase();
      items = items.filter(it => 
        (it.title || '').toLowerCase().includes(q) ||
        (it.snippet || '').toLowerCase().includes(q) ||
        (it.domain || '').toLowerCase().includes(q)
      );
    }

    if (items.length === 0) {
      container.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-muted); font-size: 0.88rem;">
          No evidence records match the selected engine or stance filters.
        </div>
      `;
      return;
    }

    container.innerHTML = items.map(item => `
      <div class="evidence-card">
        <div class="evidence-card-top">
          <a href="${this.escape(item.link || '#')}" target="_blank" rel="noopener noreferrer" class="evidence-title-link">
            <span>${this.escape(item.title)}</span>
            <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          </a>
          <span class="evidence-stance-badge stance-${item.stance}">
            ${this.escape(item.stance || 'inconclusive')}
          </span>
        </div>

        <p class="evidence-snippet">${this.escape(item.snippet)}</p>

        <div class="evidence-card-footer">
          <span class="evidence-engine-tag">
            <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
            <span>${this.escape(item.engine)} • ${this.escape(item.domain || 'External')}</span>
          </span>
          <span>Category: ${this.escape(item.category || 'Footprint')}</span>
        </div>
      </div>
    `).join('');
  },

  /**
   * Binds interactive buttons for filtering, copying, printing
   */
  attachEventListeners() {
    // Print
    const printBtn = document.getElementById('btn-print-report');
    if (printBtn) {
      printBtn.onclick = () => window.print();
    }

    // Export JSON
    const jsonBtn = document.getElementById('btn-export-json');
    if (jsonBtn) {
      jsonBtn.onclick = () => this.exportJSON();
    }

    // Copy Markdown Summary
    const copyBtn = document.getElementById('btn-copy-report');
    if (copyBtn) {
      copyBtn.onclick = () => this.copyMarkdownSummary();
    }

    // Filters
    const engineSelect = document.getElementById('evidence-filter-engine');
    if (engineSelect) {
      engineSelect.onchange = (e) => {
        this.activeFilterEngine = e.target.value;
        this.renderEvidenceList();
      };
    }

    const stanceSelect = document.getElementById('evidence-filter-stance');
    if (stanceSelect) {
      stanceSelect.onchange = (e) => {
        this.activeFilterStance = e.target.value;
        this.renderEvidenceList();
      };
    }

    const searchInput = document.getElementById('evidence-search-input');
    if (searchInput) {
      searchInput.oninput = (e) => {
        this.searchQuery = e.target.value.trim();
        this.renderEvidenceList();
      };
    }
  },

  /**
   * Exports full report as JSON download
   */
  exportJSON() {
    if (!this.currentReport) return;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.currentReport, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute('href', dataStr);
    const company = (this.currentReport.metadata.target_company || 'opportunity').toLowerCase().replace(/\s+/g, '_');
    dlAnchor.setAttribute('download', `opportunity_shield_${company}_report.json`);
    dlAnchor.click();
  },

  /**
   * Generates and copies structured markdown summary to clipboard
   */
  async copyMarkdownSummary() {
    if (!this.currentReport) return;
    const meta = this.currentReport.metadata;
    const assess = this.currentReport.assessment;
    const warnings = this.currentReport.warning_signals || [];
    const positives = this.currentReport.positive_signals || [];

    const md = `
# OpportunityShield AI — Investigation Summary
**Subject**: ${meta.target_company} — ${meta.opportunity_title}
**Date**: ${meta.generated_at}
**Assessment**: ${assess.label} (${assess.risk_score}/100 Risk Index)

## Key Findings:
- Total Sources Analyzed: ${meta.total_sources}
- Warning Flags Detected: ${warnings.length}
- Positive Signals Verified: ${positives.length}

## Assessment Rationale:
${assess.summary}

## Critical Warnings:
${warnings.map(w => `- [${w.severity}] **${w.title}**: ${w.description}`).join('\n') || '- None observed'}

## Positive Indicators:
${positives.map(p => `- [${p.strength}] **${p.title}**: ${p.description}`).join('\n') || '- None observed'}

*Report generated by OpportunityShield AI (SerpApi Hackathon 2026)*
`.trim();

    try {
      await navigator.clipboard.writeText(md);
      alert('Investigation summary copied to clipboard in Markdown format!');
    } catch (e) {
      console.error('Clipboard copy failed:', e);
    }
  },

  formatDate(isoString) {
    if (!isoString) return 'Just now';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return isoString;
    }
  },

  escape(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
};


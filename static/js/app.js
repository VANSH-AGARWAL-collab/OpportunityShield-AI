/**
 * OpportunityShield AI — Main Application Controller
 * Handles user interactions, real-time entity extraction, multi-step progress,
 * history management, benchmark scenarios, and accessible modals.
 */

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

const App = {
  activeView: 'workspace',
  inputMode: 'paste',
  extractDebounceTimer: null,
  isInvestigating: false,

  init() {
    this.bindNavigation();
    this.bindInputTabs();
    this.bindExtractionInputs();
    this.bindFormSubmission();
    this.bindBenchmarkPills();
    this.bindModals();
    this.loadHistoryCount();
    this.checkApiStatus();
  },

  /**
   * Sidebar Navigation Switches
   */
  bindNavigation() {
    const navWorkspace = document.getElementById('nav-workspace-btn');
    const navBenchmarks = document.getElementById('nav-benchmarks-btn');
    const navHistory = document.getElementById('nav-history-btn');

    if (navWorkspace) navWorkspace.onclick = () => this.switchView('workspace');
    if (navBenchmarks) navBenchmarks.onclick = () => {
      this.switchView('benchmarks');
      this.loadBenchmarksList();
    };
    if (navHistory) navHistory.onclick = () => {
      this.switchView('history');
      this.loadHistoryTable();
    };

    // Quick demo button in header
    const quickDemoBtn = document.getElementById('quick-demo-btn');
    if (quickDemoBtn) {
      quickDemoBtn.onclick = () => {
        this.switchView('workspace');
        this.loadBenchmarkIntoWorkspace('apex_scam');
      };
    }
  },

  switchView(viewName) {
    this.activeView = viewName;

    // Update nav items
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === viewName);
    });

    // Toggle content views
    const viewWorkspace = document.getElementById('view-workspace');
    const viewBenchmarks = document.getElementById('view-benchmarks');
    const viewHistory = document.getElementById('view-history');
    const titleEl = document.getElementById('current-view-title');

    if (viewWorkspace) viewWorkspace.classList.toggle('hidden', viewName !== 'workspace');
    if (viewBenchmarks) viewBenchmarks.classList.toggle('hidden', viewName !== 'benchmarks');
    if (viewHistory) viewHistory.classList.toggle('hidden', viewName !== 'history');

    if (titleEl) {
      if (viewName === 'workspace') titleEl.textContent = 'Investigation Workspace';
      if (viewName === 'benchmarks') titleEl.textContent = 'Benchmark Scenarios Catalog';
      if (viewName === 'history') titleEl.textContent = 'Past Investigations History';
    }
  },

  /**
   * Mode tabs: Paste vs Structured Fields
   */
  bindInputTabs() {
    const tabPaste = document.getElementById('tab-paste');
    const tabFields = document.getElementById('tab-fields');
    const pastePanel = document.getElementById('mode-paste-container');
    const fieldsPanel = document.getElementById('mode-fields-container');
    const clearBtn = document.getElementById('btn-clear-input');

    if (tabPaste && tabFields) {
      tabPaste.onclick = () => {
        this.inputMode = 'paste';
        tabPaste.classList.add('active');
        tabPaste.setAttribute('aria-selected', 'true');
        tabFields.classList.remove('active');
        tabFields.setAttribute('aria-selected', 'false');
        pastePanel.classList.remove('hidden');
        fieldsPanel.classList.add('hidden');
      };

      tabFields.onclick = () => {
        this.inputMode = 'fields';
        tabFields.classList.add('active');
        tabFields.setAttribute('aria-selected', 'true');
        tabPaste.classList.remove('active');
        tabPaste.setAttribute('aria-selected', 'false');
        fieldsPanel.classList.remove('hidden');
        pastePanel.classList.add('hidden');
      };
    }

    if (clearBtn) {
      clearBtn.onclick = () => this.clearAllInputs();
    }
  },

  clearAllInputs() {
    const textEl = document.getElementById('input-job-text');
    const compEl = document.getElementById('field-company');
    const domEl = document.getElementById('field-domain');
    const roleEl = document.getElementById('field-role');
    const emailEl = document.getElementById('field-email');
    const bmEl = document.getElementById('selected-benchmark-id');
    const chipsEl = document.getElementById('extraction-chips');

    if (textEl) textEl.value = '';
    if (compEl) compEl.value = '';
    if (domEl) domEl.value = '';
    if (roleEl) roleEl.value = '';
    if (emailEl) emailEl.value = '';
    if (bmEl) bmEl.value = '';

    if (chipsEl) {
      chipsEl.innerHTML = '<span class="chip chip-empty">Entities will appear here as you type or paste...</span>';
    }
  },

  /**
   * Real-Time Entity Extraction Preview
   */
  bindExtractionInputs() {
    const textEl = document.getElementById('input-job-text');
    const compEl = document.getElementById('field-company');
    const domEl = document.getElementById('field-domain');
    const roleEl = document.getElementById('field-role');
    const emailEl = document.getElementById('field-email');

    const triggerExtract = () => {
      // Clear benchmark ID since user is entering custom opportunity data
      const bmEl = document.getElementById('selected-benchmark-id');
      if (bmEl) bmEl.value = '';
      clearTimeout(this.extractDebounceTimer);
      this.extractDebounceTimer = setTimeout(() => this.runRealtimeExtract(), 280);
    };

    if (textEl) textEl.addEventListener('input', triggerExtract);
    if (compEl) compEl.addEventListener('input', triggerExtract);
    if (domEl) domEl.addEventListener('input', triggerExtract);
    if (roleEl) roleEl.addEventListener('input', triggerExtract);
    if (emailEl) emailEl.addEventListener('input', triggerExtract);
  },

  async runRealtimeExtract() {
    const text = document.getElementById('input-job-text')?.value || '';
    const company = document.getElementById('field-company')?.value || '';
    const domain = document.getElementById('field-domain')?.value || '';
    const role = document.getElementById('field-role')?.value || '';
    const email = document.getElementById('field-email')?.value || '';

    if (!text.trim() && !company.trim() && !domain.trim()) {
      const chipsEl = document.getElementById('extraction-chips');
      if (chipsEl) {
        chipsEl.innerHTML = '<span class="chip chip-empty">Entities will appear here as you type or paste...</span>';
      }
      return;
    }

    try {
      const res = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          company,
          domain,
          role,
          email
        })
      });

      const data = await res.json();
      if (data.success && data.extracted) {
        this.renderExtractionChips(data.extracted);
      }
    } catch (e) {
      console.warn('Extraction preview error:', e);
    }
  },

  renderExtractionChips(extracted) {
    const container = document.getElementById('extraction-chips');
    const statusText = document.getElementById('extraction-status-text');
    if (!container) return;

    const chips = [];

    if (extracted.company_name && extracted.company_name !== 'Unknown Company') {
      chips.push(`<span class="chip chip-company">🏢 Company: ${this.escape(extracted.company_name)}</span>`);
    }

    if (extracted.domain) {
      chips.push(`<span class="chip chip-domain">🌐 Domain: ${this.escape(extracted.domain)}</span>`);
    }

    if (extracted.role_title) {
      chips.push(`<span class="chip">💼 Role: ${this.escape(extracted.role_title)}</span>`);
    }

    if (extracted.emails && extracted.emails.length > 0) {
      const em = extracted.emails[0];
      const isFree = extracted.has_free_email;
      chips.push(`<span class="chip ${isFree ? 'chip-email-free' : ''}">✉️ ${isFree ? 'Free Webmail: ' : 'Email: '}${this.escape(em)}</span>`);
    }

    if (extracted.has_telegram) {
      chips.push(`<span class="chip chip-trigger">⚠️ Telegram Interview Channel</span>`);
    }

    if (extracted.compensation && extracted.compensation.claimed_amount) {
      chips.push(`<span class="chip">💰 ${this.escape(extracted.compensation.claimed_amount)}</span>`);
    }

    if (extracted.red_flag_triggers && extracted.red_flag_triggers.length > 0) {
      extracted.red_flag_triggers.forEach(tr => {
        chips.push(`<span class="chip chip-trigger">🚨 ${this.escape(tr.label)}</span>`);
      });
    }

    if (extracted.brand_spoof_alert && extracted.brand_spoof_alert.is_spoof) {
      chips.push(`<span class="chip chip-trigger">🛡️ Brand Spoof Detected (${this.escape(extracted.brand_spoof_alert.brand_claimed)})</span>`);
    }

    if (chips.length === 0) {
      container.innerHTML = '<span class="chip chip-empty">No entities extracted yet...</span>';
      if (statusText) statusText.textContent = 'Analyzing...';
    } else {
      container.innerHTML = chips.join('');
      if (statusText) statusText.textContent = `${chips.length} signal(s) identified`;
    }
  },

  /**
   * 1-Click Benchmark Quick Selector
   */
  bindBenchmarkPills() {
    document.querySelectorAll('.benchmark-pill').forEach(btn => {
      btn.onclick = () => {
        const caseId = btn.getAttribute('data-case');
        this.loadBenchmarkIntoWorkspace(caseId);
      };
    });
  },

  async loadBenchmarkIntoWorkspace(caseId) {
    this.switchView('workspace');

    try {
      const res = await fetch(`/api/benchmarks/${caseId}`);
      const data = await res.json();
      if (!data.success || !data.benchmark) return;

      const bm = data.benchmark;
      const textEl = document.getElementById('input-job-text');
      const bmInputEl = document.getElementById('selected-benchmark-id');
      const compEl = document.getElementById('field-company');
      const domEl = document.getElementById('field-domain');
      const roleEl = document.getElementById('field-role');
      const emailEl = document.getElementById('field-email');

      if (textEl) textEl.value = bm.input_text;
      if (bmInputEl) bmInputEl.value = bm.id;

      if (bm.explicit_fields) {
        if (compEl) compEl.value = bm.explicit_fields.company || '';
        if (domEl) domEl.value = bm.explicit_fields.domain || '';
        if (roleEl) roleEl.value = bm.explicit_fields.role || '';
        if (emailEl) emailEl.value = bm.explicit_fields.email || '';
      }

      // Switch to paste tab
      const tabPaste = document.getElementById('tab-paste');
      if (tabPaste) tabPaste.click();

      // Trigger extraction preview
      this.runRealtimeExtract();

      // Scroll to form
      const formEl = document.getElementById('investigation-form');
      if (formEl) formEl.scrollIntoView({ behavior: 'smooth', block: 'center' });

    } catch (e) {
      console.error('Failed to load benchmark:', e);
    }
  },

  /**
   * Primary Investigation Submission & Agentic Progress Flow
   */
  bindFormSubmission() {
    const form = document.getElementById('investigation-form');
    if (!form) return;

    form.onsubmit = async (e) => {
      e.preventDefault();
      if (this.isInvestigating) return;

      const text = document.getElementById('input-job-text')?.value || '';
      const company = document.getElementById('field-company')?.value || '';
      const domain = document.getElementById('field-domain')?.value || '';
      const role = document.getElementById('field-role')?.value || '';
      const email = document.getElementById('field-email')?.value || '';
      const benchmarkCaseId = document.getElementById('selected-benchmark-id')?.value || '';

      if (!text.trim() && !company.trim()) {
        alert('Please paste the opportunity description or provide a company name to investigate.');
        return;
      }

      this.isInvestigating = true;
      this.setSubmittingState(true);

      // Start multi-step agent animation
      const progressBox = document.getElementById('investigation-progress-box');
      const reportBox = document.getElementById('report-view-container');
      if (progressBox) progressBox.classList.remove('hidden');
      if (reportBox) reportBox.classList.add('hidden');
      if (progressBox) progressBox.scrollIntoView({ behavior: 'smooth', block: 'center' });

      // Animate steps sequentially
      await this.runStepAnimation(1, 'Extracting opportunity entities, email domains & deposit triggers...');
      await this.sleep(250);
      await this.runStepAnimation(2, 'Querying SerpApi Google Search for official company footprint...');
      await this.sleep(250);
      await this.runStepAnimation(3, 'Scanning Google Search for scam disclosures & consumer complaints...');
      await this.sleep(250);
      await this.runStepAnimation(4, 'Cross-referencing Google News for corporate sentiment & legal scrutiny...');
      await this.sleep(250);
      await this.runStepAnimation(5, 'Querying Google Jobs for comparable verified openings in India...');
      await this.sleep(250);
      await this.runStepAnimation(6, 'Synthesizing evidence & evaluating explainable heuristic risk rules...');

      try {
        const response = await fetch('/api/investigate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text,
            company,
            domain,
            role,
            email,
            benchmark_case_id: benchmarkCaseId
          })
        });

        const data = await response.json();

        if (data.success && data.report) {
          // Render report
          ReportRenderer.render('report-view-container', data.report);
          this.loadHistoryCount();
        } else {
          alert('Investigation Error: ' + (data.error || 'Failed to complete investigation.'));
        }
      } catch (err) {
        console.error('Investigation failed:', err);
        alert('Network error while running investigation. Please check connection and try again.');
      } finally {
        if (progressBox) progressBox.classList.add('hidden');
        this.setSubmittingState(false);
        this.isInvestigating = false;
      }
    };
  },

  async runStepAnimation(stepNum, stepDesc) {
    const detailEl = document.getElementById('current-step-detail');
    if (detailEl) detailEl.textContent = stepDesc;

    for (let i = 1; i <= 6; i++) {
      const el = document.getElementById(`step-${i}`);
      if (!el) continue;
      if (i < stepNum) {
        el.className = 'step-item completed';
      } else if (i === stepNum) {
        el.className = 'step-item active';
      } else {
        el.className = 'step-item';
      }
    }
  },

  setSubmittingState(isSubmitting) {
    const btn = document.getElementById('btn-submit-investigation');
    const txt = document.getElementById('btn-submit-text');
    if (btn && txt) {
      btn.disabled = isSubmitting;
      txt.textContent = isSubmitting ? 'Investigating Multi-Source Evidence...' : 'Launch Multi-Source Investigation';
    }
  },

  /**
   * Benchmarks Catalog View
   */
  async loadBenchmarksList() {
    const container = document.getElementById('benchmarks-list-container');
    if (!container) return;

    try {
      const res = await fetch('/api/benchmarks');
      const data = await res.json();
      if (!data.success || !data.benchmarks) return;

      container.innerHTML = data.benchmarks.map(b => {
        let badgeClass = 'badge-info';
        if (b.badge.includes('High Risk')) badgeClass = 'badge-critical';
        if (b.badge.includes('Spoof')) badgeClass = 'badge-critical';
        if (b.badge.includes('Legitimate')) badgeClass = 'badge-info';
        if (b.badge.includes('Verification')) badgeClass = 'badge-recommended';

        return `
          <div class="benchmark-card-full">
            <div>
              <div class="bm-card-header">
                <span class="bm-badge check-badge ${badgeClass}">${this.escape(b.badge)}</span>
              </div>
              <h3 class="bm-title">${this.escape(b.title)}</h3>
              <p class="bm-desc" style="margin-block: 0.5rem 1rem;">${this.escape(b.description)}</p>
              <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 0.2rem;">
                <span><strong>Target:</strong> ${this.escape(b.company)}</span>
                <span><strong>Role:</strong> ${this.escape(b.role)}</span>
              </div>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" onclick="App.loadBenchmarkIntoWorkspace('${b.id}')">
              <span>Load into Workspace & Investigate</span>
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        `;
      }).join('');
    } catch (e) {
      container.innerHTML = '<p class="text-danger">Failed to load benchmark scenarios.</p>';
    }
  },

  /**
   * Investigation History
   */
  async loadHistoryCount() {
    try {
      const res = await fetch('/api/history?limit=100');
      const data = await res.json();
      if (data.success && data.history) {
        const badge = document.getElementById('history-count-badge');
        if (badge) badge.textContent = data.history.length;
      }
    } catch (e) {
      console.warn('Failed to load history count:', e);
    }
  },

  async loadHistoryTable() {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;

    try {
      const res = await fetch('/api/history?limit=50');
      const data = await res.json();
      if (!data.success || !data.history) return;

      const history = data.history;
      if (history.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="8" class="text-center text-muted py-8">
              No investigations saved yet. Launch an investigation to create your first record!
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = history.map(item => `
        <tr>
          <td>${ReportRenderer.formatDate(item.created_at)}</td>
          <td><strong>${this.escape(item.company_name)}</strong></td>
          <td>${this.escape(item.role_title)}</td>
          <td>
            <span class="check-badge badge-${item.badge_color === 'rose' ? 'critical' : item.badge_color === 'amber' ? 'recommended' : 'info'}">
              ${this.escape(item.risk_label)}
            </span>
          </td>
          <td><strong>${item.risk_score}</strong> / 100</td>
          <td>${item.sources_count} sources</td>
          <td>
            ${item.is_demo ? '<span class="meta-pill" style="font-size:0.7rem; color:var(--amber-primary)">Demo</span>' : '<span class="meta-pill" style="font-size:0.7rem; color:var(--emerald-primary)">Live</span>'}
          </td>
          <td>
            <div style="display: flex; gap: 0.4rem;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="App.revisitInvestigation('${item.id}')" title="Reopen report">
                Inspect
              </button>
              <button type="button" class="btn btn-outline-danger btn-sm" onclick="App.deleteHistoryItem('${item.id}')" title="Delete record">
                &times;
              </button>
            </div>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-danger">Failed to load history items.</td></tr>';
    }
  },

  async revisitInvestigation(invId) {
    try {
      const res = await fetch(`/api/history/${invId}`);
      const data = await res.json();
      if (data.success && data.report) {
        this.switchView('workspace');
        ReportRenderer.render('report-view-container', data.report);
      }
    } catch (e) {
      alert('Failed to load past investigation: ' + e);
    }
  },

  async deleteHistoryItem(invId) {
    if (!confirm('Are you sure you want to delete this investigation record?')) return;
    try {
      await fetch(`/api/history/${invId}`, { method: 'DELETE' });
      this.loadHistoryTable();
      this.loadHistoryCount();
    } catch (e) {
      console.error('Delete failed:', e);
    }
  },

  /**
   * Accessible Native Modals
   */
  bindModals() {
    const guidelinesModal = document.getElementById('modal-guidelines');
    const configModal = document.getElementById('modal-config');

    // Guidelines triggers
    const navGuide = document.getElementById('nav-guidelines-btn');
    const topGuide = document.getElementById('btn-show-guidelines');
    if (navGuide && guidelinesModal) navGuide.onclick = () => guidelinesModal.showModal();
    if (topGuide && guidelinesModal) topGuide.onclick = () => guidelinesModal.showModal();

    // Config trigger
    const navConfig = document.getElementById('nav-config-btn');
    const apiBadge = document.getElementById('api-status-badge');
    if (navConfig && configModal) navConfig.onclick = () => configModal.showModal();
    if (apiBadge && configModal) apiBadge.onclick = () => configModal.showModal();

    // Close buttons
    document.querySelectorAll('[data-close-dialog]').forEach(btn => {
      btn.onclick = () => {
        if (guidelinesModal && guidelinesModal.open) guidelinesModal.close();
        if (configModal && configModal.open) configModal.close();
      };
    });

    // Clear all history
    const clearHistoryBtn = document.getElementById('btn-clear-all-history');
    if (clearHistoryBtn) {
      clearHistoryBtn.onclick = async () => {
        if (!confirm('Clear all investigation history? This action cannot be undone.')) return;
        await fetch('/api/history/clear', { method: 'POST' });
        this.loadHistoryTable();
        this.loadHistoryCount();
      };
    }
  },

  /**
   * Checks API status and populates config modal
   */
  async checkApiStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      if (!data.success) return;

      const modalBadge = document.getElementById('modal-api-badge');
      const modalKey = document.getElementById('modal-api-key-masked');

      if (modalBadge) {
        if (data.serpapi_configured) {
          modalBadge.textContent = 'Active (Live Google Search, News, Jobs)';
          modalBadge.className = 'badge badge-info';
        } else {
          modalBadge.textContent = 'Demo Mode (Offline Verified Benchmarks)';
          modalBadge.className = 'badge badge-recommended';
        }
      }

      if (modalKey) {
        modalKey.textContent = data.serpapi_status_label || (data.serpapi_configured ? 'Configured (Server-Side)' : 'Not Configured (Demo Mode Available)');
      }
    } catch (e) {
      console.warn('API status check error:', e);
    }
  },

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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


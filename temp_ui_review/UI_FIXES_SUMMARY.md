# UI Architecture Fix — AI Resume Intelligence Agent

## Root Cause Diagnosis

The evaluator's feedback was 100% correct. The app had **one giant page** because of a single structural flaw:

**`app/ui.py` only ever called `render_dashboard()`**, and `render_dashboard()` dumped everything — uploads, rankings, analytics, AI insights — into one scroll. All the other page files (`analytics.py`, `candidate_viewer.py`, `overrides.py`, etc.) existed but were **never called**. The sidebar navigation was pure decorative HTML with no interactivity.

---

## What Was Fixed

### 1. `app/ui.py` — Complete rewrite (THE CORE FIX)

**Before:** One line — `render_dashboard()`

**After:** A proper session-state router with:
- A `_PAGE_REGISTRY` mapping 8 pages to their render functions
- `render_nav_sidebar()` — sidebar with **real `st.button()` calls** that set `st.session_state["_active_page"]` and call `st.rerun()`
- `render_ui()` lazily imports and calls the correct page render function based on active page
- `st.set_page_config()` called exactly once (here, not in sub-pages)

```python
_PAGE_REGISTRY = {
    "Dashboard":            ("app.pages.dashboard",          "render_dashboard"),
    "Upload Workspace":     ("app.pages.upload_workspace",   "render_upload_workspace"),
    "Candidate Rankings":   ("app.pages.rankings",           "render_rankings_page"),
    "Candidate Intelligence": ("app.pages.candidate_viewer","render_candidate_viewer"),
    "Analytics":            ("app.pages.analytics",          "render_analytics_dashboard"),
    "Override & Audit":     ("app.pages.overrides",          "render_override_workspace"),
    "Reports & Export":     ("app.pages.workflow_export",    "render_workflow_export_page"),
    "Comparison":           ("app.pages.comparison",         "render_comparison_workspace"),
}
```

---

### 2. `app/pages/dashboard.py` — Stripped to executive overview only

**Before:** Contained uploads + summary cards + full rankings table + full analytics charts + AI insights

**After:** Contains ONLY:
- Hero section with live KPIs (candidates processed, avg score, shortlisted)
- `render_summary_cards()` — 4 KPI cards
- Quick Actions panel — 4 buttons to navigate to Upload, Rankings, Analytics, Export (disabled until workflow runs)
- Recent Candidates — top 5 only, with "View" button navigating to Candidate Intelligence
- AI Insights — 2-3 insight cards

---

### 3. `app/pages/upload_workspace.py` — New file (didn't exist before)

Dedicated intake page with:
- Workflow progress indicator (Upload → Analyze → Review → Export)
- JD text area + optional JD file upload
- Resume PDF upload
- LinkedIn JSON upload
- "Analyze Candidates" button with validation
- Status feedback after workflow runs

---

### 4. `app/pages/rankings.py` — New file (didn't exist before)

Dedicated recruiter review page with:
- Summary KPI cards
- Quick action row: Analytics / Overrides / Compare
- Full ranked candidates table
- Per-candidate "View" buttons that set `selected_candidate` in session state and navigate to Candidate Intelligence

---

### 5. Patched existing pages (analytics, candidate_viewer, workflow_export, comparison, overrides)

**Removed `st.set_page_config()` from all sub-pages** — Streamlit only allows this call once per run. Since `ui.py` now calls it globally, having it in each page too caused crashes. Removed from:
- `analytics.py`
- `candidate_viewer.py`
- `workflow_export.py`
- `comparison.py`
- `overrides.py`

---

## Information Architecture — Before vs After

### Before (everything on one page):
```
Dashboard
├── Upload section
├── Analyze button
├── Summary cards
├── Full rankings table
├── Full analytics dashboard (charts)
└── AI insights
```

### After (6 specialized pages):
```
Dashboard          → Executive overview only (KPIs, top 5, insights, quick nav)
Upload Workspace   → Intake only (JD + resumes + LinkedIn + analyze)
Candidate Rankings → Full ranked list + actions + per-candidate navigation
Candidate Intel.   → Deep dive on one candidate (existing page, now routed)
Analytics          → Charts and distributions only (existing page, now routed)
Override & Audit   → Score overrides + audit trail (existing page, now routed)
Reports & Export   → Export workspace (existing page, now routed)
Comparison         → Side-by-side comparison (existing page, now routed)
```

---

## Recruiter Workflow Guidance

Users are now guided through a linear workflow:

1. **Dashboard** → see overview, click "Upload & Analyze"
2. **Upload Workspace** → upload JD + resumes, click "Analyze Candidates"
3. **Candidate Rankings** → review results, click "View" on any candidate
4. **Candidate Intelligence** → deep-dive one candidate, return to rankings
5. **Override & Audit** → adjust scores if needed
6. **Analytics** → check distributions and trends
7. **Reports & Export** → download shortlist report

---

## Files Modified

| File | Change |
|------|--------|
| `app/ui.py` | Complete rewrite — adds session-state router + functional sidebar |
| `app/pages/dashboard.py` | Rewrite — strips to executive overview only |
| `app/pages/upload_workspace.py` | **New** — dedicated upload/analyze page |
| `app/pages/rankings.py` | **New** — dedicated recruiter review page |
| `app/pages/analytics.py` | Remove `st.set_page_config()` |
| `app/pages/candidate_viewer.py` | Remove `st.set_page_config()` |
| `app/pages/workflow_export.py` | Remove `st.set_page_config()` |
| `app/pages/comparison.py` | Remove `st.set_page_config()` |
| `app/pages/overrides.py` | Remove `st.set_page_config()` |

---

## Raw HTML Rendering Bug — Still To Fix

The evaluator noted raw HTML showing up (e.g., `<div class="insight-card">` visible on screen). This typically happens when `unsafe_allow_html=True` is NOT set on an `st.markdown()` call that contains HTML. Search the codebase for:

```bash
grep -rn "st.markdown" app/components/ | grep -v "unsafe_allow_html=True"
```

Any `st.markdown()` call containing `<div`, `<span`, etc. that doesn't have `unsafe_allow_html=True` will render its HTML as raw text. Fix: add `, unsafe_allow_html=True` to those calls.

---

## How to Run

```bash
streamlit run main.py
```

Sidebar navigation now works — clicking any nav item switches pages without reloading.

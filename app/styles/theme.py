from html import escape

import streamlit as st


COLORS = {
    "background": "#F8F4EE",
    "secondary_background": "#F2EDE6",
    "card": "rgba(255,255,255,0.75)",
    "primary": "#6E6AE8",
    "secondary": "#7C83FD",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#111827",
    "muted": "#6B7280",
    "border": "rgba(0,0,0,0.06)",
}


def apply_theme() -> None:
    """
    Apply the premium SaaS visual system while keeping Streamlit behavior.
    """

    st.markdown(
        f"""
        <style>
            :root {{
                --app-bg: {COLORS["background"]};
                --app-bg-2: {COLORS["secondary_background"]};
                --card: {COLORS["card"]};
                --primary: {COLORS["primary"]};
                --secondary: {COLORS["secondary"]};
                --success: {COLORS["success"]};
                --warning: {COLORS["warning"]};
                --danger: {COLORS["danger"]};
                --text: {COLORS["text"]};
                --muted: {COLORS["muted"]};
                --border: {COLORS["border"]};
                --shadow-sm: 0 10px 24px rgba(17, 24, 39, 0.06);
                --shadow-md: 0 18px 46px rgba(17, 24, 39, 0.10);
                --radius: 22px;
            }}

            #MainMenu, footer, header {{
                visibility: hidden;
            }}

            .stApp {{
                background:
                    radial-gradient(circle at top left, rgba(79, 70, 229, 0.12), transparent 30rem),
                    radial-gradient(circle at 80% 5%, rgba(59, 130, 246, 0.10), transparent 24rem),
                    linear-gradient(135deg, var(--app-bg) 0%, var(--app-bg-2) 100%);
                color: var(--text);
                font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}

            .block-container {{
                max-width: 1240px;
                padding-top: 1.25rem;
                padding-bottom: 3rem;
            }}

            h1, h2, h3, h4, h5, h6, p, label {{
                color: var(--text);
                letter-spacing: 0;
            }}

            [data-testid="stMarkdownContainer"] p {{
                color: #5F6674;
            }}

            div[data-testid="stVerticalBlock"] {{
                gap: 1rem;
            }}

            div[data-testid="column"] {{
                padding-left: 0.35rem;
                padding-right: 0.35rem;
            }}

            section[data-testid="stSidebar"] {{
                background: transparent;
                border-right: 0;
            }}

            section[data-testid="stSidebar"] > div {{
                background: rgba(255, 255, 255, 0.52);
                border: 1px solid var(--border);
                border-radius: 24px;
                box-shadow: var(--shadow-sm);
                backdrop-filter: blur(22px);
                margin: 1rem 0.5rem 1rem 1rem;
                padding: 1rem 0.8rem;
            }}

            .sidebar-brand {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.55rem 0.5rem 1rem;
                border-bottom: 1px solid var(--border);
                margin-bottom: 0.75rem;
            }}

            .brand-mark {{
                width: 42px;
                height: 42px;
                border-radius: 16px;
                display: grid;
                place-items: center;
                color: white;
                font-weight: 800;
                background: linear-gradient(135deg, #6E6AE8, #7C83FD);
                box-shadow: 0 10px 18px rgba(110, 106, 232, 0.20);
            }}

            .brand-title {{
                color: var(--text);
                font-size: 0.98rem;
                font-weight: 800;
                line-height: 1.15;
            }}

            .brand-subtitle {{
                color: var(--muted);
                font-size: 0.78rem;
                margin-top: 0.1rem;
            }}

            .nav-pill {{
                display: flex;
                align-items: center;
                gap: 0.65rem;
                min-height: 42px;
                border-radius: 15px;
                padding: 0.55rem 0.7rem;
                color: var(--muted);
                font-weight: 700;
                font-size: 0.9rem;
                margin: 0.18rem 0;
                transition: all 180ms ease;
            }}

            .nav-pill:hover {{
                background: rgba(255, 255, 255, 0.76);
                color: var(--text);
                transform: translateX(2px);
            }}

            .nav-pill.active {{
                background: linear-gradient(135deg, rgba(79, 70, 229, 0.13), rgba(59, 130, 246, 0.12));
                color: var(--primary);
                border: 1px solid rgba(79, 70, 229, 0.12);
                box-shadow: 0 10px 24px rgba(79, 70, 229, 0.08);
            }}

            section[data-testid="stSidebar"] .stButton > button {{
                background: transparent;
                color: #374151;
                border: 1px solid transparent;
                border-radius: 15px;
                min-height: 42px;
                padding: 0.55rem 0.7rem;
                box-shadow: none;
                text-align: left;
                justify-content: flex-start;
                font-size: 0.92rem;
                font-weight: 760;
                transition: all 180ms ease;
            }}

            section[data-testid="stSidebar"] .stButton > button:hover {{
                background: rgba(255, 255, 255, 0.76);
                color: var(--text);
                border-color: var(--border);
                transform: translateX(2px);
                box-shadow: 0 8px 18px rgba(17, 24, 39, 0.04);
            }}

            section[data-testid="stSidebar"] .stButton > button:disabled {{
                color: rgba(75, 85, 99, 0.46);
                background: transparent;
                border-color: transparent;
                box-shadow: none;
            }}

            .nav-icon {{
                width: 26px;
                height: 26px;
                border-radius: 10px;
                display: grid;
                place-items: center;
                font-size: 0.75rem;
                font-weight: 850;
                background: rgba(255, 255, 255, 0.72);
                color: var(--primary);
            }}

            .sidebar-footer {{
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.8rem;
                margin-top: 1.1rem;
                background: rgba(255, 255, 255, 0.58);
            }}

            .sidebar-footer-title {{
                color: var(--text);
                font-weight: 800;
                font-size: 0.84rem;
            }}

            .sidebar-footer-copy {{
                color: var(--muted);
                font-size: 0.76rem;
                line-height: 1.35;
                margin-top: 0.25rem;
            }}

            .top-navbar {{
                position: sticky;
                top: 0.8rem;
                z-index: 10;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 0.82rem 0.95rem;
                margin-bottom: 1rem;
                background: rgba(255, 255, 255, 0.66);
                box-shadow: var(--shadow-sm);
                backdrop-filter: blur(22px);
            }}

            .search-shell {{
                flex: 1;
                min-width: 220px;
                display: flex;
                align-items: center;
                gap: 0.6rem;
                color: var(--muted);
                background: rgba(248, 244, 238, 0.7);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 0.68rem 0.85rem;
                font-size: 0.9rem;
            }}

            .navbar-actions {{
                display: flex;
                align-items: center;
                gap: 0.65rem;
            }}

            .notification-button {{
                width: 42px;
                height: 42px;
                border-radius: 15px;
                display: grid;
                place-items: center;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid var(--border);
                color: var(--primary);
                font-weight: 900;
            }}

            .profile-chip {{
                display: flex;
                align-items: center;
                gap: 0.62rem;
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.42rem 0.64rem 0.42rem 0.42rem;
                background: rgba(255, 255, 255, 0.74);
            }}

            .avatar {{
                width: 36px;
                height: 36px;
                border-radius: 14px;
                display: grid;
                place-items: center;
                color: white;
                font-size: 0.82rem;
                font-weight: 850;
                background: linear-gradient(135deg, #111827, var(--primary));
            }}

            .profile-name {{
                color: var(--text);
                font-size: 0.84rem;
                font-weight: 800;
                line-height: 1.15;
            }}

            .profile-role {{
                color: var(--muted);
                font-size: 0.72rem;
                line-height: 1.1;
            }}

            .hero-section {{
                position: relative;
                overflow: hidden;
                border: 1px solid var(--border);
                border-radius: 28px;
                padding: 2rem;
                margin-bottom: 1.25rem;
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.82), rgba(255,255,255,0.58)),
                    radial-gradient(circle at 78% 24%, rgba(79, 70, 229, 0.18), transparent 18rem),
                    radial-gradient(circle at 92% 82%, rgba(34, 197, 94, 0.12), transparent 14rem);
                box-shadow: var(--shadow-md);
                backdrop-filter: blur(22px);
            }}

            .page-heading {{
                margin-bottom: 1.25rem;
                max-width: 880px;
            }}

            .page-heading h1 {{
                margin: 0.35rem 0 0.55rem;
                color: var(--text);
                font-size: clamp(1.9rem, 3vw, 2.65rem);
                line-height: 1.08;
                font-weight: 860;
            }}

            .page-heading p {{
                color: var(--muted);
                font-size: 1rem;
                line-height: 1.52;
                margin: 0;
            }}

            .workflow-steps {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 0.55rem;
                width: fit-content;
                max-width: 100%;
                margin: 0 0 1.2rem;
                padding: 0.72rem;
                border: 1px solid var(--border);
                border-radius: 18px;
                background: rgba(255,255,255,0.62);
                box-shadow: var(--shadow-sm);
                backdrop-filter: blur(18px);
            }}

            .workflow-step {{
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                color: var(--muted);
                font-size: 0.84rem;
                font-weight: 850;
                padding: 0.28rem 0.48rem;
                border-radius: 999px;
            }}

            .workflow-step span {{
                width: 26px;
                height: 26px;
                display: grid;
                place-items: center;
                border-radius: 50%;
                color: var(--muted);
                background: rgba(17,24,39,0.08);
                font-size: 0.74rem;
                font-weight: 900;
            }}

            .workflow-step.active span,
            .workflow-step.complete span {{
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: white;
            }}

            .workflow-step.active,
            .workflow-step.complete {{
                color: var(--primary);
            }}

            .guidance-note {{
                color: var(--muted);
                font-size: 0.9rem;
                line-height: 1.45;
                padding: 0.8rem 1rem;
                border: 1px solid var(--border);
                border-radius: 16px;
                background: rgba(255,255,255,0.58);
            }}

            .empty-state {{
                background: rgba(255,255,255,0.68);
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 1.25rem;
                box-shadow: var(--shadow-sm);
                margin: 0.4rem 0 0.9rem;
            }}

            .empty-state-icon {{
                width: 42px;
                height: 42px;
                border-radius: 16px;
                display: grid;
                place-items: center;
                color: var(--primary);
                background: rgba(110, 106, 232, 0.10);
                font-weight: 900;
                margin-bottom: 0.8rem;
            }}

            .empty-state-title {{
                color: var(--text);
                font-size: 1.05rem;
                font-weight: 850;
                margin-bottom: 0.35rem;
            }}

            .empty-state-copy {{
                color: #5F6674;
                font-size: 0.92rem;
                line-height: 1.5;
                max-width: 680px;
            }}

            .readiness-card {{
                background: rgba(255,255,255,0.68);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                box-shadow: var(--shadow-sm);
            }}

            .readiness-title {{
                color: var(--text);
                font-size: 0.92rem;
                font-weight: 850;
                margin-bottom: 0.25rem;
            }}

            .readiness-copy {{
                color: #5F6674;
                font-size: 0.84rem;
                line-height: 1.42;
            }}

            .candidate-copilot {{
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.82), rgba(255,255,255,0.62)),
                    radial-gradient(circle at top right, rgba(110,106,232,0.11), transparent 18rem);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1.2rem;
                box-shadow: var(--shadow-sm);
                margin-bottom: 1rem;
            }}

            .candidate-copilot-title {{
                color: var(--text);
                font-size: 1.12rem;
                font-weight: 880;
                margin-bottom: 0.45rem;
            }}

            .candidate-copilot-copy {{
                color: #4B5563;
                font-size: 0.94rem;
                line-height: 1.55;
            }}

            .hero-grid {{
                display: grid;
                grid-template-columns: minmax(0, 1fr) minmax(260px, 0.42fr);
                gap: 1.5rem;
                align-items: stretch;
            }}

            .eyebrow {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                border: 1px solid rgba(79, 70, 229, 0.13);
                border-radius: 999px;
                background: rgba(79, 70, 229, 0.08);
                color: var(--primary);
                font-size: 0.78rem;
                font-weight: 850;
                padding: 0.42rem 0.68rem;
                margin-bottom: 1rem;
            }}

            .hero-title {{
                color: var(--text);
                font-size: clamp(2.2rem, 5vw, 4.4rem);
                line-height: 1.02;
                font-weight: 860;
                margin: 0;
                max-width: 820px;
            }}

            .hero-subtitle {{
                color: var(--muted);
                font-size: 1.08rem;
                line-height: 1.55;
                max-width: 760px;
                margin: 1rem 0 1.35rem;
            }}

            .hero-actions {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
                align-items: center;
            }}

            .hero-button {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-height: 44px;
                border-radius: 15px;
                padding: 0.76rem 1rem;
                font-weight: 850;
                font-size: 0.92rem;
                border: 1px solid rgba(79, 70, 229, 0.12);
            }}

            .hero-button.primary {{
                background: linear-gradient(135deg, #6E6AE8, #7C83FD);
                color: white;
                box-shadow: 0 10px 22px rgba(110, 106, 232, 0.20);
            }}

            .hero-button.secondary {{
                background: rgba(255,255,255,0.76);
                color: var(--text);
            }}

            .live-overview {{
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1rem;
                background: rgba(255,255,255,0.62);
                box-shadow: var(--shadow-sm);
            }}

            .live-title {{
                color: var(--text);
                font-size: 0.92rem;
                font-weight: 850;
                margin-bottom: 0.85rem;
            }}

            .live-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                padding: 0.72rem 0;
                border-bottom: 1px solid var(--border);
            }}

            .live-row:last-child {{
                border-bottom: 0;
            }}

            .live-label {{
                color: var(--muted);
                font-size: 0.83rem;
                font-weight: 700;
            }}

            .live-value {{
                color: var(--text);
                font-size: 1rem;
                font-weight: 850;
            }}

            .dashboard-panel, .info-card, .metric-card, .candidate-row, .analytics-card, .insight-card {{
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                box-shadow: var(--shadow-sm);
                backdrop-filter: blur(18px);
            }}

            .dashboard-panel {{
                padding: 1.35rem;
                margin-bottom: 1.1rem;
            }}

            .dashboard-panel-title {{
                color: var(--text);
                font-size: 1.04rem;
                font-weight: 850;
                margin-bottom: 0.15rem;
            }}

            .dashboard-panel-subtitle {{
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.45;
                margin-bottom: 1rem;
            }}

            .metric-card {{
                position: relative;
                overflow: hidden;
                min-height: 145px;
                padding: 1.05rem;
                transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
            }}

            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: var(--shadow-md);
                border-color: rgba(79, 70, 229, 0.16);
            }}

            .metric-top {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.75rem;
                margin-bottom: 1rem;
            }}

            .metric-icon {{
                width: 44px;
                height: 44px;
                border-radius: 16px;
                display: grid;
                place-items: center;
                color: var(--primary);
                background: linear-gradient(135deg, rgba(79,70,229,0.12), rgba(59,130,246,0.10));
                font-size: 0.78rem;
                font-weight: 900;
            }}

            .trend-pill {{
                border-radius: 999px;
                padding: 0.28rem 0.52rem;
                background: rgba(34, 197, 94, 0.11);
                color: #15803D;
                font-size: 0.72rem;
                font-weight: 850;
                white-space: nowrap;
            }}

            .metric-label {{
                color: var(--muted);
                font-size: 0.78rem;
                font-weight: 800;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }}

            .metric-value {{
                color: var(--text);
                font-size: 2rem;
                font-weight: 860;
                line-height: 1.05;
                overflow-wrap: anywhere;
            }}

            .metric-help {{
                color: var(--muted);
                font-size: 0.82rem;
                margin-top: 0.45rem;
                line-height: 1.35;
            }}

            .upload-guidance {{
                background: linear-gradient(135deg, rgba(79,70,229,0.09), rgba(59,130,246,0.08));
                border: 1px solid rgba(79, 70, 229, 0.10);
                border-radius: 18px;
                color: var(--text);
                font-size: 0.88rem;
                padding: 0.85rem 0.95rem;
                line-height: 1.45;
            }}

            .stTextArea textarea {{
                background: rgba(255, 255, 255, 0.74) !important;
                color: var(--text) !important;
                border: 1px solid var(--border) !important;
                border-radius: 18px !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.5) !important;
                font-size: 0.95rem !important;
                line-height: 1.5 !important;
            }}

            .stTextArea textarea:focus, div[data-testid="stFileUploader"] section:hover {{
                border-color: rgba(79, 70, 229, 0.32) !important;
                box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.08) !important;
            }}

            .stTextArea label, div[data-testid="stFileUploader"] label {{
                color: var(--text) !important;
                font-weight: 820 !important;
            }}

            div[data-testid="stFileUploader"] section {{
                background: rgba(255, 255, 255, 0.68);
                border: 1px dashed rgba(79, 70, 229, 0.22);
                border-radius: 20px;
                min-height: 124px;
                box-shadow: var(--shadow-sm);
                transition: all 180ms ease;
            }}

            div[data-testid="stFileUploader"] section button {{
                border-radius: 13px;
                border-color: rgba(79, 70, 229, 0.18);
                color: var(--primary);
                font-weight: 800;
            }}

            .stButton > button {{
                background: rgba(255,255,255,0.72);
                color: var(--text);
                border: 1px solid rgba(0,0,0,0.06);
                border-radius: 16px;
                min-height: 46px;
                padding: 0.72rem 1.25rem;
                font-weight: 800;
                box-shadow: 0 8px 18px rgba(17, 24, 39, 0.055);
                transition: all 180ms ease;
            }}

            .stButton > button:hover {{
                color: var(--text);
                transform: translateY(-1px);
                border-color: rgba(110, 106, 232, 0.22);
                box-shadow: 0 12px 24px rgba(17, 24, 39, 0.08);
            }}

            .stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, #6E6AE8, #7C83FD);
                color: #FFFFFF;
                border: 1px solid rgba(110, 106, 232, 0.18);
                box-shadow: 0 10px 22px rgba(110, 106, 232, 0.20);
            }}

            .stButton > button[kind="primary"]:hover {{
                background: linear-gradient(135deg, #625FDB, #727AF0);
                color: #FFFFFF;
                box-shadow: 0 12px 26px rgba(110, 106, 232, 0.25);
            }}

            .button-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                border-top: 1px solid var(--border);
                margin-top: 0.35rem;
                padding-top: 0.8rem;
            }}

            .button-row-copy {{
                color: var(--muted);
                font-size: 0.88rem;
            }}

            .candidate-list {{
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }}

            .candidate-row {{
                display: grid;
                grid-template-columns: 42px minmax(180px, 1fr) 92px 120px 112px 170px;
                align-items: center;
                gap: 1rem;
                padding: 0.85rem 1rem;
                transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
            }}

            .recent-candidate-main {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                min-height: 54px;
            }}

            .recent-score {{
                color: var(--primary);
                font-weight: 900;
                font-size: 1.02rem;
                padding-top: 0.85rem;
            }}

            .candidate-row:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
                border-color: rgba(79, 70, 229, 0.16);
            }}

            .candidate-avatar {{
                width: 42px;
                height: 42px;
                border-radius: 15px;
                display: grid;
                place-items: center;
                color: white;
                font-size: 0.82rem;
                font-weight: 900;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
            }}

            .candidate-name {{
                color: var(--text);
                font-size: 0.98rem;
                font-weight: 850;
                line-height: 1.2;
            }}

            .candidate-role, .candidate-meta {{
                color: var(--muted);
                font-size: 0.8rem;
                margin-top: 0.18rem;
            }}

            .score-ring {{
                --score: 0;
                width: 56px;
                height: 56px;
                border-radius: 50%;
                display: grid;
                place-items: center;
                background: conic-gradient(var(--primary) calc(var(--score) * 1%), rgba(17, 24, 39, 0.08) 0);
                position: relative;
            }}

            .score-ring::after {{
                content: "";
                position: absolute;
                width: 42px;
                height: 42px;
                border-radius: 50%;
                background: rgba(255,255,255,0.9);
            }}

            .score-ring span {{
                position: relative;
                z-index: 1;
                color: var(--text);
                font-size: 0.8rem;
                font-weight: 900;
            }}

            .status-badge, .risk-badge {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                border-radius: 999px;
                padding: 0.34rem 0.62rem;
                font-size: 0.76rem;
                font-weight: 850;
                white-space: nowrap;
                background: rgba(59,130,246,0.12);
                color: #1D4ED8;
                border: 1px solid rgba(59,130,246,0.16);
            }}

            .status-shortlisted {{
                background: rgba(34,197,94,0.12);
                color: #15803D;
                border: 1px solid rgba(34,197,94,0.16);
            }}

            .status-review {{
                background: rgba(59,130,246,0.12);
                color: #1D4ED8;
                border: 1px solid rgba(59,130,246,0.16);
            }}

            .status-consider {{
                background: rgba(245,158,11,0.13);
                color: #B45309;
                border: 1px solid rgba(245,158,11,0.18);
            }}

            .status-low {{
                background: rgba(239,68,68,0.10);
                color: #DC2626;
                border: 1px solid rgba(239,68,68,0.16);
            }}

            .action-group {{
                display: flex;
                gap: 0.42rem;
                flex-wrap: wrap;
                justify-content: flex-end;
            }}

            .action-button {{
                border: 1px solid var(--border);
                border-radius: 999px;
                background: rgba(255,255,255,0.74);
                color: var(--text);
                font-size: 0.74rem;
                font-weight: 820;
                padding: 0.34rem 0.56rem;
            }}

            .analytics-grid {{
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.9rem;
            }}

            .analytics-card {{
                padding: 1rem;
                min-height: 210px;
                overflow: hidden;
            }}

            .analytics-title {{
                color: var(--text);
                font-size: 0.95rem;
                font-weight: 850;
                margin-bottom: 0.25rem;
            }}

            .analytics-subtitle {{
                color: var(--muted);
                font-size: 0.78rem;
                line-height: 1.4;
                margin-bottom: 0.85rem;
            }}

            .donut {{
                --value: 70;
                width: 132px;
                height: 132px;
                border-radius: 50%;
                margin: 0.4rem auto;
                display: grid;
                place-items: center;
                background: conic-gradient(var(--primary) calc(var(--value) * 1%), rgba(59,130,246,0.18) 0);
                position: relative;
            }}

            .donut::after {{
                content: "";
                position: absolute;
                width: 92px;
                height: 92px;
                border-radius: 50%;
                background: rgba(255,255,255,0.88);
            }}

            .donut-label {{
                position: relative;
                z-index: 1;
                color: var(--text);
                font-size: 1.35rem;
                font-weight: 900;
            }}

            .radar {{
                width: 150px;
                height: 150px;
                margin: 0.2rem auto;
                border-radius: 30px;
                background:
                    linear-gradient(60deg, transparent 49%, rgba(17,24,39,0.07) 50%, transparent 51%),
                    linear-gradient(120deg, transparent 49%, rgba(17,24,39,0.07) 50%, transparent 51%),
                    radial-gradient(circle, rgba(79,70,229,0.18) 0 38%, transparent 39%),
                    radial-gradient(circle, transparent 0 35%, rgba(17,24,39,0.06) 36% 37%, transparent 38% 60%, rgba(17,24,39,0.05) 61% 62%, transparent 63%);
                position: relative;
            }}

            .radar::after {{
                content: "";
                position: absolute;
                inset: 31px 23px 25px 30px;
                background: linear-gradient(135deg, rgba(79,70,229,0.74), rgba(59,130,246,0.42));
                clip-path: polygon(50% 0, 92% 32%, 76% 92%, 23% 80%, 6% 35%);
                border-radius: 18px;
            }}

            .funnel-step {{
                height: 30px;
                border-radius: 999px;
                margin: 0.45rem auto;
                background: linear-gradient(135deg, rgba(79,70,229,0.86), rgba(59,130,246,0.68));
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.76rem;
                font-weight: 850;
            }}

            .skill-progress-row {{
                margin-bottom: 0.66rem;
            }}

            .skill-progress-label {{
                display: flex;
                justify-content: space-between;
                color: var(--text);
                font-size: 0.82rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }}

            .progress-track, .chart-track {{
                width: 100%;
                height: 9px;
                background: rgba(17,24,39,0.07);
                border-radius: 999px;
                overflow: hidden;
            }}

            .progress-fill, .chart-fill {{
                height: 100%;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                border-radius: 999px;
            }}

            .insights-grid {{
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.9rem;
            }}

            .insight-card {{
                padding: 1rem;
                min-height: 150px;
                transition: transform 180ms ease, box-shadow 180ms ease;
            }}

            .insight-card:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
            }}

            .insight-icon {{
                width: 38px;
                height: 38px;
                display: grid;
                place-items: center;
                border-radius: 14px;
                color: var(--primary);
                background: rgba(79,70,229,0.10);
                font-weight: 900;
                margin-bottom: 0.8rem;
            }}

            .insight-title {{
                color: var(--text);
                font-weight: 850;
                font-size: 0.94rem;
                margin-bottom: 0.4rem;
            }}

            .insight-copy {{
                color: var(--muted);
                font-size: 0.84rem;
                line-height: 1.45;
            }}

            .evidence-card, .snapshot-card {{
                background: rgba(255,255,255,0.70);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 1rem;
                box-shadow: var(--shadow-sm);
            }}

            .info-card {{
                padding: 1rem;
                margin-bottom: 0.85rem;
            }}

            .candidate-title {{
                color: var(--text);
                font-size: 1.45rem;
                line-height: 1.18;
                font-weight: 860;
                margin-bottom: 0.28rem;
            }}

            .candidate-meta, .snapshot-subtitle, .section-caption {{
                color: var(--muted);
                font-size: 0.86rem;
                line-height: 1.45;
            }}

            .snapshot-name {{
                color: var(--text);
                font-size: 1.12rem;
                font-weight: 850;
                line-height: 1.25;
                margin-bottom: 0.25rem;
            }}

            .comparison-label, .evidence-meta {{
                color: var(--muted);
                font-size: 0.76rem;
                font-weight: 850;
                text-transform: uppercase;
                margin-bottom: 0.42rem;
            }}

            .evidence-text {{
                color: var(--text);
                font-size: 0.92rem;
                line-height: 1.52;
            }}

            .section-list {{
                color: var(--text);
                font-size: 0.92rem;
                line-height: 1.55;
                margin: 0;
                padding-left: 1.1rem;
            }}

            .score-row, .chart-row {{
                margin-bottom: 0.82rem;
            }}

            .score-label-row, .chart-label-row {{
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                color: var(--text);
                font-size: 0.86rem;
                font-weight: 820;
                margin-bottom: 0.28rem;
            }}

            .skill-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.85rem;
                padding: 0.62rem 0;
                border-bottom: 1px solid var(--border);
            }}

            .skill-name {{
                color: var(--text);
                font-size: 0.9rem;
                font-weight: 820;
            }}

            .skill-count {{
                color: var(--muted);
                font-size: 0.82rem;
                white-space: nowrap;
            }}

            .risk-badge {{
                background: rgba(239,68,68,0.10);
                color: #DC2626;
                border: 1px solid rgba(239,68,68,0.16);
            }}

            .evidence-meta, .comparison-label, .metric-label {{
                letter-spacing: 0;
            }}

            div[data-testid="stDataFrame"] {{
                border: 1px solid var(--border);
                border-radius: 18px;
                overflow: hidden;
                box-shadow: var(--shadow-sm);
            }}

            @media (max-width: 1100px) {{
                .hero-grid, .analytics-grid, .insights-grid {{
                    grid-template-columns: 1fr 1fr;
                }}

                .candidate-row {{
                    grid-template-columns: 42px minmax(180px, 1fr) 88px;
                }}

                .candidate-status, .candidate-source, .action-group {{
                    grid-column: 2 / span 2;
                    justify-content: flex-start;
                }}
            }}

            @media (max-width: 720px) {{
                .block-container {{
                    padding-left: 1rem;
                    padding-right: 1rem;
                }}

                .top-navbar, .hero-grid, .analytics-grid, .insights-grid {{
                    grid-template-columns: 1fr;
                }}

                .top-navbar {{
                    display: grid;
                }}

                .navbar-actions {{
                    justify-content: space-between;
                }}

                .hero-section {{
                    padding: 1.35rem;
                }}

                .candidate-row {{
                    grid-template-columns: 42px minmax(0, 1fr);
                }}

                .candidate-score, .candidate-status, .candidate-source, .action-group {{
                    grid-column: 1 / span 2;
                    justify-content: flex-start;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active: str = "Dashboard") -> None:
    nav_items = [
        ("DB", "Dashboard"),
        ("UP", "Upload Candidates"),
        ("JD", "JD Analysis"),
        ("RK", "Candidate Rankings"),
        ("AN", "Analytics"),
        ("RP", "Reports"),
        ("ST", "Settings"),
    ]

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-mark">AI</div>
                <div>
                    <div class="brand-title">Recruiter OS</div>
                    <div class="brand-subtitle">AI screening workspace</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for icon, label in nav_items:
            active_class = " active" if label == active else ""
            st.markdown(
                f"""
                <div class="nav-pill{active_class}">
                    <div class="nav-icon">{escape(icon)}</div>
                    <div>{escape(label)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="sidebar-footer-title">Enterprise-ready demo</div>
                <div class="sidebar-footer-copy">Deterministic ranking, human review, analytics, and export workflows remain connected.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_top_navbar() -> None:
    st.markdown(
        """
        <div class="top-navbar">
            <div class="search-shell">Search candidates, skills, reports, or roles</div>
            <div class="navbar-actions">
                <div class="notification-button">N</div>
                <div class="profile-chip">
                    <div class="avatar">HR</div>
                    <div>
                        <div class="profile-name">Recruiter Team</div>
                        <div class="profile-role">Admin workspace</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(
    candidates_processed: int = 0,
    average_score: float = 0.0,
    shortlisted: int = 0,
) -> None:
    st.markdown(
        f"""
        <section class="hero-section">
            <div class="hero-grid">
                <div>
                    <div class="eyebrow">AI recruiter intelligence platform</div>
                    <h1 class="hero-title">AI Resume Intelligence Agent</h1>
                    <p class="hero-subtitle">Accelerating recruiter decision-making with AI-powered candidate evaluation.</p>
                    <div class="hero-actions">
                        <a class="hero-button primary" href="#candidate-intake">Upload Candidate</a>
                        <a class="hero-button secondary" href="#candidate-intake">Upload JD</a>
                    </div>
                </div>
                <div class="live-overview">
                    <div class="live-title">Live Analytics Overview</div>
                    <div class="live-row">
                        <div class="live-label">Candidates processed</div>
                        <div class="live-value">{candidates_processed}</div>
                    </div>
                    <div class="live-row">
                        <div class="live-label">Average match</div>
                        <div class="live-value">{average_score:.0f}%</div>
                    </div>
                    <div class="live-row">
                        <div class="live-label">Shortlisted</div>
                        <div class="live-value">{shortlisted}</div>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_panel_start() -> None:
    return None


def render_panel_end() -> None:
    return None


def render_metric_card(
    label: str,
    value: str,
    help_text: str = "",
    icon: str = "AI",
    trend: str = "Live",
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-icon">{escape(icon)}</div>
                <div class="trend-pill">{escape(trend)}</div>
            </div>
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(str(value))}</div>
            <div class="metric-help">{escape(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_heading(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="dashboard-panel-title">{escape(title)}</div>
        <div class="dashboard-panel-subtitle">{escape(subtitle)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(label: str, variant: str = "status") -> None:
    css_class = "status-badge status-review"

    if variant == "risk":
        css_class = "status-badge status-low"
    elif variant == "success":
        css_class = "status-badge status-shortlisted"
    elif variant == "warning":
        css_class = "status-badge status-consider"

    st.markdown(
        f'<span class="{css_class}">{escape(label)}</span>',
        unsafe_allow_html=True,
    )

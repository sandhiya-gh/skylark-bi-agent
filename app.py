# ============================================================
# SKYLARK BI COPILOT
# Executive Decision Intelligence Platform
# ============================================================

import time
import textwrap
from datetime import datetime

import pandas as pd
import streamlit as st

from config import (
    APP_NAME,
    APP_VERSION,
    DEALS_BOARD_ID,
    WORK_ORDERS_BOARD_ID,
)

from monday_client import (
    MondayClient,
    MondayAPIError,
)

from data_quality import (
    clean_deals,
    clean_work_orders,
    quality_summary,
)

from analytics import (
    pipeline_summary,
    pipeline_by_sector,
    work_order_summary,
    financial_summary,
    execute_tool,
)

from agent import SkylarkAgent


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Skylark BI Copilot",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Render custom HTML safely even when the Python source is indented.
def render_html(html: str, unsafe_allow_html: bool = True) -> None:
    """Render raw HTML directly so Streamlit does not display it as a code block."""
    # Streamlit's st.markdown can render HTML, but newer Streamlit versions
    # may expose raw HTML-like content through the code-block renderer.
    # st.html is the correct renderer for custom HTML/CSS.
    st.html(textwrap.dedent(html).strip())


# ============================================================
# PROFESSIONAL DESIGN SYSTEM
# ============================================================

render_html(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap'
    );

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background: #F7F8FA;
        color: #17202A;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.6rem;
        padding-bottom: 4rem;
    }

    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background: #17202A;
        border-right: 1px solid #27313A;
    }

    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    section[data-testid="stSidebar"] .stButton button {
        background: transparent;
        border: 1px solid #47515A;
        color: #FFFFFF !important;
        border-radius: 8px;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: #26343D;
        border-color: #82909A;
    }

    /* --------------------------------------------------------
       HEADER
    -------------------------------------------------------- */

    .brand-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.3rem;
    }

    .brand {
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: #17202A;
    }

    .brand-sub {
        font-size: 0.78rem;
        color: #667085;
        letter-spacing: 0.04em;
        margin-top: -0.1rem;
    }

    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 11px;
        border: 1px solid #D0D5DD;
        border-radius: 999px;
        background: #FFFFFF;
        color: #344054;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #287D5A;
    }

    .hero-title {
        font-size: 2rem;
        line-height: 1.15;
        font-weight: 700;
        letter-spacing: -0.035em;
        margin-top: 1.25rem;
        margin-bottom: 0.35rem;
        color: #17202A;
    }

    .hero-subtitle {
        color: #667085;
        font-size: 0.92rem;
        margin-bottom: 1.35rem;
    }

    /* --------------------------------------------------------
       SECTION TITLES
    -------------------------------------------------------- */

    .section-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        color: #667085;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.65rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #17202A;
        margin-bottom: 0.7rem;
    }

    /* --------------------------------------------------------
       KPI CARDS
    -------------------------------------------------------- */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 1rem 1.05rem 1.05rem 1.05rem;
        min-height: 118px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
    }

    .kpi-label {
        color: #667085;
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.055em;
        margin-bottom: 0.45rem;
    }

    .kpi-value {
        color: #17202A;
        font-size: 1.65rem;
        line-height: 1.1;
        font-weight: 700;
        letter-spacing: -0.035em;
    }

    .kpi-meta {
        color: #667085;
        font-size: 0.74rem;
        margin-top: 0.45rem;
    }

    .kpi-positive {
        color: #287D5A;
        font-weight: 600;
    }

    .kpi-warning {
        color: #B7791F;
        font-weight: 600;
    }

    .kpi-critical {
        color: #B54747;
        font-weight: 600;
    }

    /* --------------------------------------------------------
       DECISION RADAR
    -------------------------------------------------------- */

    .radar-card {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 1rem 1.05rem;
        min-height: 145px;
    }

    .radar-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #17202A;
    }

    .radar-status {
        display: inline-block;
        margin-top: 0.65rem;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    .status-high {
        color: #8E3A3A;
        background: #FCEAEA;
    }

    .status-watch {
        color: #8A5A12;
        background: #FFF5DD;
    }

    .status-good {
        color: #216246;
        background: #EAF6F0;
    }

    .radar-number {
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
        font-size: 1.45rem;
        font-weight: 600;
        margin-top: 0.55rem;
        color: #17202A;
    }

    .radar-description {
        color: #667085;
        font-size: 0.73rem;
        line-height: 1.45;
        margin-top: 0.3rem;
    }

    /* --------------------------------------------------------
       INSIGHT CARDS
    -------------------------------------------------------- */

    .insight-card {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 1rem 1.05rem;
        height: 100%;
    }

    .insight-number {
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
        color: #667085;
        font-size: 0.72rem;
        font-weight: 600;
    }

    .insight-title {
        color: #17202A;
        font-size: 0.92rem;
        font-weight: 700;
        margin-top: 0.35rem;
    }

    .insight-value {
        color: #1F4E5F;
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 0.35rem;
    }

    .insight-description {
        color: #667085;
        font-size: 0.75rem;
        line-height: 1.5;
        margin-top: 0.4rem;
    }

    /* --------------------------------------------------------
       CHAT
    -------------------------------------------------------- */

    .ask-box {
        background: #17202A;
        border-radius: 14px;
        padding: 1.25rem;
        color: #FFFFFF;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    .ask-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .ask-subtitle {
        color: #AEB7BE;
        font-size: 0.76rem;
    }

    /* --------------------------------------------------------
       DATA CONFIDENCE
    -------------------------------------------------------- */

    .confidence-card {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 1rem;
    }

    .confidence-label {
        font-size: 0.72rem;
        color: #667085;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .confidence-value {
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
        font-size: 1.6rem;
        font-weight: 600;
        color: #17202A;
        margin-top: 0.35rem;
    }

    .confidence-bar {
        height: 6px;
        background: #EAECF0;
        border-radius: 99px;
        margin-top: 0.55rem;
        overflow: hidden;
    }

    .confidence-fill {
        height: 100%;
        background: #1F4E5F;
        border-radius: 99px;
    }

    /* --------------------------------------------------------
       TABLES
    -------------------------------------------------------- */

    .table-header {
        color: #667085;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-weight: 700;
    }

    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer {
        text-align: center;
        color: #98A2B3;
        font-size: 0.7rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E4E7EC;
    }

    /* --------------------------------------------------------
       STREAMLIT OVERRIDES
    -------------------------------------------------------- */

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 0.8rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #667085 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #17202A !important;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #E4E7EC;
        border-radius: 10px;
        background: #FFFFFF;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def money_display(value, fallback="₹0"):
    """Safely format INR values."""
    if value is None:
        return fallback

    try:
        value = float(value)

        crore = value / 10_000_000
        lakh = value / 100_000

        if crore >= 1:
            return f"₹{crore:.2f} Cr"

        if lakh >= 1:
            return f"₹{lakh:.2f} L"

        return f"₹{value:,.0f}"

    except Exception:
        return str(value)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return default


def get_display(data, display_key, numeric_key, default="₹0"):
    if not isinstance(data, dict):
        return default

    if data.get(display_key) is not None:
        return str(data[display_key])

    return money_display(
        data.get(numeric_key),
        default,
    )


def status_for_concentration(value):
    value = safe_float(value)

    if value >= 60:
        return "HIGH", "status-high"

    if value >= 40:
        return "WATCH", "status-watch"

    return "GOOD", "status-good"


def status_for_collection(value):
    value = safe_float(value)

    if value < 60:
        return "HIGH", "status-high"

    if value < 80:
        return "WATCH", "status-watch"

    return "GOOD", "status-good"


def status_for_backlog(value):
    value = safe_float(value)

    if value >= 50:
        return "HIGH", "status-high"

    if value >= 30:
        return "WATCH", "status-watch"

    return "GOOD", "status-good"


def calculate_confidence(pipeline):
    """
    Overall confidence based on value and probability coverage.
    """
    if not isinstance(pipeline, dict):
        return 0

    value_coverage = safe_float(
        pipeline.get("data_coverage", {}).get(
            "value_coverage_pct",
            0,
        )
    )

    probability_coverage = safe_float(
        pipeline.get("data_coverage", {}).get(
            "probability_coverage_pct",
            0,
        )
    )

    if value_coverage == 0 and probability_coverage == 0:
        return 0

    return round(
        (value_coverage + probability_coverage) / 2,
        1,
    )


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False,
)
def load_data():

    client = MondayClient()

    deals_raw, deals_board = client.get_board_dataframe(
        DEALS_BOARD_ID
    )

    work_orders_raw, work_orders_board = (
        client.get_board_dataframe(
            WORK_ORDERS_BOARD_ID
        )
    )

    deals = clean_deals(
        deals_raw
    )

    work_orders = clean_work_orders(
        work_orders_raw
    )

    quality = quality_summary(
        deals,
        work_orders,
    )

    return (
        deals,
        work_orders,
        quality,
        deals_board,
        work_orders_board,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "previous_snapshot" not in st.session_state:
    st.session_state.previous_snapshot = None

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()


# ============================================================
# LOAD DATA
# ============================================================

try:

    (
        deals,
        work_orders,
        quality,
        deals_board,
        work_orders_board,
    ) = load_data()

except MondayAPIError as exc:

    st.error(
        "### Monday.com connection failed\n\n"
        f"{exc}\n\n"
        "Please check the Monday API token and board IDs."
    )

    st.stop()

except Exception as exc:

    st.error(
        "### Application error\n\n"
        f"{exc}"
    )

    st.stop()


# ============================================================
# CORE ANALYTICS
# ============================================================

pipeline = pipeline_summary(
    deals
)

operations = work_order_summary(
    work_orders
)

financials = financial_summary(
    work_orders
)

sector_rows = pipeline_by_sector(
    deals
)

confidence = calculate_confidence(
    pipeline
)

# Shared metrics used by multiple pages (must be outside page blocks)
concentration = safe_float(
    pipeline.get(
        "top_sector_concentration_pct"
    )
)

collection_rate = safe_float(
    financials.get(
        "collection_rate_pct"
    )
)

backlog_ratio = safe_float(
    financials.get(
        "billing_backlog_ratio_pct"
    )
)


# ============================================================
# CURRENT SNAPSHOT
# ============================================================

current_snapshot = {
    "gross_pipeline": safe_float(
        pipeline.get("gross_pipeline")
    ),
    "weighted_pipeline": safe_float(
        pipeline.get("weighted_pipeline")
    ),
    "open_deals": safe_int(
        pipeline.get("open_deals")
    ),
    "active_work_orders": safe_int(
        operations.get("active_work_orders")
    ),
    "receivable": safe_float(
        financials.get("amount_receivable")
    ),
}


# ============================================================
# SNAPSHOT CHANGE DETECTION
# ============================================================

previous_snapshot = st.session_state.previous_snapshot

changes = {}

if previous_snapshot:

    changes["gross_pipeline"] = (
        current_snapshot["gross_pipeline"]
        - previous_snapshot["gross_pipeline"]
    )

    changes["weighted_pipeline"] = (
        current_snapshot["weighted_pipeline"]
        - previous_snapshot["weighted_pipeline"]
    )

    changes["open_deals"] = (
        current_snapshot["open_deals"]
        - previous_snapshot["open_deals"]
    )

    changes["active_work_orders"] = (
        current_snapshot["active_work_orders"]
        - previous_snapshot["active_work_orders"]
    )

    changes["receivable"] = (
        current_snapshot["receivable"]
        - previous_snapshot["receivable"]
    )

st.session_state.previous_snapshot = current_snapshot


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        "assets/skylark_logo.jpeg",
        width="stretch",
    )

    st.markdown(
        """
        <div style="
            margin-top:-8px;
            margin-bottom:18px;
            color:#98A2B3;
            font-size:0.68rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
        ">
            Decision Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        "### Workspace"
    )

    page = st.radio(
        "Navigate",
        [
            "Command Center",
            "Pipeline Intelligence",
            "Cash Control",
            "Operations",
            "Decision Radar",
            "Scenario Lab",
            "Ask Skylark",
            "Data Health",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        "### Data Sources"
    )

    st.success(
        "● Monday.com connected"
    )

    st.caption(
        f"Deals Board · {DEALS_BOARD_ID}"
    )

    st.caption(
        f"Work Orders Board · {WORK_ORDERS_BOARD_ID}"
    )

    st.divider()

    if st.button(
        "↻  Refresh live data",
        width="stretch",
    ):

        st.cache_data.clear()

        st.session_state.last_refresh = datetime.now()

        st.rerun()

    st.divider()

    st.caption(
        f"Last refresh: "
        f"{st.session_state.last_refresh.strftime('%H:%M:%S')}"
    )

    st.caption(
        f"Version {APP_VERSION}"
    )


# ============================================================
# TOP HEADER
# ============================================================

render_html(
    """
    <div class="brand-row">

        <div>
            <div class="hero-title" style="
                margin-top:0;
                margin-bottom:4px;
            ">
                Executive Command Center
            </div>

            <div class="hero-subtitle">
                Business decision intelligence across pipeline,
                execution, cash and risk.
            </div>
        </div>

        <div class="live-pill">
            <span class="live-dot"></span>
            LIVE DATA
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "Command Center":

    render_html(
        '<div class="hero-title">'
        'Executive Command Center'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'A real-time view of pipeline, execution, cash and '
        'leadership risk.'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Open Pipeline
                </div>

                <div class="kpi-value">
                    {get_display(
                        pipeline,
                        "gross_pipeline_display",
                        "gross_pipeline"
                    )}
                </div>

                <div class="kpi-meta">
                    {safe_int(
                        pipeline.get("open_deals")
                    )} open deals
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Weighted Pipeline
                </div>

                <div class="kpi-value">
                    {get_display(
                        pipeline,
                        "weighted_pipeline_display",
                        "weighted_pipeline"
                    )}
                </div>

                <div class="kpi-meta">
                    Probability-adjusted opportunity
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Active Work Orders
                </div>

                <div class="kpi-value">
                    {safe_int(
                        operations.get(
                            "active_work_orders"
                        )
                    )}
                </div>

                <div class="kpi-meta">
                    of {safe_int(
                        operations.get(
                            "total_work_orders"
                        )
                    )} total work orders
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:

        render_html(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    Receivables
                </div>

                <div class="kpi-value">
                    {get_display(
                        financials,
                        "amount_receivable_display",
                        "amount_receivable"
                    )}
                </div>

                <div class="kpi-meta">
                    {safe_float(
                        financials.get(
                            "collection_rate_pct"
                        )
                    )}% collection rate
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # DECISION RADAR
    # --------------------------------------------------------

    render_html(
        '<div class="section-label">'
        'Decision Radar'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="section-title">'
        'Where should leadership look?'
        '</div>',
        unsafe_allow_html=True,
    )

    r1, r2, r3, r4 = st.columns(4)

    concentration_status, concentration_class = (
        status_for_concentration(
            concentration
        )
    )

    collection_status, collection_class = (
        status_for_collection(
            collection_rate
        )
    )

    backlog_status, backlog_class = (
        status_for_backlog(
            backlog_ratio
        )
    )

    confidence_status = (
        "GOOD"
        if confidence >= 85
        else "WATCH"
        if confidence >= 70
        else "HIGH"
    )

    confidence_class = (
        "status-good"
        if confidence >= 85
        else "status-watch"
        if confidence >= 70
        else "status-high"
    )

    with r1:

        render_html(
            f"""
            <div class="radar-card">

                <div class="radar-title">
                    Pipeline concentration
                </div>

                <span class="radar-status {concentration_class}">
                    {concentration_status}
                </span>

                <div class="radar-number">
                    {concentration:.1f}%
                </div>

                <div class="radar-description">
                    Top sector share of total pipeline.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2:

        render_html(
            f"""
            <div class="radar-card">

                <div class="radar-title">
                    Collection efficiency
                </div>

                <span class="radar-status {collection_class}">
                    {collection_status}
                </span>

                <div class="radar-number">
                    {collection_rate:.1f}%
                </div>

                <div class="radar-description">
                    Collected amount relative to billed value.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with r3:

        render_html(
            f"""
            <div class="radar-card">

                <div class="radar-title">
                    Billing backlog
                </div>

                <span class="radar-status {backlog_class}">
                    {backlog_status}
                </span>

                <div class="radar-number">
                    {backlog_ratio:.1f}%
                </div>

                <div class="radar-description">
                    Amount still to be billed as a share of total billable value
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with r4:

        render_html(
            f"""
            <div class="radar-card">

                <div class="radar-title">
                    Data confidence
                </div>

                <span class="radar-status {confidence_class}">
                    {confidence_status}
                </span>

                <div class="radar-number">
                    {confidence:.1f}%
                </div>

                <div class="radar-description">
                    Combined value and probability coverage.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # LEADERSHIP SIGNALS
    # --------------------------------------------------------

    render_html(
        '<div class="section-label">'
        'Leadership signals'
        '</div>',
        unsafe_allow_html=True,
    )

    signal_cols = st.columns(4)

    top_sector = (
        sector_rows[0]
        if sector_rows
        else {}
    )

    with signal_cols[0]:

        render_html(
            f"""
            <div class="insight-card">

                <div class="insight-number">
                    01
                </div>

                <div class="insight-title">
                    Largest exposure
                </div>

                <div class="insight-value">
                    {top_sector.get(
                        "sector",
                        "Unavailable"
                    )}
                </div>

                <div class="insight-description">
                    {top_sector.get(
                        "pipeline_display",
                        "₹0"
                    )} of pipeline value.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with signal_cols[1]:

        render_html(
            f"""
            <div class="insight-card">

                <div class="insight-number">
                    02
                </div>

                <div class="insight-title">
                    Cash pressure
                </div>

                <div class="insight-value">
                    {get_display(
                        financials,
                        "amount_to_be_billed_display",
                        "amount_to_be_billed"
                    )}
                </div>

                <div class="insight-description">
                    Current amount still to be billed.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with signal_cols[2]:

        render_html(
            f"""
            <div class="insight-card">

                <div class="insight-number">
                    03
                </div>

                <div class="insight-title">
                    Execution load
                </div>

                <div class="insight-value">
                    {safe_int(
                        operations.get(
                            "active_work_orders"
                        )
                    )} active
                </div>

                <div class="insight-description">
                    Live work orders requiring execution attention.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with signal_cols[3]:

        render_html(
            f"""
            <div class="insight-card">

                <div class="insight-number">
                    04
                </div>

                <div class="insight-title">
                    Data gaps
                </div>

                <div class="insight-value">
                    {safe_int(
                        pipeline.get(
                            "deals_missing_value"
                        )
                    )} values missing
                </div>

                <div class="insight-description">
                    Plus {safe_int(
                        pipeline.get(
                            "deals_without_probability"
                        )
                    )} deals without probability.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # PIPELINE + OPERATIONS
    # --------------------------------------------------------

    render_html(
        '<div class="section-label">'
        'Portfolio'
        '</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [1.35, 1]
    )

    with left:

        render_html(
            '<div class="section-title">'
            'Pipeline by sector'
            '</div>',
            unsafe_allow_html=True,
        )

        if sector_rows:

            chart_df = pd.DataFrame(
                sector_rows
            )

            if "pipeline" in chart_df.columns:

                chart_df = chart_df[
                    [
                        c
                        for c in [
                            "sector",
                            "pipeline",
                        ]
                        if c in chart_df.columns
                    ]
                ].copy()

                chart_df = chart_df.set_index(
                    "sector"
                )

                st.bar_chart(
                    chart_df[
                        "pipeline"
                    ],
                    height=330,
                )

        else:

            st.info(
                "No sector pipeline data available."
            )

    with right:

        render_html(
            '<div class="section-title">'
            'Operational snapshot'
            '</div>',
            unsafe_allow_html=True,
        )

        op_data = pd.DataFrame(
            {
                "Metric": [
                    "Total work orders",
                    "Active",
                    "Completed",
                    "Active share",
                    "Completion share",
                    "Amount to be billed",
                ],
                "Value": [
                    str(operations.get("total_work_orders", 0)),
                    str(operations.get("active_work_orders", 0)),
                    str(operations.get("completed_work_orders", 0)),
                    f"{operations.get('active_share_pct', 0)}%",
                    f"{operations.get('completion_share_pct', 0)}%",
                    str(
                        financials.get(
                            "amount_to_be_billed_display",
                            "₹0",
                        )
                    ),
                ],
            }
        )

        # Keep the display column explicitly string-typed.
        # This prevents PyArrow from inferring an integer dtype from
        # values such as "55" and then failing on percentage strings
        # such as "31.25%".
        op_data["Metric"] = op_data["Metric"].astype("string")
        op_data["Value"] = op_data["Value"].astype("string")

        st.dataframe(
            op_data,
            hide_index=True,
            width="stretch",
            height=310,
        )

    # --------------------------------------------------------
    # WHAT CHANGED
    # --------------------------------------------------------

    if previous_snapshot:

        render_html(
            '<div class="section-label">'
            'Change detection'
            '</div>',
            unsafe_allow_html=True,
        )

        render_html(
            '<div class="section-title">'
            'What changed since the previous refresh?'
            '</div>',
            unsafe_allow_html=True,
        )

        change_cols = st.columns(5)

        change_items = [
            (
                "Pipeline",
                changes.get(
                    "gross_pipeline",
                    0,
                ),
                True,
            ),
            (
                "Weighted pipeline",
                changes.get(
                    "weighted_pipeline",
                    0,
                ),
                True,
            ),
            (
                "Open deals",
                changes.get(
                    "open_deals",
                    0,
                ),
                False,
            ),
            (
                "Active WOs",
                changes.get(
                    "active_work_orders",
                    0,
                ),
                False,
            ),
            (
                "Receivables",
                changes.get(
                    "receivable",
                    0,
                ),
                True,
            ),
        ]

        for column, item in zip(
            change_cols,
            change_items,
        ):

            label, value, is_money = item

            with column:

                if is_money:

                    formatted = money_display(
                        abs(value)
                    )

                else:

                    formatted = (
                        f"{abs(value):,.0f}"
                    )

                if value > 0:

                    prefix = "+"

                elif value < 0:

                    prefix = "−"

                else:

                    prefix = ""

                st.metric(
                    label,
                    f"{prefix}{formatted}",
                )

    # --------------------------------------------------------
    # ASK SKYLARK CTA
    # --------------------------------------------------------

    render_html(
        """
        <div class="ask-box">

            <div class="ask-title">
                Ask Skylark
            </div>

            <div class="ask-subtitle">
                Ask a founder-level question across Sales,
                Operations and Finance.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        'Try: "What should leadership focus on right now?"'
    )


# ============================================================
# PIPELINE INTELLIGENCE
# ============================================================

elif page == "Pipeline Intelligence":

    render_html(
        '<div class="hero-title">'
        'Pipeline Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'Understand concentration, opportunity quality and sales-stage exposure.'
        '</div>',
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.metric(
            "Gross pipeline",
            get_display(
                pipeline,
                "gross_pipeline_display",
                "gross_pipeline",
            ),
        )

    with p2:
        st.metric(
            "Weighted pipeline",
            get_display(
                pipeline,
                "weighted_pipeline_display",
                "weighted_pipeline",
            ),
        )

    with p3:
        st.metric(
            "Open deals",
            pipeline.get(
                "open_deals",
                0,
            ),
        )

    with p4:
        st.metric(
            "Top-sector concentration",
            f"{concentration:.1f}%",
        )

    st.divider()

    left, right = st.columns(2)

    with left:

        render_html(
            '<div class="section-title">'
            'Sector distribution'
            '</div>',
            unsafe_allow_html=True,
        )

        if sector_rows:

            df = pd.DataFrame(
                sector_rows
            )

            if "pipeline" in df.columns:

                st.bar_chart(
                    df.set_index("sector")[
                        "pipeline"
                    ],
                    height=430,
                )

    with right:

        render_html(
            '<div class="section-title">'
            'Sector intelligence'
            '</div>',
            unsafe_allow_html=True,
        )

        display_rows = []

        for row in sector_rows:

            display_rows.append(
                {
                    "Sector": row.get(
                        "sector",
                        "Unknown",
                    ),
                    "Pipeline": row.get(
                        "pipeline_display",
                        money_display(
                            row.get(
                                "pipeline",
                                0,
                            )
                        ),
                    ),
                    "Deals": row.get(
                        "deals",
                        0,
                    ),
                    "Share": (
                        f"{row.get(
                            'pipeline_share_pct',
                            0
                        )}%"
                    ),
                }
            )

        if display_rows:

            st.dataframe(
                pd.DataFrame(
                    display_rows
                ),
                hide_index=True,
                width="stretch",
                height=430,
            )

    st.divider()

    render_html(
        '<div class="section-title">'
        'Pipeline data integrity'
        '</div>',
        unsafe_allow_html=True,
    )

    q1, q2, q3 = st.columns(3)

    with q1:
        st.metric(
            "Value coverage",
            f"{pipeline.get(
                'data_coverage',
                {}
            ).get(
                'value_coverage_pct',
                0
            )}%",
        )

    with q2:
        st.metric(
            "Probability coverage",
            f"{pipeline.get(
                'data_coverage',
                {}
            ).get(
                'probability_coverage_pct',
                0
            )}%",
        )

    with q3:
        st.metric(
            "Unclassified deals",
            pipeline.get(
                "unknown_sector_deals",
                0,
            ),
        )


# ============================================================
# CASH CONTROL
# ============================================================

elif page == "Cash Control":

    render_html(
        '<div class="hero-title">'
        'Cash Control Center'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'Working-capital visibility across billing, collections and receivables.'
        '</div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.metric(
            "Billed",
            get_display(
                financials,
                "billed_value_display",
                "billed_value",
            ),
        )

    with f2:
        st.metric(
            "Collected",
            get_display(
                financials,
                "collected_amount_display",
                "collected_amount",
            ),
        )

    with f3:
        st.metric(
            "Receivable",
            get_display(
                financials,
                "amount_receivable_display",
                "amount_receivable",
            ),
        )

    with f4:
        st.metric(
            "To be billed",
            get_display(
                financials,
                "amount_to_be_billed_display",
                "amount_to_be_billed",
            ),
        )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        render_html(
            '<div class="section-title">'
            'Collection performance'
            '</div>',
            unsafe_allow_html=True,
        )

        collection = safe_float(
            financials.get(
                "collection_rate_pct"
            )
        )

        st.progress(
            min(
                max(
                    collection / 100,
                    0,
                ),
                1,
            )
        )

        render_html(
            f"""
            <div style="
                font-size:2rem;
                font-weight:700;
                color:#17202A;
                margin-top:.5rem;
            ">
                {collection:.1f}%
            </div>

            <div style="
                color:#667085;
                font-size:.78rem;
            ">
                Current collection rate
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:

        render_html(
            '<div class="section-title">'
            'Billing pressure'
            '</div>',
            unsafe_allow_html=True,
        )

        backlog = safe_float(
            financials.get(
                "billing_backlog_ratio_pct"
            )
        )

        st.progress(
            min(
                max(
                    backlog / 100,
                    0,
                ),
                1,
            )
        )

        render_html(
            f"""
            <div style="
                font-size:2rem;
                font-weight:700;
                color:#17202A;
                margin-top:.5rem;
            ">
                {backlog:.1f}%
            </div>

            <div style="
                color:#667085;
                font-size:.78rem;
            ">
                Billing backlog ratio
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    render_html(
        '<div class="section-title">'
        'Cash-control questions'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Use Ask Skylark to identify which sectors "
        "carry the largest billing or receivable exposure."
    )


# ============================================================
# OPERATIONS
# ============================================================

elif page == "Operations":

    render_html(
        '<div class="hero-title">'
        'Operations Control'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'Execution health across the live work-order portfolio.'
        '</div>',
        unsafe_allow_html=True,
    )

    o1, o2, o3, o4 = st.columns(4)

    with o1:
        st.metric(
            "Total work orders",
            operations.get(
                "total_work_orders",
                0,
            ),
        )

    with o2:
        st.metric(
            "Active",
            operations.get(
                "active_work_orders",
                0,
            ),
        )

    with o3:
        st.metric(
            "Completed",
            operations.get(
                "completed_work_orders",
                0,
            ),
        )

    with o4:
        st.metric(
            "Completion share",
            f"{operations.get(
                'completion_share_pct',
                0
            )}%",
        )

    st.divider()

    status_breakdown = operations.get(
        "status_breakdown",
        {},
    )

    if status_breakdown:

        render_html(
            '<div class="section-title">'
            'Work-order status'
            '</div>',
            unsafe_allow_html=True,
        )

        status_df = pd.DataFrame(
            {
                "Status": list(
                    status_breakdown.keys()
                ),
                "Work Orders": list(
                    status_breakdown.values()
                ),
            }
        )

        st.bar_chart(
            status_df.set_index(
                "Status"
            )["Work Orders"],
            height=420,
        )

        st.dataframe(
            status_df,
            hide_index=True,
            width="stretch",
        )


# ============================================================
# DECISION RADAR
# ============================================================

elif page == "Decision Radar":

    render_html(
        '<div class="hero-title">'
        'Decision Radar'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'Signals that deserve management attention based on the current portfolio.'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LEADERSHIP ANALYSIS
    # --------------------------------------------------------

    try:

        leadership = execute_tool(
            tool_name="leadership_update",
            deals=deals,
            work_orders=work_orders,
            quality=quality,
            sector=None,
            period=None,
        )

    except Exception:

        leadership = {}

    signals = []

    if isinstance(
        leadership,
        dict,
    ):

        signals = leadership.get(
            "leadership_signals",
            [],
        )

    render_html(
        '<div class="section-title">'
        'Priority signals'
        '</div>',
        unsafe_allow_html=True,
    )

    if signals:

        for index, signal in enumerate(
            signals[:8],
            start=1,
        ):

            if isinstance(
                signal,
                dict,
            ):

                message = signal.get(
                    "message",
                    "",
                )

            else:

                message = str(
                    signal
                )

            render_html(
                f"""
                <div class="insight-card"
                     style="margin-bottom:.7rem;">

                    <div class="insight-number">
                        {index:02d}
                    </div>

                    <div class="insight-title">
                        {message}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "No leadership signals are currently available."
        )

    st.divider()

    render_html(
        '<div class="section-title">'
        'Signal summary'
        '</div>',
        unsafe_allow_html=True,
    )

    radar_df = pd.DataFrame(
        {
            "Signal": [
                "Pipeline concentration",
                "Collection efficiency",
                "Billing backlog",
                "Data confidence",
            ],
            "Value": [
                concentration,
                collection_rate,
                backlog_ratio,
                confidence,
            ],
        }
    )

    st.dataframe(
        radar_df,
        hide_index=True,
        width="stretch",
    )


# ============================================================
# SCENARIO LAB
# ============================================================

elif page == "Scenario Lab":

    render_html(
        '<div class="hero-title">'
        'Scenario Lab'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'Stress-test the portfolio using transparent, evidence-based scenarios.'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="section-title">'
        'Scenario 01 · Remove the largest sector'
        '</div>',
        unsafe_allow_html=True,
    )

    if sector_rows:

        largest = sector_rows[0]

        largest_value = safe_float(
            largest.get(
                "pipeline",
                0,
            )
        )

        total_pipeline = safe_float(
            pipeline.get(
                "gross_pipeline"
            )
        )

        scenario_pipeline = (
            total_pipeline
            - largest_value
        )

        scenario_share = (
            (
                scenario_pipeline
                / total_pipeline
                * 100
            )
            if total_pipeline
            else 0
        )

        s1, s2, s3 = st.columns(3)

        with s1:

            st.metric(
                "Current pipeline",
                money_display(
                    total_pipeline
                ),
            )

        with s2:

            st.metric(
                f"Excluding {largest.get('sector', 'top sector')}",
                money_display(
                    scenario_pipeline
                ),
            )

        with s3:

            st.metric(
                "Pipeline removed",
                money_display(
                    largest_value
                ),
            )

        st.warning(
            f"This stress test removes the entire "
            f"{largest.get('sector', 'top sector')} sector "
            f"from the gross pipeline. It is a risk scenario, "
            f"not a forecast."
        )

    st.divider()

    render_html(
        '<div class="section-title">'
        'Scenario 02 · Collection improvement'
        '</div>',
        unsafe_allow_html=True,
    )

    current_collection = safe_float(
        financials.get(
            "collection_rate_pct"
        )
    )

    target_collection = st.slider(
        "Target collection rate",
        min_value=50,
        max_value=100,
        value=min(
            max(
                int(current_collection) + 10,
                50,
            ),
            100,
        ),
        step=1,
    )

    billed = safe_float(
        financials.get(
            "billed_value"
        )
    )

    collected = safe_float(
        financials.get(
            "collected_amount"
        )
    )

    current_gap = max(
        billed - collected,
        0,
    )

    target_collected = (
        billed
        * target_collection
        / 100
    )

    additional_cash = max(
        target_collected - collected,
        0,
    )

    sc1, sc2, sc3 = st.columns(3)

    with sc1:

        st.metric(
            "Current collected",
            money_display(
                collected
            ),
        )

    with sc2:

        st.metric(
            "Scenario collected",
            money_display(
                target_collected
            ),
        )

    with sc3:

        st.metric(
            "Potential additional cash",
            money_display(
                additional_cash
            ),
        )

    st.caption(
        "This scenario assumes the target collection rate "
        "is applied to the currently billed value. It does "
        "not predict timing of collections."
    )


# ============================================================
# ASK SKYLARK
# ============================================================

elif page == "Ask Skylark":

    render_html(
        '<div class="hero-title">'
        'Ask Skylark'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'Ask questions in natural language. Skylark converts live business data into executive decisions.'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        """
        <div class="ask-box">

            <div class="ask-title">
                What would you like to know?
            </div>

            <div class="ask-subtitle">
                Pipeline · Operations · Finance · Risk · Leadership
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    examples = [
        "How is our pipeline looking overall?",
        "Which sectors have the strongest pipeline?",
        "Where is our biggest business risk?",
        "How much money is currently receivable?",
        "Which sectors need leadership attention?",
        "Compare sales pipeline with execution.",
        "Prepare a leadership update.",
        "What data quality issues should I know about?",
    ]

    cols = st.columns(2)

    for index, example in enumerate(examples):

        with cols[index % 2]:

            if st.button(
                example,
                key=f"ask_example_{index}",
                width="stretch",
            ):
                st.session_state.pending_question = example


    if "pending_question" not in st.session_state:
        st.session_state.pending_question = ""

    question = st.chat_input(
        "Ask a business question..."
    )


    if question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message(
            "user"
        ):

            st.markdown(
                question
            )

        agent = SkylarkAgent()

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Analyzing live business data..."
            ):

                try:

                    answer, plan, result = (
                        agent.answer(
                            question,
                            deals,
                            work_orders,
                            quality,
                        )
                    )

                    st.markdown(
                        answer
                    )

                    # ------------------------------------------------
                    # AI / DATA STATUS
                    # ------------------------------------------------

                    if result.get(
                        "llm_used",
                        False,
                    ):

                        st.caption(
                            "● Executive explanation generated "
                            "from verified analytics."
                        )

                    else:

                        st.caption(
                            "● Deterministic analytical response."
                        )

                    # ------------------------------------------------
                    # EVIDENCE
                    # ------------------------------------------------

                    with st.expander(
                        "Evidence & analysis trace"
                    ):

                        st.write(
                            "Analytical operation"
                        )

                        st.code(
                            plan.get(
                                "tool",
                                "unknown",
                            )
                        )

                        if plan.get(
                            "sector"
                        ):

                            st.write(
                                f"Sector: "
                                f"`{plan['sector']}`"
                            )

                        if plan.get(
                            "period"
                        ):

                            st.write(
                                f"Period: "
                                f"`{plan['period']}`"
                            )

                        st.write(
                            "Data confidence"
                        )

                        st.progress(
                            min(
                                max(
                                    confidence / 100,
                                    0,
                                ),
                                1,
                            )
                        )

                        st.caption(
                            f"{confidence:.1f}% based on "
                            "current analytical coverage."
                        )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as exc:

                    st.error(
                        "Skylark could not complete the "
                        f"analysis: {exc}"
                    )

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    if st.session_state.messages:

        st.divider()

        render_html(
            '<div class="section-title">'
            'Conversation'
            '</div>',
            unsafe_allow_html=True,
        )

        for message in st.session_state.messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )


# ============================================================
# DATA HEALTH
# ============================================================

elif page == "Data Health":

    render_html(
        '<div class="hero-title">'
        'Data Health'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="hero-subtitle">'
        'Transparency into the quality and completeness of the data powering decisions.'
        '</div>',
        unsafe_allow_html=True,
    )

    render_html(
        '<div class="section-title">'
        'Pipeline data confidence'
        '</div>',
        unsafe_allow_html=True,
    )

    d1, d2, d3 = st.columns(3)

    value_coverage = safe_float(
        pipeline.get(
            "data_coverage",
            {}
        ).get(
            "value_coverage_pct",
            0,
        )
    )

    probability_coverage = safe_float(
        pipeline.get(
            "data_coverage",
            {}
        ).get(
            "probability_coverage_pct",
            0,
        )
    )

    with d1:

        render_html(
            f"""
            <div class="confidence-card">

                <div class="confidence-label">
                    Overall confidence
                </div>

                <div class="confidence-value">
                    {confidence:.1f}%
                </div>

                <div class="confidence-bar">
                    <div class="confidence-fill"
                         style="width:{min(confidence,100)}%;">
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with d2:

        render_html(
            f"""
            <div class="confidence-card">

                <div class="confidence-label">
                    Deal value coverage
                </div>

                <div class="confidence-value">
                    {value_coverage:.1f}%
                </div>

                <div class="confidence-bar">
                    <div class="confidence-fill"
                         style="width:{min(value_coverage,100)}%;">
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with d3:

        render_html(
            f"""
            <div class="confidence-card">

                <div class="confidence-label">
                    Probability coverage
                </div>

                <div class="confidence-value">
                    {probability_coverage:.1f}%
                </div>

                <div class="confidence-bar">
                    <div class="confidence-fill"
                         style="width:{min(probability_coverage,100)}%;">
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    render_html(
        '<div class="section-title">'
        'Known data gaps'
        '</div>',
        unsafe_allow_html=True,
    )

    gaps = [
        (
            "Missing deal values",
            pipeline.get(
                "deals_missing_value",
                0,
            ),
            "Open deals without a usable financial value.",
        ),
        (
            "Missing probabilities",
            pipeline.get(
                "deals_without_probability",
                0,
            ),
            "Open deals without a usable closure probability.",
        ),
        (
            "Unclassified deals",
            pipeline.get(
                "unknown_sector_deals",
                0,
            ),
            "Deals without a recognised sector classification.",
        ),
    ]

    for index, gap in enumerate(
        gaps,
        start=1,
    ):

        label, count, description = gap

        render_html(
            f"""
            <div class="insight-card"
                 style="margin-bottom:.75rem;">

                <div class="insight-number">
                    {index:02d}
                </div>

                <div class="insight-title">
                    {label}
                </div>

                <div class="insight-value">
                    {count}
                </div>

                <div class="insight-description">
                    {description}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    render_html(
        '<div class="section-title">'
        'Source coverage'
        '</div>',
        unsafe_allow_html=True,
    )

    source_df = pd.DataFrame(
        {
            "Dataset": [
                "Deals",
                "Work Orders",
            ],
            "Records": [
                len(deals),
                len(work_orders),
            ],
            "Source": [
                "Monday.com",
                "Monday.com",
            ],
        }
    )

    st.dataframe(
        source_df,
        hide_index=True,
        width="stretch",
    )


# ============================================================
# FOOTER
# ============================================================

render_html(
    f"""
    <div class="footer">
        SKYLARK BI COPILOT · {APP_VERSION}
        · Live Monday.com decision intelligence
    </div>
    """,
    unsafe_allow_html=True,
)
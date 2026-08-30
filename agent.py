"""
Skylark BI Copilot
==================

Conversational orchestration layer.

Architecture:

User question
      ↓
Intent detection
      ↓
Deterministic analytics
      ↓
Gemini explanation
      ↓
Executive answer

Important:
The LLM does NOT calculate financial metrics.
Python analytics remains the source of truth.
"""

import json
import time
from typing import Any, Dict, Optional

from google import genai

from analytics import execute_tool
from config import GEMINI_API_KEY, GEMINI_MODEL


# ============================================================
# GEMINI CLIENT
# ============================================================

_gemini_client = None


def get_gemini_client():
    """Create the Gemini client once and reuse it."""

    global _gemini_client

    if _gemini_client is None:

        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is missing."
            )

        _gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    return _gemini_client


# ============================================================
# KNOWN SECTORS
# ============================================================

KNOWN_SECTORS = [
    "energy",
    "renewables",
    "mining",
    "railways",
    "powerline",
    "construction",
    "tender",
    "dsp",
    "security and surveillance",
]


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    """Normalize text for query matching."""

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def extract_sector(
    question: str
) -> Optional[str]:
    """Extract a known sector from a user question."""

    q = normalize_text(question)

    for sector in KNOWN_SECTORS:

        if sector in q:

            return sector.title()

    return None


def extract_period(
    question: str
) -> Optional[str]:
    """Extract a business period from a question."""

    q = normalize_text(question)

    # Quarter
    if (
        "this quarter" in q
        or "current quarter" in q
        or "quarter" in q
        or "qtd" in q
    ):
        return "this quarter"

    # Month
    if (
        "this month" in q
        or "current month" in q
        or "month" in q
        or "mtd" in q
    ):
        return "this month"

    # Year
    if (
        "this year" in q
        or "current year" in q
        or "year" in q
        or "ytd" in q
    ):
        return "this year"

    return None


# ============================================================
# QUERY UNDERSTANDING
# ============================================================

def classify_query(
    question: str
) -> Dict[str, Any]:
    """
    Convert founder-style natural language into a
    deterministic analytics operation.
    """

    q = normalize_text(question)

    # --------------------------------------------------------
    # LEADERSHIP
    # --------------------------------------------------------

    leadership_terms = [
        "leadership",
        "executive",
        "founder",
        "management",
        "board update",
        "leadership update",
        "what should we focus",
        "where should we focus",
        "what needs attention",
        "needs attention",
        "priority",
        "priorities",
        "key risks",
        "risks",
        "business health",
        "overall health",
        "leadership attention",
    ]

    if any(
        term in q
        for term in leadership_terms
    ):

        return {
            "tool": "leadership_update",
            "sector": None,
            "period": None,
        }

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    quality_terms = [
        "data quality",
        "missing data",
        "missing fields",
        "data issue",
        "data issues",
        "data problem",
        "data problems",
        "incomplete records",
        "incomplete data",
    ]

    if any(
        term in q
        for term in quality_terms
    ):

        return {
            "tool": "data_quality",
            "sector": None,
            "period": None,
        }

    # --------------------------------------------------------
    # CROSS BOARD
    # --------------------------------------------------------

    cross_terms = [
        "compare pipeline",
        "compare sales",
        "sales and execution",
        "sales vs execution",
        "pipeline and execution",
        "pipeline with execution",
        "pipeline versus execution",
        "pipeline and work orders",
        "across boards",
        "cross board",
        "cross-board",
    ]

    if any(
        term in q
        for term in cross_terms
    ):

        return {
            "tool": "cross_board",
            "sector": extract_sector(q),
            "period": None,
        }

    # --------------------------------------------------------
    # FINANCIAL
    # --------------------------------------------------------

    financial_terms = [
        "receivable",
        "receivables",
        "collection",
        "collections",
        "collected",
        "cash",
        "billing",
        "billed",
        "to be billed",
        "financial",
        "finance",
        "revenue",
        "money",
        "outstanding",
        "payment",
        "payments",
    ]

    if any(
        term in q
        for term in financial_terms
    ):

        return {
            "tool": "financial_summary",
            "sector": extract_sector(q),
            "period": None,
        }

    # --------------------------------------------------------
    # WORK ORDERS
    # --------------------------------------------------------

    operational_terms = [
        "work order",
        "work orders",
        "execution",
        "operations",
        "operational",
        "project execution",
        "active projects",
        "completed projects",
        "projects",
    ]

    if any(
        term in q
        for term in operational_terms
    ):

        return {
            "tool": "work_order_summary",
            "sector": extract_sector(q),
            "period": None,
        }

    # --------------------------------------------------------
    # PIPELINE BY SECTOR
    # --------------------------------------------------------

    sector_terms = [
        "by sector",
        "sector wise",
        "sector-wise",
        "sector breakdown",
        "sector performance",
        "which sector",
        "strongest sector",
        "largest sector",
        "top sector",
        "sector pipeline",
        "best sector",
        "leading sector",
    ]

    if any(
        term in q
        for term in sector_terms
    ):

        return {
            "tool": "pipeline_by_sector",
            "sector": None,
            "period": None,
        }

    # --------------------------------------------------------
    # PIPELINE BY STAGE
    # --------------------------------------------------------

    stage_terms = [
        "stage",
        "stages",
        "sales stage",
        "deal stage",
        "funnel",
        "funnel stage",
        "pipeline stage",
    ]

    if any(
        term in q
        for term in stage_terms
    ):

        return {
            "tool": "pipeline_by_stage",
            "sector": None,
            "period": None,
        }

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return {
        "tool": "pipeline_summary",
        "sector": extract_sector(q),
        "period": extract_period(q),
    }


# ============================================================
# JSON SAFETY
# ============================================================

def json_safe(
    value: Any
) -> Any:

    if isinstance(value, dict):

        return {
            str(key): json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, list):

        return [
            json_safe(item)
            for item in value
        ]

    if hasattr(
        value,
        "isoformat"
    ):

        return value.isoformat()

    try:

        json.dumps(value)

        return value

    except (
        TypeError,
        ValueError
    ):

        return str(value)


# ============================================================
# GEMINI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Skylark BI Copilot, a founder-level business
intelligence assistant.

You answer questions using LIVE Monday.com business data
processed by a deterministic analytics engine.

Your job is to explain the analytical result clearly.

============================================================
ABSOLUTE RULES
============================================================

1. NEVER invent a number.

2. NEVER invent a sector, deal, work order, customer, date,
   revenue figure, probability, or financial value.

3. Treat the supplied ANALYTICS RESULT as the source of truth.

4. Python analytics has already performed the calculations.

5. Do not independently calculate business metrics.

6. Clearly distinguish FACTS from INTERPRETATION.

7. If the requested sector has zero records, say that there
   are zero records in the source classification.

8. Do NOT merge Energy with Renewables unless the source
   data explicitly provides such a mapping.

9. Mention meaningful data-quality caveats.

10. Do not overwhelm executives with raw fields.

11. Prioritize what the result means for the business.

12. Give actionable recommendations only when supported
    by the analytical evidence.

============================================================
RESPONSE STYLE
============================================================

Use this structure where appropriate:

### Executive view

2-3 sentences summarizing the result.

### What stands out

2-4 concise bullets.

### Leadership attention

1-3 concrete actions.

### Data caveat

Only include when relevant.

Tone:

- confident
- concise
- analytical
- business-oriented
- founder-friendly

Do not mention Python, APIs, prompts, tools, or internal
implementation details in the answer.
"""


# ============================================================
# GEMINI GENERATION
# ============================================================

def generate_gemini_response(
    question: str,
    analysis: Any
) -> Optional[str]:
    """
    Generate an executive explanation from deterministic
    analytics.

    Returns None if Gemini is temporarily unavailable.
    """

    client = get_gemini_client()

    safe_analysis = json_safe(
        analysis
    )

    prompt = f"""
{SYSTEM_PROMPT}

============================================================
USER QUESTION
============================================================

{question}

============================================================
DETERMINISTIC ANALYTICS RESULT
============================================================

{json.dumps(
    safe_analysis,
    indent=2,
    ensure_ascii=False
)}

============================================================
TASK
============================================================

Answer the user's question using ONLY the analytical result.

Do not invent missing information.

If the result contains a data-quality warning, communicate
it clearly.

Make the answer useful to a founder or executive.
"""

    # --------------------------------------------------------
    # RETRIES
    # --------------------------------------------------------

    attempts = 3

    for attempt in range(attempts):

        try:

            response = (
                client.models
                .generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                )
            )

            text = getattr(
                response,
                "text",
                None
            )

            if text:
                return text.strip()

            return None

        except Exception:

            if attempt < attempts - 1:

                time.sleep(
                    1.5 * (attempt + 1)
                )

    return None


# ============================================================
# DISPLAY HELPERS
# ============================================================

def _display(
    analysis: Dict[str, Any],
    display_key: str,
    numeric_key: str,
    default: str = "₹0"
) -> str:

    value = analysis.get(
        display_key
    )

    if value is not None:
        return str(value)

    value = analysis.get(
        numeric_key
    )

    if value is None:
        return default

    try:

        value = float(value)

        crore = value / 10_000_000

        if crore >= 1:
            return f"₹{crore:.2f} Cr"

        lakh = value / 100_000

        if lakh >= 1:
            return f"₹{lakh:.2f} L"

        return f"₹{value:,.0f}"

    except Exception:

        return str(value)


# ============================================================
# DETERMINISTIC FALLBACK
# ============================================================

def fallback_response(
    question: str,
    analysis: Any,
    tool: str
) -> str:
    """
    Guaranteed response if Gemini is unavailable.
    """

    # --------------------------------------------------------
    # PIPELINE SUMMARY
    # --------------------------------------------------------

    if tool == "pipeline_summary":

        if not isinstance(
            analysis,
            dict
        ):

            return (
                "### Executive view\n\n"
                "The pipeline analysis is currently "
                "unavailable."
            )

        message = analysis.get(
            "message"
        )

        if message:

            return (
                "### Executive view\n\n"
                f"{message}\n\n"
                "### Data caveat\n\n"
                "The result is based on the exact sector "
                "classification in Monday.com."
            )

        gross = _display(
            analysis,
            "gross_pipeline_display",
            "gross_pipeline",
        )

        weighted = _display(
            analysis,
            "weighted_pipeline_display",
            "weighted_pipeline",
        )

        open_deals = analysis.get(
            "open_deals",
            0
        )

        response = (
            "### Executive view\n\n"
            f"The current open pipeline is "
            f"**{gross} gross** and "
            f"**{weighted} weighted** across "
            f"**{open_deals} open deals**."
        )

        concentration = analysis.get(
            "top_sector_concentration_pct"
        )

        if concentration is not None:

            response += (
                "\n\n### What stands out\n\n"
                f"- The largest sector represents "
                f"**{concentration}%** of gross pipeline."
            )

        caveats = []

        missing_probability = analysis.get(
            "deals_without_probability",
            0
        )

        missing_value = analysis.get(
            "deals_missing_value",
            0
        )

        if missing_probability:

            caveats.append(
                f"{missing_probability} deals lack a "
                "usable closure probability."
            )

        if missing_value:

            caveats.append(
                f"{missing_value} deals are missing "
                "deal value."
            )

        if caveats:

            response += (
                "\n\n### Data caveat\n\n"
                + "\n".join(
                    f"- {item}"
                    for item in caveats
                )
            )

        return response

    # --------------------------------------------------------
    # PIPELINE BY SECTOR
    # --------------------------------------------------------

    if tool == "pipeline_by_sector":

        if not analysis:

            return (
                "### Pipeline by sector\n\n"
                "No sector-level pipeline data is "
                "currently available."
            )

        lines = []

        for row in analysis[:8]:

            lines.append(
                f"- **{row.get('sector', 'Unknown')}** — "
                f"{row.get('pipeline_display', '₹0')} "
                f"across {row.get('deals', 0)} deals "
                f"({row.get('pipeline_share_pct', 0)}% "
                f"of pipeline)"
            )

        return (
            "### Pipeline by sector\n\n"
            + "\n".join(lines)
            + "\n\n"
            "### Leadership attention\n\n"
            "Review concentration in the largest "
            "pipeline segments and their conversion "
            "confidence."
        )

    # --------------------------------------------------------
    # PIPELINE BY STAGE
    # --------------------------------------------------------

    if tool == "pipeline_by_stage":

        if not analysis:

            return (
                "### Pipeline funnel\n\n"
                "No pipeline-stage data is currently "
                "available."
            )

        lines = []

        for row in analysis[:8]:

            lines.append(
                f"- **{row.get('stage', 'Unknown')}** — "
                f"{row.get('pipeline_display', '₹0')} "
                f"({row.get('deals', 0)} deals)"
            )

        return (
            "### Pipeline funnel\n\n"
            + "\n".join(lines)
        )

    # --------------------------------------------------------
    # WORK ORDERS
    # --------------------------------------------------------

    if tool == "work_order_summary":

        if not isinstance(
            analysis,
            dict
        ):

            return (
                "### Operational view\n\n"
                "No operational analysis is currently "
                "available."
            )

        total = analysis.get(
            "total_work_orders",
            0
        )

        active = analysis.get(
            "active_work_orders",
            0
        )

        completed = analysis.get(
            "completed_work_orders",
            0
        )

        return (
            "### Operational view\n\n"
            f"There are **{total} work orders**, "
            f"with **{active} active** and "
            f"**{completed} completed**.\n\n"
            "### Leadership attention\n\n"
            "Focus on active execution, billing "
            "backlog, and collection dependencies."
        )

    # --------------------------------------------------------
    # FINANCIAL
    # --------------------------------------------------------

    if tool == "financial_summary":

        if not isinstance(
            analysis,
            dict
        ):

            return (
                "### Financial view\n\n"
                "No financial analysis is currently "
                "available."
            )

        billed = _display(
            analysis,
            "billed_value_display",
            "billed_value",
        )

        collected = _display(
            analysis,
            "collected_amount_display",
            "collected_amount",
        )

        to_bill = _display(
            analysis,
            "amount_to_be_billed_display",
            "amount_to_be_billed",
        )

        receivable = _display(
            analysis,
            "amount_receivable_display",
            "amount_receivable",
        )

        collection_rate = analysis.get(
            "collection_rate_pct",
            0
        )

        return (
            "### Financial view\n\n"
            f"- Billed: **{billed}**\n"
            f"- Collected: **{collected}**\n"
            f"- Yet to be billed: **{to_bill}**\n"
            f"- Receivables: **{receivable}**\n"
            f"- Collection rate: **{collection_rate}%**\n\n"
            "### Leadership attention\n\n"
            "Receivables and the amount still to be "
            "billed are the immediate working-capital "
            "areas to review."
        )

    # --------------------------------------------------------
    # CROSS BOARD
    # --------------------------------------------------------

    if tool == "cross_board":

        if not analysis:

            return (
                "### Cross-board executive view\n\n"
                "No cross-board data is currently "
                "available."
            )

        rows = sorted(
            analysis,
            key=lambda x: x.get(
                "billing_backlog",
                0
            ),
            reverse=True,
        )

        lines = []

        for row in rows[:5]:

            lines.append(
                f"- **{row.get('sector', 'Unknown')}** — "
                f"pipeline {row.get('pipeline_display', '₹0')}, "
                f"{row.get('active_work_orders', 0)} active WOs, "
                f"billing backlog "
                f"{row.get('billing_backlog_display', '₹0')}"
            )

        return (
            "### Cross-board executive view\n\n"
            + "\n".join(lines)
            + "\n\n"
            "### Leadership attention\n\n"
            "Prioritize sectors where active execution "
            "and billing backlog occur together."
        )

    # --------------------------------------------------------
    # LEADERSHIP UPDATE
    # --------------------------------------------------------

    if tool == "leadership_update":

        if not isinstance(
            analysis,
            dict
        ):

            return (
                "### Leadership update\n\n"
                "The leadership analysis is currently "
                "unavailable."
            )

        pipeline = analysis.get(
            "pipeline",
            {}
        )

        operations = analysis.get(
            "operations",
            {}
        )

        financials = analysis.get(
            "financials",
            {}
        )

        signals = analysis.get(
            "leadership_signals",
            []
        )

        pipeline_gross = _display(
            pipeline,
            "gross_pipeline_display",
            "gross_pipeline",
        )

        pipeline_weighted = _display(
            pipeline,
            "weighted_pipeline_display",
            "weighted_pipeline",
        )

        receivable = _display(
            financials,
            "amount_receivable_display",
            "amount_receivable",
        )

        to_bill = _display(
            financials,
            "amount_to_be_billed_display",
            "amount_to_be_billed",
        )

        response = (
            "### Leadership update\n\n"
            f"**Pipeline:** "
            f"{pipeline_gross} gross / "
            f"{pipeline_weighted} weighted across "
            f"{pipeline.get('open_deals', 0)} open deals.\n\n"
            f"**Operations:** "
            f"{operations.get('active_work_orders', 0)} "
            f"active work orders out of "
            f"{operations.get('total_work_orders', 0)}.\n\n"
            f"**Cash & billing:** "
            f"{receivable} receivable and "
            f"{to_bill} yet to be billed."
        )

        if signals:

            response += (
                "\n\n### Leadership attention\n\n"
            )

            for index, signal in enumerate(
                signals[:5],
                start=1
            ):

                if isinstance(
                    signal,
                    dict
                ):

                    message = signal.get(
                        "message",
                        ""
                    )

                else:

                    message = str(signal)

                response += (
                    f"{index}. {message}\n"
                )

        return response

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    if tool == "data_quality":

        if not analysis:

            return (
                "### Data quality overview\n\n"
                "No data-quality report is currently "
                "available."
            )

        response = (
            "### Data quality overview\n\n"
        )

        if isinstance(
            analysis,
            dict
        ):

            for dataset, report in analysis.items():

                if isinstance(
                    report,
                    dict
                ):

                    response += (
                        f"**{str(dataset).title()}** — "
                        f"{report.get('rows', 0)} rows\n"
                    )

                    for issue in report.get(
                        "issues",
                        []
                    )[:5]:

                        response += (
                            f"- {issue}\n"
                        )

        return response

    # --------------------------------------------------------
    # GENERIC FALLBACK
    # --------------------------------------------------------

    return (
        "### Analysis\n\n"
        "The requested business analysis is "
        "currently unavailable."
    )


# ============================================================
# CORE ANSWER FUNCTION
# ============================================================

def answer_question(
    question: str,
    deals,
    work_orders,
    quality
) -> Dict[str, Any]:
    """
    Main conversational agent function.
    """

    question = (
        question or ""
    ).strip()

    if not question:

        return {
            "answer":
                "Please enter a business question.",
            "tool":
                None,
            "sector":
                None,
            "period":
                None,
            "analysis":
                None,
            "llm_used":
                False,
            "status":
                "empty_question",
        }

    # --------------------------------------------------------
    # UNDERSTAND
    # --------------------------------------------------------

    classification = classify_query(
        question
    )

    tool = classification[
        "tool"
    ]

    sector = classification.get(
        "sector"
    )

    period = classification.get(
        "period"
    )

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    try:

        analysis = execute_tool(
            tool_name=tool,
            deals=deals,
            work_orders=work_orders,
            quality=quality,
            sector=sector,
            period=period,
        )

    except Exception as error:

        return {
            "answer": (
                "I couldn't complete that analysis "
                "because the analytics engine returned "
                "an error. Please try again."
            ),
            "tool":
                tool,
            "sector":
                sector,
            "period":
                period,
            "analysis":
                None,
            "llm_used":
                False,
            "status":
                "analytics_error",
            "error":
                str(error),
        }

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    ai_answer = None

    try:

        ai_answer = generate_gemini_response(
            question,
            analysis,
        )

    except Exception:

        ai_answer = None

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if ai_answer:

        answer = ai_answer
        llm_used = True
        status = "success"

    else:

        answer = fallback_response(
            question,
            analysis,
            tool,
        )

        llm_used = False
        status = "llm_fallback"

    return {
        "answer":
            answer,
        "tool":
            tool,
        "sector":
            sector,
        "period":
            period,
        "analysis":
            analysis,
        "llm_used":
            llm_used,
        "status":
            status,
    }


# ============================================================
# SKYLARK AGENT CLASS
# ============================================================

class SkylarkAgent:
    """
    High-level wrapper used by the Streamlit application.

    This class exists so app.py can simply do:

        agent = SkylarkAgent()

        result = agent.ask(
            question,
            deals,
            work_orders,
            quality
        )
    """

    def __init__(
        self,
        deals=None,
        work_orders=None,
        quality=None,
    ):

        self.deals = deals
        self.work_orders = work_orders
        self.quality = quality


    def set_data(
        self,
        deals,
        work_orders,
        quality=None,
    ):
        """
        Update the datasets used by the agent.
        """

        self.deals = deals
        self.work_orders = work_orders
        self.quality = quality


    def ask(
        self,
        question: str,
        deals=None,
        work_orders=None,
        quality=None,
    ) -> Dict[str, Any]:
        """
        Ask a founder-level business question.
        """

        final_deals = (
            deals
            if deals is not None
            else self.deals
        )

        final_work_orders = (
            work_orders
            if work_orders is not None
            else self.work_orders
        )

        final_quality = (
            quality
            if quality is not None
            else self.quality
        )

        if final_deals is None:

            return {
                "answer": (
                    "Deals data is not loaded yet."
                ),
                "tool": None,
                "sector": None,
                "period": None,
                "analysis": None,
                "llm_used": False,
                "status": "missing_deals",
            }

        if final_work_orders is None:

            return {
                "answer": (
                    "Work Orders data is not loaded yet."
                ),
                "tool": None,
                "sector": None,
                "period": None,
                "analysis": None,
                "llm_used": False,
                "status": "missing_work_orders",
            }

        return answer_question(
            question=question,
            deals=final_deals,
            work_orders=final_work_orders,
            quality=final_quality,
        )


    def answer(
        self,
        question: str,
        deals=None,
        work_orders=None,
        quality=None,
    ):
        """
        Compatibility method for app.py.

        app.py expects:
            answer, plan, result = agent.answer(...)

        The existing ask() method correctly returns a single
        result dictionary. This method keeps that API intact while
        exposing the same information as a 3-tuple for Streamlit.
        """

        result = self.ask(
            question=question,
            deals=deals,
            work_orders=work_orders,
            quality=quality,
        )

        plan = {
            "tool": result.get("tool"),
            "sector": result.get("sector"),
            "period": result.get("period"),
        }

        return (
            result.get("answer", ""),
            plan,
            result,
        )


    def classify(
        self,
        question: str,
    ) -> Dict[str, Any]:
        """
        Expose query classification for testing.
        """

        return classify_query(
            question
        )
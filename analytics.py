"""
Skylark BI Copilot - Deterministic Business Intelligence Engine

This module contains all business calculations used by the agent.

IMPORTANT:
- Data comes dynamically from Monday.com.
- No CSV values are hardcoded here.
- The LLM should explain these results, not calculate them.
"""

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


# ============================================================
# CONSTANTS
# ============================================================

ACTIVE_WORK_ORDER_STATUSES = {
    "ongoing",
    "not started",
    "partial completed",
    "partialcompleted",
    "pause / struck",
    "details pending from client",
    "executed until current month",
}

OPEN_DEAL_STATUSES = {
    "open",
    "on hold",
}

KNOWN_SECTORS = {
    "energy",
    "renewables",
    "mining",
    "railways",
    "powerline",
    "construction",
    "tender",
    "dsp",
    "security and surveillance",
}


# ============================================================
# FORMATTING HELPERS
# ============================================================

def money(value: Any) -> str:
    """
    Convert INR into an executive-friendly representation.

    Examples:
        688152293 -> ₹68.82 Cr
        2560000   -> ₹25.60 L
        50000     -> ₹50,000
    """

    if value is None:
        return "₹0"

    try:
        if pd.isna(value):
            return "₹0"
    except (TypeError, ValueError):
        pass

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "₹0"

    if abs(value) >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"

    if abs(value) >= 100_000:
        return f"₹{value / 100_000:.2f} L"

    return f"₹{value:,.0f}"


def percentage(
    numerator: float,
    denominator: float
) -> float:
    """Return a safe percentage."""

    if denominator in (0, None):
        return 0.0

    return round(
        (float(numerator) / float(denominator)) * 100,
        2
    )


def normalize_text(value: Any) -> str:
    """
    Normalize a text field for reliable comparisons.

    Handles:
        None
        NaN
        leading/trailing spaces
        repeated spaces
        case differences
    """

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    text = str(value).strip().lower()

    # Collapse repeated whitespace.
    text = " ".join(text.split())

    return text


def display_text(
    value: Any,
    unknown_label: str = "Unknown / Unclassified"
) -> str:
    """Return clean display text."""

    if value is None:
        return unknown_label

    try:
        if pd.isna(value):
            return unknown_label
    except (TypeError, ValueError):
        pass

    text = str(value).strip()

    if not text:
        return unknown_label

    return text


def numeric_series(
    df: pd.DataFrame,
    column: str
) -> pd.Series:
    """Safely convert a dataframe column into numeric values."""

    if column not in df.columns:
        return pd.Series(
            0.0,
            index=df.index,
            dtype="float64"
        )

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# DATE / PERIOD HELPERS
# ============================================================

def _quarter_dates(
    reference_date: Optional[pd.Timestamp] = None
) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Return current calendar-quarter start and end.

    The end date is exclusive.
    """

    if reference_date is None:
        today = pd.Timestamp.today().normalize()
    else:
        today = pd.Timestamp(reference_date).normalize()

    quarter = ((today.month - 1) // 3) + 1

    start_month = (
        3 * (quarter - 1)
    ) + 1

    start = pd.Timestamp(
        year=today.year,
        month=start_month,
        day=1
    )

    if quarter == 4:

        end = pd.Timestamp(
            year=today.year + 1,
            month=1,
            day=1
        )

    else:

        end = pd.Timestamp(
            year=today.year,
            month=start_month + 3,
            day=1
        )

    return start, end


def _apply_period(
    df: pd.DataFrame,
    date_column: str,
    period: Optional[str]
) -> pd.DataFrame:
    """
    Filter a dataframe using a natural-language period.

    Supported:
        this quarter
        current quarter
        quarter
        qtd

        this month
        current month
        month
        mtd

        this year
        current year
        year
        ytd
    """

    if df.empty:
        return df.copy()

    if not period:
        return df.copy()

    period_lower = normalize_text(period)

    if period_lower in {
        "all",
        "overall",
        "all periods",
    }:
        return df.copy()

    if date_column not in df.columns:
        return df.copy()

    dates = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    today = pd.Timestamp.today().normalize()

    # --------------------------------------------------------
    # CURRENT QUARTER
    # --------------------------------------------------------

    if (
        "quarter" in period_lower
        or "qtd" in period_lower
    ):

        start, end = _quarter_dates(today)

        mask = (
            dates >= start
        ) & (
            dates < end
        )

        return df.loc[mask].copy()

    # --------------------------------------------------------
    # CURRENT MONTH
    # --------------------------------------------------------

    if (
        "month" in period_lower
        or "mtd" in period_lower
    ):

        start = today.replace(day=1)

        mask = (
            dates >= start
        ) & (
            dates <= today
        )

        return df.loc[mask].copy()

    # --------------------------------------------------------
    # CURRENT YEAR
    # --------------------------------------------------------

    if (
        "year" in period_lower
        or "ytd" in period_lower
    ):

        start = today.replace(
            month=1,
            day=1
        )

        mask = (
            dates >= start
        ) & (
            dates <= today
        )

        return df.loc[mask].copy()

    return df.copy()


# ============================================================
# SECTOR FILTER
# ============================================================

def _filter_sector(
    df: pd.DataFrame,
    sector: Optional[str]
) -> pd.DataFrame:
    """
    Case-insensitive exact sector filtering.

    IMPORTANT:
    Energy and Renewables are intentionally separate.
    We do not infer that one means the other.
    """

    if not sector:
        return df.copy()

    if "sector" not in df.columns:
        return df.copy()

    requested = normalize_text(sector)

    normalized = (
        df["sector"]
        .apply(normalize_text)
    )

    return df.loc[
        normalized == requested
    ].copy()


# ============================================================
# DEAL STATUS
# ============================================================

def _open_deals(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Keep currently open/on-hold deals.
    """

    if df.empty:
        return df.copy()

    if "deal_status" not in df.columns:
        return df.copy()

    status = (
        df["deal_status"]
        .apply(normalize_text)
    )

    return df.loc[
        status.isin(
            OPEN_DEAL_STATUSES
        )
    ].copy()


# ============================================================
# PIPELINE SUMMARY
# ============================================================

def pipeline_summary(
    deals: pd.DataFrame,
    sector: Optional[str] = None,
    period: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate executive sales-pipeline metrics.

    Calculations are deterministic and performed in Python.

    The LLM does not calculate these numbers.
    """

    df = deals.copy()

    # --------------------------------------------------------
    # OPEN DEALS
    # --------------------------------------------------------

    df = _open_deals(df)

    total_open_before_filters = len(df)

    # --------------------------------------------------------
    # SECTOR
    # --------------------------------------------------------

    if sector:

        if "sector" not in df.columns:

            return {
                "metric": "Pipeline Summary",
                "sector": sector,
                "period": period or "All periods",
                "open_deals": 0,
                "gross_pipeline": 0.0,
                "gross_pipeline_display": "₹0",
                "weighted_pipeline": 0.0,
                "weighted_pipeline_display": "₹0",
                "message": (
                    "Sector information is unavailable "
                    "in the Deals board."
                ),
            }

        df = _filter_sector(
            df,
            sector
        )

    after_sector_filter = len(df)

    # --------------------------------------------------------
    # PERIOD
    # --------------------------------------------------------

    period_warning = None

    if period:

        period_lower = normalize_text(
            period
        )

        if (
            "quarter" in period_lower
            or "qtd" in period_lower
        ):

            date_column = (
                "tentative_close_date"
            )

            if date_column in df.columns:

                df = _apply_period(
                    df,
                    date_column,
                    period
                )

                period_warning = (
                    "Quarter filtering uses Tentative "
                    "Close Date because the actual Close "
                    "Date field is highly incomplete."
                )

            else:

                period_warning = (
                    "Tentative Close Date is unavailable, "
                    "so quarter filtering could not be applied."
                )

        elif (
            "month" in period_lower
            or "mtd" in period_lower
        ):

            date_column = (
                "tentative_close_date"
            )

            if date_column in df.columns:

                df = _apply_period(
                    df,
                    date_column,
                    period
                )

                period_warning = (
                    "Month filtering uses Tentative "
                    "Close Date."
                )

        elif (
            "year" in period_lower
            or "ytd" in period_lower
        ):

            date_column = (
                "tentative_close_date"
            )

            if date_column in df.columns:

                df = _apply_period(
                    df,
                    date_column,
                    period
                )

                period_warning = (
                    "Year filtering uses Tentative "
                    "Close Date."
                )

    # --------------------------------------------------------
    # DEAL VALUE
    # --------------------------------------------------------

    if "deal_value" not in df.columns:

        result = {
            "metric": "Pipeline Summary",
            "sector": sector or "All sectors",
            "period": period or "All periods",
            "open_deals": len(df),
            "gross_pipeline": 0.0,
            "gross_pipeline_display": "₹0",
            "weighted_pipeline": 0.0,
            "weighted_pipeline_display": "₹0",
            "message": (
                "Deal value is unavailable "
                "in the Deals board."
            ),
        }

        if period_warning:
            result["period_warning"] = period_warning

        return result

    df["deal_value_numeric"] = numeric_series(
        df,
        "deal_value"
    )

    # --------------------------------------------------------
    # VALUE COVERAGE
    # --------------------------------------------------------

    value_available = (
        df["deal_value_numeric"]
        .notna()
    )

    missing_value_count = int(
        (~value_available).sum()
    )

    valid_values = df.loc[
        value_available
    ]

    gross_pipeline = float(
        valid_values[
            "deal_value_numeric"
        ].sum()
    )

    # --------------------------------------------------------
    # PROBABILITY
    # --------------------------------------------------------

    weighted_pipeline = 0.0

    deals_without_probability = 0

    weighted_deal_count = 0

    if "probability_numeric" in df.columns:

        probability = pd.to_numeric(
            df["probability_numeric"],
            errors="coerce"
        )

        # Probability should normally be between 0 and 1.
        # If the cleaning layer gives percentages such as 70,
        # normalize them to 0.70.
        probability = probability.where(
            probability <= 1,
            probability / 100
        )

        probability_available = (
            probability.notna()
            & probability.between(
                0,
                1
            )
        )

        deals_without_probability = int(
            (~probability_available).sum()
        )

        weighted_mask = (
            probability_available
            & value_available
        )

        weighted_deal_count = int(
            weighted_mask.sum()
        )

        weighted_pipeline = float(
            (
                df.loc[
                    weighted_mask,
                    "deal_value_numeric"
                ]
                * probability.loc[
                    weighted_mask
                ]
            ).sum()
        )

    else:

        deals_without_probability = len(df)

    # --------------------------------------------------------
    # UNKNOWN SECTORS
    # --------------------------------------------------------

    unknown_sector_count = 0

    if "sector" in df.columns:

        normalized_sector = (
            df["sector"]
            .apply(normalize_text)
        )

        unknown_sector_count = int(
            (
                normalized_sector == ""
            ).sum()
        )

    # --------------------------------------------------------
    # PIPELINE CONCENTRATION
    # --------------------------------------------------------

    concentration_pct = 0.0

    if (
        gross_pipeline > 0
        and "sector" in df.columns
    ):

        sector_values = (
            df["deal_value_numeric"]
            .fillna(0)
            .groupby(
                df["sector"]
                .apply(
                    lambda x:
                    display_text(x)
                )
            )
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if not sector_values.empty:

            concentration_pct = percentage(
                sector_values.iloc[0],
                gross_pipeline
            )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result = {

        "metric":
            "Pipeline Summary",

        "sector":
            sector or "All sectors",

        "period":
            period or "All periods",

        "open_deals":
            int(len(df)),

        "gross_pipeline":
            gross_pipeline,

        "gross_pipeline_display":
            money(gross_pipeline),

        "weighted_pipeline":
            weighted_pipeline,

        "weighted_pipeline_display":
            money(weighted_pipeline),

        "deals_without_probability":
            int(deals_without_probability),

        "deals_missing_value":
            int(missing_value_count),

        "unknown_sector_deals":
            int(unknown_sector_count),

        "weighted_deal_count":
            int(weighted_deal_count),

        "top_sector_concentration_pct":
            concentration_pct,

        "data_coverage": {

            "open_deals_before_filters":
                int(total_open_before_filters),

            "after_sector_filter":
                int(after_sector_filter),

            "deals_after_filters":
                int(len(df)),

            "deals_with_value":
                int(value_available.sum()),

            "deals_used_for_weighted_pipeline":
                int(weighted_deal_count),

            "value_coverage_pct":
                percentage(
                    value_available.sum(),
                    len(df)
                ),

            "probability_coverage_pct":
                percentage(
                    len(df)
                    - deals_without_probability,
                    len(df)
                ),
        },
    }

    if period_warning:
        result[
            "period_warning"
        ] = period_warning

    # --------------------------------------------------------
    # ZERO RESULT
    # --------------------------------------------------------

    if (
        sector
        and len(df) == 0
    ):

        result["message"] = (
            f"No open deals are currently "
            f"classified under the exact "
            f"sector '{sector}'."
        )

    return result


# ============================================================
# PIPELINE BY SECTOR
# ============================================================

def pipeline_by_sector(
    deals: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Compare open pipeline by sector.

    Missing sectors are explicitly labelled.
    """

    df = _open_deals(
        deals.copy()
    )

    if df.empty:
        return []

    if "deal_value" not in df.columns:
        return []

    df["deal_value_numeric"] = numeric_series(
        df,
        "deal_value"
    ).fillna(0)

    if "sector" not in df.columns:

        total_pipeline = float(
            df[
                "deal_value_numeric"
            ].sum()
        )

        return [
            {
                "sector":
                    "Unknown / Unclassified",

                "deals":
                    int(len(df)),

                "pipeline":
                    total_pipeline,

                "pipeline_display":
                    money(total_pipeline),
            }
        ]

    df["sector_display"] = (
        df["sector"]
        .apply(display_text)
    )

    grouped = (
        df.groupby(
            "sector_display",
            dropna=False
        )
        .agg(
            deals=(
                "deal_value_numeric",
                "size"
            ),
            pipeline=(
                "deal_value_numeric",
                "sum"
            ),
        )
        .reset_index()
        .sort_values(
            "pipeline",
            ascending=False
        )
    )

    total_pipeline = float(
        grouped["pipeline"].sum()
    )

    rows = []

    for _, row in grouped.iterrows():

        pipeline_value = float(
            row["pipeline"]
        )

        rows.append({

            "sector":
                row["sector_display"],

            "deals":
                int(row["deals"]),

            "pipeline":
                pipeline_value,

            "pipeline_display":
                money(pipeline_value),

            "pipeline_share_pct":
                percentage(
                    pipeline_value,
                    total_pipeline
                ),
        })

    return rows


# ============================================================
# PIPELINE BY STAGE
# ============================================================

def pipeline_by_stage(
    deals: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Analyze open pipeline by sales stage.
    """

    df = _open_deals(
        deals.copy()
    )

    if df.empty:
        return []

    if (
        "deal_stage" not in df.columns
        or "deal_value" not in df.columns
    ):
        return []

    df["deal_value_numeric"] = numeric_series(
        df,
        "deal_value"
    ).fillna(0)

    df["stage_display"] = (
        df["deal_stage"]
        .apply(display_text)
    )

    grouped = (
        df.groupby(
            "stage_display",
            dropna=False
        )
        .agg(
            deals=(
                "deal_value_numeric",
                "size"
            ),
            pipeline=(
                "deal_value_numeric",
                "sum"
            ),
        )
        .reset_index()
        .sort_values(
            "pipeline",
            ascending=False
        )
    )

    total_pipeline = float(
        grouped["pipeline"].sum()
    )

    rows = []

    for _, row in grouped.iterrows():

        pipeline_value = float(
            row["pipeline"]
        )

        rows.append({

            "stage":
                row["stage_display"],

            "deals":
                int(row["deals"]),

            "pipeline":
                pipeline_value,

            "pipeline_display":
                money(pipeline_value),

            "pipeline_share_pct":
                percentage(
                    pipeline_value,
                    total_pipeline
                ),
        })

    return rows


# ============================================================
# WORK ORDER SUMMARY
# ============================================================

def work_order_summary(
    work_orders: pd.DataFrame,
    sector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Summarize operational execution.

    Active statuses include:
        Ongoing
        Not Started
        Partial Completed
        Pause / Struck
        Details Pending from Client
        Executed Until Current Month
    """

    df = work_orders.copy()

    if sector:
        df = _filter_sector(
            df,
            sector
        )

    total = len(df)

    active = 0
    completed = 0

    status_breakdown: Dict[str, int] = {}

    if "execution_status" in df.columns:

        normalized_status = (
            df["execution_status"]
            .apply(normalize_text)
        )

        active = int(
            normalized_status
            .isin(
                ACTIVE_WORK_ORDER_STATUSES
            )
            .sum()
        )

        completed = int(
            (
                normalized_status
                == "completed"
            ).sum()
        )

        status_breakdown = {
            display_text(
                status,
                "Unknown / Unclassified"
            ):
                int(count)

            for status, count
            in (
                df["execution_status"]
                .fillna("")
                .astype(str)
                .str.strip()
                .replace(
                    "",
                    "Unknown / Unclassified"
                )
                .value_counts()
                .items()
            )
        }

    return {

        "metric":
            "Work Order Summary",

        "sector":
            sector or "All sectors",

        "total_work_orders":
            int(total),

        "active_work_orders":
            int(active),

        "completed_work_orders":
            int(completed),

        "active_share_pct":
            percentage(
                active,
                total
            ),

        "completion_share_pct":
            percentage(
                completed,
                total
            ),

        "status_breakdown":
            status_breakdown,
    }


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

def financial_summary(
    work_orders: pd.DataFrame,
    sector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate operational financial metrics.

    Uses inclusive-of-GST values where available because
    these represent the cash/billing figures shown in the
    operational board.
    """

    df = work_orders.copy()

    if sector:
        df = _filter_sector(
            df,
            sector
        )

    def total(
        column: str
    ) -> float:

        if column not in df.columns:
            return 0.0

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        return float(
            values.fillna(0).sum()
        )

    billed = total(
        "billed_value_incl"
    )

    collected = total(
        "collected_amount"
    )

    to_be_billed = total(
        "amount_to_be_billed_incl"
    )

    receivable = total(
        "amount_receivable"
    )

    # --------------------------------------------------------
    # COLLECTION RATE
    # --------------------------------------------------------

    collection_rate = percentage(
        collected,
        billed
    )

    # --------------------------------------------------------
    # RECEIVABLE AS % OF BILLED
    # --------------------------------------------------------

    receivable_ratio = percentage(
        receivable,
        billed
    )

    # --------------------------------------------------------
    # BILLING BACKLOG AS % OF BILLED + TO-BE-BILLED
    # --------------------------------------------------------

    billing_base = (
        billed
        + to_be_billed
    )

    billing_backlog_ratio = percentage(
        to_be_billed,
        billing_base
    )

    return {

        "metric":
            "Operational Financial Summary",

        "sector":
            sector or "All sectors",

        "billed_value":
            billed,

        "billed_value_display":
            money(billed),

        "collected_amount":
            collected,

        "collected_amount_display":
            money(collected),

        "amount_to_be_billed":
            to_be_billed,

        "amount_to_be_billed_display":
            money(to_be_billed),

        "amount_receivable":
            receivable,

        "amount_receivable_display":
            money(receivable),

        "collection_rate_pct":
            collection_rate,

        "receivable_as_pct_of_billed":
            receivable_ratio,

        "billing_backlog_ratio_pct":
            billing_backlog_ratio,
    }


# ============================================================
# CROSS-BOARD SECTOR ANALYSIS
# ============================================================

def sector_performance(
    deals: pd.DataFrame,
    work_orders: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Combine sales and operations by sector.

    Each sector receives:

        Pipeline
        Number of deals
        Active work orders
        Total work orders
        Billing backlog

    This creates a leadership-oriented cross-board view.
    """

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    pipeline_rows = pipeline_by_sector(
        deals
    )

    pipeline_df = pd.DataFrame(
        pipeline_rows
    )

    # --------------------------------------------------------
    # WORK ORDERS
    # --------------------------------------------------------

    wo = work_orders.copy()

    if wo.empty:
        wo_summary = pd.DataFrame(
            columns=[
                "sector",
                "active_work_orders",
                "total_work_orders",
                "billing_backlog",
            ]
        )

    elif "sector" not in wo.columns:

        wo_summary = pd.DataFrame(
            [
                {
                    "sector":
                        "Unknown / Unclassified",

                    "active_work_orders":
                        0,

                    "total_work_orders":
                        len(wo),

                    "billing_backlog":
                        0.0,
                }
            ]
        )

    else:

        # ----------------------------------------------------
        # ACTIVE STATUS
        # ----------------------------------------------------

        if (
            "execution_status"
            in wo.columns
        ):

            status = (
                wo["execution_status"]
                .apply(normalize_text)
            )

            wo["_active"] = (
                status.isin(
                    ACTIVE_WORK_ORDER_STATUSES
                )
            )

        else:

            wo["_active"] = False

        # ----------------------------------------------------
        # BILLING BACKLOG
        # ----------------------------------------------------

        if (
            "amount_to_be_billed_incl"
            in wo.columns
        ):

            wo[
                "_billing_backlog"
            ] = numeric_series(
                wo,
                "amount_to_be_billed_incl"
            ).fillna(0)

        else:

            wo[
                "_billing_backlog"
            ] = 0.0

        # ----------------------------------------------------
        # SECTOR
        # ----------------------------------------------------

        wo["sector_display"] = (
            wo["sector"]
            .apply(display_text)
        )

        # ----------------------------------------------------
        # GROUP
        # ----------------------------------------------------

        wo_summary = (
            wo.groupby(
                "sector_display",
                dropna=False
            )
            .agg(

                active_work_orders=(
                    "_active",
                    "sum"
                ),

                total_work_orders=(
                    "_active",
                    "size"
                ),

                billing_backlog=(
                    "_billing_backlog",
                    "sum"
                ),
            )
            .reset_index()
            .rename(
                columns={
                    "sector_display":
                        "sector"
                }
            )
        )

    # --------------------------------------------------------
    # IF NO PIPELINE
    # --------------------------------------------------------

    if pipeline_df.empty:

        records = []

        for _, row in wo_summary.iterrows():

            backlog = float(
                row.get(
                    "billing_backlog",
                    0
                )
            )

            records.append({

                "sector":
                    row["sector"],

                "deals":
                    0,

                "pipeline":
                    0.0,

                "pipeline_display":
                    "₹0",

                "pipeline_share_pct":
                    0.0,

                "active_work_orders":
                    int(
                        row[
                            "active_work_orders"
                        ]
                    ),

                "total_work_orders":
                    int(
                        row[
                            "total_work_orders"
                        ]
                    ),

                "billing_backlog":
                    backlog,

                "billing_backlog_display":
                    money(backlog),
            })

        return records

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    merged = pipeline_df.merge(
        wo_summary,
        on="sector",
        how="outer"
    )

    # --------------------------------------------------------
    # FILL METRIC VALUES
    # --------------------------------------------------------

    metric_columns = [
        "deals",
        "pipeline",
        "pipeline_share_pct",
        "active_work_orders",
        "total_work_orders",
        "billing_backlog",
    ]

    for column in metric_columns:

        if column not in merged.columns:
            merged[column] = 0

        merged[column] = (
            pd.to_numeric(
                merged[column],
                errors="coerce"
            )
            .fillna(0)
        )

    # --------------------------------------------------------
    # BUILD RECORDS
    # --------------------------------------------------------

    records = []

    for _, row in merged.iterrows():

        pipeline_value = float(
            row["pipeline"]
        )

        backlog = float(
            row["billing_backlog"]
        )

        records.append({

            "sector":
                display_text(
                    row["sector"]
                ),

            "deals":
                int(row["deals"]),

            "pipeline":
                pipeline_value,

            "pipeline_display":
                money(
                    pipeline_value
                ),

            "pipeline_share_pct":
                float(
                    row[
                        "pipeline_share_pct"
                    ]
                ),

            "active_work_orders":
                int(
                    row[
                        "active_work_orders"
                    ]
                ),

            "total_work_orders":
                int(
                    row[
                        "total_work_orders"
                    ]
                ),

            "billing_backlog":
                backlog,

            "billing_backlog_display":
                money(backlog),
        })

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    records.sort(
        key=lambda x: (
            x["pipeline"],
            x["billing_backlog"],
        ),
        reverse=True
    )

    return records


# ============================================================
# LEADERSHIP UPDATE
# ============================================================

def leadership_update(
    deals: pd.DataFrame,
    work_orders: pd.DataFrame,
    quality: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Prepare a complete structured leadership briefing.

    The function provides facts and signals.
    The LLM converts them into executive prose.
    """

    pipeline = pipeline_summary(
        deals
    )

    sectors = pipeline_by_sector(
        deals
    )

    stages = pipeline_by_stage(
        deals
    )

    operations = work_order_summary(
        work_orders
    )

    financials = financial_summary(
        work_orders
    )

    cross_board = sector_performance(
        deals,
        work_orders
    )

    # --------------------------------------------------------
    # TOP BILLING-BACKLOG SECTORS
    # --------------------------------------------------------

    top_backlog_sectors = sorted(
        cross_board,
        key=lambda x:
            x.get(
                "billing_backlog",
                0
            ),
        reverse=True
    )[:5]

    # --------------------------------------------------------
    # TOP ACTIVE-EXECUTION SECTORS
    # --------------------------------------------------------

    top_execution_sectors = sorted(
        cross_board,
        key=lambda x:
            x.get(
                "active_work_orders",
                0
            ),
        reverse=True
    )[:5]

    # --------------------------------------------------------
    # PIPELINE CONCENTRATION
    # --------------------------------------------------------

    top_pipeline_sector = None

    if sectors:

        top_pipeline_sector = (
            sectors[0]
        )

    # --------------------------------------------------------
    # LEADERSHIP SIGNALS
    # --------------------------------------------------------

    leadership_signals = []

    if top_pipeline_sector:

        concentration = (
            top_pipeline_sector
            .get(
                "pipeline_share_pct",
                0
            )
        )

        if concentration >= 50:

            leadership_signals.append(
                {
                    "type":
                        "pipeline_concentration",

                    "severity":
                        "high",

                    "sector":
                        top_pipeline_sector[
                            "sector"
                        ],

                    "share_pct":
                        concentration,

                    "message":
                        (
                            "A single sector accounts "
                            "for more than half of the "
                            "current gross pipeline."
                        ),
                }
            )

        elif concentration >= 30:

            leadership_signals.append(
                {
                    "type":
                        "pipeline_concentration",

                    "severity":
                        "medium",

                    "sector":
                        top_pipeline_sector[
                            "sector"
                        ],

                    "share_pct":
                        concentration,

                    "message":
                        (
                            "Pipeline is materially "
                            "concentrated in the leading "
                            "sector."
                        ),
                }
            )

    if (
        financials[
            "amount_receivable"
        ] > 0
    ):

        leadership_signals.append(
            {
                "type":
                    "receivables",

                "severity":
                    "medium",

                "amount":
                    financials[
                        "amount_receivable"
                    ],

                "amount_display":
                    financials[
                        "amount_receivable_display"
                    ],

                "message":
                    (
                        "Outstanding receivables "
                        "require collection attention."
                    ),
            }
        )

    if (
        financials[
            "amount_to_be_billed"
        ] > 0
    ):

        leadership_signals.append(
            {
                "type":
                    "billing_backlog",

                "severity":
                    "medium",

                "amount":
                    financials[
                        "amount_to_be_billed"
                    ],

                "amount_display":
                    financials[
                        "amount_to_be_billed_display"
                    ],

                "message":
                    (
                        "There is a material amount "
                        "still to be billed."
                    ),
            }
        )

    if (
        pipeline[
            "deals_without_probability"
        ] > 0
    ):

        leadership_signals.append(
            {
                "type":
                    "forecast_quality",

                "severity":
                    "medium",

                "deals":
                    pipeline[
                        "deals_without_probability"
                    ],

                "message":
                    (
                        "Some open deals lack usable "
                        "closure probability, limiting "
                        "weighted-pipeline confidence."
                    ),
            }
        )

    if (
        pipeline[
            "deals_missing_value"
        ] > 0
    ):

        leadership_signals.append(
            {
                "type":
                    "commercial_data_quality",

                "severity":
                    "medium",

                "deals":
                    pipeline[
                        "deals_missing_value"
                    ],

                "message":
                    (
                        "Some open deals have missing "
                        "deal values."
                    ),
            }
        )

    return {

        "pipeline":
            pipeline,

        "top_sectors":
            sectors[:5],

        "pipeline_stages":
            stages[:8],

        "operations":
            operations,

        "financials":
            financials,

        "cross_board":
            cross_board,

        "top_billing_backlog_sectors":
            top_backlog_sectors,

        "top_execution_sectors":
            top_execution_sectors,

        "leadership_signals":
            leadership_signals,

        "quality":
            quality,
    }


# ============================================================
# ANALYTICS TOOL ROUTER
# ============================================================

def execute_tool(
    tool_name: str,
    deals: pd.DataFrame,
    work_orders: pd.DataFrame,
    quality: Dict[str, Any],
    sector: Optional[str] = None,
    period: Optional[str] = None
):
    """
    Route an agent request to the correct deterministic
    analytics operation.
    """

    if tool_name == "pipeline_summary":

        return pipeline_summary(
            deals,
            sector,
            period
        )

    if tool_name == "pipeline_by_sector":

        return pipeline_by_sector(
            deals
        )

    if tool_name == "pipeline_by_stage":

        return pipeline_by_stage(
            deals
        )

    if tool_name == "work_order_summary":

        return work_order_summary(
            work_orders,
            sector
        )

    if tool_name == "financial_summary":

        return financial_summary(
            work_orders,
            sector
        )

    if tool_name == "cross_board":

        return sector_performance(
            deals,
            work_orders
        )

    if tool_name == "leadership_update":

        return leadership_update(
            deals,
            work_orders,
            quality
        )

    if tool_name == "data_quality":

        return quality

    raise ValueError(
        f"Unknown analytics tool: {tool_name}"
    )
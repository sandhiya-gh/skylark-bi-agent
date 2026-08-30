import re
from typing import Dict, List

import numpy as np
import pandas as pd


# ============================================================
# GENERAL NORMALIZATION
# ============================================================

def normalize_key(value) -> str:
    if value is None:
        return ""

    value = str(value).strip().lower()

    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def normalize_text(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if not value:
        return np.nan

    return value


# ============================================================
# SECTOR
# ============================================================

def normalize_sector(value):

    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    aliases = {
        "energy": "Energy",
        "energy sector": "Energy",

        "renewable": "Renewables",
        "renewables": "Renewables",
        "renewable energy": "Renewables",

        "railway": "Railways",
        "railways": "Railways",

        "power line": "Powerline",
        "powerline": "Powerline",

        "construction": "Construction",
        "mining": "Mining",
        "manufacturing": "Manufacturing",

        "security and surveillance":
            "Security and Surveillance",
    }

    return aliases.get(
        value,
        value.title()
    )


# ============================================================
# STATUS
# ============================================================

def normalize_status(value):

    if pd.isna(value):
        return np.nan

    return str(value).strip().title()


# ============================================================
# MONEY
# ============================================================

def normalize_money(value):

    if pd.isna(value):
        return np.nan

    if isinstance(
        value,
        (
            int,
            float,
            np.integer,
            np.floating
        )
    ):
        return float(value)

    text = str(value).strip()

    if not text:
        return np.nan

    # Remove currency symbols, commas, spaces etc.
    cleaned = re.sub(
        r"[^0-9.\-]",
        "",
        text
    )

    if not cleaned:
        return np.nan

    try:
        return float(cleaned)

    except ValueError:
        return np.nan


# ============================================================
# PROBABILITY
# ============================================================

def normalize_probability(value):

    if pd.isna(value):
        return np.nan

    text = str(value).strip().lower()

    mapping = {
        "very high": 0.90,
        "high": 0.80,
        "medium": 0.50,
        "low": 0.20,
        "very low": 0.10,
    }

    if text in mapping:
        return mapping[text]

    try:

        numeric = float(
            text.replace("%", "")
        )

        if numeric > 1:
            numeric /= 100

        if 0 <= numeric <= 1:
            return numeric

    except ValueError:
        pass

    return np.nan


# ============================================================
# DATES
# ============================================================

def normalize_dates(series):

    return pd.to_datetime(
        series,
        errors="coerce"
    )


# ============================================================
# COLUMN FINDER
# ============================================================

def _find_column(
    df,
    aliases: List[str]
):

    normalized_columns = {
        normalize_key(column): column
        for column in df.columns
    }

    normalized_aliases = [
        normalize_key(alias)
        for alias in aliases
    ]

    # Exact match
    for alias in normalized_aliases:

        if alias in normalized_columns:
            return normalized_columns[alias]

    # Partial match
    for alias in normalized_aliases:

        for (
            normalized_column,
            original_column
        ) in normalized_columns.items():

            if (
                alias
                and alias in normalized_column
            ):
                return original_column

    return None


def rename_to_canonical(
    df,
    mapping: Dict[str, List[str]]
):

    df = df.copy()

    rename_map = {}

    for (
        canonical_name,
        aliases
    ) in mapping.items():

        column = _find_column(
            df,
            aliases
        )

        if (
            column
            and column != canonical_name
        ):
            rename_map[column] = (
                canonical_name
            )

    return df.rename(
        columns=rename_map
    )


# ============================================================
# DEAL COLUMN MAPPING
# ============================================================

DEAL_MAPPING = {

    "deal_name": [
        "Deal Name",
        "item name",
        "name"
    ],

    "owner_code": [
        "Owner code"
    ],

    "client_code": [
        "Client Code"
    ],

    "deal_status": [
        "Deal Status"
    ],

    "close_date": [
        "Close Date (A)",
        "Close Date A",
        "Close Date"
    ],

    "closure_probability": [
        "Closure Probability"
    ],

    "deal_value": [
        "Masked Deal value",
        "Masked Deal Value",
        "Deal value"
    ],

    "tentative_close_date": [
        "Tentative Close Date"
    ],

    "deal_stage": [
        "Deal Stage"
    ],

    "product_deal": [
        "Product deal"
    ],

    "sector": [
        "Sector/service",
        "Sector service",
        "Sector"
    ],

    "created_date": [
        "Created Date"
    ],
}


# ============================================================
# WORK ORDER COLUMN MAPPING
# ============================================================

WORK_ORDER_MAPPING = {

    "deal_name": [
        "Deal name masked",
        "Deal Name",
        "item name",
        "name"
    ],

    "customer_code": [
        "Customer Name Code"
    ],

    "serial_no": [
        "Serial #",
        "Serial"
    ],

    "nature_of_work": [
        "Nature of Work"
    ],

    "last_executed_month": [
        "Last executed month of recurring project"
    ],

    "execution_status": [
        "Execution Status"
    ],

    "data_delivery_date": [
        "Data Delivery Date"
    ],

    "po_date": [
        "Date of PO/LOI",
        "Date of PO LOI"
    ],

    "document_type": [
        "Document Type"
    ],

    "probable_start_date": [
        "Probable Start Date"
    ],

    "probable_end_date": [
        "Probable End Date"
    ],

    "owner_code": [
        "BD/KAM Personnel code",
        "BD KAM Personnel code"
    ],

    "sector": [
        "Sector"
    ],

    "type_of_work": [
        "Type of Work"
    ],

    "software_platform": [
        "Is any Skylark software platform part of the client deliverables in this deal?"
    ],

    "last_invoice_date": [
        "Last invoice date"
    ],

    "invoice_no": [
        "latest invoice no."
    ],

    "contract_value_excl": [
        "Amount in Rupees (Excl of GST) (Masked)",
        "Amount in Rupees (Excl. of GST) (Masked)"
    ],

    "contract_value_incl": [
        "Amount in Rupees (Incl of GST) (Masked)",
        "Amount in Rupees (Incl. of GST) (Masked)"
    ],

    "billed_value_excl": [
        "Billed Value in Rupees (Excl. of GST.) (Masked)",
        "Billed Value in Rupees (Excl of GST.) (Masked)"
    ],

    "billed_value_incl": [
        "Billed Value in Rupees (Incl. of GST.) (Masked)",
        "Billed Value in Rupees (Incl of GST.) (Masked)"
    ],

    "collected_amount": [
        "Collected Amount in Rupees (Incl. of GST.) (Masked)",
        "Collected Amount in Rupees (Incl of GST.) (Masked)"
    ],

    "amount_to_be_billed_excl": [
        "Amount to be billed in Rs. (Exl. of GST) (Masked)",
        "Amount to be billed in Rs Exl of GST Masked"
    ],

    "amount_to_be_billed_incl": [
        "Amount to be billed in Rs. (Incl. of GST) (Masked)",
        "Amount to be billed in Rs Incl of GST Masked"
    ],

    "amount_receivable": [
        "Amount Receivable (Masked)"
    ],

    "ar_priority": [
        "AR Priority account"
    ],

    "quantity_ops": [
        "Quantity by Ops"
    ],

    "quantity_po": [
        "Quantities as per PO"
    ],

    "quantity_billed": [
        "Quantity billed (till date)"
    ],

    "balance_quantity": [
        "Balance in quantity"
    ],

    "invoice_status": [
        "Invoice Status"
    ],

    "expected_billing_month": [
        "Expected Billing Month"
    ],

    "actual_billing_month": [
        "Actual Billing Month"
    ],

    "actual_collection_month": [
        "Actual Collection Month"
    ],

    "wo_status_billed": [
        "WO Status (billed)"
    ],

    "collection_status": [
        "Collection status"
    ],

    "collection_date": [
        "Collection Date"
    ],

    "billing_status": [
        "Billing Status"
    ],
}


# ============================================================
# CLEAN DEALS
# ============================================================

def clean_deals(df):

    df = rename_to_canonical(
        df,
        DEAL_MAPPING
    )

    if (
        "deal_name" not in df.columns
        and "__item_name" in df.columns
    ):
        df["deal_name"] = df[
            "__item_name"
        ]

    # Remove accidental header rows
    if "deal_name" in df.columns:

        df = df[
            df["deal_name"]
            .astype(str)
            .str.strip()
            .str.lower()
            != "deal name"
        ]

    if "sector" in df.columns:

        df["sector"] = (
            df["sector"]
            .apply(normalize_sector)
        )

    if "deal_status" in df.columns:

        df["deal_status"] = (
            df["deal_status"]
            .apply(normalize_status)
        )

    if "deal_value" in df.columns:

        df["deal_value"] = (
            df["deal_value"]
            .apply(normalize_money)
        )

    if "closure_probability" in df.columns:

        df["probability_numeric"] = (
            df["closure_probability"]
            .apply(normalize_probability)
        )

    for column in [
        "close_date",
        "tentative_close_date",
        "created_date"
    ]:

        if column in df.columns:

            df[column] = normalize_dates(
                df[column]
            )

    return df.reset_index(
        drop=True
    )


# ============================================================
# CLEAN WORK ORDERS
# ============================================================

def clean_work_orders(df):

    df = rename_to_canonical(
        df,
        WORK_ORDER_MAPPING
    )

    if (
        "deal_name" not in df.columns
        and "__item_name" in df.columns
    ):
        df["deal_name"] = df[
            "__item_name"
        ]

    if "sector" in df.columns:

        df["sector"] = (
            df["sector"]
            .apply(normalize_sector)
        )

    if "execution_status" in df.columns:

        df["execution_status"] = (
            df["execution_status"]
            .apply(normalize_status)
        )

    money_columns = [

        "contract_value_excl",
        "contract_value_incl",

        "billed_value_excl",
        "billed_value_incl",

        "collected_amount",

        "amount_to_be_billed_excl",
        "amount_to_be_billed_incl",

        "amount_receivable",
    ]

    for column in money_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .apply(normalize_money)
            )

    date_columns = [

        "data_delivery_date",
        "po_date",

        "probable_start_date",
        "probable_end_date",

        "last_invoice_date",
        "collection_date",
    ]

    for column in date_columns:

        if column in df.columns:

            df[column] = normalize_dates(
                df[column]
            )

    return df.reset_index(
        drop=True
    )


# ============================================================
# DATA QUALITY
# ============================================================

def build_quality_report(
    df,
    dataset_name
):

    if df.empty:

        return {
            "dataset": dataset_name,
            "rows": 0,
            "columns": 0,
            "issues": [
                "No records returned from Monday.com."
            ]
        }

    issues = []

    missing = df.isna().sum()

    for column, count in missing.items():

        if count > 0:

            percentage = round(
                (count / len(df)) * 100,
                1
            )

            if percentage >= 10:

                issues.append(
                    f"{column}: "
                    f"{count} missing "
                    f"({percentage}%)"
                )

    duplicate_count = (
        df.duplicated().sum()
    )

    if duplicate_count:

        issues.append(
            f"{duplicate_count} duplicate "
            f"rows detected."
        )

    return {
        "dataset": dataset_name,
        "rows": len(df),
        "columns": len(df.columns),
        "issues": issues,
    }


def quality_summary(
    deals,
    work_orders
):

    return {

        "deals": build_quality_report(
            deals,
            "Deals"
        ),

        "work_orders": build_quality_report(
            work_orders,
            "Work Orders"
        ),
    }
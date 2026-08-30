import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)
# ============================================================
# MONDAY.COM CONFIGURATION
# ============================================================

MONDAY_API_URL = get_secret(
    "MONDAY_API_URL",
    "https://api.monday.com/v2"
).strip()

MONDAY_API_TOKEN = get_secret(
    "MONDAY_API_TOKEN",
    ""
).strip()

DEALS_BOARD_ID = get_secret(
    "DEALS_BOARD_ID",
    ""
).strip()

WORK_ORDERS_BOARD_ID = get_secret(
    "WORK_ORDERS_BOARD_ID",
    ""
).strip()


# ============================================================
# OPENAI CONFIGURATION
# ============================================================

# Kept for compatibility with the existing project.
# The current application uses Gemini.

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
).strip()

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5"
).strip()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
).strip()


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "Skylark BI Copilot"

APP_VERSION = "1.0.0"


# ============================================================
# MONDAY CONFIGURATION VALIDATION
# ============================================================

def validate_monday_config():
    """
    Validate configuration required to connect to Monday.com.
    """

    missing = []

    if not MONDAY_API_URL:
        missing.append("MONDAY_API_URL")

    if not MONDAY_API_TOKEN:
        missing.append("MONDAY_API_TOKEN")

    if not DEALS_BOARD_ID:
        missing.append("DEALS_BOARD_ID")

    if not WORK_ORDERS_BOARD_ID:
        missing.append("WORK_ORDERS_BOARD_ID")

    if missing:
        raise RuntimeError(
            "Missing Monday.com configuration: "
            + ", ".join(missing)
        )


# ============================================================
# GEMINI CONFIGURATION VALIDATION
# ============================================================

def validate_gemini_config():
    """
    Validate Gemini configuration.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    if not GEMINI_MODEL:
        raise RuntimeError(
            "GEMINI_MODEL is not configured."
        )


# ============================================================
# COMPLETE CONFIGURATION VALIDATION
# ============================================================

def validate_config():
    """
    Validate the complete application configuration.
    """

    validate_monday_config()
    validate_gemini_config()


# ============================================================
# SAFE CONFIGURATION STATUS
# ============================================================

def config_status():
    """
    Return configuration status without exposing secrets.
    """

    return {
        "monday_api_url": MONDAY_API_URL,
        "monday_token_set": bool(MONDAY_API_TOKEN),
        "deals_board_id": DEALS_BOARD_ID,
        "work_orders_board_id": WORK_ORDERS_BOARD_ID,
        "gemini_key_set": bool(GEMINI_API_KEY),
        "gemini_model": GEMINI_MODEL,
    }
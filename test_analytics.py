from config import (
    DEALS_BOARD_ID,
    WORK_ORDERS_BOARD_ID,
)

from monday_client import MondayClient

from data_quality import (
    clean_deals,
    clean_work_orders,
    quality_summary,
)

from analytics import (
    pipeline_summary,
    pipeline_by_sector,
    pipeline_by_stage,
    work_order_summary,
    financial_summary,
    sector_performance,
)


print("=" * 70)
print("SKYLARK BI COPILOT - BUSINESS INTELLIGENCE TEST")
print("=" * 70)


# ---------------------------------------------------------
# LOAD LIVE DATA
# ---------------------------------------------------------

client = MondayClient()

print("\nLoading live Monday.com data...")

deals_raw, _ = client.get_board_dataframe(
    DEALS_BOARD_ID
)

work_orders_raw, _ = client.get_board_dataframe(
    WORK_ORDERS_BOARD_ID
)

deals = clean_deals(deals_raw)

work_orders = clean_work_orders(
    work_orders_raw
)

quality = quality_summary(
    deals,
    work_orders
)

print(
    f"✓ Deals: {len(deals)}"
)

print(
    f"✓ Work Orders: {len(work_orders)}"
)


# ---------------------------------------------------------
# 1. PIPELINE
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("1. PIPELINE SUMMARY")
print("-" * 70)

pipeline = pipeline_summary(
    deals
)

for key, value in pipeline.items():

    if not key.endswith("_display"):

        print(
            f"{key}: {value}"
        )


# ---------------------------------------------------------
# 2. ENERGY
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("2. ENERGY PIPELINE")
print("-" * 70)

energy = pipeline_summary(
    deals,
    sector="Energy"
)

for key, value in energy.items():

    if not key.endswith("_display"):

        print(
            f"{key}: {value}"
        )


# ---------------------------------------------------------
# 3. SECTOR ANALYSIS
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("3. PIPELINE BY SECTOR")
print("-" * 70)

sector_rows = pipeline_by_sector(
    deals
)

for row in sector_rows:

    print(
        f"{row['sector']}: "
        f"{row['pipeline_display']} "
        f"({row['deals']} deals)"
    )


# ---------------------------------------------------------
# 4. STAGE ANALYSIS
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("4. PIPELINE BY STAGE")
print("-" * 70)

stage_rows = pipeline_by_stage(
    deals
)

for row in stage_rows:

    print(
        f"{row['stage']}: "
        f"{row['pipeline_display']} "
        f"({row['deals']} deals)"
    )


# ---------------------------------------------------------
# 5. OPERATIONS
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("5. WORK ORDER SUMMARY")
print("-" * 70)

operations = work_order_summary(
    work_orders
)

for key, value in operations.items():

    print(
        f"{key}: {value}"
    )


# ---------------------------------------------------------
# 6. FINANCIALS
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("6. FINANCIAL SUMMARY")
print("-" * 70)

financials = financial_summary(
    work_orders
)

for key, value in financials.items():

    if not key.endswith("_display"):

        print(
            f"{key}: {value}"
        )


# ---------------------------------------------------------
# 7. CROSS BOARD
# ---------------------------------------------------------

print("\n" + "-" * 70)
print("7. CROSS-BOARD SECTOR ANALYSIS")
print("-" * 70)

cross = sector_performance(
    deals,
    work_orders
)

for row in cross:

    print(
        f"{row.get('sector')}: "
        f"pipeline={row.get('pipeline_display')}, "
        f"active WOs={row.get('active_work_orders')}, "
        f"billing backlog="
        f"{row.get('billing_backlog_display')}"
    )


# ---------------------------------------------------------
# COMPLETE
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("🎉 BUSINESS INTELLIGENCE TEST COMPLETE")
print("=" * 70)
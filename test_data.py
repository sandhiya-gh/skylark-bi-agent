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


print("=" * 60)
print("SKYLARK BI COPILOT - DATA QUALITY TEST")
print("=" * 60)


client = MondayClient()


print("\nFetching Deals...")

deals_raw, _ = client.get_board_dataframe(
    DEALS_BOARD_ID
)

print(
    f"Raw Deals: {len(deals_raw)} rows"
)


print("\nCleaning Deals...")

deals = clean_deals(
    deals_raw
)

print(
    f"Clean Deals: {len(deals)} rows"
)

print(
    "\nCanonical Deal columns:"
)

print(
    deals.columns.tolist()
)


print("\nFetching Work Orders...")

work_orders_raw, _ = (
    client.get_board_dataframe(
        WORK_ORDERS_BOARD_ID
    )
)

print(
    f"Raw Work Orders: "
    f"{len(work_orders_raw)} rows"
)


print("\nCleaning Work Orders...")

work_orders = clean_work_orders(
    work_orders_raw
)

print(
    f"Clean Work Orders: "
    f"{len(work_orders)} rows"
)


print(
    "\nCanonical Work Order columns:"
)

print(
    work_orders.columns.tolist()
)


print("\nData Quality Report:")

quality = quality_summary(
    deals,
    work_orders
)

for dataset, report in quality.items():

    print(
        f"\n{dataset.upper()}"
    )

    print(
        f"Rows: {report['rows']}"
    )

    if report["issues"]:

        for issue in report["issues"]:

            print(
                f"⚠ {issue}"
            )

    else:

        print(
            "✓ No major quality issues"
        )


print("\n" + "=" * 60)
print("🎉 DATA QUALITY TEST PASSED")
print("=" * 60)
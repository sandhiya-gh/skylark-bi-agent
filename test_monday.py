from config import (
    DEALS_BOARD_ID,
    WORK_ORDERS_BOARD_ID,
)

from monday_client import MondayClient


print("=" * 60)
print("SKYLARK BI COPILOT - MONDAY CONNECTION TEST")
print("=" * 60)


client = MondayClient()


# ---------------------------------------------------------
# 1. Authentication
# ---------------------------------------------------------

print("\n[1/5] Testing Monday authentication...")

me = client.test_connection()

user = me.get("me", {})

print("✓ Connected to Monday.com")
print(f"✓ User: {user.get('name', 'Unknown')}")


# ---------------------------------------------------------
# 2. Deals board
# ---------------------------------------------------------

print("\n[2/5] Checking Deals board...")

deals_board = client.get_board_info(
    DEALS_BOARD_ID
)

print(
    f"✓ Board: {deals_board.get('name')}"
)

print(
    f"✓ Columns: {len(deals_board.get('columns', []))}"
)


# ---------------------------------------------------------
# 3. Work Orders board
# ---------------------------------------------------------

print("\n[3/5] Checking Work Orders board...")

work_orders_board = client.get_board_info(
    WORK_ORDERS_BOARD_ID
)

print(
    f"✓ Board: {work_orders_board.get('name')}"
)

print(
    f"✓ Columns: "
    f"{len(work_orders_board.get('columns', []))}"
)


# ---------------------------------------------------------
# 4. Retrieve Deals
# ---------------------------------------------------------

print("\n[4/5] Retrieving Deals data...")

deals_df, _ = client.get_board_dataframe(
    DEALS_BOARD_ID
)

print(
    f"✓ Deals retrieved: {len(deals_df)} rows"
)

print(
    f"✓ Deals columns: {len(deals_df.columns)}"
)


# ---------------------------------------------------------
# 5. Retrieve Work Orders
# ---------------------------------------------------------

print("\n[5/5] Retrieving Work Orders data...")

work_orders_df, _ = client.get_board_dataframe(
    WORK_ORDERS_BOARD_ID
)

print(
    f"✓ Work Orders retrieved: "
    f"{len(work_orders_df)} rows"
)

print(
    f"✓ Work Orders columns: "
    f"{len(work_orders_df.columns)}"
)


print("\n" + "=" * 60)
print("🎉 MONDAY.COM CONNECTION TEST PASSED")
print("=" * 60)

print("\nDeals preview:")
print(deals_df.head(3).to_string())

print("\nWork Orders preview:")
print(work_orders_df.head(3).to_string())
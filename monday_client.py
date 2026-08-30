import requests

from typing import Dict, List, Any

from config import (
    MONDAY_API_URL,
    MONDAY_API_TOKEN,
)


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class MondayAPIError(Exception):
    """
    Raised when the Monday.com API returns an error
    or when a connection problem occurs.
    """

    pass


# ============================================================
# MONDAY CLIENT
# ============================================================

class MondayClient:

    def __init__(self, token: str | None = None):

        self.token = (
            token.strip()
            if token
            else MONDAY_API_TOKEN
        )

        if not self.token:
            raise ValueError(
                "MONDAY_API_TOKEN is missing."
            )

        self.api_url = MONDAY_API_URL

        if not self.api_url:
            raise ValueError(
                "MONDAY_API_URL is missing."
            )

        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "API-Version": "2026-07",
        }


    # ========================================================
    # INTERNAL API REQUEST
    # ========================================================

    def _request(
        self,
        query: str,
        variables: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL request against Monday.com.

        Args:
            query:
                GraphQL query string.

            variables:
                Optional GraphQL variables.

        Returns:
            GraphQL data dictionary.

        Raises:
            MondayAPIError:
                When the API request fails.
        """

        payload = {
            "query": query,
            "variables": variables or {},
        }

        try:

            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30,
            )

        except requests.RequestException as exc:

            raise MondayAPIError(
                f"Unable to connect to Monday.com: {exc}"
            ) from exc


        # ----------------------------------------------------
        # HTTP STATUS CHECK
        # ----------------------------------------------------

        if response.status_code != 200:

            raise MondayAPIError(
                "Monday.com returned HTTP "
                f"{response.status_code}: "
                f"{response.text[:500]}"
            )


        # ----------------------------------------------------
        # JSON PARSING
        # ----------------------------------------------------

        try:

            result = response.json()

        except ValueError as exc:

            raise MondayAPIError(
                "Monday.com returned an invalid JSON response."
            ) from exc


        # ----------------------------------------------------
        # GRAPHQL ERROR CHECK
        # ----------------------------------------------------

        if result.get("errors"):

            messages = []

            for error in result["errors"]:

                message = error.get(
                    "message",
                    "Unknown GraphQL error",
                )

                messages.append(message)

            raise MondayAPIError(
                "Monday.com API error: "
                + " | ".join(messages)
            )


        # ----------------------------------------------------
        # RETURN DATA
        # ----------------------------------------------------

        return result.get("data", {})


    # ========================================================
    # TEST CONNECTION
    # ========================================================

    def test_connection(self) -> Dict[str, Any]:
        """
        Test authentication by retrieving
        the current Monday.com user.
        """

        query = """
        query {
            me {
                id
                name
                email
            }
        }
        """

        return self._request(query)


    # ========================================================
    # GET BOARD INFORMATION
    # ========================================================

    def get_board_info(
        self,
        board_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve board metadata and column definitions.
        """

        if not board_id:
            raise MondayAPIError(
                "Board ID is missing."
            )

        query = """
        query ($board_id: ID!) {

            boards(ids: [$board_id]) {

                id
                name
                state

                columns {
                    id
                    title
                    type
                }
            }
        }
        """

        data = self._request(
            query,
            {
                "board_id": str(board_id),
            },
        )

        boards = data.get(
            "boards",
            [],
        )

        if not boards:

            raise MondayAPIError(
                f"Board {board_id} was not found "
                "or is inaccessible."
            )

        return boards[0]


    # ========================================================
    # GET ALL ITEMS FROM BOARD
    # ========================================================

    def get_all_items(
        self,
        board_id: str,
        page_size: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all items from a Monday.com board.

        Handles pagination automatically.
        """

        if not board_id:

            raise MondayAPIError(
                "Board ID is missing."
            )

        page_size = min(
            max(page_size, 1),
            500,
        )


        # ----------------------------------------------------
        # FIRST PAGE
        # ----------------------------------------------------

        query = """
        query ($board_id: ID!, $limit: Int!) {

            boards(ids: [$board_id]) {

                items_page(limit: $limit) {

                    cursor

                    items {

                        id
                        name
                        created_at
                        updated_at

                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
        }
        """

        data = self._request(
            query,
            {
                "board_id": str(board_id),
                "limit": page_size,
            },
        )

        boards = data.get(
            "boards",
            [],
        )

        if not boards:

            raise MondayAPIError(
                f"Board {board_id} was not found "
                "or is inaccessible."
            )


        page = boards[0].get(
            "items_page",
            {},
        )

        items = page.get(
            "items",
            [],
        )

        cursor = page.get(
            "cursor"
        )


        # ----------------------------------------------------
        # PAGINATION
        # ----------------------------------------------------

        while cursor:

            next_query = """
            query ($cursor: String!, $limit: Int!) {

                next_items_page(
                    cursor: $cursor,
                    limit: $limit
                ) {

                    cursor

                    items {

                        id
                        name
                        created_at
                        updated_at

                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
            """

            next_data = self._request(
                next_query,
                {
                    "cursor": cursor,
                    "limit": page_size,
                },
            )

            next_page = next_data.get(
                "next_items_page",
                {},
            )

            next_items = next_page.get(
                "items",
                [],
            )

            items.extend(
                next_items
            )

            cursor = next_page.get(
                "cursor"
            )


        return items


    # ========================================================
    # GET BOARD AS PANDAS DATAFRAME
    # ========================================================

    def get_board_dataframe(
        self,
        board_id: str,
    ):
        """
        Retrieve an entire Monday.com board and convert it
        into a pandas DataFrame.

        Returns:
            tuple[pandas.DataFrame, dict]
        """

        import pandas as pd


        # ----------------------------------------------------
        # BOARD METADATA
        # ----------------------------------------------------

        board = self.get_board_info(
            board_id
        )


        # ----------------------------------------------------
        # BOARD ITEMS
        # ----------------------------------------------------

        items = self.get_all_items(
            board_id
        )


        # ----------------------------------------------------
        # COLUMN ID -> COLUMN TITLE
        # ----------------------------------------------------

        column_map = {
            column["id"]: column["title"]
            for column in board.get(
                "columns",
                [],
            )
        }


        records = []


        # ----------------------------------------------------
        # CONVERT ITEMS TO RECORDS
        # ----------------------------------------------------

        for item in items:

            record = {

                "__item_id": item.get(
                    "id"
                ),

                "__item_name": item.get(
                    "name"
                ),

                "__created_at": item.get(
                    "created_at"
                ),

                "__updated_at": item.get(
                    "updated_at"
                ),
            }


            # ------------------------------------------------
            # COLUMN VALUES
            # ------------------------------------------------

            for column in item.get(
                "column_values",
                [],
            ):

                column_id = column.get(
                    "id"
                )

                title = column_map.get(
                    column_id,
                    column_id,
                )

                text_value = column.get(
                    "text"
                )


                # Normalize missing values
                if text_value is None:
                    text_value = ""


                record[title] = text_value


            records.append(
                record
            )


        # ----------------------------------------------------
        # DATAFRAME
        # ----------------------------------------------------

        dataframe = pd.DataFrame(
            records
        )


        return dataframe, board
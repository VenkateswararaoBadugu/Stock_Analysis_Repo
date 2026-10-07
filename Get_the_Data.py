"""
Get_the_Data.py

Company search and stock market data.

Uses Yahoo Finance web endpoints through requests.
"""

import requests
from datetime import datetime, timedelta


# ==========================================================
# Yahoo Finance URLs
# ==========================================================

YAHOO_SEARCH_URL = (
    "https://query2.finance.yahoo.com/"
    "v1/finance/search"
)

YAHOO_CHART_URL = (
    "https://query1.finance.yahoo.com/"
    "v8/finance/chart/{symbol}"
)


# ==========================================================
# HTTP Headers
# ==========================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),

    "Accept": (
        "application/json,text/plain,*/*"
    ),

    "Accept-Language": (
        "en-US,en;q=0.9"
    ),
}


session = requests.Session()

session.headers.update(
    HEADERS
)


# ==========================================================
# Search Companies
# ==========================================================

def search_companies(
    query,
    max_results=8
):

    query = query.strip()

    if not query:
        return []

    try:

        params = {
            "q": query,
            "quotesCount": max_results,
            "newsCount": 0,
            "listsCount": 0,
            "enableFuzzyQuery": "true",
        }

        response = session.get(
            YAHOO_SEARCH_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        quotes = data.get(
            "quotes",
            []
        )

        results = []

        for quote in quotes:

            quote_type = quote.get(
                "quoteType",
                ""
            )

            if quote_type != "EQUITY":
                continue

            symbol = quote.get(
                "symbol"
            )

            if not symbol:
                continue

            name = (
                quote.get("longname")
                or quote.get("shortname")
                or symbol
            )

            exchange = quote.get(
                "exchange",
                ""
            )

            results.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "exchange": exchange,
                }
            )

            if len(results) >= max_results:
                break

        return results

    except Exception as error:

        print(
            "Company search error:",
            error
        )

        return []


# ==========================================================
# Find Company
# ==========================================================

def find_company(query):

    results = search_companies(
        query,
        max_results=8
    )

    if not results:
        return None

    query_lower = (
        query.strip().lower()
    )

    # Exact symbol
    for company in results:

        if (
            company["symbol"].lower()
            == query_lower
        ):
            return company

    # Exact name
    for company in results:

        if (
            company["name"].lower()
            == query_lower
        ):
            return company

    # First result
    return results[0]


# ==========================================================
# Get Chart Data
# ==========================================================

def get_chart_data(symbol):

    try:

        period2 = datetime.now()

        period1 = (
            period2
            - timedelta(days=370)
        )

        params = {

            "period1": int(
                period1.timestamp()
            ),

            "period2": int(
                period2.timestamp()
            ),

            "interval": "1d",

            "events": "div,splits",

            "includeAdjustedClose": "true",
        }

        url = YAHOO_CHART_URL.format(
            symbol=symbol
        )

        response = session.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        chart = data.get(
            "chart",
            {}
        )

        if chart.get("error"):

            return {
                "success": False,
                "message": str(
                    chart["error"]
                )
            }

        results = chart.get(
            "result"
        )

        if not results:

            return {
                "success": False,
                "message": (
                    "Yahoo Finance returned "
                    "no chart data."
                )
            }

        result = results[0]

        timestamps = result.get(
            "timestamp",
            []
        )

        indicators = result.get(
            "indicators",
            {}
        )

        quote_list = indicators.get(
            "quote",
            []
        )

        if not quote_list:

            return {
                "success": False,
                "message": (
                    "No price information "
                    "was returned."
                )
            }

        quote = quote_list[0]

        closes = quote.get(
            "close",
            []
        )

        # --------------------------------------------------
        # Valid closing prices
        # --------------------------------------------------

        valid_prices = []

        for timestamp, close in zip(
            timestamps,
            closes
        ):

            if close is not None:

                valid_prices.append(
                    (
                        timestamp,
                        float(close)
                    )
                )

        if len(valid_prices) < 2:

            return {
                "success": False,
                "message": (
                    "Not enough price data "
                    "was returned."
                )
            }

        # --------------------------------------------------
        # Starting / current price
        # --------------------------------------------------

        starting_price = (
            valid_prices[0][1]
        )

        current_price = (
            valid_prices[-1][1]
        )

        if starting_price != 0:

            price_change = (
                (
                    current_price
                    - starting_price
                )
                / starting_price
            ) * 100

        else:

            price_change = 0.0

        # --------------------------------------------------
        # Calculate daily gain/loss contribution
        # --------------------------------------------------

        total_gain = 0.0
        total_loss = 0.0

        previous_price = (
            valid_prices[0][1]
        )

        for _, current_day_price in (
            valid_prices[1:]
        ):

            daily_change = (
                current_day_price
                - previous_price
            )

            if daily_change > 0:

                total_gain += daily_change

            elif daily_change < 0:

                total_loss += abs(
                    daily_change
                )

            previous_price = (
                current_day_price
            )

        # --------------------------------------------------
        # Convert gain/loss to 100%
        # --------------------------------------------------

        total_movement = (
            total_gain
            + total_loss
        )

        if total_movement > 0:

            gain_percentage = (
                total_gain
                / total_movement
            ) * 100

            loss_percentage = (
                total_loss
                / total_movement
            ) * 100

        else:

            gain_percentage = 0.0
            loss_percentage = 0.0

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        meta = result.get(
            "meta",
            {}
        )

        currency = meta.get(
            "currency",
            "Unknown"
        )

        exchange_name = meta.get(
            "exchangeName",
            ""
        )

        return {

            "success": True,

            "current_price":
                current_price,

            "starting_price":
                starting_price,

            "price_change_percentage":
                price_change,

            "currency":
                currency,

            "exchange":
                exchange_name,

            "gain_percentage":
                gain_percentage,

            "loss_percentage":
                loss_percentage,
        }

    except requests.exceptions.RequestException as error:

        return {

            "success": False,

            "message": (
                "Unable to connect to "
                "Yahoo Finance.\n\n"
                f"Network error:\n{error}"
            )
        }

    except ValueError as error:

        return {

            "success": False,

            "message": (
                "Yahoo Finance returned "
                "an invalid response.\n\n"
                f"Error:\n{error}"
            )
        }

    except Exception as error:

        return {

            "success": False,

            "message": (
                "Unable to retrieve "
                "market data.\n\n"
                f"Error:\n{error}"
            )
        }


# ==========================================================
# Get Company Data
# ==========================================================

def get_company_data(
    company_or_symbol
):

    company_or_symbol = (
        company_or_symbol.strip()
    )

    if not company_or_symbol:

        return {

            "success": False,

            "message": (
                "Please enter a company "
                "name or stock symbol."
            )
        }

    print(
        "Searching Yahoo Finance for:",
        company_or_symbol
    )

    company = find_company(
        company_or_symbol
    )

    if not company:

        return {

            "success": False,

            "message": (
                f"No company found for "
                f"'{company_or_symbol}'."
            )
        }

    symbol = company["symbol"]

    company_name = company["name"]

    print(
        f"Resolved company: "
        f"{company_name} ({symbol})"
    )

    chart_result = get_chart_data(
        symbol
    )

    if not chart_result["success"]:

        return {

            "success": False,

            "message": (
                f"Found company:\n"
                f"{company_name} ({symbol})\n\n"
                f"But market data could not "
                f"be retrieved.\n\n"
                f"{chart_result['message']}"
            )
        }

    return {

        "success": True,

        "data": {

            "company_name":
                company_name,

            "symbol":
                symbol,

            "current_price":
                chart_result[
                    "current_price"
                ],

            "starting_price":
                chart_result[
                    "starting_price"
                ],

            "price_change_percentage":
                chart_result[
                    "price_change_percentage"
                ],

            "currency":
                chart_result[
                    "currency"
                ],

            "exchange":
                chart_result[
                    "exchange"
                ],

            "gain_percentage":
                chart_result[
                    "gain_percentage"
                ],

            "loss_percentage":
                chart_result[
                    "loss_percentage"
                ],

            "sector":
                "Not available yet",

            "industry":
                "Not available yet",

            "period":
                "Approximately 1 Year",
        }
    }

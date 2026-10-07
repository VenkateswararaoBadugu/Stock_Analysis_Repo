"""
Get_the_Data.py

Company search, stock market data, company profile, and buy recommendations using Yahoo Finance.
"""

import requests
from datetime import datetime, timedelta

YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
YAHOO_PROFILE_URL = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=assetProfile,financialData"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)


def search_companies(query, max_results=8):
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

        response = session.get(YAHOO_SEARCH_URL, params=params, timeout=8)
        response.raise_for_status()
        quotes = response.json().get("quotes", [])

        results = []
        for quote in quotes:
            if quote.get("quoteType") != "EQUITY":
                continue

            symbol = quote.get("symbol")
            if not symbol:
                continue

            name = quote.get("longname") or quote.get("shortname") or symbol
            exchange = quote.get("exchange", "")

            results.append({
                "name": name,
                "symbol": symbol,
                "exchange": exchange,
            })

            if len(results) >= max_results:
                break

        return results
    except Exception as error:
        print("Company search error:", error)
        return []


def find_company(query):
    results = search_companies(query, max_results=8)
    if not results:
        return None

    query_lower = query.strip().lower()

    for company in results:
        if company["symbol"].lower() == query_lower:
            return company

    for company in results:
        if company["name"].lower() == query_lower:
            return company

    return results[0]


def get_profile_data(symbol):
    """Fetch business description, leadership, sector, and analyst buy recommendations."""
    try:
        url = YAHOO_PROFILE_URL.format(symbol=symbol)
        response = session.get(url, timeout=8)
        if response.status_code == 200:
            summary = response.json().get("quoteSummary", {}).get("result", [])
            if summary:
                profile = summary[0].get("assetProfile", {})
                financial = summary[0].get("financialData", {})

                # Main Business Summary
                long_summary = profile.get("longBusinessSummary", "Business description not available.")

                # Officers / CEO / Business Owners
                officers = profile.get("companyOfficers", [])
                executives = []
                for officer in officers[:3]:
                    name = officer.get("name")
                    title = officer.get("title", "")
                    if name:
                        executives.append(f"{name} ({title})" if title else name)
                leadership = ", ".join(executives) if executives else "Leadership details not available."

                # Analyst Recommendation
                rec_key = financial.get("recommendationKey", "none").lower()
                rec_mean = financial.get("recommendationMean", {}).get("raw", None)

                return {
                    "sector": profile.get("sector", "N/A"),
                    "industry": profile.get("industry", "N/A"),
                    "summary": long_summary,
                    "leadership": leadership,
                    "recommendation_key": rec_key,
                    "recommendation_mean": rec_mean,
                }
    except Exception as err:
        print("Profile fetch error:", err)

    return {
        "sector": "N/A",
        "industry": "N/A",
        "summary": "Business description not available.",
        "leadership": "Leadership details not available.",
        "recommendation_key": "none",
        "recommendation_mean": None,
    }


def get_chart_data(symbol):
    try:
        period2 = datetime.now()
        period1 = period2 - timedelta(days=370)

        params = {
            "period1": int(period1.timestamp()),
            "period2": int(period2.timestamp()),
            "interval": "1d",
            "events": "div,splits",
            "includeAdjustedClose": "true",
        }

        url = YAHOO_CHART_URL.format(symbol=symbol)
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()

        chart = response.json().get("chart", {})
        if chart.get("error"):
            return {"success": False, "message": str(chart["error"])}

        results = chart.get("result")
        if not results:
            return {"success": False, "message": "No chart data returned."}

        result = results[0]
        timestamps = result.get("timestamp", [])
        quote_list = result.get("indicators", {}).get("quote", [])

        if not quote_list:
            return {"success": False, "message": "No price information returned."}

        closes = quote_list[0].get("close", [])
        valid_prices = [(t, float(c)) for t, c in zip(timestamps, closes) if c is not None]

        if len(valid_prices) < 2:
            return {"success": False, "message": "Not enough historical price data available."}

        starting_price = valid_prices[0][1]
        current_price = valid_prices[-1][1]
        price_change = ((current_price - starting_price) / starting_price * 100) if starting_price else 0.0

        total_gain = 0.0
        total_loss = 0.0
        previous_price = valid_prices[0][1]

        for _, current_day_price in valid_prices[1:]:
            daily_change = current_day_price - previous_price
            if daily_change > 0:
                total_gain += daily_change
            elif daily_change < 0:
                total_loss += abs(daily_change)
            previous_price = current_day_price

        total_movement = total_gain + total_loss
        if total_movement > 0:
            gain_percentage = (total_gain / total_movement) * 100
            loss_percentage = (total_loss / total_movement) * 100
        else:
            gain_percentage = loss_percentage = 0.0

        meta = result.get("meta", {})
        return {
            "success": True,
            "current_price": current_price,
            "starting_price": starting_price,
            "price_change_percentage": price_change,
            "currency": meta.get("currency", "USD"),
            "exchange": meta.get("exchangeName", ""),
            "gain_percentage": gain_percentage,
            "loss_percentage": loss_percentage,
        }

    except Exception as error:
        return {"success": False, "message": f"Unable to retrieve market data: {error}"}


def get_company_data(company_or_symbol):
    company_or_symbol = company_or_symbol.strip()
    if not company_or_symbol:
        return {"success": False, "message": "Please enter a valid ticker or name."}

    company = find_company(company_or_symbol)
    if not company:
        return {"success": False, "message": f"No company found for '{company_or_symbol}'."}

    symbol = company["symbol"]
    company_name = company["name"]

    chart_result = get_chart_data(symbol)
    if not chart_result["success"]:
        return {
            "success": False,
            "message": f"Found company {company_name} ({symbol}), but market data could not be loaded.\n{chart_result['message']}"
        }

    profile = get_profile_data(symbol)

    # --------------------------------------------------
    # Evaluate "Worthy to Buy or Not"
    # --------------------------------------------------
    rec_key = profile["recommendation_key"]
    rec_mean = profile["recommendation_mean"]
    price_change = chart_result["price_change_percentage"]
    gain_pct = chart_result["gain_percentage"]

    if rec_key in ["buy", "strong_buy"]:
        is_worthy = True
        recommendation_reason = f"Analyst Consensus: {rec_key.replace('_', ' ').title()} rating."
    elif rec_mean is not None and rec_mean <= 2.5:
        is_worthy = True
        recommendation_reason = f"Analyst Score: {rec_mean:.1f}/5.0 (Positive Growth Outlook)."
    elif rec_key in ["sell", "underperform"]:
        is_worthy = False
        recommendation_reason = f"Analyst Consensus: {rec_key.replace('_', ' ').title()} rating."
    elif price_change > 0 and gain_pct >= 50.0:
        is_worthy = True
        recommendation_reason = f"Positive 1-Year Trend (+{price_change:.2f}% return with {gain_pct:.1f}% gain contribution)."
    else:
        is_worthy = False
        recommendation_reason = f"Cautious Outlook (1-Year Change: {price_change:+.2f}%, Gain Ratio: {gain_pct:.1f}%)."

    return {
        "success": True,
        "data": {
            "company_name": company_name,
            "symbol": symbol,
            "current_price": chart_result["current_price"],
            "starting_price": chart_result["starting_price"],
            "price_change_percentage": chart_result["price_change_percentage"],
            "currency": chart_result["currency"],
            "exchange": chart_result["exchange"],
            "gain_percentage": chart_result["gain_percentage"],
            "loss_percentage": chart_result["loss_percentage"],
            "sector": profile["sector"],
            "industry": profile["industry"],
            "summary": profile["summary"],
            "leadership": profile["leadership"],
            "is_worthy": is_worthy,
            "recommendation_reason": recommendation_reason,
        }
    }
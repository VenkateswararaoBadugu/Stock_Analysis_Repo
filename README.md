# Stock Analysis Repo

A repository for stock analysis and company-level financial insights.

## Overview
This project focuses on:
- Stock market analysis
- Searching for a company
- Viewing company information
- Displaying financial and performance trends
- Comparing top gainers and losers over selectable trading-day periods
- Visualizing data with charts such as doughnut charts

## Application Layout

```text
┌────────────────────────────────────────────────────────────────────┐
│ STOCK MARKET ANALYSIS                                                 │
│                                                                      │
│ Search for a company...                 [ Search bar ] [ Search ]   │
│                                                                      │
│ Suggestions                                                          │
└────────────────────────────────────────────────────────────────────┘

Fixed Top Area
────────────────────────────────────────────────────────────────────

Scrollable Analysis Area
├── Company Analysis
├── Company Information
├── Key Metrics
├── Financial Overview
└── Doughnut Chart
```

## Main Sections

### 1. Top Bar
- Search input for company lookup
- Search button
- Suggested company names

### 2. Company Analysis
- Overview of stock/company performance
- Market-related insights
- AI chat button answers questions about the currently analyzed company using its profile and metrics

### 3. Company Information
- Basic company details
- Industry and business context

### 4. Visual Data Representation
- Doughnut chart for segmented analysis
- Helps compare key metrics visually

### 5. Trending
- Shows separate Top Gainers and Top Losers lists
- Each list has its own 1, 5, 10, 30, or 90 trading-day selector
- Each list independently selects 5, 10, 20, or 30 companies
- Yahoo Finance's current daily mover lists are ranked by the selected historical return

## Purpose
The project is designed to provide a simple and structured dashboard for analyzing a company within the stock market context.

## Future Improvements
- Add real-time stock data
- Include price charts and historical trends
- Add comparison tools for multiple companies
- Improve search and suggestion functionality

## Notes
This README reflects the current UI and feature structure of the application and can be expanded as the project grows.

## AI Chat Configuration
The company chat uses OpenRouter's `apodex/apodex-1.1-mini:free` model with reasoning enabled. Put a newly generated API key in the `OPENROUTER_API_KEY` entry in the app-local `.env` file. This file is ignored by Git. Do not use keys shared in chat or commit `.env`.

If `.env` is missing, create it beside `app.py` with `OPENROUTER_API_KEY=your-replacement-key`.

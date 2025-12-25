DATA-DRIVEN STOCK ANALYSIS: ORGANIZING, CLEANING, AND VISUALIZING MARKET TRENDS
Project Overview
The Stock Performance Dashboard provides a comprehensive visualization and analysis of Nifty 50 stocks over the past year.
It extracts, cleans, and processes daily stock data (open, close, high, low, volume) and generates interactive dashboards using Streamlit and Power BI.
This project helps investors, analysts, and enthusiasts make informed decisions by identifying top-performing stocks, analyzing volatility, sector-wise performance, and monthly gainers/losers.
Problem Statement
The goal is to:
- Analyze daily Nifty 50 stock data.
- Clean and transform YAML-based datasets into structured CSV files.
- Generate insights such as top gainers/losers, volatility, cumulative returns, sector performance, and correlations.
- Provide interactive dashboards for decision support.
Business Use Cases
- Stock Performance Ranking: Identify top 10 best-performing (green) and worst-performing (red) stocks.
- Market Overview: Summarize average performance and percentage of green vs red stocks.
- Investment Insights: Highlight consistent growth vs significant declines.
- Decision Support: Provide insights into average prices, volatility, and stock behavior.
Tech Stack
Languages: Python
Database: MySQL / PostgreSQL
Visualization Tools: Streamlit, Power BI
Libraries: Pandas, Matplotlib, SQLAlchemy
Approach
1. Data Extraction & Transformation
	- Input: YAML files organized by months and dates.
	- Output: 50 CSV files (one per stock symbol).
	- Transformation: Clean and validate data, store in SQL database.
2. Data Analysis & Metrics
	- Top 10 Green Stocks: Based on yearly return.
	- Top 10 Loss Stocks: Based on yearly return.
	- Market Summary: green vs red stocks.
Key Analytics & Visualizations
1.	Market Overview Dashboard
Total stocks
Green vs Red stocks
2.	Top Gainers & Losers
Top 10 gainers (yearly return)
Top 10 losers (yearly return)
3.	Volatility Analysis
Standard deviation of daily returns
Top 10 most volatile stocks
4.	Cumulative Return Analysis
Cumulative growth over time
Top 5 performing stocks
5.	Sector-wise Performance
Average yearly return by sector
6.	Correlation & Risk Analysis
Stock return correlation matrix
Risk identification using correlation strength
7.	Monthly Gainers & Losers
Top 5 gainers and losers for each month
Results
- Fully functional dashboard showing top-performing and worst-performing stocks.
- Insights into market trends, volatility, and sector performance.
- Interactive dashboards in Streamlit and Power BI.


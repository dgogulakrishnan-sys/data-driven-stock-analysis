import os
import yaml
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


RAW_DATA = r"D:\PROJECTS\DATA_DRIVEN_STOCK_ANALYSIS\data\raw_yaml"
CSV_DATA = r"D:\PROJECTS\DATA_DRIVEN_STOCK_ANALYSIS\data\processed_csv"
SECTOR_CSV = r"D:\PROJECTS\DATA_DRIVEN_STOCK_ANALYSIS\data\sector.csv"
DB_URL = "mysql+mysqlconnector://root:BanuD8695@localhost:3306/data_driven_stock_analysis"

def convert_yaml_to_csv(raw_data_path, csv_output_path, ticker_key="Ticker"):
    os.makedirs(csv_output_path, exist_ok=True)
    symbol_data = {}

    for root, _, files in os.walk(raw_data_path):
        for file in files:
            if file.endswith((".yaml", ".yml")):
                with open(os.path.join(root, file), "r") as f:
                    data = yaml.safe_load(f)

                records = data if isinstance(data, list) else [data]

                for record in records:
                    if isinstance(record, dict):
                        symbol = record.get(ticker_key)
                        if symbol:
                            symbol_data.setdefault(symbol, []).append(record)

    for symbol, records in symbol_data.items():
        pd.DataFrame(records).to_csv(
            os.path.join(csv_output_path, f"{symbol}.csv"),
            index=False
        )

    return len(symbol_data)

def load_csv_to_mysql(csv_path, db_url, table_name="stock_prices"):
    engine = create_engine(db_url)

    for file in os.listdir(csv_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(csv_path, file))
            df.rename(columns={"Ticker": "ticker"}, inplace=True)
            df["date"] = pd.to_datetime(df["date"]).dt.date

            df.to_sql(table_name, engine, if_exists="append", index=False)

            print(f"Inserted {file}")

    print("All CSV files loaded into MySQL")

@st.cache_data(show_spinner=True)
def fetch_and_save_sector_data(csv_path, sector_csv_path):

    # If already saved, just load it
    if os.path.exists(sector_csv_path):
        return pd.read_csv(sector_csv_path)

    sector_data = []

    for file in os.listdir(csv_path):
        if file.endswith(".csv"):
            ticker = file.replace(".csv", "")
            try:
                info = yf.Ticker(ticker + ".NS").info
                sector = info.get("sector", "Unknown")
            except Exception:
                sector = "Unknown"

            sector_data.append({
                "ticker": ticker,
                "sector": sector
            })

    df = pd.DataFrame(sector_data)
    df.to_csv(sector_csv_path, index=False)

    return df

@st.cache_data(show_spinner=True)
def load_stock_data(csv_path):
    frames = []

    for file in os.listdir(csv_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(csv_path, file))
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")  # IMPORTANT FIX
            df["ticker"] = file.replace(".csv", "")
            df["daily_return"] = df["close"].pct_change()
            frames.append(df)

    return pd.concat(frames, ignore_index=True)

@st.cache_data
def calculate_yearly_returns(stocks_df):
    return (
        stocks_df.groupby("ticker")["daily_return"]
        .apply(lambda x: (1 + x.dropna()).prod() - 1)
        .reset_index(name="yearly_return")
    )

@st.cache_data
def top_gainers_losers(yearly_returns, top_n=10):
    gainers = (
        yearly_returns
        .sort_values("yearly_return", ascending=False)
        .head(top_n)
    )

    losers = (
        yearly_returns
        .sort_values("yearly_return", ascending=True)
        .head(top_n)
    )

    return gainers, losers

@st.cache_data
def calculate_volatility(stocks_df):
    return (
        stocks_df.groupby("ticker")["daily_return"]
        .std()
        .sort_values(ascending=False)
        .head(10)
    )

@st.cache_data
def calculate_cumulative_returns(stocks_df, tickers):
    cumulative_data = {}
    for ticker in tickers:
        df = stocks_df.loc[stocks_df["ticker"] == ticker,["date", "daily_return"]].copy()  
        df["cumulative_return"] = (1 + df["daily_return"]).cumprod()
        cumulative_data[ticker] = df
    return cumulative_data

@st.cache_data
def calculate_sector_performance(stocks_df, sector_df):

    if "ticker" not in sector_df.columns:
        raise ValueError(
            f"sector_df columns are {sector_df.columns.tolist()}"
        )
    yearly_returns = calculate_yearly_returns(stocks_df)
    merged = yearly_returns.merge(sector_df,on="ticker",how="left")
    merged = merged.dropna(subset=["sector", "yearly_return"])
    return (merged.groupby("sector", as_index=False)["yearly_return"].mean().sort_values("yearly_return", ascending=False))

@st.cache_data
def calculate_stock_correlation(stocks_df):
    price_df = stocks_df.pivot_table(index="date", columns="ticker", values="close")
    return price_df.pct_change().dropna().corr()

@st.cache_data(show_spinner=False)
def calculate_monthly_returns(stocks_df):
    df = stocks_df.copy()
    df["month"] = df["date"].dt.to_period("M")

    monthly = (
        df.groupby(["month", "ticker"])["close"]
        .agg(first_price="first", last_price="last")
        .reset_index()
    )

    monthly["monthly_return"] = (
        (monthly["last_price"] - monthly["first_price"])
        / monthly["first_price"]
    ) * 100

    return monthly

@st.cache_data
def calculate_monthly_gainers_losers(monthly_df, selected_month, top_n=10):
    month_df = monthly_df[monthly_df["month"].astype(str) == selected_month]

    gainers = (
        month_df.sort_values("monthly_return", ascending=False)
        .head(top_n)
    )

    losers = (
        month_df.sort_values("monthly_return", ascending=True)
        .head(top_n)
    )

    return gainers, losers

st.set_page_config("Stock Dashboard", layout="wide")

st.title("DATA_DRIVEN STOCK ANALYSIS")

stocks_df = load_stock_data(CSV_DATA)
sector_df = fetch_and_save_sector_data(CSV_DATA, SECTOR_CSV)

yearly_returns = calculate_yearly_returns(stocks_df)
top_gainers, top_losers = top_gainers_losers(yearly_returns)

green = (yearly_returns["yearly_return"] > 0).sum()
red = (yearly_returns["yearly_return"] <= 0).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Stocks", len(yearly_returns))
col2.metric("Green Stocks", green)
col3.metric("Red Stocks", red)

section = st.sidebar.radio(
    "Choose section",
    (
        "Top 10 Gainers & Losers",
        "Volatility",
        "Cumulative Return",
        "Sector-wise Performance",
        "Correlation",
        "Monthly Gainers & Losers",
    ),
)

if section == "Top 10 Gainers & Losers":
    st.subheader("Top 10 Gainers & Losers")
    col1, col2 = st.columns(2)
    col1.bar_chart(top_gainers.set_index("ticker")["yearly_return"])
    col2.bar_chart(top_losers.set_index("ticker")["yearly_return"])

elif section == "Volatility":
    st.subheader("Volatility Analysis")
    vol = calculate_volatility(stocks_df)
    fig, ax = plt.subplots()
    vol.plot(kind="bar", ax=ax)
    ax.set_ylabel("Volatility")
    st.pyplot(fig)

elif section == "Cumulative Return":
    st.subheader("Cumulative Return Over Time")
    top5 = top_gainers["ticker"].head(5).tolist()
    cumulative_data = calculate_cumulative_returns(stocks_df, top5)
    fig, ax = plt.subplots()
    for ticker, df in cumulative_data.items():
        ax.plot(df["date"], df["cumulative_return"], label=ticker)
    ax.legend()
    st.pyplot(fig)

elif section == "Sector-wise Performance":
    st.subheader("Sector-wise Performance")
    sector_perf = calculate_sector_performance(stocks_df, sector_df)
    fig, ax = plt.subplots()
    ax.barh(sector_perf["sector"], sector_perf["yearly_return"])
    st.pyplot(fig)

elif section == "Correlation":
    st.subheader("Stock Price Correlation")
    corr = calculate_stock_correlation(stocks_df)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=90)
    ax.set_yticklabels(corr.index)
    fig.colorbar(im, ax=ax)
    st.pyplot(fig)

elif section == "Monthly Gainers & Losers":
    st.subheader("Top Gainers & Losers (Monthly)")
    monthly_df = calculate_monthly_returns(stocks_df)
    selected_month = st.selectbox(
        "Select Month",
        sorted(monthly_df["month"].astype(str).unique()),
    )
    gainers, losers = calculate_monthly_gainers_losers(
        monthly_df, selected_month
    )
    combined = pd.concat([gainers, losers])
    colors = ["green" if x > 0 else "red"
              for x in combined["monthly_return"]]
    fig, ax = plt.subplots()
    ax.bar(combined["ticker"], combined["monthly_return"], color=colors)
    ax.tick_params(axis="x", rotation=90)
    ax.set_ylabel("Monthly Return (%)")
    st.pyplot(fig)

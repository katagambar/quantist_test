import yfinance as yf
import pandas as pd
import datetime
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Gunakan DATABASE_URL yang sama dengan web app
DB_URL = os.getenv("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DB_URL and DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DB_URL, pool_pre_ping=True)

def fetch_yfinance_data(tickers, start_date=None):
    if not start_date:
        start_date = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    print(f"Fetching data from {start_date}...")

    # Download data
    df = yf.download([t + ".JK" for t in tickers], start=start_date, group_by="ticker")

    if len(tickers) == 1:
        # yfinance behavior is different for single ticker
        df = {tickers[0]+".JK": df}

    all_data = []
    for ticker in tickers:
        ticker_jk = ticker + ".JK"
        if ticker_jk not in df:
            continue

        stock_df = df[ticker_jk].dropna()
        if stock_df.empty:
            continue

        stock_df = stock_df.reset_index()
        # Rename columns to match Supabase database
        stock_df = stock_df.rename(columns={
            "Date": "date",
            "Open": "openprice",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        # Calculate derived columns needed by Quantist
        stock_df['code'] = ticker
        stock_df['previous'] = stock_df['close'].shift(1)
        stock_df['change'] = stock_df['close'] - stock_df['previous']
        stock_df['value'] = stock_df['volume'] * ((stock_df['high'] + stock_df['low'] + stock_df['close'])/3)
        stock_df['frequency'] = 0 # yfinance doesn't provide trade frequency
        stock_df['foreignbuy'] = 0 # Default if no data
        stock_df['foreignsell'] = 0 # Default if no data

        all_data.append(stock_df)

    if all_data:
        final_df = pd.concat(all_data, ignore_options=True)
        # Select only required columns
        columns_to_insert = ['code', 'date', 'openprice', 'high', 'low', 'close', 'previous', 'change', 'volume', 'value', 'frequency', 'foreignbuy', 'foreignsell']
        final_df = final_df[columns_to_insert]

        # Upsert into database
        # In production we should handle duplicates better, this is a basic script
        print("Inserting into database...")
        final_df.to_sql('stockdata', engine, if_exists='append', index=False)
        print("Done!")
    else:
        print("No new data to insert.")

if __name__ == "__main__":
    # Example: LQ45 top stocks
    tickers = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "AMMN", "ADRO"]
    fetch_yfinance_data(tickers)

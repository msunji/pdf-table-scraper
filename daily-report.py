import re
from io import BytesIO
import requests
import gspread as gs
import pdfplumber as plumber
import pandas as pd

from modules import gsheet_actions
from modules import scraper

# def clean_data(data, date):
#   df = pd.DataFrame(data)

#   portfolio_stocks = equity_sh.worksheet("stocks").col_values(1)
#   wow_stocks = equity_sh.worksheet("test_gainers_losers").col_values(1)

#   stocks_to_scrape = list(set(portfolio_stocks + wow_stocks))

#   # Replace blank cells ('-') with zero
#   # Also remove commas from all cells
#   df = (df.replace('[-]', 0, regex=True).replace('[,]', '', regex=True))

#   # Add column names
#   df.columns = ["Symbol", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"]

#   # Convert () to negative number
#   df["Net Foreign"] = (df["Net Foreign"].replace('[(]', '-', regex=True).replace('[)]', '', regex=True))

#   # Add date column using date parsed from PDF
#   df["Date"] = date

#   # Rearrange columns
#   df = df.reindex(columns=["Symbol", "Date", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"])

#   # Set data types
#   data_types = {
#     "Symbol": object,
#     "Date": object,
#     "Bid": float,
#     "Ask": float,
#     "Open": float,
#     "High": float,
#     "Low": float,
#     "Close": float,
#     "Volume": float,
#     "Value PHP":  float,
#     "Net Foreign": float,
#   }

#   df = df.astype(data_types)

#   # Create separate dataframes for WoW data and portfolio data
#   portfolio_df = df[df["Symbol"].isin(portfolio_stocks)]
#   wow_df = df[df["Symbol"].isin(wow_stocks)]

#   print(portfolio_df.head())
#   print(wow_df.head())

#   # Return dataframes
#   return portfolio_df, wow_df

def clean_data(data, date):
  df = pd.DataFrame(data)

  # Get portfolio stock codes
  portfolio_stocks = gsheet_actions.getWSColVals("stocks", 1)

  # portfolio_stocks = equity_sh.worksheet("stocks").col_values(1)
  # wow_stocks = equity_sh.worksheet("wow_report_stocks").col_values(1)
  # wow_stock_test = pd.DataFrame(equity_sh.worksheet("wow_report_stocks").get_all_records())
  # wow_stock_test.columns = ["Symbol", "Mid Cap or Other"]

  # stocks_to_scrape = list(set(portfolio_stocks + wow_stocks))

  # Replace blank cells ('-') with zero
  # Also remove commas from all cells
  df = (df.replace('[-]', 0, regex=True).replace('[,]', '', regex=True))

  # Add column names
  df.columns = ["Symbol", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"]

  # Convert () to negative number
  df["Net Foreign"] = (df["Net Foreign"].replace('[(]', '-', regex=True).replace('[)]', '', regex=True))

  # Add date column using date parsed from PDF
  df["Date"] = date

  # Rearrange columns
  df = df.reindex(columns=["Symbol", "Date", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"])

  # Set data types
  data_types = {
    "Symbol": object,
    "Date": object,
    "Bid": float,
    "Ask": float,
    "Open": float,
    "High": float,
    "Low": float,
    "Close": float,
    "Volume": float,
    "Value PHP":  float,
    "Net Foreign": float,
  }

  df = df.astype(data_types)

  # Create separate dataframes for WoW data and portfolio data
  portfolio_df = df[df["Symbol"].isin(portfolio_stocks)]
  # wow_df = df[df["Symbol"].isin(wow_stocks)]
  # merged_df = pd.merge(wow_df, wow_stock_test, on="Symbol")

  # print(portfolio_df.head())

  # Return dataframes
  # return portfolio_df, wow_df
  return portfolio_df

def extract_EOD_data(url):
  try:
    global pdf_data
    req = requests.get(url)
    temp = BytesIO(req.content)
    pdf = plumber.open(temp)
    pdf_data, pdf_date = scraper.scrape_pdfs(pdf)
  except:
    print('Something went wrong')
  return clean_data(pdf_data, pdf_date)

# Get worksheets
portfolio_eod = gsheet_actions.getWorksheet("portfolio_eod_mkt_report")
# wow_eod = equity_sh.worksheet("wow_eod_mkt_report")

# todays_pdf = get_todays_pdf_url()
cleaned_data = extract_EOD_data("https://documents.pse.com.ph/market_report/December%2005,%202023-EOD.pdf")

# Append new values to spreadsheet
portfolio_eod.append_rows(cleaned_data.values.tolist())
# wow_eod.append_rows(cleaned_data.values.tolist())

# Export as CSV
# cleaned_data.to_csv("Nov21.csv", index=False)
import re
from io import BytesIO
import requests
import pdfplumber as plumber
import pandas as pd

from modules import gsheet_actions
from modules import scraper

# def clean_data(data, date):
#   df = pd.DataFrame(data)

#   # Get portfolio stock codes
#   portfolio_stocks = gsheet_actions.getWSColVals("stocks", 1)

#   # portfolio_stocks = equity_sh.worksheet("stocks").col_values(1)
#   # wow_stocks = equity_sh.worksheet("wow_report_stocks").col_values(1)
#   # wow_stock_test = pd.DataFrame(equity_sh.worksheet("wow_report_stocks").get_all_records())
#   # wow_stock_test.columns = ["Symbol", "Mid Cap or Other"]

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
#   # wow_df = df[df["Symbol"].isin(wow_stocks)]
#   # merged_df = pd.merge(wow_df, wow_stock_test, on="Symbol")

#   # print(portfolio_df.head())

#   # Return dataframes
#   # return portfolio_df, wow_df
#   return portfolio_df

def clean_data(data, date, *ignore, report_type):
  # Get data into a dataframe first and do a bit of tidying up
  df = pd.DataFrame(data)

  # Replace blank cells ('-') with zero
  # Also remove commas from all cells
  df = (df.replace('[-]', 0, regex=True).replace('[,]', '', regex=True))

  # Set data frame column names
  df.columns = ["Symbol", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"]

  # Convert () to negative number
  df["Net Foreign"] = (df["Net Foreign"].replace('[(]', '-', regex=True).replace('[)]', '', regex=True))

  # Add date column using date parsed from PDF
  df["Date"] = date

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

  # Rearrange columns
  df = df.reindex(columns=["Symbol", "Date", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"])
  df = df.astype(data_types)

  if report_type.lower() == "daily":
    # Get portfolio stock codes
    portfolio_stocks = gsheet_actions.getWSColVals("stocks", 1)
    # Get destination worksheet for data
    portfolio_eod = gsheet_actions.getWorksheet("portfolio_eod_mkt_report")
    # Return filtered data - should only show portfolio stocks
    return df[df["Symbol"].isin(portfolio_stocks)]
  elif report_type.lower() == "weekly":
    # Get weekly report stock codes and respective categories (2 cols)
    wow_stocks = pd.DataFrame(gsheet_actions.getAllWSRecords("wow_report_stocks"))
    wow_stocks.columns = ["Symbol", "Mid Cap or Other"]
    return df[df["Symbol"].isin(wow_stocks)]
  else:
    raise TypeError("Keyword argument not recognised")

def extract_EOD_data(url, *ignore, report_type):
  try:
    global pdf_data
    req = requests.get(url)
    temp = BytesIO(req.content)
    pdf = plumber.open(temp)
    pdf_data, pdf_date = scraper.scrape_pdfs(pdf)
  except:
    print('Something went wrong')
  return clean_data(pdf_data, pdf_date, report_type=report_type)

# Get worksheets

# wow_eod = equity_sh.worksheet("wow_eod_mkt_report")

# todays_pdf = get_todays_pdf_url()
cleaned_data = extract_EOD_data("https://documents.pse.com.ph/market_report/December%2005,%202023-EOD.pdf", report_type="weekly")

# Append new values to spreadsheet
# portfolio_eod.append_rows(cleaned_data.values.tolist())
# wow_eod.append_rows(cleaned_data.values.tolist())

# Export as CSV
cleaned_data.to_csv("Dec5.csv", index=False)
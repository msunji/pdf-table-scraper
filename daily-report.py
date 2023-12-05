import os
import re
from io import BytesIO
from datetime import datetime
import requests
import gspread as gs
import pdfplumber as plumber
import pandas as pd

from modules import gsheet_actions

# GSheets credentials dict
# credentials = {
#   "type": os.getenv("GAPI_TYPE"),
#   "project_id": os.getenv("PROJECT_ID"),
#   "private_key_id": os.getenv("PRIVATE_KEY_ID"),
#   "private_key": os.getenv("PRIVATE_KEY"),
#   "client_email": os.getenv("CLIENT_EMAIL"),
#   "client_id": os.getenv("CLIENT_ID"),
#   "auth_uri": os.getenv("AUTH_URI"),
#   "token_uri": os.getenv("TOKEN_URI"),
#   "auth_provider_x509_cert_url": os.getenv("AUTH_CERT_URL"),
#   "client_x509_cert_url": os.getenv("CLIENT_CERT_URL")
# }

# Visual debugging
# def debug_pdf(page):
#   """
#   Helps figure out if we're extracting the right thing.
#   """
#   img = page.to_image()
#   img.debug_tablefinder({
#     "horizontal_strategy": "text",
#     "vertical_strategy": "text",
#     "snap_y_tolerance": 5,
#     "snap_x_tolerance": 5,
#   })
#   img.save("debug.png")

# gc = gs.service_account_from_dict(credentials)
# equity_sh = gc.open("PH Equity Data")

def extractTables(page):
    """
    Extracts tables from each page of the PDF document.
    Crops pages to only the relevant bits, extracts tables, then returns a list.
    """
    cropped_page = page.crop((32.07, 165.26, page.width, 604+165.26))
    table = cropped_page.extract_tables(table_settings={
      "horizontal_strategy": "text",
      "vertical_strategy": "text",
      "snap_y_tolerance": 5,
      "snap_x_tolerance": 5,
    })

    """
    Clean extracted table first. Remember to only get the first element in table list
    so you're not left with overly nested lists.
    cleaned_table is a list with lists containing strings, numbers, and '-' symbols.
    It also omits the full company name (first column)

    In other words, blank rows parsed by extract_tables should be removed accordingly.
    """
    # Remove blanks
    no_blanks_list = [row for row in table[0] if not '' in row[1:]]

    # Remove the first element in each list (full company name)
    cleaned_list = [list[1:] for list in no_blanks_list]
    return cleaned_list

def scrape_pdfs(pdf):
    """
    Get PDF EOD date
    """
    page1 = pdf.pages[0]
    cropped_header = page1.crop((29.2, 107.76, page1.width, 16.3+107.76))
    date_str = cropped_header.extract_text()
    date_parsed = datetime.strptime(date_str, "%B %d, %Y").strftime("%m-%d-%Y")

    """
    Scrape and compiled tables from pages 1-7 of the PDF document.
    Returns a list of all scraped and cleaned data, as well as the date
    written in the parsed PDF
    """
    all_tables = []
    for index, page in enumerate(pdf.pages):
      new_table= extractTables(page)
      all_tables.extend(new_table)
      if index == 6:
          break
    return all_tables, date_parsed

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
    pdf_data, pdf_date = scrape_pdfs(pdf)
  except:
    print('Something went wrong')
  return clean_data(pdf_data, pdf_date)

# Get worksheets
# portfolio_eod = equity_sh.worksheet("portfolio_eod_mkt_report")
# wow_eod = equity_sh.worksheet("wow_eod_mkt_report")

# todays_pdf = get_todays_pdf_url()
cleaned_data = extract_EOD_data("https://documents.pse.com.ph/market_report/December%2004,%202023-EOD.pdf")

# Append new values to spreadsheet
# portfolio_eod.append_rows(cleaned_data.values.tolist())
# wow_eod.append_rows(cleaned_data.values.tolist())

# Export as CSV
cleaned_data.to_csv("Nov21.csv", index=False)
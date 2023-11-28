import os
import re
from io import BytesIO
from datetime import datetime
import requests
import gspread as gs
import pdfplumber as plumber
import pandas as pd

# GSheets credentials dict
credentials = {
  "type": os.getenv("GAPI_TYPE"),
  "project_id": os.getenv("PROJECT_ID"),
  "private_key_id": os.getenv("PRIVATE_KEY_ID"),
  "private_key": os.getenv("PRIVATE_KEY"),
  "client_email": os.getenv("CLIENT_EMAIL"),
  "client_id": os.getenv("CLIENT_ID"),
  "auth_uri": os.getenv("AUTH_URI"),
  "token_uri": os.getenv("TOKEN_URI"),
  "auth_provider_x509_cert_url": os.getenv("AUTH_CERT_URL"),
  "client_x509_cert_url": os.getenv("CLIENT_CERT_URL")
}

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

def clean_data(data, date):
  df = pd.DataFrame(data)
  stocks_ws = equity_sh.worksheet("stocks")

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

  # Filter dataframe to stocks in portfolio
  portfolio_df = df[df["Symbol"].isin(stocks_ws.col_values(1))]
  print(portfolio_df.head())
  # Return clean dataframe
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

def get_todays_pdf_url():
  date_str = datetime.today().strftime("%B-%d-%Y")
  date_list = date_str.split("-")
  return "https://documents.pse.com.ph/market_report/" + date_list[0] + "%20"+ date_list[1] + ",%20" + date_list[2]+ "-EOD.pdf"

gc = gs.service_account_from_dict(credentials)
equity_sh = gc.open("PH Equity Data")

# Get worksheets
net_foreign_ws = equity_sh.worksheet("daily_net_foreign")

todays_pdf = get_todays_pdf_url()
cleaned_data = extract_EOD_data("https://documents.pse.com.ph/market_report/November%2028,%202023-EOD.pdf")

# Append new values to spreadsheet
# test_ws.update([portfolio_df.columns.values.tolist()] + portfolio_df.values.tolist())
net_foreign_ws.append_rows(cleaned_data.values.tolist())

# Export as CSV
# cleaned_data.to_csv("April27.csv", index=False)
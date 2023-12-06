import re
from io import BytesIO
import requests
import pdfplumber as plumber
import pandas as pd

from modules import gsheet_actions
from modules import scraper

def clean_data(data, date, *ignore, report_type):
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

  # Get data into a dataframe first and do a bit of tidying up
  pdf_data = (
    pd.DataFrame(data, columns=["Symbol", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"])
    .replace('[-]', 0, regex=True)
    .replace('[,]', '', regex=True)
  )

  # Convert () to negative number
  pdf_data["Net Foreign"] = (
    pdf_data["Net Foreign"]
    .replace('[(]', '-', regex=True)
    .replace('[)]', '', regex=True)
  )

  # Add date column using date parsed from PDF
  pdf_data["Date"] = date

  # Rearrange columns
  pdf_data = (pdf_data
    .reindex(columns=["Symbol", "Date", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"])
    .astype(data_types)
  )

  if report_type.lower() == "daily":
    # Get portfolio stock codes
    portfolio_stocks = gsheet_actions.getWSColVals("stocks", 1)
    # Get destination worksheet for data
    portfolio_eod = gsheet_actions.getWorksheet("portfolio_eod_mkt_report")

    # Return filtered data - should only show portfolio stocks
    # Push new data to spreadsheet
    return portfolio_eod.append_rows(
      pdf_data[pdf_data["Symbol"].isin(portfolio_stocks)]
      .values.tolist()
    )
  elif report_type.lower() == "weekly":
    # Get weekly report stock codes and respective categories (2 cols)
    weekly_stocks = pd.DataFrame(gsheet_actions.getAllWSRecords("wow_report_stocks"), columns=["Symbol", "Mid Cap or Other"])

    # Get destination worksheet for data
    weekly_report_data = gsheet_actions.getWorksheet("test_worksheet")

    filtered_data = pdf_data[pdf_data["Symbol"].isin(list(weekly_stocks["Symbol"]))]
    print(weekly_stocks["Symbol"].tolist())

    return (
      pd
      .merge(filtered_data, weekly_stocks, on="Symbol")
      .reindex(columns=["Symbol", "Mid Cap or Other", "Date", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"])
    )
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

extract_EOD_data("https://documents.pse.com.ph/market_report/December%2005,%202023-EOD.pdf", report_type="weekly")

# wow_eod.append_rows(cleaned_data.values.tolist())

# Export as CSV
# cleaned_data.to_csv("Dec5.csv", index=False)
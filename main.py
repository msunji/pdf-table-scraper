from io import BytesIO
import requests
import pandas as pd

from modules import gsheet_actions
from modules import scraper

def clean_update_data(data, date, *ignore, report_type):
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
    portfolio_stocks = gsheet_actions.get_ws_col_vals("stocks", 1)

    # Push filtered dataframe to "portfolio_eod_mkt_report" sheet where daily EOD data lives
    return (
      gsheet_actions.update_sheet("portfolio_eod_mkt_report", pdf_data[pdf_data["Symbol"].isin(portfolio_stocks)]
      .values.tolist())
    )
  elif report_type.lower() == "weekly":
    # Get weekly report stock codes and respective categories (2 cols)
    weekly_stocks = gsheet_actions.get_ws_col_vals("wow_report_stocks", 1)
    weekly_stocks_class = gsheet_actions.get_ws_col_vals("wow_report_stocks", 2)

    # Filter datagrame
    filtered_data = pdf_data[pdf_data["Symbol"].isin(weekly_stocks)]

    weekly_stocks_df = (
      pd.DataFrame({
        "Symbol": weekly_stocks,
        "Index or other": weekly_stocks_class
      })
      .merge(filtered_data, on="Symbol")
    )
    # print(weekly_stocks_df.head())
    return gsheet_actions.update_sheet("test_worksheet", weekly_stocks_df.values.tolist())
  else:
    raise TypeError("Keyword argument not recognised")

def extract_EOD_data(url, *ignore, report_type):
  try:
    global pdf_data
    req = requests.get(url)
    temp = BytesIO(req.content)
    pdf_data, pdf_date = scraper.scrape_pdfs(temp)
  except:
    print('Something went wrong')
  return clean_update_data(pdf_data, pdf_date, report_type=report_type)

extract_EOD_data("https://documents.pse.com.ph/market_report/December%2006,%202023-EOD.pdf", report_type="weekly")

# Export as CSV
# cleaned_data.to_csv("Dec5.csv", index=False)
import os
import gspread as gs
import pdfplumber as plumber
import pandas as pd

# Work with Gsheets
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

gc = gs.service_account_from_dict(credentials)
equity_sh = gc.open("PH Equity Data")
# Get worksheet
stocks_ws = equity_sh.worksheet("stocks")
net_foreign_ws = equity_sh.worksheet("daily_net_foreign")
# Get stocks list
stocks_list = stocks_ws.col_values(1)

# Visual debugging
def debug_pdf(page):
  """
  Helps figure out if we're extracting the right thing.
  """
  img = page.to_image()
  img.debug_tablefinder({
    "horizontal_strategy": "text",
    "vertical_strategy": "text",
    "snap_y_tolerance": 5,
    "snap_x_tolerance": 5,
  })
  img.save("debug.png")

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

    In other words, blank rows parsed by extract_tables should be removed accordingly.
    """

    no_blanks_list = [row for row in table[0] if not '' in row[1:]]
    # Remove the first element in each list (full company name)
    cleaned_list = [list[1:] for list in no_blanks_list]
    return cleaned_list

def scrape_pdfs(pdf):
    """
    Scrape and compiled tables from pages 1-7 of the PDF document.
    Returns a list of all scraped and cleaned data.
    """
    all_tables = []
    for index, page in enumerate(pdf.pages):
      new_table = extractTables(page)
      all_tables.extend(new_table)
      if index == 6:
          break
    return all_tables

# Open PDF to extract
pdf = plumber.open("./files/April26.pdf")
pdf_data = scrape_pdfs(pdf)

# Convert to pandas dataframe
df = pd.DataFrame(pdf_data)

# Add column names
df.columns = ["Symbol", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"]

# Add date column -- date is date when data is collected
df["Date"] = pd.to_datetime('today').strftime('%m-%d-%Y')
# Set data types

# Convert () to negative float
# df["Net Foreign"] = (df["Net Foreign"].replace('[(]', '-', regex=True).replace('[),]', '', regex=True).astype(float))

# Filter dataframe to stocks in portfolio
portfolio_df = df[df["Symbol"].isin(stocks_list)]

# Rearrange columns
portfolio_df = portfolio_df.reindex(columns=["Symbol", "Date", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"])

# Update spreadsheet
# net_foreign_ws.update([net_foreign_portfolio.columns.values.tolist()] + net_foreign_portfolio.values.tolist())
# net_foreign_ws.append_rows(net_foreign_portfolio.values.tolist())
# Export as CSV
# print(net_foreign_portfolio.dtypes)
portfolio_df.to_csv("April26.csv", index=False)



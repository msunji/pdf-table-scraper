import pdfplumber as plumber
import pandas as pd

# Open PDF to extract
pdf = plumber.open("./files/April25.pdf")

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
    Clean extracted table first. Remember to only get the first element in table list so you're not left with overly nested lists. cleaned_table is a list with lists containing strings, numbers, and '-' symbols.

    In other words, blank rows parsed by extract_tables should be removed accordingly.
    """

    cleaned_table = [row for row in table[0] if not '' in row[1:]]
    return cleaned_table

def scrape_pdfs():
    """
    Scrape and compiled tables from pages 1-7 of the PDF document.
    Returns a list of all scraped and cleaned data.
    """
    for index, page in enumerate(pdf.pages):
      all_tables = []
      new_table = extractTables(page)
      all_tables.extend(new_table)
      if index == 6:
          break
    return all_tables


pdf_data = scrape_pdfs()

# Convert to pandas dataframe
df = pd.DataFrame(pdf_data)

# Add column names
df.columns = ["Stock Name", "Symbol", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"]
# print(df.head())

# df.to_csv("April24.csv", index=False)



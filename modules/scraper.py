import re
from io import BytesIO
from datetime import datetime
import pdfplumber as plumber
import pandas as pd

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


def get_tables(page):
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

def scrape_pdfs(pdf_content):
    pdf = plumber.open(pdf_content)
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
      new_table= get_tables(page)
      all_tables.extend(new_table)
      if index == 6:
          break
    return all_tables, date_parsed
import pdfplumber as plumber
import pandas as pd

# # Read PDF pages 1-7 only
# Open PDF to extract
pdf = plumber.open("./files/April18.pdf")

def extractTables(page):
    cropped_page = page.crop((32.07, 165.26, page.width, 604+165.26))
    table = cropped_page.extract_tables(table_settings={
      "horizontal_strategy": "text",
      "vertical_strategy": "text",
      "snap_y_tolerance": 5,
      "snap_x_tolerance": 5,
    })
    # Clean table
    # Remember to only get the first element in table list
    # no_blanks should be a list of lists with lists containing strings, numbers and '-' symbols
    cleaned_table = [row for row in table[0] if not '' in row[1:]]
    return cleaned_table

# Clean table
# Remember to only get the first element in table list
# no_blanks should be a list of lists with lists containing strings, numbers and '-' symbols
# no_blanks = [row for row in table[0] if not '' in row[1:]]
# print(no_blanks)
all_tables = []
for index, page in enumerate(pdf.pages):
    new_table = extractTables(page)
    all_tables.extend(new_table)
    if index == 6:
        break
# print(all_tables)

# Convert to pandas dataframe
df = pd.DataFrame(all_tables)

# Add column names
df.columns = ["Stock Name", "Symbol", "Bid", "Ask", "Open", "High", "Low", "Close", "Volume", "Value PHP", "Net Foreign"]
print(df.head())

df.to_csv("test.csv", index=False)

# Visual debugging
# im = cropped.to_image()
# im.debug_tablefinder({
#     "horizontal_strategy": "text",
#     "vertical_strategy": "text",
#     "snap_y_tolerance": 5,
#     "snap_x_tolerance": 5,
# })
# im.save("debug.png")

import pdfplumber as plumber
import pandas as pd

# # Read PDF pages 1-7 only
pdf = plumber.open("./files/April18.pdf")
p0 = pdf.pages[0]
cropped = p0.crop((32.07, 140.37, p0.width, 604+140.37))

# Visual debugging
im = cropped.to_image()
im.debug_tablefinder({
    "horizontal_strategy": "text",
    "vertical_strategy": "text",
    "snap_y_tolerance": 5,
    "snap_x_tolerance": 5,
})
im.save("debug.png")

# Extract table
table = cropped.extract_tables(table_settings={
    "horizontal_strategy": "text",
    "vertical_strategy": "text",
    "snap_y_tolerance": 5,
    "snap_x_tolerance": 5,
})

# Clean table
# Remember to only get the first element in table list
no_blanks = [row for row in table[0] if not '' in row[1:]]
print(no_blanks)

# clean_rows_df.to_csv("test.csv")
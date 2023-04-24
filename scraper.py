import pdfplumber as plumber
import pandas as pd

# # Read PDF pages 1-7 only
pdf = plumber.open("./files/April18.pdf")
p0 = pdf.pages[0]
cropped = p0.crop((32.07, 140.37, p0.width, 604+140.37))

# im = cropped.to_image()
# im.debug_tablefinder({
#     "horizontal_strategy": "text",
#     "vertical_strategy": "text",
#     "snap_y_tolerance": 5,
#     "join_y_tolerance": 2,
# })
# im.save("debug.png")

# Test tables
table = cropped.extract_tables(table_settings={
    "horizontal_strategy": "text",
    "vertical_strategy": "text",
    "snap_y_tolerance": 5,
    "join_y_tolerance": 2,
})
print(table)

# Clean data
# Only get first and last columns
# print(dfs[0])
# col_df = dfs[0].loc[:, ["Issue Name Symbol", "Buying/(Selling),"]]

# # Rename columns
# col_df.columns = ["Stock", "Net Foreign"]

# # Drop ALL rows with at least one NaN value
# # This is not the same as cells with '-' values
# # Clears rows we really don't need
# clean_rows_df = col_df.dropna(axis=0, how="any")
# # print(clean_rows_df)

# clean_rows_df.to_csv("test.csv")
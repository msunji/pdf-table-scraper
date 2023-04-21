import pdfplumber as plumber
import tabula
import pandas as pd

# # Read PDF pages 1-7 only
pdf = plumber.open("./files/April18.pdf")
p0 = pdf.pages[0]
cropped = p0.crop((33.37, 129.45, p0.width, p0.height))

im = cropped.to_image();
im.debug_tablefinder({
    "horizontal_strategy": "text",
    "explicit_vertical_lines": [34.39, 110, 156.7, 195, 230, 263.09, 305, 336.24, 400, 461, 579]
})
im.save("debug.png")
# p0.crop()
# lines = p0.extract_text()
# print(len(lines))
# print(lines)
# dfs = tabula.read_pdf('./files/April18.pdf', pages="1-7", columns=[34.39, 110, 156.7, 195, 230, 263.09, 305, 336.24, 400, 461, 579], multiple_tables=False, stream=True)
# print(dfs)




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
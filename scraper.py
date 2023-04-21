import tabula
import pandas as pd

# Read PDF pages 1-7 only
dfs = tabula.read_pdf('./files/April18.pdf', pages=[1,7], columns=[32.39, 110, 161.33, 192.32, 231.10, 263.09, 305, 336.24, 399, 461, 525])
print(len(dfs))
# print(dfs[0])

# Clean data
# Only get first and last columns
col_df = dfs[0].loc[:, ["Issue Name Symbol", "Buying/(Selling),"]]
# Rename columns
col_df.columns = ["Stock", "Net Foreign"]
# Drop rows with NaN
clean_rows_df = col_df.dropna(axis=0)
print(clean_rows_df)

# Remove blank cells

# # Select columns
# print(dfs[0].iloc[:,0])
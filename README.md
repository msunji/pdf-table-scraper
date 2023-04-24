# Extracting PSE EOD Quotes
Every day the Philippine Stock Exchange (PSE) provides a daily quotation report for equities. This report is provided in the form of a PDF and covers a number of indicators. This sort of data is usually manually compiled by hand which can be quite time-consuming and cumbersome. 

This Python script uses [pdfplumber](https://github.com/jsvine/pdfplumber) to extract data from the EOD Quotation Report PDFs. Data is then cleaned accordingly, transformed into a pandas dataframe and outputted as a CSV.
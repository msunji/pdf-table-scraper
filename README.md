# Extracting PSE EOD Quotes
Every day the Philippine Stock Exchange (PSE) provides a daily quotation report for equities. This report is provided in the form of a PDF and covers a number of indicators. This sort of data is usually manually compiled by hand which can be quite time-consuming and cumbersome. So I started working on this to reduce some of the time spent collating data at work and give analysts more time to well...analyse things, instead of spending hours collecting data manually.

This Python script uses [pdfplumber](https://github.com/jsvine/pdfplumber) to extract data from the EOD Quotation Report PDFs. Data is then cleaned, transformed into a pandas dataframe, and appended to a Google Sheets spreadsheet.

# Todos
- [x] Figure out how to scrape PDFs
- [x] Clean data
- [x] Read remote PDF url instead of pulling from a local file
- [ ] Get URL automatically from PSE Market Reports page
- [ ] Run as cron job


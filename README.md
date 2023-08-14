# Extracting PSE EOD Quotes
Every day the Philippine Stock Exchange (PSE) provides a daily quotation report for equities - you can have a look at these reports [here](https://www.pse.com.ph/market-report/). End-of-day Quote reports are provided in the form of a PDF, covering a number of indicators, such as stock price indicators, trade volume, and net foreign transactions. Typically, analysts would manually comb through these reports, transferring data from PDFs to spreadsheets. Unsurprisingly, this process can be quite time-consuming and cumbersome. To make this process more efficient, I wrote this script to go through the daily PSE market reports and automatically transfer the data to a shared Google Sheets document that the investment analyst team uses.

This Python script uses [pdfplumber](https://github.com/jsvine/pdfplumber) to extract data from the EOD Quotation Report PDFs. Data is then cleaned, transformed into a pandas dataframe, and appended to a Google Sheets spreadsheet.

In a nutshell, this script takes data from documents that look like this: 

<p align="center">
  <img src="https://res.cloudinary.com/dxzcdb0pm/image/upload/v1691996315/portfolio/misc-screens/Example1-PythonPDF_mbzky0.jpg" alt="Screenshot of a PSE end-of-day quote report">
</p>

and pulls the data into Google Sheets that turn out like this:

<p align="center">
  <img src="https://res.cloudinary.com/dxzcdb0pm/image/upload/v1691996315/portfolio/misc-screens/Example2-PythonPDF_yhrvx6.png" alt="Screenshot of a PSE end-of-day quote report">
</p>

# Todos
- [x] Figure out how to scrape PDFs
- [x] Clean data
- [x] Read remote PDF url instead of pulling from a local file
- [ ] Refactor and fix `UnboundLocalError` when pulling data sometimes


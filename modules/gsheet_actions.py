import gspread as gs
import os

# GSheets credentials dict
credentials = {
  "type": os.getenv("GAPI_TYPE"),
  "project_id": os.getenv("PROJECT_ID"),
  "private_key_id": os.getenv("PRIVATE_KEY_ID"),
  "private_key": os.getenv("PRIVATE_KEY"),
  "client_email": os.getenv("CLIENT_EMAIL"),
  "client_id": os.getenv("CLIENT_ID"),
  "auth_uri": os.getenv("AUTH_URI"),
  "token_uri": os.getenv("TOKEN_URI"),
  "auth_provider_x509_cert_url": os.getenv("AUTH_CERT_URL"),
  "client_x509_cert_url": os.getenv("CLIENT_CERT_URL")
}

all_sheets = gs.service_account_from_dict(credentials)
ph_equity_sh = all_sheets.open("PH Equity Data")

def getWorksheet(worksheet_name):
  worksheet = ph_equity_sh.worksheet(worksheet_name)
  return worksheet

def getAllWSRecords(worksheet_name):
  all_records = ph_equity_sh.worksheet(worksheet_name).get_all_records()
  return all_records

def getWSColVals(worksheet_name, col_val):
  col_values = ph_equity_sh.worksheet(worksheet_name).col_values(col_val)
  return col_values

def updateSheet(worksheet_name, data):
  worksheet_name.append_rows(data.tolist())
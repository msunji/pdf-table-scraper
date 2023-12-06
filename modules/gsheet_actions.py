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

def get_worksheet(worksheet_name):
  return ph_equity_sh.worksheet(worksheet_name)

def get_all_ws_records(worksheet_name):
  return ph_equity_sh.worksheet(worksheet_name).get_all_records()

def get_ws_col_vals(worksheet_name, col_val):
  return ph_equity_sh.worksheet(worksheet_name).col_values(col_val)

def update_sheet(worksheet_name, data):
  worksheet_to_update = get_worksheet(worksheet_name)
  worksheet_to_update.append_rows(data)
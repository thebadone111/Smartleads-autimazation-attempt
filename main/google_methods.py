import gspread
from oauth2client.service_account import ServiceAccountCredentials
from analytics import logger
from analytics import error


def get_gspread():
        try:
                # use creds to create a client to interact with the Google Drive API
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name('/home/ubuntu/app/main/keys/key_google.json', scope)
                client = gspread.authorize(creds)

                # Open the workbook and worksheet
                sheet = client.open('Honeypot -  Tailor Your Service (Svar)').worksheet('worksheet 1')

                # Get all values from the worksheet
                values = sheet.get_all_values()
                values.pop(0)
                
                return values
        except Exception as e:
                logger.critical(f"Error while getting data from gSpread, Error: {e}")
                error(f"Error while getting data from gSpread, Error: {e}")
                return None

def add_data_to_gspread(row, id, date):
        try:
                # use creds to create a client to interact with the Google Drive API
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name('/home/ubuntu/app/main/keys/key_google.json', scope)
                client = gspread.authorize(creds)

                # Open the workbook and worksheet
                sheet = client.open('Honeypot -  Tailor Your Service (Svar)').worksheet('worksheet 1')
                
                # Update cell with new value
                last = sheet.col_count
                second = sheet.col_count - 1
                third = sheet.col_count - 2
                fourth = sheet.col_count - 3
                sheet.update_cell(row+2, last, date) 
                sheet.update_cell(row+2, second, date)
                sheet.update_cell(row+2, third, date)
                sheet.update_cell(row+2, fourth, id)
        except Exception as e:
                logger.error(f"Error while adding data to gSpread, Error: {e}")
                error(f"Error while adding data to gSpread, Error: {e}")

                return None

def increase_week(row, date):
        try:
                # use creds to create a client to interact with the Google Drive API
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name('/home/ubuntu/app/main/keys/key_google.json', scope)
                client = gspread.authorize(creds)

                # Open the workbook and worksheet
                sheet = client.open('Honeypot -  Tailor Your Service (Svar)').worksheet('worksheet 1')
                
                # Update cell with new value
                last = sheet.col_count
                sheet.update_cell(row+2, last, date)
        except Exception as e:
                logger.error(f"Error increasing week count, Error: {e}, Row: {row}")
                error(f"Error while incraeing weekly count, Error: {e}, Row: {row}")

def increase_month  (row, date):
        try:
                # use creds to create a client to interact with the Google Drive API
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name('/home/ubuntu/app/main//keys/key_google.json', scope)
                client = gspread.authorize(creds)

                # Open the workbook and worksheet
                sheet = client.open('Honeypot -  Tailor Your Service (Svar)').worksheet('worksheet 1')
                
                # Update cell with new value
                last = sheet.col_count
                sheet.update_cell(row+2, last, date)
        except Exception as e:
                logger.error(f"Error increasing month count, Error: {e}, Row {row}")
                error(f"Error increasing month count, Error: {e}, Row {row}")

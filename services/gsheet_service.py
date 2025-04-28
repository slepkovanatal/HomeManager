from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.credentials import GOOGLE_CREDENTIALS_PATH, SPREADSHEET_ID

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
RANGE_NAME = 'Sheet1!A:B'  # Adjust range as needed

def get_google_sheets_service():
    """Get authenticated Google Sheets service."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f'Failed to create service: {e}')
        return None

def append_item_to_sheet(item_name: str, item_price: float) -> bool:
    """
    Append an item and its price to the Google Sheet.
    
    Args:
        item_name: Name of the item to add
        item_price: Price of the item
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        service = get_google_sheets_service()
        if not service:
            return False

        values = [[item_name, item_price]]
        body = {'values': values}
        
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        return True

    except HttpError as error:
        print(f'Google Sheets API error: {error}')
        return False
    except Exception as e:
        print(f'Error appending item: {e}')
        return False

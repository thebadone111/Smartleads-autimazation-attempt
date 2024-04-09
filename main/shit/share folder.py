from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def share_folder_with_user(service_account_file_path, folder_name, email_address, role='writer'):
    """
    Shares a folder with a given email address.
    :param service_account_file_path: Path to the service account key file.
    :param folder_id: ID of the folder to share.
    :param email_address: Email address of the user to share the folder with.
    :param role: Role to assign to the user (default is 'writer').
    :return: The permission ID of the new user permission.
    """
    # Load credentials from the JSON file
    credentials = service_account.Credentials.from_service_account_file(service_account_file_path)

    # Create an authorized Drive client
    service = build('drive', 'v3', credentials=credentials)

    # Create a new permission for the user
    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email_address
    }

    folder_id = get_folder_id(service, folder_name)

    try:
        permission = service.permissions().create(
            fileId=folder_id,
            body=permission,
            sendNotificationEmail=True
        ).execute()
        permission_id = permission['id']
        print(f"Folder shared with {email_address} ({permission_id})")
        return permission_id
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    

def get_folder_id(service, folder_name):
    # Search for the folder by name
    query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and name='{folder_name}'"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    folder_id = items[0]['id']

    return folder_id
    
service_account_file_path = 'keys/key_upload_logs.json'
folder_name = 'Logs'
email_address = 'jonathangroschel5@gmail.com'
role = 'writer'

share_folder_with_user(service_account_file_path, folder_name, email_address, role)

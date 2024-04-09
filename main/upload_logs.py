from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import os
from analytics import logger

# Handlers
handlers = ["tiger.gjers@gmail.com"]

def upload_file_to_folder(file_path, folder_name):
    # Load credentials from the JSON file
    credentials = service_account.Credentials.from_service_account_file('/home/ubuntu/app/main/keys/key_upload_logs.json')

    # Create an authorized Drive client
    service = build('drive', 'v3', credentials=credentials)

    # Get the ID of the folder to upload the file to
    folder_id = get_folder_id(service, folder_name)

    # Create a MediaFileUpload object for the file
    file_name = os.path.basename(file_path)
    file_metadata = {'mimeType': 'text/plain', 'name': file_name, 'parents': [folder_id]}
    logger.info(f"Uploading log file: {file_name}")
    media = MediaFileUpload(file_path, mimetype="text/plain")

    # Upload the file to the specified folder
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        logger.info(f"File uploaded to folder: {file_id}")
    except HttpError as error:
        logger.error(f'An error occured while uploading file to folder: {error}')
        file = None
    
    # Share file with handlers
    #TODO FIX THIS SHIT 
    '''
    for handler in handlers:
        share_file_with_user(service, file_id, handler)
    '''
    
def get_folder_id(service, folder_name):
    # Search for the folder by name
    query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and name='{folder_name}'"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    # If folder not found, create it
    if not items:
        folder_id = create_folder(service, folder_name)
    else:
        folder_id = items[0]['id']

    return folder_id


def create_folder(service, folder_name):
    # Create the folder
    file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    folder = service.files().create(body=file_metadata, fields='id').execute()
    logger.info('Folder created: %s' % folder.get('id'))
    return folder.get('id')

def share_file_with_user(service, file_id, email_address):
    try:
        # Define the permission to be created
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email_address
        }

        # Create the permission
        response = service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=True,
            emailMessage="Log files for today"
        ).execute()

        # Print the response
        logger.info(f"Logs shared with user {email_address}: {response}")
    except HttpError as error:
        logger.error(f"An error occurred: {error}")

def list_files_in_folder():
    # Load credentials from the JSON file
    credentials = service_account.Credentials.from_service_account_file('/home/ubuntu/app/main/keys/key_upload_logs.json')

    # Create an authorized Drive API client
    service = build('drive', 'v3', credentials=credentials)

    folder_id = get_folder_id(service, "logs")

    # Query for files in the folder
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    files = results.get('files', [])

    # Print the file names and IDs
    if files:
        print(f"Files in folder '{folder_id}':")
        for file in files:
            print(f"{file['name']} ({file['id']})")
    else:
        print(f"No files found in folder '{folder_id}'")
    return service, folder_id

def delete_all_files_in_folder(service, folder_id):
    try:
        # Get all the files in the folder
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        # Delete each file in the folder
        for item in items:
            service.files().delete(fileId=item['id']).execute()
            print(f"File '{item['name']}' with ID '{item['id']}' deleted from the folder with ID '{folder_id}'")

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == "__main__":
    serv, id = list_files_in_folder()
    #" delete_all_files_in_folder(service=serv, folder_id=id)


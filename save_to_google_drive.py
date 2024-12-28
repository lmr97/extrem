import os.path
os.system("")   # makes colors process right for Windows
import sys
import json
import mimetypes
from json.decoder import JSONDecoder

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


class FileToUpload:
    def __init__(self, filepath, dest_Drive_folder=None):

        if (not filepath or filepath == ""): 
            raise FileNotFoundError("I need a filename!")

        self.filepath    = os.path.abspath(filepath)

        # strip out local path
        if (os.name == "nt"):
            self.filename = self.filepath.split("\\")[-1]
        else:
            self.filename = self.filepath.split("/")[-1]

        self.dest_folder = dest_Drive_folder
        self.mime_type = mimetypes.guess_type(self.filename)[0]

        print("\nAuthenticating...")
        self.creds   = self.authenticate()

        print("Locating file (in given folder, if specified)...")
        self.service = build("drive", "v3", credentials=self.creds)

        if (dest_Drive_folder and dest_Drive_folder != ""):
            self.folder_ID = self.find_folder_ID()
        else:
            self.folder_ID = None
        
        self.file_ID = self.find_file_ID()


    def authenticate(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                # Credentials.to_json() returns a str, 
                # so convert it to a dict so it can be 
                # dumped with nice formatting
                creds_json = JSONDecoder().decode(creds.to_json())
                json.dump(creds_json, token, indent=4)
    
        return creds

    # searches specified folder, if given
    def find_file_ID(self):
        
        # build the query, depending on whether folder was specified/found
        query = "name = '" + self.filename + "'"
        if (self.folder_ID):
            query += " and '" + self.folder_ID + "' in parents"

        files = []
        page_token = None
        while True:

            response = (
                self.service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, trashed)",
                    orderBy="modifiedTime desc",
                    pageToken=page_token,
                )
                .execute()
            )

            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
                

        # if no matches, simply return None
        if not files:
            return None
        
        # if the file has been trashed, no ID (we can upload again)
        elif (bool(files[0].get("trashed"))):  
            return None
        
        else:
            # If multiple matches, take ID of most recently modified file
            return files[0]['id']
    

    def find_folder_ID(self):
        
        folders = []
        page_token = None
        while True:

            response = (
                self.service.files()
                .list(
                    q="name = '" + self.dest_folder 
                        + "' and mimeType = 'application/vnd.google-apps.folder'",
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    orderBy="modifiedTime desc",
                    pageToken=page_token,
                )
                .execute()
            )

            folders.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
        
        # if no matches, return None
        if not folders:
            return None
        else:
            # if multiple matches, take the most recent modified
            return folders[0]['id']


    def create_file(self):

        file_metadata = {"name": self.filename}
        if self.folder_ID:
            file_metadata.update({"parents": [self.folder_ID]})
    
        media = MediaFileUpload(self.filepath, 
                                mimetype=self.mime_type)

        # Call the Drive v3 API
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )


    def update_file(self):
        media = MediaFileUpload(self.filepath, mimetype=self.mime_type)

        self.service.files().update(fileId=self.file_ID, 
                                    media_body=media
                                    ).execute()




def main():

    dest_folder = None

    if len(sys.argv) == 3:
        dest_folder = sys.argv[2]

    try:
        file = FileToUpload(filepath=sys.argv[1], dest_Drive_folder=dest_folder)
    except FileNotFoundError:
        print("\033[0;31mA file was not specified. One is needed to run this program.\003[0m")
        print("Exiting...")
        exit(1)

    if (file.file_ID):      # if the file is already on Drive...
        print("File found. Updating...")
        file.update_file()
    else:
        print("File not uploaded yet, uploading now...")
        file.create_file()

    print("\n\033[0;32mProcess complete!\033[0m")
    print("\033[3mthank you for using my program! :)\033[0m\n")



if __name__ == "__main__":
  main()
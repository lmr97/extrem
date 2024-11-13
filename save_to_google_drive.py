import os.path
os.system("")   # makes colors process right for Windows
import sys
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


class FileToUpload:
    def __init__(self, filename, dest_Drive_folder=None):

        self.filename    = filename
        self.dest_folder = dest_Drive_folder

        # These are the supported MIME types for this application
        self.mime_lookup = {
            "pdf": "application/pdf",
            "psd": "image/vnd.adobe.photoshop",
            "jpg": "image/jpeg"
        }

        file_ext = self.filename.split(".")[1]
        try:
            self.mime_type = self.mime_lookup[file_ext]
        except KeyError as e:
            print("\n\033[0;31mI'm sorry, it looks like I haven't accounted for that kind of file yet.\033[0m")
            print("Please let me know if you see this.\n")
            exit()              # application cannot continue without MIME type

        print("\nAuthenticating...")
        self.creds   = self.authenticate()

        print("Locating file (in given folder, if specified)...")
        self.service = build("drive", "v3", credentials=self.creds)

        self.known_file_IDs   = json.load(open("file_IDs.json", "r"))
        self.known_folder_IDs = json.load(open("folder_IDs.json", "r"))

        if (dest_Drive_folder):
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
                    token.write(creds.to_json())
        
        return creds

    # searches specified folder, if given
    def find_file_ID(self):
        
        # if (self.filename in self.known_file_IDs.keys()):
        #     return self.known_file_IDs[self.filename]
        
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
        
        # We shouldn't count trashed files, and update JSONs/dicts accordingly
        if bool(files[0].get("trashed")):
            self.known_file_IDs.pop(self.filename)

            with open("files_IDs.json", "w") as f:
                json.dump(self.known_file_IDs, f, indent=4)
                
            return None

        # If multiple matches, take ID of most recently modified file
        files_dict = {files[0]['name']: files[0]['id']}
        self.known_file_IDs.update(files_dict)

        # update file for read-in later
        with open("files_IDs.json", "w") as f:
            json.dump(self.known_file_IDs, f, indent=4)

        if (self.filename in self.known_file_IDs.keys()):
            return self.known_file_IDs[self.filename]
        else:
            return None
    

    def find_folder_ID(self):

        # if (self.dest_folder in self.known_folder_IDs.keys()):
        #     return self.known_folder_IDs[self.dest_folder]
        
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

        # if multiple matches, take the most recent modified
        folders_dict = {folders[0]['name']: folders[0]['id']}
        self.known_folder_IDs.update(folders_dict)

        # update file for read-in later
        with open("folder_IDs.json", "w") as f:
            json.dump(self.known_folder_IDs, f, indent=4)

        if (self.dest_folder in self.known_folder_IDs.keys()):
            return self.known_folder_IDs[self.dest_folder]
        else:
            return None


    def create_file(self):
        file_metadata = {"name": self.filename}
        if self.folder_ID:
            file_metadata.update({"parents": [self.folder_ID]})
        
        media = MediaFileUpload(self.filename, 
                                mimetype=self.mime_type)

        # Call the Drive v3 API
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        new_file_ID = file.get("id")
        self.known_file_IDs.update({self.filename: new_file_ID})

        with open("file_IDs.json", "w") as f:
            json.dump(self.known_file_IDs, f, indent=4)


    def update_file(self):
        media = MediaFileUpload(self.filename, mimetype=self.mime_type)

        self.service.files().update(fileId=self.file_ID, 
                                    media_body=media
                                    ).execute()




def main():

    dest_folder = None

    if len(sys.argv) == 3:
        dest_folder = sys.argv[2]

    file = FileToUpload(filename=sys.argv[1], dest_Drive_folder=dest_folder)

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
import json
from json.decoder import JSONDecoder
import mimetypes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from requests import Session
import pycurl
from urllib.parse import urlencode

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.apps.readonly"]


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

        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.HTTPHEADER, [f"Authorization: Bearer {self.creds.token}"])
        self.curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
        
        self.requests_session = Session()
        self.requests_session.headers = {"authorization": f"Bearer {self.creds.token}"}

        print("Locating file (in given folder, if specified)...")

        if (dest_Drive_folder and dest_Drive_folder != ""):
            self.folder_ID = self.find_folder_ID()
        else:
            self.folder_ID = None
        
        self.file_ID = self.find_file_ID()


    # Since this part requires user/browser interaction, 
    # so it needs to stay using the Python API
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


    def find_file_ID(self):

        query = "name = '" + self.filename + "'"
        if (self.folder_ID):
            query += " and '" + self.folder_ID + "' in parents"

        params_find_file = {
            "fields": "files(id, name, trashed)",
            "orderBy": "modifiedByMeTime desc",
            "pageSize": 10,
            "q": query
        }

        self.curl.setopt(pycurl.URL, "https://www.googleapis.com/drive/v3/files"
                         + "?" + urlencode(params_find_file)
                         )
        resp_str  = self.curl.perform_rs()
        resp_json = JSONDecoder().decode(resp_str)
        files     = resp_json["files"]

        # If it's not on the Drive yet, or trashed, 
        # we don't want it
        if not files:
            return None
        if bool(files[0]["trashed"]):
            return None
        else:
            # If multiple matches, take ID of most recently modified file
            return files[0]["id"]  


    def find_folder_ID(self):
        params_find_folder = {
            "fields": "files(id, name, trashed)",
            "orderBy": "modifiedByMeTime desc",
            "pageSize": 10,
            "q": "name = '" + self.dest_folder + "' "
                    + "and mimeType = " 
                    + "'application/vnd.google-apps.folder'"
        }

        self.curl.setopt(pycurl.URL, "https://www.googleapis.com/drive/v3/files"
                         + "?" + urlencode(params_find_folder)
                         )
        resp_str  = self.curl.perform_rs()
        resp_json = JSONDecoder().decode(resp_str)
        folders   = resp_json["files"]  # folders are considered files in Drive

        # If it's not on the Drive yet, or trashed, 
        # it effectively has no ID
        if not folders:
            return None
        # if the most recent one is trashed, the user doesn't want it
        if bool(folders[0]["trashed"]):
            return None
        else:
            # If multiple matches, take ID of most recently modified file
            return folders[0]["id"]  


    # using Requests library for this and update_file()
    # because, frankly, PyCurl is a pain when it comes to 
    # POST requests to the Google Drive API.
    # I'll keep the PyCurl bits included earler, though, for better speed.
    def create_file(self):

        file_metadata = {
            "name": self.filename,
        }
        if self.folder_ID:
            file_metadata.update({"parents": [self.folder_ID]})

        upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        upload_package = {
            'metadata': 
                (
                    None, 
                    str(file_metadata), 
                    'application/json'
                ),
            'media': 
                (
                    self.filename, 
                    open(self.filepath, "rb"), 
                    self.mime_type
                )
        }
        resp = self.requests_session.post(upload_url, files=upload_package)
        
        return resp
    
    # Intended to update the content of an existing file,
    # without altering its metadata. Thus, it assumes that 
    # the file type doesn't change (e.g. you're not 
    # uploading a PDF in place of a JPEG).
    #
    # This method also assumes that the local filename is 
    # the same as the filename in Google Drive. 
    #
    # If the folder is not specified, this updates the file
    # in whatever folder it currently is located in. 
    # And if there are multiple files of the same name 
    # in different folders, and the folder is still not 
    # specified, it will update the file that was most 
    # recently modified. 
    # (Note: much of this logic is implemented in the the 
    # way the fileID is queried, in find_folder_ID())
    def update_file(self):

        file_metadata = {
            "name": self.filename,
        }
        if self.folder_ID:
            file_metadata.update({"parents": [self.folder_ID]})

        upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{self.file_ID}?uploadType=media"

        resp = self.requests_session.patch(upload_url,
                                           headers={'content-type': self.mime_type},
                                           data=open(self.filepath, "rb"))
        
        return resp
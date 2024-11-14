# make sure external drive filepaths end with a slash

import json

with open("external_drive_paths.json", "r") as paths_file:
    drive_paths = json.load(paths_file)

if (drive_paths["UnixFilePath"][-1] != "/"):
    drive_paths["UnixFilePath"] += "/"

if (drive_paths["DOSFilePath"][-1] != "\\"):
    drive_paths["DOSFilePath"] += "\\"

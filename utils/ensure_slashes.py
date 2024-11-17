# make sure external drive filepaths end with a slash

import os
import json

with open(os.path.abspath("./utils/external_drive_paths.json"), "r") as paths_file:
    drive_paths = json.load(paths_file)

if (drive_paths["UnixFilePath"]):

    if (drive_paths["UnixFilePath"][-1] != "/"):
        drive_paths["UnixFilePath"] += "/"

if (drive_paths["DOSFilePath"]):

    if (drive_paths["DOSFilePath"][-1] != "\\"):
        drive_paths["DOSFilePath"] += "\\"

# else, do nothing

with open(os.path.abspath("./utils/external_drive_paths.json"), "w") as paths_file:
    json.dump(drive_paths, paths_file, indent=4)
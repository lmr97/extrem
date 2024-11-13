import os
import json

with open("external_drive_paths.json", "r") as paths_file:
    drive_paths = json.load(paths_file)

dos_like  = "backslashes (\\)"
unix_like = "forward slashes (/)"
prompt  = "Please enter the absolute filepath to your external hard drive,"

if (os.name == "nt"):
    prompt += "using " + dos_like + " to separate folders.\n"
    path = input(prompt)
    drive_paths["DOSFilePath"] = path
else:
    prompt += "using " + unix_like + " to separate folders.\n\n"
    path = input(prompt)
    drive_paths["UnixFilePath"] = path

with open("external_drive_paths.json", "w") as paths_file:
    json.dump(drive_paths, paths_file, indent=4)

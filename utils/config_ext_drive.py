import os
import json

with open(os.path.abspath("./utils/external_drive_paths.json"), "r") as paths_file:
    drive_paths = json.load(paths_file)

print("It looks like you haven't selected an external drive yet.")

prompt  = """
    Please enter the (absolute) filepath to your external hard drive,
    using %s to separate folder names.
    (this path will be saved for latter, so you won't have to enter it again.)

    To find the filepath to your drive: 
        1. Open File Explorer, and navigate to your external hard drive.
        2. In the bar near the top of the window, right-click your drive's name.
        3. In the right-click menu, select "Copy Address".
        4. Paste the address below!
"""
os.path.abspath

dos_like  = "backslashes (\\)"
unix_like = "forward slashes (/)"

filepath_is_valid = False

while(not filepath_is_valid):

    # if it's a Windows operating system
    if (os.name == "nt"):
        path = input(prompt % dos_like)
        drive_paths["DOSFilePath"] = path
    else:
        path = input(prompt % unix_like)
        drive_paths["UnixFilePath"] = path
    
    filepath_is_valid = os.path.exists(path)

    if (not filepath_is_valid):
        print("\033[0;31mThat path does not lead to an external drive.\033[0m")
        print("Make sure to check the spelling, and try again!")


print("\nThanks! If you use a different drive, please let me know.")

with open(os.path.abspath("./utils/external_drive_paths.json"), "w") as paths_file:
    json.dump(drive_paths, paths_file, indent=4)

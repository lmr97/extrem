import os
os.system("")   # makes colors process right for Windows
import sys
from FileToUpload import FileToUpload

def main():

    dest_folder = None

    if len(sys.argv) == 3:
        dest_folder = sys.argv[2]

    try:
        file = FileToUpload(filepath=sys.argv[1], dest_Drive_folder=dest_folder)
    except IndexError:
        print("\033[0;31mA file was not specified. One is needed to run this program.\033[0m")
        print("Exiting...")
        exit(1)

    response = None
    if (file.file_ID):      # if the file is already on Drive...
        print("File found. Updating...")
        response = file.update_file()
    else:
        print("File not uploaded yet, uploading now...")
        response = file.create_file()

    file.curl.close()
    
    if response.status_code == 200:
        print("\n\033[0;32mProcess complete!\033[0m")
    else:
        print("There was an issue with the file upload/update: ")
        print(f"The request received a response code of {response.status_code},")
        print(f"and the following response content:\n{response.text}")
        
    print("\033[3mthank you for using my program! :)\033[0m\n")



if __name__ == "__main__":
  main()
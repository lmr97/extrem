import sys
from FileToUpload import FileToUpload


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
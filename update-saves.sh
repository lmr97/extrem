# this script copies the given file to your external drive,
# then saves it to your Google Drive.

# Usage: 
# bash update-saves.sh FILE [FOLDER]

if [ -d "D:\\exdrive\\Photoshop" ]; then
    cp "C:\\Documents\\Photoshop\\$1" "D:\\exdrive\\Photoshop"
else
    echo -e "\n\e[0;31mIt looks like the external hard drive is not connected.\e[0m"
    echo -e "Please check to make sure it's plugged in, and try running this program again.\n"
    return 1
fi

poetry run python save-to-google-drive.py $1 $2
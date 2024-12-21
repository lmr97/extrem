# ExtRem

***Ext**ernal and **Rem**ote file copy progam*

This program takes a given file, and copies it to a chosen external drive, as well as the user's Google Drive. A destination folder common to both locations can be specified if so desired.  

## Installation

1. Clone the repository
    ```
    git clone https://github.com/lmr97/extrem
    cd ./extrem
    ```
2. Set up the Python virtual environment. There are a few options available to do so:
    
    <u>**Poetry**</u> (*prefered*): This program uses [Poetry](https://python-poetry.org/docs/) for Python dependency management, so if you have it installed, all you need to do is run `poetry install`.

    <u>**Conda**</u> There is an environment file, `env.yml`, you can use to set up a Conda virtual environment by running:
    ```
    conda create -f env.yml
    conda activate extrem
    ```

    <u>**Manual**</u> There is a `requirements.txt` file you can use if you already have an environment you'd like to run this in.

3. **For Windows users**: Since this runs off a PowerShell script, will need to [sign](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_signing?view=powershell-7.4) the main script `update-saves.ps1`.

## Basic Usage

Instead of a CLI, this program has an iteractive interface for user-friendliness. It runs as a PowerShell program that gets some of the user input, performs the file transfer, and calls several Python scripts. 

Since `update-saves.ps1`, the main script, handles all the rest of the executions, all you need to do to run the program is open a PowerShell window/shell, make sure you're in the cloned directory, and run:

```
.\update-saves.ps1
```

The program will prompt you for the input it needs from there. 

Hope you enjoy!
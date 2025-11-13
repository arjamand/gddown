|Note: This project was developed solely for personal, educational, and recreational programming purposes. Any misuse, malicious activity, or unauthorized application of this software — and any resulting consequences — are the sole responsibility of the user, not the developer.|
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

A Command line application that downloads view-only(Download-locked) PDFs from Google Drive .

### Features
- Download PDFs from Google Drive links
- Download entire Google Drive folder with all pdfs in it 
- Support for single links, folders, or batch processing from text/CSV files

### Features which may or may not be available in future
- Support For downloading all formats (For now its just pdfs)

### Requirements
- Python 3.8+
- Windows, macOS, or Linux

### Installation
 - There's a easy way for windows user :
   Go to start menu and search for CMD , right click the command prompt and run as administrator.
   Copy and paste below command in ther termianl and press enter :
   ```bash
   powershell -Command "iwr https://raw.githubusercontent.com/arjamand/gddown/main/install.bat -OutFile install.bat; Start-Process cmd -ArgumentList '/c install.bat' -Verb RunAs"
   ```
 - Sroll down to Usage Section for Usage Instructions 
 - For Linux / MacOS users you will have to go the long way for now , sorry :)

   **Make Sure you have git and python installed**
1. **clone the repository or download as zip**
   ```bash
   git clone https://github.com/arjamand/gddown.git
   cd gddown
   ```

2. **Create a virtual environment (optional):**
   ```bash
   python -m venv venv
   # Activate venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browser (required once):**
   ```bash
   playwright install chromium
   ```

## Usage
### Easy Guided Usage 
```bash 
# This will list the options and you can interact with it 
python interactive-mode.py
```

### Single Command Usage 
```bash
# Usage Help 
python gddown.py --help 

# Download a Single File 
python gddown.py --link "https://drive.google.com/file/d/XXXXX/view"

# Download all PDFs from a folder (creates local folder with same name)
python gddown.py --link "https://drive.google.com/drive/folders/FOLDER_ID"

# From a text file (one URL per line):
python gddown.py.py --file links.txt

# From a CSV file:
python gddown.py.py --file links.csv

# Run in headless mode (no visible browser):
python gddown.py --link "https://drive.google.com/file/d/XXXXX/view" --headless

# Increase timeout for slow connections (seconds):
python gddown.py --file links.txt --timeout 60

# Combine options:
python gddown.py --file links.txt --headless --timeout 45
```


## Supported URL Formats
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
- `https://drive.google.com/file/d/FILE_ID/view?usp=sharing&resourcekey=KEY`

## Support

For issues or questions:
1. Check the log file: `gddown.log`
2. Try with `--timeout 60` for slower connections
3. Verify the link is accessible (test opening manually)
4. Ensure all dependencies are correctly installed

# Google Drive PDF Downloader

A robust Python application that downloads PDFs from Google Drive links using browser automation. The tool captures PDF pages as images and compiles them into a single PDF file, replicating the behavior of the provided JavaScript mechanism.

## Features

✨ **Core Functionality:**
- Download PDFs from Google Drive links
- **Download entire Google Drive folders** (new!)
  - Automatically scans folder for PDF files
  - Creates local folder with same name
  - Downloads all files to the folder
- Support for single links, folders, or batch processing from text/CSV files
- Automatic document title detection and use as PDF filename
- Browser automation with Playwright (Chrome/Chromium/Edge)
- Visible or headless mode execution
- Proper error handling and logging

🔧 **Technical Features:**
- Async/await for efficient concurrent processing
- Blob image capture from Google Drive PDF viewer
- Image-to-PDF compilation using `img2pdf`
- Automatic RGBA to RGB conversion for compatibility
- Filename sanitization (removes illegal characters)
- Duplicate filename handling with automatic numbering
- Configurable page load timeout
- Comprehensive logging to console and file

## Requirements

- Python 3.8+
- Windows, macOS, or Linux

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd gddown
   ```

2. **Create a virtual environment (optional but recommended):**
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
   Or install specific browser:
   ```bash
   playwright install chrome
   playwright install edge
   ```

## Usage

### Single PDF File Download

```bash
python gdrive_pdf_downloader.py --link "https://drive.google.com/file/d/XXXXX/view"
```

### Download Entire Google Drive Folder

```bash
# Download all PDFs from a folder (creates local folder with same name)
python gdrive_pdf_downloader.py --link "https://drive.google.com/drive/folders/FOLDER_ID"
```

This will:
1. Scan the Google Drive folder for all PDF files
2. Create a local folder with the same name as the Drive folder
3. Download all PDFs from the folder to the local folder

### Batch Download from File

```bash
# From a text file (one URL per line):
python gdrive_pdf_downloader.py --file links.txt

# From a CSV file:
python gdrive_pdf_downloader.py --file links.csv
```

### With Options

```bash
# Run in headless mode (no visible browser):
python gdrive_pdf_downloader.py --link "https://drive.google.com/file/d/XXXXX/view" --headless

# Increase timeout for slow connections (seconds):
python gdrive_pdf_downloader.py --file links.txt --timeout 60

# Combine options:
python gdrive_pdf_downloader.py --file links.txt --headless --timeout 45
```

## Input File Formats

### Text File (links.txt)
```
# You can mix file and folder links
https://drive.google.com/file/d/FILE_ID_1/view
https://drive.google.com/drive/folders/FOLDER_ID_1
https://drive.google.com/file/d/FILE_ID_2/view?usp=sharing
```

### CSV File (links.csv)
```
url
https://drive.google.com/file/d/FILE_ID_1/view
https://drive.google.com/drive/folders/FOLDER_ID_1
https://drive.google.com/file/d/FILE_ID_2/view?usp=sharing
```

## Output

- **Downloads Directory:** PDFs are saved in the `downloads/` folder
- **File PDFs:** Automatically named based on Google Drive document title
- **Folder PDFs:** Downloaded to a subfolder with the same name as the Google Drive folder
- **Logging:** Console output + `gdrive_pdf_downloader.log` file

### Example Output
```
downloads/
├── My Research Paper.pdf
├── Project Report.pdf
├── Project Folder/
│   ├── Chapter 1.pdf
│   ├── Chapter 2.pdf
│   └── Chapter 3.pdf
└── Technical Documentation.pdf
```

## How It Works

1. **Browser Launch:** Opens Chromium browser (visible or headless)
2. **Navigation:** Opens the Google Drive PDF link
3. **Page Detection:** Waits for PDF pages to render as blob images
4. **Image Capture:** Extracts each PDF page as a PNG image using Playwright's fetch API
5. **Conversion:** Converts images to RGB format for PDF compatibility
6. **Compilation:** Combines all images into a single PDF using `img2pdf`
7. **Cleanup:** Removes temporary image files
8. **Logging:** Reports success/failure for each URL

## Supported URL Formats

- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
- `https://drive.google.com/file/d/FILE_ID/view?usp=sharing&resourcekey=KEY`

## Error Handling

The application gracefully handles:
- Invalid or inaccessible links
- Network timeouts
- Missing or corrupted PDF pages
- File system errors
- Duplicate filenames

Each error is logged with context, and the application continues processing remaining URLs.

## Configuration

### Timeout
Default: 30 seconds
- Increase for slow internet connections
- Example: `--timeout 60`

### Headless Mode
- Default: False (visible browser)
- Use `--headless` for background processing

### Browser Type
By default uses Chromium. To use other browsers, modify the code:
```python
# In download_multiple() method, change:
browser = await p.chromium.launch(headless=self.headless)
# To:
browser = await p.firefox.launch(headless=self.headless)
# Or:
browser = await p.webkit.launch(headless=self.headless)
```

## Logging

Detailed logs are available in:
- **Console:** Real-time progress and errors
- **File:** `gdrive_pdf_downloader.log`

Log levels:
- `INFO`: General progress (links processed, PDFs saved)
- `DEBUG`: Detailed technical information
- `WARNING`: Recoverable issues
- `ERROR`: Critical failures

## Troubleshooting

### "Could not detect PDF pages"
- Google Drive may have changed page structure
- Try increasing timeout: `--timeout 60`
- Check if you have view access to the document
- Verify the document is a PDF (not Google Docs, Sheets, etc.)

### "Failed to capture PDF pages"
- Ensure images are loading in the visible browser
- Try with `--headless false` to debug visually
- Check internet connection stability

### Permission Errors
- Ensure you're logged into Google Drive in the browser
- Share settings on Google Drive may require authentication
- Try opening the link manually first

### Out of Memory
- Process fewer files at once
- Increase system RAM
- Run in headless mode to save resources

## Dependencies

| Package | Purpose |
|---------|---------|
| `playwright` | Browser automation |
| `pillow` | Image processing (RGBA to RGB) |
| `img2pdf` | PDF compilation from images |
| `aiohttp` | Async HTTP requests |

## Performance Notes

- **First run:** Playwright downloads ~200MB browser (one-time only)
- **Per PDF:** Typically 10-60 seconds depending on:
  - Number of pages
  - Internet speed
  - Page load timeout setting
- **Memory:** ~500MB-2GB per concurrent download

## Limitations

- Requires a visible or headless browser (cannot work in restricted environments)
- Only works with PDFs accessible to the user
- Large PDFs (100+ pages) may take several minutes
- Google Drive rate limits may apply for batch downloads

## Advanced Usage

### Processing Large Batches

Create a `batch_links.csv`:
```csv
url,description
https://drive.google.com/file/d/ID1/view,Report_Q1
https://drive.google.com/file/d/ID2/view,Report_Q2
https://drive.google.com/file/d/ID3/view,Report_Q3
```

Run:
```bash
python gdrive_pdf_downloader.py --file batch_links.csv --headless --timeout 45
```

### Automating with Cron/Task Scheduler

Windows (Task Scheduler):
```
Program: python.exe
Arguments: C:\path\to\gdrive_pdf_downloader.py --file links.txt --headless
Start in: C:\path\to\project
```

Linux/macOS (Crontab):
```bash
0 2 * * * cd /path/to/project && python gdrive_pdf_downloader.py --file links.txt --headless
```

## Limitations & Disclaimer

- This tool is for personal/authorized use only
- Respect Google Drive's Terms of Service
- Do not use for unauthorized downloading of private documents
- Google may change their PDF viewer implementation, requiring code updates
- Performance depends on internet speed and system resources

## Contributing

To improve this tool:
1. Test with various PDF types and sizes
2. Report issues with specific Google Drive links
3. Suggest enhancements for performance or features

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the log file: `gdrive_pdf_downloader.log`
2. Try with `--timeout 60` for slower connections
3. Verify the link is accessible (test opening manually)
4. Ensure all dependencies are correctly installed

## Changelog

### v1.0.0 (2025-11-12)
- Initial release
- Single and batch download support
- Blob image capture from Google Drive
- PDF compilation from images
- Comprehensive error handling and logging
- Headless mode support
- Configurable timeouts

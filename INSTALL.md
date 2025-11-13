# Installation Guide

## Step-by-Step Setup

### Step 1: Verify Python Installation

Open PowerShell and check your Python version:

```powershell
python --version
```

Expected output: `Python 3.8` or higher

If Python is not installed, download it from [python.org](https://www.python.org)

### Step 2: Navigate to Project Directory

```powershell
cd C:\Users\slowmo\Documents\gddown
```

### Step 3: Create Virtual Environment (Optional but Recommended)

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your PowerShell prompt.

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

Expected output: Multiple packages being downloaded and installed

### Step 5: Install Playwright Browsers

This downloads the browser executable (approximately 200MB):

```powershell
playwright install chromium
```

Or install multiple browsers:

```powershell
playwright install
```

### Step 6: Verify Installation

Run the verification script:

```powershell
python verify_setup.py
```

You should see:

```
✓ All checks passed! You're ready to use the downloader.
```

### Step 7: View Help

```powershell
python gdrive_pdf_downloader.py --help
```

## You're All Set! 🎉

Now you can start downloading PDFs from Google Drive.

## Quick Start Commands

### Single PDF Download

```powershell
python gdrive_pdf_downloader.py --link "https://drive.google.com/file/d/YOUR_FILE_ID/view"
```

### Batch Download

```powershell
python gdrive_pdf_downloader.py --file links.txt
```

### Interactive Mode

```powershell
python interactive_mode.py
```

## Troubleshooting Installation

### Issue: "python: command not found"

**Solution:** Add Python to PATH
1. Reinstall Python and check "Add Python to PATH" during installation
2. Or use the full path: `C:\Python311\python.exe` (adjust version as needed)

### Issue: "pip: command not found"

**Solution:** Use Python module directly:
```powershell
python -m pip install -r requirements.txt
```

### Issue: Permission denied errors

**Solution:** Run PowerShell as Administrator:
1. Right-click PowerShell
2. Select "Run as administrator"
3. Re-run the commands

### Issue: "playwright: command not found"

**Solution:** Use Python module:
```powershell
python -m playwright install chromium
```

### Issue: ModuleNotFoundError

**Solution:** Ensure virtual environment is activated:
```powershell
venv\Scripts\activate
```

### Issue: "No module named playwright"

**Solution:** Install all dependencies:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## Next Steps

1. **Prepare your links:**
   - Edit `links.txt` (one URL per line)
   - Or create a CSV file with a `url` column

2. **Test with a single PDF:**
   ```powershell
   python gdrive_pdf_downloader.py --link "YOUR_DRIVE_LINK"
   ```

3. **Check the downloads folder:**
   ```powershell
   ls downloads
   ```

4. **For batch processing:**
   ```powershell
   python gdrive_pdf_downloader.py --file links.txt
   ```

## Updating Dependencies

To update all packages to their latest versions:

```powershell
pip install --upgrade -r requirements.txt
```

## Deactivating Virtual Environment

When you're done, deactivate the virtual environment:

```powershell
deactivate
```

## Need Help?

Check these resources:

1. **README.md** - Full documentation
2. **QUICKSTART.md** - Quick reference
3. **gdrive_pdf_downloader.log** - Detailed error logs
4. **verify_setup.py** - Run verification script

Good luck with downloading your PDFs! 📄

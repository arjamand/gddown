"""
Configuration file for Google Drive PDF Downloader.
Customize these settings to your needs.
"""

# ============================================================================
# BROWSER SETTINGS
# ============================================================================

# Run browser in headless mode (no visible window)
# Set to True for background processing, False for visible browser
HEADLESS_MODE = False

# Browser type: 'chromium', 'chrome', 'firefox', 'webkit'
BROWSER_TYPE = 'chromium'

# ============================================================================
# TIMEOUT SETTINGS
# ============================================================================

# Maximum time to wait for page to load (seconds)
# Increase this for slow internet connections
PAGE_LOAD_TIMEOUT = 30

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

# Directory where PDFs will be saved
DOWNLOADS_DIRECTORY = 'downloads'

# Temporary directory for image files
TEMP_DIRECTORY = 'temp_images'

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Log file name
LOG_FILE = 'gdrive_pdf_downloader.log'

# Log level: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
LOG_LEVEL = 'INFO'

# ============================================================================
# PDF SETTINGS
# ============================================================================

# Image quality for JPEG conversion (1-100)
# Higher = better quality but larger file size
IMAGE_QUALITY = 95

# ============================================================================
# PROCESSING SETTINGS
# ============================================================================

# Delay between downloads in seconds (to avoid rate limiting)
DOWNLOAD_DELAY = 2

# Maximum number of pages to capture (0 = unlimited)
MAX_PAGES = 0

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Whether to keep temporary image files (for debugging)
KEEP_TEMP_FILES = False

# Maximum number of retry attempts for page loading
MAX_RETRIES = 10

# Wait time between retry attempts (seconds)
RETRY_DELAY = 2

# ============================================================================
# USAGE
# ============================================================================

# To use these settings in your code:
#
# from config import HEADLESS_MODE, PAGE_LOAD_TIMEOUT, DOWNLOADS_DIRECTORY
#
# downloader = GoogleDrivePDFDownloader(
#     headless=HEADLESS_MODE,
#     timeout=PAGE_LOAD_TIMEOUT
# )

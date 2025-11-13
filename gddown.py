"""
Google Drive PDF Downloader
A Python application that downloads PDFs from Google Drive links using Playwright.
Captures PDF pages as images and compiles them into a single PDF.
"""

import argparse
import asyncio
import csv
import logging
import os
import re
import sys
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
from PIL import Image
from playwright.async_api import async_playwright, Page, Browser
import img2pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('gdrive_pdf_downloader.log', encoding='utf-8')
    ],
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


class GoogleDrivePDFDownloader:
    """Downloads PDFs from Google Drive links using browser automation."""

    def __init__(self, headless: bool = False, timeout: int = 30):
        """
        Initialize the downloader.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Maximum time to wait for page load (seconds)
        """
        self.headless = headless
        self.timeout = timeout * 1000  # Convert to milliseconds for Playwright
        self.downloads_dir = Path("downloads")
        self.downloads_dir.mkdir(exist_ok=True)
        self.temp_dir = Path("temp_images")
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"Output directory: {self.downloads_dir.absolute()}")

    def sanitize_filename(self, filename: str) -> str:
        """Remove illegal characters from filename."""
        # Remove invalid characters
        illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(illegal_chars, '_', filename)
        # Remove trailing dots and spaces
        sanitized = sanitized.rstrip('. ')
        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        return sanitized

    def extract_file_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract Google Drive file ID from URL.
        
        Supports formats:
        - https://drive.google.com/file/d/FILE_ID/view
        - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
        """
        match = re.search(r'/file/d/([a-zA-Z0-9-_]+)/', url)
        if match:
            return match.group(1)
        return None

    def extract_folder_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract Google Drive folder ID from URL.
        
        Supports formats:
        - https://drive.google.com/drive/folders/FOLDER_ID
        - https://drive.google.com/drive/folders/FOLDER_ID?usp=sharing
        """
        match = re.search(r'/drive/folders/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        return None

    def is_folder_url(self, url: str) -> bool:
        """Check if URL is a Google Drive folder URL."""
        return '/drive/folders/' in url

    def is_file_url(self, url: str) -> bool:
        """Check if URL is a Google Drive file URL."""
        return '/file/d/' in url

    async def wait_for_pdf_pages(self, page: Page, max_retries: int = 10) -> bool:
        """
        Wait for PDF pages (blob images) to load in Google Drive viewer.
        
        Detects blob images that start with 'blob:https://drive.google.com/'
        """
        logger.info("Waiting for PDF pages to load...")
        
        for attempt in range(max_retries):
            try:
                # Wait for images to load
                await page.wait_for_load_state('networkidle', timeout=5000)
            except Exception as e:
                logger.debug(f"Network idle wait timeout (attempt {attempt + 1}): {e}")

            # Check if blob images are present
            blob_images_count = await page.evaluate("""
                () => {
                    let imgs = document.getElementsByTagName('img');
                    let count = 0;
                    for (let i = 0; i < imgs.length; i++) {
                        if (imgs[i].src.startsWith('blob:https://drive.google.com/')) {
                            count++;
                        }
                    }
                    return count;
                }
            """)

            if blob_images_count > 0:
                logger.info(f"Found {blob_images_count} PDF pages")
                return True

            logger.debug(f"Attempt {attempt + 1}/{max_retries}: Found {blob_images_count} pages, waiting...")
            await asyncio.sleep(2)

        logger.warning("Could not detect PDF pages")
        return False

    async def get_document_title(self, page: Page) -> str:
        """Extract document title from the page."""
        title = await page.evaluate("""
            () => {
                // Try to get title from various sources
                let title = document.title;
                if (title && title.includes(' - Google Drive')) {
                    title = title.replace(' - Google Drive', '');
                }
                if (!title || title.length === 0) {
                    title = 'gdrive_document';
                }
                return title;
            }
        """)
        return title.strip() or 'gdrive_document'

    async def capture_blob_images(self, page: Page) -> List[bytes]:
        """
        Capture all blob images (PDF pages) from Google Drive viewer.
        
        Returns list of image data (bytes) for each page.
        """
        logger.info("Capturing PDF pages as images (will scroll to load all pages)...")

        image_data_list: List[bytes] = []

        try:
            collected_urls: List[str] = []

            # Try to discover all blob URLs by scrolling the viewer.
            max_scroll_attempts = 8
            no_new_count = 0
            max_pages_cap = 200  # safety cap to avoid infinite loops

            logger.debug("Beginning scroll/discovery loop for blob images")
            for attempt in range(0, 1000):
                # Get current blob image URLs in DOM order
                urls = await page.evaluate("""
                    () => {
                        let imgs = document.getElementsByTagName('img');
                        let urls = [];
                        for (let i = 0; i < imgs.length; i++) {
                            let src = imgs[i].src || '';
                            if (src.startsWith('blob:https://drive.google.com/')) {
                                urls.push(src);
                            }
                        }
                        return urls;
                    }
                """)

                added = 0
                for u in urls:
                    if u not in collected_urls:
                        collected_urls.append(u)
                        added += 1

                logger.debug(f"Discovery attempt {attempt}: found {len(urls)} urls, total collected {len(collected_urls)} (added {added})")

                # If we've hit a reasonable page cap, stop
                if len(collected_urls) >= max_pages_cap:
                    logger.warning(f"Reached max page cap ({max_pages_cap}), stopping discovery")
                    break

                if added == 0:
                    no_new_count += 1
                else:
                    no_new_count = 0

                # If we've seen no new URLs for a few iterations, assume all loaded
                if no_new_count >= max_scroll_attempts:
                    logger.debug("No new URLs detected after multiple attempts, finishing discovery")
                    break

                # Scroll the last image into view to trigger lazy-loading
                try:
                    await page.evaluate("""
                        () => {
                            let imgs = document.getElementsByTagName('img');
                            if (imgs.length > 0) {
                                imgs[imgs.length - 1].scrollIntoView({behavior: 'auto', block: 'center'});
                            } else {
                                window.scrollBy(0, window.innerHeight);
                            }
                        }
                    """)
                except Exception:
                    # Fallback: page keyboard page down
                    try:
                        await page.keyboard.press('PageDown')
                    except Exception:
                        pass

                # Wait briefly for new pages to load
                await asyncio.sleep(1.0)

            logger.info(f"Found {len(collected_urls)} blob image URLs after discovery")

            # Now attempt to download each collected blob URL in order
            for idx, blob_url in enumerate(collected_urls, 1):
                try:
                    logger.info(f"Capturing page {idx}/{len(collected_urls)}...")

                    # Primary: fetch blob via page context
                    try:
                        image_buffer = await page.evaluate("""
                            async (url) => {{
                                try {{
                                    let response = await fetch(url, {{ headers: {{ 'Accept': 'image/*' }} }});
                                    if (!response.ok) throw new Error('HTTP ' + response.status);
                                    let blob = await response.blob();
                                    let arrayBuffer = await blob.arrayBuffer();
                                    return Array.from(new Uint8Array(arrayBuffer));
                                }} catch (e) {{
                                    console.error('Fetch error:', e);
                                    throw e;
                                }}
                            }}
                        """, blob_url)

                        image_data_list.append(bytes(image_buffer))
                        logger.debug(f"Successfully captured page {idx} via fetch")

                    except Exception as fetch_error:
                        logger.debug(f"Fetch failed for page {idx}, attempting canvas fallback: {fetch_error}")
                        # Fallback: render image to canvas and read base64
                        try:
                            img_b64 = await page.evaluate("""
                                (url) => {
                                    let imgs = document.getElementsByTagName('img');
                                    for (let img of imgs) {
                                        if (img.src === url) {
                                            let canvas = document.createElement('canvas');
                                            canvas.width = img.naturalWidth || img.width || 1000;
                                            canvas.height = img.naturalHeight || img.height || 1000;
                                            let ctx = canvas.getContext('2d');
                                            try {
                                                ctx.drawImage(img, 0, 0);
                                            } catch (e) {
                                                return null;
                                            }
                                            return canvas.toDataURL('image/png').split(',')[1];
                                        }
                                    }
                                    return null;
                                }
                            """, blob_url)

                            if img_b64:
                                image_buffer = base64.b64decode(img_b64)
                                image_data_list.append(image_buffer)
                                logger.debug(f"Successfully captured page {idx} via canvas fallback")
                            else:
                                logger.warning(f"Canvas fallback returned no data for page {idx}")

                        except Exception as canvas_err:
                            logger.warning(f"Canvas fallback failed for page {idx}: {canvas_err}")
                            continue

                except Exception as e:
                    logger.warning(f"Failed to capture page {idx}: {e}")
                    continue

            logger.info(f"Successfully captured {len(image_data_list)} pages")
            return image_data_list

        except Exception as e:
            logger.error(f"Error capturing blob images: {e}")
            return []

    async def compile_pdf(self, image_data_list: List[bytes], output_path: Path) -> bool:
        """
        Compile captured images into a single PDF.
        
        Args:
            image_data_list: List of image data (bytes)
            output_path: Path where PDF should be saved
            
        Returns:
            True if successful, False otherwise
        """
        if not image_data_list:
            logger.error("No images to compile")
            return False

        try:
            logger.info(f"Compiling {len(image_data_list)} images into PDF...")
            
            # Save images temporarily
            temp_image_paths = []
            for idx, img_data in enumerate(image_data_list):
                temp_path = self.temp_dir / f"page_{idx:04d}.png"
                with open(temp_path, 'wb') as f:
                    f.write(img_data)
                temp_image_paths.append(temp_path)

            # Convert images to RGB if necessary (for PNG with transparency)
            rgb_image_paths = []
            for img_path in temp_image_paths:
                try:
                    img = Image.open(img_path)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Convert to RGB
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        rgb_path = img_path.with_suffix('.jpg')
                        rgb_img.save(rgb_path, 'JPEG', quality=95)
                        rgb_image_paths.append(rgb_path)
                    else:
                        rgb_image_paths.append(img_path)
                except Exception as e:
                    logger.warning(f"Error converting image {img_path}: {e}")
                    rgb_image_paths.append(img_path)

            # Compile to PDF using img2pdf
            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert([str(p) for p in rgb_image_paths]))

            logger.info(f"PDF compiled successfully: {output_path}")
            
            # Clean up temp images
            for img_path in temp_image_paths + rgb_image_paths:
                if img_path.exists():
                    img_path.unlink()

            return True

        except Exception as e:
            logger.error(f"Error compiling PDF: {e}")
            return False

    async def extract_files_from_folder(self, folder_url: str, browser: Browser) -> Tuple[List[str], str]:
        """
        Extract all PDF file links from a Google Drive folder and get folder name.
        
        Args:
            folder_url: Google Drive folder URL
            browser: Playwright browser instance
            
        Returns:
            Tuple of (file_urls: List[str], folder_name: str)
        """
        file_urls = []
        folder_name = "gdrive_folder"
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(self.timeout)
            
            logger.info(f"Opening folder: {folder_url}")
            await page.goto(folder_url, wait_until='networkidle', timeout=self.timeout)
            
            # Wait for folder contents to load
            await asyncio.sleep(3)
            
            # Try to get folder name from page title
            try:
                page_title = await page.title()
                if page_title and page_title != 'Google Drive':
                    folder_name = page_title.replace(' - Google Drive', '').strip()
                    if folder_name:
                        folder_name = self.sanitize_filename(folder_name)
            except Exception:
                pass
            
            # Scroll and collect all file IDs from the folder view
            logger.info("Scanning folder for PDF files...")
            
            max_scroll_attempts = 15
            no_new_count = 0
            collected_file_ids = set()
            
            for attempt in range(100):
                try:
                    # Extract all file data-ids and names from the current view
                    # Google Drive uses data-id and data attributes in the table rows
                    file_data = await page.evaluate("""
                        () => {
                            let files = [];
                            
                            // Look for all rows with data-id attributes (files/folders in the list)
                            let rows = document.querySelectorAll('[data-id][role="row"], tr[data-id]');
                            for (let row of rows) {
                                let fileId = row.getAttribute('data-id');
                                if (!fileId) continue;
                                
                                // Try to find the name within the row
                                let nameElem = row.querySelector('[data-tooltip]') || row.querySelector('.a65Cwf') || row;
                                let name = '';
                                
                                if (nameElem && nameElem.getAttribute('data-tooltip')) {
                                    name = nameElem.getAttribute('data-tooltip');
                                } else {
                                    name = nameElem ? (nameElem.textContent || '') : '';
                                }
                                
                                // Only include PDFs (check by name ending with .pdf or containing PDF type indicator)
                                if (name.toLowerCase().includes('.pdf') || 
                                    row.textContent.toLowerCase().includes('pdf')) {
                                    files.push({
                                        id: fileId,
                                        name: name.trim()
                                    });
                                }
                            }
                            
                            return files;
                        }
                    """)
                    
                    added = 0
                    for file_data_item in file_data:
                        file_id = file_data_item.get('id')
                        if file_id and file_id not in collected_file_ids:
                            collected_file_ids.add(file_id)
                            added += 1
                            logger.debug(f"Found PDF: {file_data_item.get('name', 'Unknown')}")
                    
                    logger.debug(f"Folder scan attempt {attempt}: found {len(file_data)} files, total collected {len(collected_file_ids)} (added {added})")
                    
                    if added == 0:
                        no_new_count += 1
                    else:
                        no_new_count = 0
                    
                    # If no new links for several attempts, assume we've found all
                    if no_new_count >= max_scroll_attempts:
                        logger.debug("No new files detected, finishing folder scan")
                        break
                    
                    # Scroll down to load more files (Google Drive lazy-loads)
                    try:
                        await page.evaluate("() => window.scrollBy(0, window.innerHeight * 2)")
                    except Exception:
                        try:
                            await page.keyboard.press('PageDown')
                        except Exception:
                            pass
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.debug(f"Error during folder scan attempt {attempt}: {e}")
                    break
            
            # Convert file IDs to Google Drive file URLs
            for file_id in collected_file_ids:
                file_url = f"https://drive.google.com/file/d/{file_id}/view"
                file_urls.append(file_url)
            
            logger.info(f"Found {len(file_urls)} PDF files in folder '{folder_name}'")
            
            await page.close()
            return file_urls, folder_name
            
        except Exception as e:
            logger.error(f"Error extracting files from folder: {e}")
            try:
                await page.close()
            except Exception:
                pass
            return [], folder_name

    async def download_pdf(self, drive_url: str, browser: Browser, output_dir: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Download a single PDF from Google Drive.
        
        Args:
            drive_url: Google Drive PDF link
            browser: Playwright browser instance
            output_dir: Optional custom output directory (defaults to self.downloads_dir)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        page = None
        try:
            logger.info(f"Processing: {drive_url}")
            
            # Use provided output dir or default
            if output_dir is None:
                output_dir = self.downloads_dir
            else:
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Open new page
            page = await browser.new_page()
            page.set_default_timeout(self.timeout)

            # Navigate to the URL
            logger.info("Loading Google Drive PDF...")
            await page.goto(drive_url, wait_until='domcontentloaded')

            # Wait for PDF pages to load
            if not await self.wait_for_pdf_pages(page):
                return False, "Could not detect PDF pages"

            # Get document title
            title = await self.get_document_title(page)
            logger.info(f"Document title: {title}")

            # Capture images
            image_data_list = await self.capture_blob_images(page)
            if not image_data_list:
                return False, "Failed to capture PDF pages"

            # Compile PDF
            sanitized_title = self.sanitize_filename(title)
            pdf_filename = f"{sanitized_title}.pdf"
            output_path = output_dir / pdf_filename

            # Handle duplicate filenames
            counter = 1
            base_path = output_path
            while output_path.exists():
                pdf_filename = f"{sanitized_title}_{counter}.pdf"
                output_path = output_dir / pdf_filename
                counter += 1

            if not await self.compile_pdf(image_data_list, output_path):
                return False, "Failed to compile PDF"

            logger.info(f"[OK] Successfully saved: {output_path}")
            return True, f"Saved to {output_path}"

        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return False, f"Error: {str(e)}"

        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.debug(f"Error closing page: {e}")

    async def download_multiple(self, urls: List[str]) -> None:
        """Download PDFs from multiple URLs, including handling folder links."""
        if not urls:
            logger.error("No URLs provided")
            return

        results = {'success': 0, 'failed': 0, 'details': []}
        
        # Separate folder URLs and file URLs
        folder_urls = []
        file_urls = []
        
        for url in urls:
            if self.is_folder_url(url):
                folder_urls.append(url)
            elif self.is_file_url(url):
                file_urls.append(url)
            else:
                logger.warning(f"Unrecognized URL format, treating as file URL: {url}")
                file_urls.append(url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            
            try:
                # Process folders first
                if folder_urls:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Processing {len(folder_urls)} folder(s)")
                    logger.info(f"{'='*60}")
                    
                    for folder_idx, folder_url in enumerate(folder_urls, 1):
                        logger.info(f"\n{'='*60}")
                        logger.info(f"Folder {folder_idx}/{len(folder_urls)}")
                        logger.info(f"{'='*60}")
                        
                        # Extract files from folder
                        extracted_files, folder_name = await self.extract_files_from_folder(folder_url, browser)
                        
                        if not extracted_files:
                            logger.warning(f"No files found in folder: {folder_url}")
                            results['failed'] += 1
                            results['details'].append({'url': folder_url, 'status': 'FAILED', 'message': 'No files found in folder'})
                            continue
                        
                        # Create folder directory
                        folder_output_dir = self.downloads_dir / folder_name
                        folder_output_dir.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created local folder: {folder_output_dir}")
                        
                        # Download each file in the folder
                        for file_idx, file_url in enumerate(extracted_files, 1):
                            logger.info(f"\n  File {file_idx}/{len(extracted_files)}")
                            success, message = await self.download_pdf(file_url, browser, output_dir=folder_output_dir)
                            
                            if success:
                                results['success'] += 1
                            else:
                                results['failed'] += 1
                            
                            results['details'].append({'url': file_url, 'status': 'SUCCESS' if success else 'FAILED', 'message': message})
                            
                            # Small delay between downloads
                            await asyncio.sleep(1)
                        
                        # Small delay between folders
                        await asyncio.sleep(2)
                
                # Process individual files
                if file_urls:
                    total_files = len(folder_urls) + len(file_urls)
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Processing {len(file_urls)} file(s)")
                    logger.info(f"{'='*60}")
                    
                    for file_idx, file_url in enumerate(file_urls, 1):
                        logger.info(f"\n{'='*60}")
                        logger.info(f"File {file_idx}/{len(file_urls)}")
                        logger.info(f"{'='*60}")
                        
                        success, message = await self.download_pdf(file_url, browser)
                        
                        if success:
                            results['success'] += 1
                            results['details'].append({'url': file_url, 'status': 'SUCCESS', 'message': message})
                        else:
                            results['failed'] += 1
                            results['details'].append({'url': file_url, 'status': 'FAILED', 'message': message})

                        # Small delay between downloads
                        if file_idx < len(file_urls):
                            await asyncio.sleep(2)

            finally:
                await browser.close()

        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("DOWNLOAD SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total processed: {len(urls)}")
        logger.info(f"Successful: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"{'='*60}")
        
        for detail in results['details']:
            status_icon = "[OK]" if detail['status'] == 'SUCCESS' else "[FAIL]"
            logger.info(f"{status_icon} {detail['url']}")
            logger.info(f"  {detail['message']}")

    def load_urls_from_file(self, file_path: str) -> List[str]:
        """Load URLs from a text or CSV file."""
        urls = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Check if it's a CSV file
                if file_path.lower().endswith('.csv'):
                    reader = csv.reader(f)
                    for row in reader:
                        if row and row[0].strip().startswith('http'):
                            urls.append(row[0].strip())
                else:
                    # Treat as plain text file
                    for line in f:
                        line = line.strip()
                        if line and line.startswith('http'):
                            urls.append(line)

            logger.info(f"Loaded {len(urls)} URLs from {file_path}")
            return urls

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading URLs from file: {e}")
            return []


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Download PDFs from Google Drive links and folders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download a single PDF file
  python gdrive_pdf_downloader.py --link "https://drive.google.com/file/d/XXXXX/view"
  
  # Download a folder (creates local folder and downloads all PDFs inside)
  python gdrive_pdf_downloader.py --link "https://drive.google.com/drive/folders/XXXXX"
  
  # Download multiple files/folders from a list
  python gdrive_pdf_downloader.py --file links.txt
  python gdrive_pdf_downloader.py --file links.csv --headless
  
  # With timeout setting
  python gdrive_pdf_downloader.py --link "https://drive.google.com/file/d/XXXXX/view" --timeout 60
        """
    )

    parser.add_argument(
        '--link',
        type=str,
        help='Single Google Drive PDF link or folder link'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Text or CSV file containing Google Drive file and folder links (one per line)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=False,
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Page load timeout in seconds (default: 30)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.link and not args.file:
        parser.print_help()
        sys.exit(1)

    # Initialize downloader
    downloader = GoogleDrivePDFDownloader(headless=args.headless, timeout=args.timeout)

    # Prepare URLs
    urls = []
    if args.link:
        urls.append(args.link)
    if args.file:
        urls.extend(downloader.load_urls_from_file(args.file))

    if not urls:
        logger.error("No valid URLs to process")
        sys.exit(1)

    # Run download
    try:
        asyncio.run(downloader.download_multiple(urls))
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

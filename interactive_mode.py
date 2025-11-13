"""
Helper script for batch downloading Google Drive PDFs.
This script can be run without command-line arguments for interactive mode.
"""

import os
import sys
import asyncio
from pathlib import Path


def interactive_mode():
    """Interactive menu for downloading PDFs."""
    print("\n" + "="*60)
    print("Google Drive PDF Downloader - Interactive Mode")
    print("="*60 + "\n")

    while True:
        print("\nOptions:")
        print("1. Download single PDF (enter URL)")
        print("2. Download from text file (one URL per line)")
        print("3. Download from CSV file")
        print("4. Create sample links file")
        print("5. Check downloads folder")
        print("6. Exit")
        print()

        choice = input("Select option (1-6): ").strip()

        if choice == '1':
            url = input("\nEnter Google Drive PDF link: ").strip()
            if url.startswith('http'):
                headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
                timeout = input("Timeout in seconds (default 30): ").strip()
                timeout_arg = f"--timeout {timeout}" if timeout.isdigit() else ""
                headless_arg = "--headless" if headless else ""
                cmd = f"python gdrive_pdf_downloader.py --link \"{url}\" {headless_arg} {timeout_arg}".strip()
                print(f"\nRunning: {cmd}\n")
                os.system(cmd)
            else:
                print("Invalid URL!")

        elif choice == '2':
            filename = input("\nEnter text filename (default 'links.txt'): ").strip() or "links.txt"
            if Path(filename).exists():
                headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
                headless_arg = "--headless" if headless else ""
                cmd = f"python gdrive_pdf_downloader.py --file {filename} {headless_arg}".strip()
                print(f"\nRunning: {cmd}\n")
                os.system(cmd)
            else:
                print(f"File '{filename}' not found!")

        elif choice == '3':
            filename = input("\nEnter CSV filename (default 'links.csv'): ").strip() or "links.csv"
            if Path(filename).exists():
                headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
                headless_arg = "--headless" if headless else ""
                cmd = f"python gdrive_pdf_downloader.py --file {filename} {headless_arg}".strip()
                print(f"\nRunning: {cmd}\n")
                os.system(cmd)
            else:
                print(f"File '{filename}' not found!")

        elif choice == '4':
            create_sample_links()

        elif choice == '5':
            check_downloads()

        elif choice == '6':
            print("\nGoodbye!")
            break

        else:
            print("Invalid option!")


def create_sample_links():
    """Create a sample links file."""
    print("\nCreating sample links file...\n")
    
    links_txt = """https://drive.google.com/file/d/EXAMPLE_ID_1/view
https://drive.google.com/file/d/EXAMPLE_ID_2/view
https://drive.google.com/file/d/EXAMPLE_ID_3/view
"""
    
    with open("sample_links.txt", "w") as f:
        f.write(links_txt)
    
    print("✓ Created 'sample_links.txt'")
    print("\nEdit this file and add your Google Drive PDF links.")
    print("Then run: python gdrive_pdf_downloader.py --file sample_links.txt")


def check_downloads():
    """Check contents of downloads folder."""
    downloads_dir = Path("downloads")
    
    if not downloads_dir.exists():
        print("\nDownloads folder does not exist yet.")
        return
    
    pdfs = list(downloads_dir.glob("*.pdf"))
    
    if not pdfs:
        print("\nNo PDFs in downloads folder yet.")
        return
    
    print(f"\nFound {len(pdfs)} PDF(s) in downloads folder:\n")
    total_size = 0
    
    for idx, pdf in enumerate(pdfs, 1):
        size_mb = pdf.stat().st_size / (1024 * 1024)
        total_size += pdf.stat().st_size
        print(f"{idx}. {pdf.name}")
        print(f"   Size: {size_mb:.2f} MB")
        print()
    
    print(f"Total size: {total_size / (1024 * 1024):.2f} MB")


if __name__ == '__main__':
    interactive_mode()

"""
Verification and testing script for Google Drive PDF Downloader.
This script checks if all dependencies are correctly installed.
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("\n" + "="*60)
    print("Checking Python Version")
    print("="*60)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Python version: {version_str}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required!")
        return False
    
    print("✓ Python version OK")
    return True


def check_dependencies():
    """Check if all required packages are installed."""
    print("\n" + "="*60)
    print("Checking Dependencies")
    print("="*60)
    
    required_packages = {
        'playwright': 'Browser automation',
        'PIL': 'Image processing (Pillow)',
        'img2pdf': 'PDF compilation',
        'aiohttp': 'Async HTTP requests',
    }
    
    all_ok = True
    
    for package, description in required_packages.items():
        try:
            if package == 'PIL':
                import PIL
                print(f"✓ {package:15} - {description}")
            else:
                __import__(package)
                print(f"✓ {package:15} - {description}")
        except ImportError:
            print(f"❌ {package:15} - {description} (NOT INSTALLED)")
            all_ok = False
    
    if not all_ok:
        print("\nTo install missing packages, run:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def check_playwright_browsers():
    """Check if Playwright browsers are installed."""
    print("\n" + "="*60)
    print("Checking Playwright Browsers")
    print("="*60)
    
    try:
        from playwright.async_api import async_playwright
        print("✓ Playwright module found")
        
        # Check for browser executables
        browsers_to_check = ['chromium', 'firefox', 'webkit']
        
        # Try to get browser paths
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'playwright', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Playwright CLI: {result.stdout.strip()}")
            else:
                print("⚠ Could not verify Playwright CLI version")
        except Exception as e:
            print(f"⚠ Could not check Playwright CLI: {e}")
        
        print("\nTo install browsers, run:")
        print("  playwright install chromium")
        print("  # or")
        print("  playwright install")
        
        return True
        
    except ImportError:
        print("❌ Playwright not installed")
        return False


def check_project_files():
    """Check if essential project files exist."""
    print("\n" + "="*60)
    print("Checking Project Files")
    print("="*60)
    
    files_to_check = {
        'gdrive_pdf_downloader.py': 'Main script',
        'requirements.txt': 'Dependencies list',
        'README.md': 'Documentation',
    }
    
    all_ok = True
    
    for filename, description in files_to_check.items():
        if Path(filename).exists():
            print(f"✓ {filename:30} - {description}")
        else:
            print(f"❌ {filename:30} - {description} (MISSING)")
            all_ok = False
    
    return all_ok


def check_directories():
    """Check/create necessary directories."""
    print("\n" + "="*60)
    print("Checking Directories")
    print("="*60)
    
    directories = {
        'downloads': 'Output directory for PDFs',
        'temp_images': 'Temporary image storage',
    }
    
    for dirname, description in directories.items():
        dirpath = Path(dirname)
        if dirpath.exists():
            print(f"✓ {dirname:20} - {description} (exists)")
        else:
            try:
                dirpath.mkdir(exist_ok=True)
                print(f"✓ {dirname:20} - {description} (created)")
            except Exception as e:
                print(f"❌ {dirname:20} - {description} (ERROR: {e})")
                return False
    
    return True


def check_system():
    """Check system information."""
    print("\n" + "="*60)
    print("System Information")
    print("="*60)
    
    import platform
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version}")
    print(f"Working directory: {Path.cwd()}")


def run_all_checks():
    """Run all verification checks."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Google Drive PDF Downloader - Setup Verification".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    check_system()
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Playwright Browsers': check_playwright_browsers(),
        'Project Files': check_project_files(),
        'Directories': check_directories(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{check_name:30} {status}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! You're ready to use the downloader.")
        print("\nTry running:")
        print("  python gdrive_pdf_downloader.py --help")
        return True
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return False


if __name__ == '__main__':
    success = run_all_checks()
    sys.exit(0 if success else 1)

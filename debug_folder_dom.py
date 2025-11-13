"""
Debug script to inspect the DOM structure of a Google Drive folder
and find the correct selectors for PDF files.
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_folder_dom():
    """Inspect the DOM structure of a Google Drive folder."""
    
    folder_url = "https://drive.google.com/drive/folders/18t4PrOWpINDDOeBc4clbVXsqDh7tYJ8E"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible so you can see
        page = await browser.new_page()
        
        print("Opening folder...")
        await page.goto(folder_url, wait_until='networkidle', timeout=60000)
        
        print("Waiting for folder content to load...")
        await asyncio.sleep(5)
        
        # Try multiple selector approaches
        selectors_to_test = [
            # Original approach
            'a[href*="/file/d/"]',
            # Alternative: data attributes
            '[data-id][data-name]',
            # Links in list
            'a[href*="drive.google.com"]',
            # Divs with file info
            '[role="button"][data-id]',
            # All links on page
            'a',
        ]
        
        print("\n" + "="*60)
        print("Testing different selectors:")
        print("="*60)
        
        for selector in selectors_to_test:
            try:
                elements = await page.query_selector_all(selector)
                print(f"\nSelector: {selector}")
                print(f"  Found: {len(elements)} elements")
                
                if len(elements) > 0 and len(elements) <= 10:
                    for i, elem in enumerate(elements[:5]):
                        href = await elem.get_attribute('href')
                        text = await elem.text_content()
                        data_id = await elem.get_attribute('data-id')
                        data_name = await elem.get_attribute('data-name')
                        
                        print(f"    [{i}] href={href}, text={text[:50] if text else 'N/A'}, data-id={data_id}, data-name={data_name}")
            except Exception as e:
                print(f"\nSelector: {selector} - Error: {e}")
        
        # Get full HTML of first few items to understand structure
        print("\n" + "="*60)
        print("Full HTML structure of first item:")
        print("="*60)
        
        try:
            # Try to get the inner HTML of the folder contents area
            html = await page.evaluate("""
                () => {
                    // Try to find folder content container
                    let container = document.querySelector('[role="main"]') || 
                                   document.querySelector('[role="region"]') ||
                                   document.querySelector('.a-b-d-b-a');
                    
                    if (container) {
                        // Get first few items
                        let items = container.querySelectorAll('[role="button"], a, [data-id]');
                        let result = [];
                        for (let i = 0; i < Math.min(5, items.length); i++) {
                            result.push({
                                html: items[i].outerHTML,
                                tagName: items[i].tagName,
                                className: items[i].className,
                                attrs: {
                                    href: items[i].getAttribute('href'),
                                    'data-id': items[i].getAttribute('data-id'),
                                    'data-name': items[i].getAttribute('data-name'),
                                    'data-type': items[i].getAttribute('data-type'),
                                    role: items[i].getAttribute('role'),
                                    tabindex: items[i].getAttribute('tabindex'),
                                }
                            });
                        }
                        return result;
                    }
                    return null;
                }
            """)
            
            if html:
                for i, item in enumerate(html):
                    print(f"\nItem {i}:")
                    print(f"  Tag: {item['tagName']}")
                    print(f"  Class: {item['className']}")
                    print(f"  Attributes: {item['attrs']}")
                    print(f"  HTML (first 200 chars): {item['html'][:200]}")
        except Exception as e:
            print(f"Error extracting HTML: {e}")
        
        # Get all links with PDF in name
        print("\n" + "="*60)
        print("All links containing 'pdf' or with /file/d/ in href:")
        print("="*60)
        
        try:
            pdf_links = await page.evaluate("""
                () => {
                    let links = [];
                    let anchors = document.querySelectorAll('a');
                    for (let a of anchors) {
                        let href = a.href || '';
                        let text = a.textContent || '';
                        if (href.includes('/file/d/') || text.toLowerCase().includes('pdf')) {
                            links.push({
                                href: href,
                                text: text.substring(0, 100)
                            });
                        }
                    }
                    return links;
                }
            """)
            
            print(f"Found {len(pdf_links)} PDF links")
            for link in pdf_links[:10]:
                print(f"  href: {link['href']}")
                print(f"  text: {link['text']}")
                print()
        except Exception as e:
            print(f"Error: {e}")
        
        # Try to list all visible text in the folder
        print("\n" + "="*60)
        print("All visible item names in folder:")
        print("="*60)
        
        try:
            items = await page.evaluate("""
                () => {
                    // Look for file/folder names in various possible locations
                    let items = [];
                    
                    // Method 1: Look for elements with data attributes
                    let elements = document.querySelectorAll('[data-id]');
                    for (let el of elements) {
                        let name = el.getAttribute('data-name') || el.textContent || '';
                        items.push({source: 'data-id', name: name.substring(0, 100)});
                    }
                    
                    // Method 2: Look for buttons with file names
                    let buttons = document.querySelectorAll('[role="button"]');
                    for (let btn of buttons) {
                        let text = btn.textContent || '';
                        if (text.length > 0 && text.length < 200) {
                            items.push({source: 'button', name: text.substring(0, 100)});
                        }
                    }
                    
                    return items;
                }
            """)
            
            print(f"Found {len(items)} items")
            seen = set()
            for item in items[:20]:
                if item['name'] not in seen:
                    print(f"  [{item['source']}] {item['name']}")
                    seen.add(item['name'])
        except Exception as e:
            print(f"Error: {e}")
        
        await page.close()
        await browser.close()


if __name__ == '__main__':
    asyncio.run(debug_folder_dom())

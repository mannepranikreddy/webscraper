import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_page(self):
        """Fetch the webpage content"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching page: {e}")
            return False
    
    def search_by_tag(self, tag_name, limit=None):
        """Search for all elements with a specific HTML tag"""
        if not self.soup:
            return []
        elements = self.soup.find_all(tag_name, limit=limit)
        return [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
    
    def search_by_class(self, class_name, limit=None):
        """Search for elements with a specific class name"""
        if not self.soup:
            return []
        elements = self.soup.find_all(class_=class_name, limit=limit)
        return [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
    
    def search_by_id(self, id_name):
        """Search for an element with a specific ID"""
        if not self.soup:
            return None
        element = self.soup.find(id=id_name)
        return element.get_text(strip=True) if element else None
    
    def search_by_text(self, search_text, exact=False):
        """Search for elements containing specific text"""
        if not self.soup:
            return []
        if exact:
            elements = self.soup.find_all(string=search_text)
        else:
            elements = self.soup.find_all(string=re.compile(search_text, re.IGNORECASE))
        return [elem.strip() for elem in elements if elem.strip()]
    
    def search_links(self, keyword=None):
        """Extract all links, optionally filtered by keyword"""
        if not self.soup:
            return []
        links = self.soup.find_all('a', href=True)
        if keyword:
            return [link['href'] for link in links if keyword.lower() in link.get_text().lower()]
        return [link['href'] for link in links]
    
    def search_images(self, alt_keyword=None):
        """Extract all image URLs, optionally filtered by alt text"""
        if not self.soup:
            return []
        images = self.soup.find_all('img', src=True)
        if alt_keyword:
            return [img['src'] for img in images if alt_keyword.lower() in img.get('alt', '').lower()]
        return [img['src'] for img in images]
    
    def custom_search(self, tag=None, attrs=None, text=None):
        """Perform a custom search with multiple criteria"""
        if not self.soup:
            return []
        elements = self.soup.find_all(tag, attrs=attrs, string=text)
        return [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]


class DocumentExporter:
    """Handles exporting results to text and HTML files"""
    
    @staticmethod
    def export_to_txt(results, search_info, filename):
        """Export results to a text file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write("WEB SCRAPING RESULTS REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                # Write metadata
                f.write(f"URL:          {search_info['url']}\n")
                f.write(f"Search Type:  {search_info['search_type']}\n")
                f.write(f"Search Query: {search_info['query']}\n")
                f.write(f"Date:         {search_info['date']}\n")
                f.write(f"Total Results: {search_info['count']}\n")
                f.write("\n" + "-" * 80 + "\n\n")
                
                # Write results
                f.write("RESULTS:\n")
                f.write("-" * 80 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"{i}. {result}\n\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("End of Report\n")
                f.write("=" * 80 + "\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating text file: {e}")
            return False
    
    @staticmethod
    def export_to_html(results, search_info, filename):
        """Export results to an HTML file"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraping Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2C3E50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .metadata {{
            background: #f8f9fa;
            padding: 30px 40px;
            border-bottom: 3px solid #e9ecef;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .metadata-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        .metadata-label {{
            font-weight: bold;
            color: #2C3E50;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .metadata-value {{
            color: #555;
            font-size: 1.1em;
            word-wrap: break-word;
        }}
        
        .results {{
            padding: 40px;
        }}
        
        .results h2 {{
            color: #2C3E50;
            margin-bottom: 30px;
            font-size: 2em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .result-item {{
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
        }}
        
        .result-item:hover {{
            background: #e9ecef;
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .result-number {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            margin-right: 15px;
            font-size: 0.9em;
        }}
        
        .result-content {{
            display: inline;
            color: #333;
            line-height: 1.6;
        }}
        
        .footer {{
            background: #2C3E50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px;
            color: #999;
            font-size: 1.2em;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            .result-item {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Web Scraping Results</h1>
            <p>Professional Data Extraction Report</p>
        </div>
        
        <div class="metadata">
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="metadata-label">🔗 URL</div>
                    <div class="metadata-value">{search_info['url']}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">🔍 Search Type</div>
                    <div class="metadata-value">{search_info['search_type']}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">📝 Search Query</div>
                    <div class="metadata-value">{search_info['query']}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">📅 Date</div>
                    <div class="metadata-value">{search_info['date']}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">📊 Total Results</div>
                    <div class="metadata-value">{search_info['count']}</div>
                </div>
            </div>
        </div>
        
        <div class="results">
            <h2>Results</h2>
"""
            
            if results:
                for i, result in enumerate(results, 1):
                    # Escape HTML characters
                    result_escaped = str(result).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    html_content += f"""
            <div class="result-item">
                <span class="result-number">{i}</span>
                <span class="result-content">{result_escaped}</span>
            </div>
"""
            else:
                html_content += """
            <div class="no-results">
                <p>No results found</p>
            </div>
"""
            
            html_content += """
        </div>
        
        <div class="footer">
            <p>Generated by Advanced Web Scraper Tool</p>
        </div>
    </div>
</body>
</html>
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating HTML file: {e}")
            return False


def print_header():
    """Print a nice header for the application"""
    print("\n" + "=" * 70)
    print("║" + " " * 68 + "║")
    print("║" + "          🌐 ADVANCED WEB SCRAPER TOOL 🌐          ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("=" * 70)
    print("║  Extract data from any website with ease!                       ║")
    print("║  Export your results to TXT or HTML documents                   ║")
    print("=" * 70 + "\n")


def print_menu():
    """Print the main menu with improved formatting"""
    print("\n" + "┌" + "─" * 68 + "┐")
    print("│" + " WHAT WOULD YOU LIKE TO SEARCH FOR? ".center(68) + "│")
    print("├" + "─" * 68 + "┤")
    print("│  1. 🏷️  Search by HTML tag (e.g., h1, p, div)                   │")
    print("│  2. 🎨 Search by class name                                     │")
    print("│  3. 🆔 Search by ID                                             │")
    print("│  4. 📝 Search by text content                                   │")
    print("│  5. 🔗 Extract all links                                        │")
    print("│  6. 🖼️  Extract all images                                      │")
    print("│  7. ⚙️  Custom search                                           │")
    print("│  8. 🚪 Exit                                                     │")
    print("└" + "─" * 68 + "┘")


def display_results(results, search_type, query):
    """Display results with improved formatting"""
    print("\n" + "┌" + "─" * 68 + "┐")
    print("│" + f" 📊 RESULTS FOUND: {len(results)} ".center(68) + "│")
    print("├" + "─" * 68 + "┤")
    
    if results:
        # Show first 50 results
        display_count = min(50, len(results))
        for i, result in enumerate(results[:display_count], 1):
            # Truncate long results
            result_str = str(result)
            if len(result_str) > 100:
                result_str = result_str[:97] + "..."
            print(f"│ {i:2d}. {result_str:<63} │")
        
        if len(results) > 50:
            print("├" + "─" * 68 + "┤")
            print(f"│ ... and {len(results) - 50} more results (export to see all)          │")
    else:
        print("│" + " No results found. Try a different search. ".center(68) + "│")
    
    print("└" + "─" * 68 + "┘")


def save_results(results, search_info):
    """Handle saving results to TXT or HTML"""
    if not results:
        print("\n⚠️  No results to save!")
        return
    
    print("\n" + "┌" + "─" * 68 + "┐")
    print("│" + " EXPORT OPTIONS ".center(68) + "│")
    print("├" + "─" * 68 + "┤")
    print("│  1. 📄 Export to Text File (.txt)                              │")
    print("│  2. 🌐 Export to HTML File (.html)                             │")
    print("│  3. 📋 Export to both formats                                   │")
    print("│  4. ❌ Skip export                                              │")
    print("└" + "─" * 68 + "┘")
    
    choice = input("\n👉 Choose export format (1-4): ").strip()
    
    if choice == '4':
        print("✅ Skipping export.")
        return
    
    # Get base filename
    default_name = f"scraping_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    filename = input(f"\n📝 Enter filename (default: {default_name}): ").strip()
    filename = filename if filename else default_name
    
    # Remove extension if user added it
    filename = filename.replace('.txt', '').replace('.html', '')
    
    success = False
    
    if choice in ['1', '3']:
        txt_filename = f"{filename}.txt"
        print(f"\n⏳ Creating text file: {txt_filename}...")
        if DocumentExporter.export_to_txt(results, search_info, txt_filename):
            print(f"✅ Text file saved successfully: {txt_filename}")
            success = True
        else:
            print(f"❌ Failed to create text file")
    
    if choice in ['2', '3']:
        html_filename = f"{filename}.html"
        print(f"\n⏳ Creating HTML file: {html_filename}...")
        if DocumentExporter.export_to_html(results, search_info, html_filename):
            print(f"✅ HTML file saved successfully: {html_filename}")
            print(f"💡 Tip: Open {html_filename} in your web browser to view the formatted report!")
            success = True
        else:
            print(f"❌ Failed to create HTML file")
    
    if not success and choice not in ['1', '2', '3']:
        print("❌ Invalid choice. Export cancelled.")


def main():
    print_header()
    
    # Get URL from user
    print("🌐 Let's start by entering the website you want to scrape.")
    url = input("\n👉 Enter the website URL: ").strip()
    
    # Create scraper instance
    scraper = WebScraper(url)
    
    # Fetch the page
    print("\n⏳ Fetching page...")
    if not scraper.fetch_page():
        print("❌ Failed to fetch the page. Please check the URL and try again.")
        return
    
    print("✅ Page fetched successfully!\n")
    
    # Main loop
    while True:
        print_menu()
        choice = input("\n👉 Enter your choice (1-8): ").strip()
        
        results = []
        search_type = ""
        query = ""
        
        if choice == '1':
            tag = input("\n🏷️  Enter HTML tag name (e.g., h1, p, a): ").strip()
            limit = input("🔢 Limit results? (press Enter for all, or enter a number): ").strip()
            limit = int(limit) if limit.isdigit() else None
            
            print("\n⏳ Searching...")
            results = scraper.search_by_tag(tag, limit)
            search_type = "HTML Tag"
            query = f"{tag}" + (f" (limit: {limit})" if limit else "")
            
        elif choice == '2':
            class_name = input("\n🎨 Enter class name: ").strip()
            limit = input("🔢 Limit results? (press Enter for all, or enter a number): ").strip()
            limit = int(limit) if limit.isdigit() else None
            
            print("\n⏳ Searching...")
            results = scraper.search_by_class(class_name, limit)
            search_type = "Class Name"
            query = f"{class_name}" + (f" (limit: {limit})" if limit else "")
            
        elif choice == '3':
            id_name = input("\n🆔 Enter ID name: ").strip()
            
            print("\n⏳ Searching...")
            result = scraper.search_by_id(id_name)
            results = [result] if result else []
            search_type = "ID"
            query = id_name
            
        elif choice == '4':
            text = input("\n📝 Enter text to search for: ").strip()
            exact = input("🎯 Exact match? (y/n): ").strip().lower() == 'y'
            
            print("\n⏳ Searching...")
            results = scraper.search_by_text(text, exact)
            search_type = "Text Content"
            query = f"{text} ({'exact' if exact else 'partial'} match)"
            
        elif choice == '5':
            keyword = input("\n🔗 Filter links by keyword (press Enter for all): ").strip()
            keyword = keyword if keyword else None
            
            print("\n⏳ Extracting links...")
            results = scraper.search_links(keyword)
            search_type = "Links"
            query = f"keyword: {keyword}" if keyword else "all links"
            
        elif choice == '6':
            keyword = input("\n🖼️  Filter images by alt text (press Enter for all): ").strip()
            keyword = keyword if keyword else None
            
            print("\n⏳ Extracting images...")
            results = scraper.search_images(keyword)
            search_type = "Images"
            query = f"alt text: {keyword}" if keyword else "all images"
            
        elif choice == '7':
            tag = input("\n⚙️  Enter tag (press Enter to skip): ").strip() or None
            attr_key = input("🔑 Enter attribute name (press Enter to skip): ").strip()
            attr_value = input("💎 Enter attribute value (press Enter to skip): ").strip()
            attrs = {attr_key: attr_value} if attr_key and attr_value else None
            
            print("\n⏳ Searching...")
            results = scraper.custom_search(tag, attrs)
            search_type = "Custom Search"
            query = f"tag: {tag}, attrs: {attrs}"
            
        elif choice == '8':
            print("\n" + "=" * 70)
            print("👋 Thank you for using Advanced Web Scraper!")
            print("=" * 70 + "\n")
            break
            
        else:
            print("\n❌ Invalid choice. Please try again.")
            continue
        
        # Display results
        display_results(results, search_type, query)
        
        # Create search info for export
        search_info = {
            'url': url,
            'search_type': search_type,
            'query': query,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'count': len(results)
        }
        
        # Ask to save
        save_results(results, search_info)


if __name__ == "__main__":
    main()
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import argparse
import sys # sys is included for cleaner exit if needed, though argparse handles most errors

# --- Configuration ---

# A broad regex for URLs, adjusted for potential JavaScript formats (e.g., in strings)
# Looks for: http:// or https://, or // followed by non-whitespace characters, 
# or a simple path-like structure (e.g., /api/data) inside quotes.
URL_REGEX = re.compile(
    r"""
    ['"] (?:https?://|//) [^\s'"]+ ['"] | # Matches 'http://...' or '//...' inside quotes
    ['"] / [^\s'"]+ ['"]                  # Matches '/path/...' inside quotes (relative paths)
    """, 
    re.VERBOSE
)

# --- Core Functions ---

def get_full_url(base_url, relative_url):
    """Joins a relative URL to the base URL, stripping quotes if present."""
    # Strip surrounding quotes from the matched URL segment
    if relative_url.startswith(("'", '"')) and relative_url.endswith(("'", '"')):
        relative_url = relative_url[1:-1]
        
    # Ensure the full URL is properly constructed
    return urljoin(base_url, relative_url)

def extract_js_links(js_content, base_url):
    """
    Uses regex to find potential URLs in the JavaScript content.
    Returns a set of unique, absolute URLs.
    """
    found_urls = set()
    matches = URL_REGEX.findall(js_content)
    
    for match in matches:
        # Resolve the URL to an absolute URL
        absolute_url = get_full_url(base_url, match)
        
        # Simple check to filter out non-HTTP/HTTPS schemes (e.g., mailto:, javascript:void(0))
        parsed = urlparse(absolute_url)
        if parsed.scheme in ('http', 'https') and absolute_url not in found_urls:
            found_urls.add(absolute_url)
            
    return found_urls

def fetch_js_content(js_url):
    """Fetches the content of a single JavaScript file."""
    try:
        print(f"  -> Fetching JS: {js_url}")
        # Add a common User-Agent to avoid being blocked by simple checks
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; ReconBot/1.0; +https://your.security.site)'}
        response = requests.get(js_url, timeout=10, headers=headers)
        
        # Check for successful response
        response.raise_for_status()
        
        # Return content only if it looks like JavaScript/text
        content_type = response.headers.get('Content-Type', '').lower()
        if 'javascript' in content_type or 'text/plain' in content_type or len(response.text) > 0:
            return response.text
        return None
    except requests.RequestException as e:
        # Log error but continue
        print(f"  -> Error fetching {js_url}: {e}")
        return None

def find_all_js_files(target_url):
    """
    Fetches the main page, finds all external JS file URLs, 
    and returns a set of unique absolute JS URLs.
    """
    print(f"🔍 Starting scrape on: {target_url}")
    js_urls = set()
    
    try:
        # Add a common User-Agent for the initial request
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; ReconBot/1.0; +https://your.security.site)'}
        response = requests.get(target_url, timeout=10, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
    except requests.RequestException as e:
        print(f"❌ Error fetching main page {target_url}: {e}")
        return js_urls

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all <script> tags
    for script in soup.find_all('script', src=True): # Only search for tags with 'src'
        relative_url = script['src']
        absolute_url = urljoin(target_url, relative_url)
        
        parsed = urlparse(absolute_url)
        # Ensure it is a valid HTTP/HTTPS URL
        if parsed.scheme in ('http', 'https'):
            js_urls.add(absolute_url)

    print(f"✅ Found {len(js_urls)} unique external JS files.")
    return js_urls

# --- Main Execution ---

def main():
    """Main function to orchestrate the scraping process."""
    parser = argparse.ArgumentParser(
        description="Ethical Security Tool: Scrapes a target URL, extracts all external JavaScript files, and searches their content for potential hidden URLs and API endpoints."
    )
    
    # Define the positional argument for the target URL
    parser.add_argument(
        'target_url', 
        help='The full URL of the website to scrape (e.g., https://example.com).'
    )
    
    args = parser.parse_args()
    
    # Assign the command-line argument value to the variable
    TARGET_URL = args.target_url
    
    # Validation check: Ensure the URL starts with a scheme
    if not TARGET_URL.startswith(('http://', 'https://')):
        print(f"❌ Error: Target URL must include the scheme (e.g., https://{TARGET_URL})")
        sys.exit(1)

    js_files = find_all_js_files(TARGET_URL)
    all_extracted_links = set()
    
    print("\n--- Extracting Links from JS Files ---")
    
    # Process each JavaScript file
    for js_url in js_files:
        # Pass the TARGET_URL as base_url to ensure proper resolution of relative paths
        js_content = fetch_js_content(js_url)
        
        if js_content:
            # Use the JS file's URL as the base for resolving relative paths within it
            links_in_js = extract_js_links(js_content, js_url) 
            if links_in_js:
                print(f"  -> Found {len(links_in_js)} links in {js_url}")
                all_extracted_links.update(links_in_js)
            else:
                print(f"  -> No links found in {js_url}")
            
    print("\n--- Final List of All Extracted Links ---")
    if all_extracted_links:
        for link in sorted(list(all_extracted_links)):
            print(link)
        print(f"\nTotal unique links found: {len(all_extracted_links)}")
    else:
        print("No links were extracted from any JavaScript files.")

if __name__ == "__main__":
    main()

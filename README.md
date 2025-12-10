### URList3r.py
The URList3r.py is a Python script designed for a crucial reconnaissance step of identifying hidden URLs, API endpoints, and configuration paths often hardcoded within external JS files.

#### Description

The URList3r.py is a Python script designed for ethical security researchers and penetration testers. It automates the crucial reconnaissance step of identifying hidden URLs, API endpoints, and configuration paths often hardcoded within external JavaScript files.

By scraping a target webpage for all linked .js files and applying powerful regular expressions to their content, this tool helps uncover potential attack surfaces that might be missed by simple link scraping, providing valuable data for vulnerability analysis.

#### 🛡️ Ethical Hacking & Responsible Disclosure

This tool is created for legal, authorized, and ethical security testing only.

- You must have explicit, written permission from the asset owner or be operating within the defined scope of an authorized bug bounty program before running this script against any external target.
- Do not use this tool for unauthorized, malicious, or illegal activity.
- The developer assumes no liability and encourages responsible disclosure of any vulnerabilities found.

#### Features

- Deep Link Discovery: Finds URLs and relative paths hidden deep within JavaScript code, including those defined inside variable strings.
- Automatic Resolution: Uses urllib.parse.urljoin to automatically resolve relative paths (e.g., /api/v1/user) into absolute URLs based on the source file's location.
- Robust Parsing: Leverages BeautifulSoup to reliably find all external <script src="..."> tags.
- Flexible Input: Uses argparse to accept the target URL directly as a command-line argument.

#### Requirements
Prerequisites

- Python 3.6+.
- requests
- beautifulsoup4
  
#### Setup

1. Clone the repository:
```
git clone https://github.com/YourUsername/URList3r.py.git
cd URList3r.py
```

2. Install the required libraries:

```
pip install -r requirements.txt
```

#### Usage

The tool requires a single positional argument: the full URL of the target website, including the scheme (http:// or https://).

```
python URList3r.py https://target.com/
```

Example with Specific Path

```
python URList3r.py https://staging.target.com/app/dashboard
```

Output Example
```
🔍 Starting scrape on: https://target.com/
✅ Found 5 unique external JS files.

--- Extracting Links from JS Files ---
-> Fetching JS: https://target.com/assets/core.js
-> Found 12 links in https://target.com/assets/core.js
-> Fetching JS: https://target.com/modules/user.js
-> Found 3 links in https://target.com/modules/user.js

  
--- Final List of All Extracted Links ---
https://api.target.com/v2/login
https://target.com/assets/images/logo.png
https://target.com/api/admin/healthcheck
https://target.com/dashboard/settings

Total unique links found: 45
```

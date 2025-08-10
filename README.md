# EZDorker - Advanced Search Engine Dorking Tool

EZDorker is a powerful Python tool for automated passive reconnaissance using advanced search engine dorking techniques across multiple search engines.

Developed by ***Luca Armiraglio***

## Features

- **Multi-engine support**: Google, Bing, DuckDuckGo, Yahoo, Baidu, Yandex
- **Comprehensive dork categories**:
  - Filetype searching (PDF, DOC, XLS, etc.)
  - Login pages and admin portals
  - Configuration files
  - Vulnerability indicators
  - Subdomain discovery
- **Multiple output formats**: JSON, CSV, plain text
- **Advanced options**:
  - Selective engine targeting
  - Category filtering
  - Browser automation
  - Verbose output mode
- **Configurable parameters**:
  - Request delays
  - Timeouts
  - Max results per query

## Installation

### Prerequisites

- Python 3.6+
- pip package manager

### Quick Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ezdorker.git
   cd ezdorker
   ```

2. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ``` 
Or install them manually:   
  ```bash
    pip install requests beautifulsoup4
  ```

### Usage
```bash
python ezdorker.py example.com
```

### Advanced Options
Option	Description	Example
-o OUTPUT	Save results to file (supports .json, .csv, .txt)	-o results.json
-e ENGINES	Search engines to use (space-separated)	-e google bing
-c CATEGORIES	Dork categories to use (space-separated)	-c filetype login
-b	Open dorks in browser	-b
-v	Verbose output mode	-v

### Example:
```bash
python ezdorker.py example.com -o results.csv -e google bing duckduckgo -c filetype config -v
```

EZDorker was developed for educational and ethical security testing purposes only.


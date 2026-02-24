# Valid Person Finder 

A powerful search tool that discovers key personnel (CEO, Founder, Directors) at companies by searching public sources. The system uses intelligent query generation and multi-source validation to provide accurate results.

## Features

- **Smart Query Generation** - Automatically generates search queries with designation aliases (CEO, Chief Executive Officer, Founder, Co-Founder, etc.)
- **Multi-Source Search** - Searches across public websites using DuckDuckGo API
- **Intelligent Name Extraction** - Pattern matching and NLP-inspired techniques to extract person names
- **Confidence Scoring** - Cross-validates results from multiple sources
- **Clean Web Interface** - Simple, responsive UI for easy interaction
- **Test Data Included** - Pre-configured mappings for popular companies

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Search API**: DuckDuckGo Search
- **Web Scraping**: BeautifulSoup4, Requests
- **Additional**: python-dotenv for configuration

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

## Usage

1. **Create and activate virtual environment**
   On Windows
    python -m venv venv
    venv\Scripts\activate
   
   On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    
3. **Install dependencies**
     pip install -r requirements.txt

4. **Start the backend server**
     cd backend
     python app.py

5. **Open the frontend**
     Open index.html in your web browser

6. **Search for personnel**
    Enter a company name (e.g., "Tesla", "Apple", "Google")
    Enter a designation (e.g., "CEO", "Founder", "CTO")
    Click "Search" and wait for results
